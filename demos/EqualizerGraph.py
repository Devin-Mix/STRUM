import numpy as np
import pyaudio
from scipy.fft import rfft, rfftfreq
import pygame
from pygame.locals import *

# Constants, should be replaced in an interactive deployment
LATENCY_SCALER = 12 # Weighs latency against pitch accuracy (higher number = higher latency, lower pitch accuracy)
BLOCK_SIZE = pow(2, LATENCY_SCALER) # Scales exponentially based on above
# Frequencies of each note in the second octave:
# TODO: Calculation of each frequency should be done in some sort of function rather than based solely off of the harmonics
frequencies = {"C": 65.406, "C#": 69.296, "D": 73.416, "D#": 77.782, "E": 82.407, "F": 87.307, "F#": 92.499, "G": 97.999, "G#": 103.826, "A": 110.0, "A#": 116.541, "B": 123.471}

def main():
    # Establish new pyaudio instance
    p = pyaudio.PyAudio()

    # Get number of devices
    device_count = p.get_device_count()

    # Establish list of devices
    device_names = []
    for ii in range(device_count):
        ii_device_info = p.get_device_info_by_index(ii)
        if not ii_device_info["name"] in device_names:
            device_names.append(ii_device_info["name"])

    # Prompt user for device to use
    print("Select device from list below:")
    for ii in range(len(device_names)):
        print("{}) {}".format(ii, device_names[ii]))
    device_name = device_names[int(input("Device number: "))]

    # Find device whose name matches device_name with lowest input latency
    minimum_device_latency = 1000
    target_device_info = None
    for ii in range(device_count):
        ii_device_info = p.get_device_info_by_index(ii)
        if ii_device_info["name"] == device_name and ii_device_info["defaultLowInputLatency"] < minimum_device_latency:
            minimum_device_latency = ii_device_info["defaultLowInputLatency"]
            target_device_info = ii_device_info

    # Check to make sure target device has been found...
    if target_device_info is None:
        raise NameError

    # Create input stream
    input_stream = p.open(round(target_device_info["defaultSampleRate"]),
                          # Sample rate of target device, rounded to nearest int
                          1,  # Number of channels
                          pyaudio.paInt16,  # Datatype of input
                          input=True, # Is this an input device?
                          input_device_index=target_device_info["index"], # Self-explanatory
                          frames_per_buffer=pow(2, LATENCY_SCALER + 2)  # Comment to remove buffer size limits
                          #                          (I think? This isn't clearly documented)
                          )

    # Things to do with the stream happen here...
    print("Stream started successfully!")
    try:
        # Setup of the pygame instance (note: no framerate management is done in this demo, but should be done in
        # production)
        pygame.init()
        screen = pygame.display.set_mode((800, 600))
        background = pygame.Surface(screen.get_size())
        background = background.convert()
        background.fill((0, 0, 0))
        # Highest amplitude recorded so far (used to scale display dynamically)
        peak = 0.0
        while True:
            # Poll (both so that Windows doesn't kill the instance prematurely & to enable the close button)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    input_stream.close()
                    pygame.quit()
                    exit()
            # TODO: Better polling of available samples without busy-waiting
            # This is a really bad way of doing things in a single-threaded environment and could introduce instability
            # in the framerate of projects that use it. If this is the approach used, multiprocessing is a must
            while input_stream.get_read_available() < BLOCK_SIZE:
                continue
            # Get appropriate amount of data from the input stream
            block_raw_data = np.frombuffer(input_stream.read(BLOCK_SIZE), np.int16)
            # Get the amplitudes and frequencies of the raw data from the (reverse) FFT
            block_amplitudes = np.abs(rfft(block_raw_data))
            block_frequencies = rfftfreq(BLOCK_SIZE, 1 / round(target_device_info["defaultSampleRate"]))
            notes = None
            # Draw over the background
            # TODO: This is a really bad way of doing things that mimics Processing more than PyGame. Functionally it's
            # fine, but in practice you would want to do something like blitting objects to the background itself before
            # blitting the background to the screen. See PyGame docs for more info.
            screen.blit(background, (0, 0))
            # Very bad pitch detection. We'll want to do better than this.
            for ii in range(4):
                for pitch in frequencies.keys():
                    octave_frequency = frequencies[pitch] * pow(2, ii)
                    nearest_frequency_index = (np.abs(block_frequencies - octave_frequency)).argmin()
                    if notes is None:
                        notes = np.array(block_amplitudes[nearest_frequency_index])
                    else:
                        notes = np.append(notes, np.array(block_amplitudes[nearest_frequency_index]))
            if notes[notes.argmax()] > peak:
                peak = notes[notes.argmax()]
            # Draw the output chart
            column_width = screen.get_width() / notes.shape[0]
            for ii in range(notes.shape[0]):
                pygame.draw.rect(screen, (0, 0, 255), Rect(ii * column_width, np.interp(notes[ii], [0, peak], [screen.get_height() - 1, 1]), column_width, screen.get_height() - np.interp(notes[ii], [0, peak], [screen.get_height() - 1, 1])))
            pygame.display.update()
    except:
        # Clean up before shutdown
        input_stream.close()


if __name__ == '__main__':
    main()
