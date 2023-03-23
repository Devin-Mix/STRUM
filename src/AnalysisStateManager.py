import numpy as np
from math import floor, log10
from Message import Message
from queue import Queue
from Renderables import *
from scipy.fft import rfft, rfftfreq

class AnalysisStateManager:
    def __init__(self, incoming_queue, outgoing_queue):
        if not isinstance(incoming_queue, Queue):
            raise TypeError("Invalid incoming_queue type for RecordingStateManager (expected queue.Queue, got {})".
                            format(type(incoming_queue)))
        elif not isinstance(outgoing_queue, Queue):
            raise TypeError("Invalid outgoing_queue type for RecordingStateManager (expected queue.Queue, got {})"
                            .format(type(incoming_queue)))
        else:
            self.incoming_queue = incoming_queue
            self.outgoing_queue = outgoing_queue
            self.input_latency = None
            self.recording_data = None
            self.recording_start_time = None
            self.playback_start_time = None
            self.tone_wave = None
            self.load_percent = None
            self.total_input_delay_seconds = None
            self.framerate = None
            self.total_input_delay_samples = None
            self.precision_level = None
            self.number_of_ffts = None
            self.current_num_divisions = None

    def handle(self):
        if not self.incoming_queue.empty():
            message = self.incoming_queue.get()
            if message.type == "Start analysis":
                self.input_latency = message.content["latency"]
                self.recording_data = np.frombuffer(message.content["data"], message.content["sample_format"])[0::2]
                self.recording_data_normalized = self.recording_data / np.max(np.abs(self.recording_data))
                self.recording_start_time = message.content["recording_start_time"]
                self.playback_start_time = message.content["playback_start_time"]
                self.tone_wave = np.frombuffer(message.content["tone_wave"], message.content["sample_format"])[0::2]
                self.tone_wave_normalized = self.tone_wave / np.max(np.abs(self.tone_wave))
                self.framerate = message.content["sample_rate"]
                self.load_percent = 0.0
                print("Input latency: {}, Input start time: {}, Output start time: {}".format(self.input_latency, self.recording_start_time, self.playback_start_time))
                self.total_input_delay_seconds = self.recording_start_time - self.playback_start_time
                self.total_input_delay_samples = 2 * floor(self.total_input_delay_seconds * self.framerate)
                self.tone_wave = self.tone_wave[self.total_input_delay_samples:]
                if np.size(self.tone_wave) > np.size(self.recording_data):
                    self.tone_wave = self.tone_wave[:np.size(self.recording_data)]
                else:
                    self.recording_data = self.recording_data[:np.size(self.tone_wave)]
                self.precision_level = 8
                self.current_num_divisions = 1
                self.current_division_num = 0
                self.number_of_ffts = np.sum(np.arange(self.precision_level + 1))
                print(self.number_of_ffts)
                self.outgoing_queue.put(Message(target="GUIEventBroker",
                                                source="AnalysisStateManager",
                                                message_type="render",
                                                content=[LoadBar(45.0, 95.0, 10.0, self.load_percent)]))

            if message.type == "Get GUI update":
                low_index = floor(self.current_division_num * np.size(self.tone_wave) / self.current_num_divisions)
                high_index = floor((self.current_division_num + 1) * np.size(self.tone_wave) / self.current_num_divisions)
                dynamics_score, accuracy_score = get_scores(low_index, high_index, self.tone_wave_normalized, self.tone_wave_normalized, self.framerate)
                print("Dynamics score for segment {} of {}: {}".format(self.current_division_num + 1, self.current_num_divisions, dynamics_score))
                print("Accuracy score for segment {} of {}: {}".format(self.current_division_num + 1, self.current_num_divisions, accuracy_score))
                self.load_percent = self.load_percent + (100.0 / self.number_of_ffts)
                self.current_division_num = self.current_division_num + 1
                if self.current_division_num == self.current_num_divisions:
                    self.current_division_num = 0
                    self.current_num_divisions = self.current_num_divisions + 1
                if round(self.load_percent) >= 100.0:
                    self.outgoing_queue.put(Message(target="GUIEventBroker",
                                                    source="AnalysisStateManager",
                                                    message_type="Quit",
                                                    content=None))
                else:
                    self.outgoing_queue.put(Message(target="GUIEventBroker",
                                                    source="AnalysisStateManager",
                                                    message_type="render",
                                                    content=[LoadBar(45.0, 95.0, 10.0, self.load_percent)]))


def get_scores(low_index, high_index, recording_data_normalized, tone_wave_normalized, framerate):
    recording_amplitudes = np.abs(rfft(recording_data_normalized[low_index:high_index]))
    tone_amplitudes = np.abs(rfft(tone_wave_normalized[low_index:high_index]))
    frequencies = rfftfreq(high_index - low_index, 1 / int(framerate))
    difference_amplitudes = abs(recording_amplitudes - tone_amplitudes)
    difference_power = np.sum(difference_amplitudes)
    tone_power = np.sum(tone_amplitudes)
    recording_power = np.sum(recording_amplitudes)
    dynamics_ratio = abs(recording_power / tone_power)
    dynamics_score = 1.0 / pow(log10(abs(dynamics_ratio - 1.0) + 10.0), 100.0)
    accuracy_ratio = abs(difference_power / tone_power)
    accuracy_score = 1.0 - (1.0 / pow(log10(abs(accuracy_ratio - 1.0) + 10.0), 100.0))
    return dynamics_score, accuracy_score
