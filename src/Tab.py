from math import floor
import numpy as np


def pa_data_type_to_np(pyaudio_data_type):
    if pyaudio_data_type == 1:
        np_data_type = np.float32
    elif pyaudio_data_type == 2:
        np_data_type = np.int32
    elif pyaudio_data_type == 4:
        np_data_type = np.int24
    elif pyaudio_data_type == 8:
        np_data_type = np.int16
    elif pyaudio_data_type == 16:
        np_data_type = np.int8
    elif pyaudio_data_type == 32:
        np_data_type = np.uint8
    else:
        raise ValueError("Invalid data type for generating tone wave ({})".format(pyaudio_data_type))
    return np_data_type


class Tab:
    def __init__(self, file_to_open):
        if type(file_to_open) != str:
            raise TypeError("Invalid argument for Tab.__init__(str) (Expected str, got {}".format(type(file_to_open)))
        with open(file_to_open, "r") as f:
            raw_data = f.read().splitlines()
            f.close()
        parsing_header = True
        self.tuning = [0, 0, 0, 0, 0, 0]
        self.bpm = 120
        self.artist = None
        self.title = None
        scan_time = 0.0
        self.chords = []
        for line in raw_data:
            if parsing_header:
                if line == "///":
                    parsing_header = False
                elif len(line) > 7 and line[0:7] == "Tuning=":
                    try:
                        t = [int(i) for i in line.split("Tuning=")[1].split(",")]
                    except ValueError:
                        print("ValueError setting tuning for {} (\"{}\"), discarding tuning".format(file_to_open, line))
                        continue
                    if len(t) != 6:
                        print("Invalid number of tuning arguments for {} (\"{}\"), discarding tuning".
                              format(file_to_open, line))
                    else:
                        self.tuning = t
                elif len(line) > 4 and line[0:4] == "BPM=":
                    try:
                        self.bpm = float(line.split("BPM=")[1])
                    except ValueError:
                        print("ValueError setting tempo for {} (\"{}\"), discarding tempo".format(file_to_open, line))
                elif len(line) > 10 and line[0:10] == "Song file=":
                    self.song_file = str(line.split("Song file=")[1])
                elif len(line) > 6 and line[0:6] == "Title=":
                    self.title = line.split("Title=")[1]
                elif len(line) > 7 and line[0:7] == "Artist=":
                    self.artist = line.split("Artist=")[1]
                else:
                    print("Invalid header argument detected for {} (\"{}\"), disregarding...".
                          format(file_to_open, line))
            else:
                if len(line) < 6:
                    print("Line too short in {} (\"{}\"), disregarding...".format(file_to_open, line))
                else:
                    line_chord = Chord(line)
                    chord_len_sec = pow(self.bpm * (1.0 / 60.0), -1.0) * line_chord.chord_len
                    self.chords.append((line_chord, scan_time, chord_len_sec))
                    scan_time = scan_time + chord_len_sec

    def get_next_chords(self, current_time):
        return [i for i in self.chords if i[1] >= current_time]

    def midi_number_to_frequency(self, string_number, fret_number):
        default_midi_numbers = [40, 45, 50, 55, 59, 64]
        target_midi_number = default_midi_numbers[string_number] + self.tuning[string_number] + fret_number
        return 440 * pow(2, (target_midi_number - 69) / 12)

    def get_tone_wave(self, sample_rate, pyaudio_data_type, num_channels=2):
        output_wave = None
        last_output_chunk_num_samples = None
        output_chunk_count = 0
        for group in self.chords:
            output_chunk = None
            chord = group[0]
            chord_len = group[2]
            samples = None
            num_active_strings = chord.play_string.count(True)
            for i in range(6):
                if chord.play_string[i]:
                    string_frequency = self.midi_number_to_frequency(i, chord.string_fret[i])
                    # Big credit to
                    # https://stackoverflow.com/questions/48043004/how-do-i-generate-a-sine-wave-using-python
                    samples = np.arange(chord_len * sample_rate) / sample_rate
                    last_output_chunk_num_samples = np.size(samples)
                    if output_chunk is None:
                        output_chunk = np.sin(2 * np.pi * string_frequency * samples) / num_active_strings
                    else:
                        output_chunk = output_chunk + \
                                       (np.sin(2 * np.pi * string_frequency * samples) / num_active_strings)
                else:
                    continue

            if output_wave is not None:
                mix_chunk = None
                count_samples_to_mix = floor(-last_output_chunk_num_samples / 4)
                for i in range(6):
                    if chord.play_string[i]:
                        string_frequency = self.midi_number_to_frequency(i, chord.string_fret[i])
                        # Big credit to
                        # https://stackoverflow.com/questions/48043004/how-do-i-generate-a-sine-wave-using-python
                        mix_samples = np.arange(count_samples_to_mix, 0) / sample_rate
                        if mix_chunk is None:
                            mix_chunk = np.sin(2 * np.pi * string_frequency * mix_samples) / num_active_strings
                        else:
                            mix_chunk = mix_chunk + \
                                           (np.sin(2 * np.pi * string_frequency * mix_samples) / num_active_strings)
                    else:
                        continue
                output_wave[count_samples_to_mix:] = output_wave[count_samples_to_mix:] * \
                    np.arange(1, 0, 1 / count_samples_to_mix)
                mix_chunk = mix_chunk * np.arange(0, 1, abs(1 / count_samples_to_mix))
                output_wave[count_samples_to_mix:] = output_wave[count_samples_to_mix:] + mix_chunk
                last_output_chunk_num_samples = np.size(samples)
            else:
                last_output_chunk_num_samples = np.size(samples)

            if output_chunk is None and output_wave is None:
                output_wave = np.zeros(floor(chord_len * sample_rate))
            elif output_chunk is None and output_wave is not None:
                output_wave = np.concatenate([output_wave, np.zeros(chord_len * sample_rate)])
            elif output_chunk is not None and output_wave is None:
                output_wave = output_chunk
            else:
                output_wave = np.concatenate([output_wave, output_chunk])

            output_chunk_count = output_chunk_count + 1

        count_samples_to_mix = floor(-last_output_chunk_num_samples / 4)
        output_wave[count_samples_to_mix:] = output_wave[count_samples_to_mix:] * np.arange(1, 0,
                                                                                            1 / count_samples_to_mix)

        # with wave.open("output_tone.wav".format(output_chunk_count), "wb") as file:
        #     file.setnchannels(1)
        #     file.setsampwidth(np.dtype(pa_data_type_to_np(pyaudio_data_type)).itemsize)
        #     file.setframerate(sample_rate)
        #     np_data_type = pa_data_type_to_np(pyaudio_data_type)
        #     print("Tone wave bytes per sample: {}".format(np.dtype(np_data_type).itemsize))
        #     if np_data_type is np.uint8:
        #         scaler = np.iinfo(np_data_type).max
        #     else:
        #         scaler = min(abs(np.iinfo(np_data_type).min), abs(np.iinfo(np_data_type).max))
        #     file.writeframes(pa_data_type_to_np(pyaudio_data_type)(output_wave * scaler).tobytes())

        to_flatten = []
        for i in range(num_channels):
            to_flatten.append(output_wave)
        output_wave = np.array(to_flatten).T.flatten()

        np_data_type = pa_data_type_to_np(pyaudio_data_type)
        if np_data_type is np.uint8:
            scaler = np.iinfo(np_data_type).max
        else:
            scaler = min(abs(np.iinfo(np_data_type).min), abs(np.iinfo(np_data_type).max))
        output_wave = output_wave * scaler
        return np_data_type(output_wave).tobytes()


class Chord:
    def __init__(self, chord_string):
        strings_string = chord_string[0:6]
        length_string = chord_string[6:]
        self.play_string = [i != "|" for i in strings_string]
        self.string_fret = []
        for i in strings_string:
            if i == "|":
                self.string_fret.append(0)
            else:
                self.string_fret.append(int(i))
        self.chord_len = 0.0
        for tie_part in length_string.split("+"):
            num_hyphens = tie_part.count("-")
            num_periods = tie_part.count(".")
            note_len = 1.0 / pow(2.0, num_hyphens)
            dots_len = 0.0
            for i in range(num_periods):
                dots_len = dots_len + (note_len * (1.0 / pow(2.0, i + 1)))
            self.chord_len = self.chord_len + note_len + dots_len
        self.chord_len = self.chord_len * 4.0
