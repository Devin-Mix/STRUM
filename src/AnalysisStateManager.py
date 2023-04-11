import wave
import numpy as np
from datetime import datetime
from math import floor, log10
from Message import Message
from queue import Queue
from Renderables import *
from scipy.fft import rfft, rfftfreq
from time import time

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
            self.analysing = None
            self.number_of_ffts_completed = None
            self.current_tab = None
            self.skip_render = None
            self.config = None
            self.first_session_render = True
            self.doing_fade_in = False
            self.now_time = None
            self.fade_in_start_time = None
            self.doing_fade_out = False
            self.fade_out_start_time = None

    def handle(self):
        if not self.incoming_queue.empty():
            message = self.incoming_queue.get()
            if message.type == "Config":
                self.config = message.content
            elif message.type == "Start analysis":
                self.now_time = time()
                if self.first_session_render:
                    self.first_session_render = False
                    self.doing_fade_in = True
                    self.fade_in_start_time = self.now_time
                self.analysing = True
                self.input_latency = message.content["latency"]
                self.recording_data_bytes = message.content["data"]
                self.original_sample_width = message.content["original_sample_width"]
                self.original_sample_format = message.content["sample_format"]
                self.recording_data_to_save = np.frombuffer(self.recording_data_bytes, message.content["sample_format"])
                self.recording_data = np.frombuffer(self.recording_data_bytes, message.content["sample_format"])[0::2]
                self.recording_data_normalized = self.recording_data / np.max(np.abs(self.recording_data))
                self.recording_start_time = message.content["recording_start_time"]
                self.playback_start_time = message.content["playback_start_time"]
                self.tone_wave = np.frombuffer(message.content["tone_wave"], message.content["sample_format"])[0::2]
                self.tone_wave_normalized = self.tone_wave / np.max(np.abs(self.tone_wave))
                self.framerate = message.content["sample_rate"]
                self.current_tab = message.content["tab"]
                self.load_percent = 0.0
                self.total_input_delay_seconds = self.recording_start_time - self.playback_start_time
                self.total_input_delay_samples = 2 * floor(self.total_input_delay_seconds * self.framerate)
                self.tone_wave = self.tone_wave[self.total_input_delay_samples:]
                if np.size(self.tone_wave) > np.size(self.recording_data):
                    self.tone_wave = self.tone_wave[:np.size(self.recording_data)]
                else:
                    self.recording_data = self.recording_data[:np.size(self.tone_wave)]
                self.precision_level = 16
                self.current_num_divisions = 1
                self.current_division_num = 0
                self.number_of_ffts = np.sum(np.arange(self.precision_level + 1))
                self.number_of_ffts_completed = 0
                self.dynamics_scores = {1: []}
                self.accuracy_scores = {1: []}
                to_draw = [LoadBar(50, 95.0, 10.0, self.load_percent)]
                if self.doing_fade_in:
                    if self.now_time - self.fade_in_start_time >= self.config.fade_length:
                        self.doing_fade_in = False
                    else:
                        to_draw.append(Blackout(self.now_time - self.fade_in_start_time, self.config.fade_length))
                        for ii in range(len(to_draw)):
                            to_draw[ii].function = no_function
                self.outgoing_queue.put(Message(target="GUIEventBroker",
                                                source="AnalysisStateManager",
                                                message_type="render",
                                                content=to_draw))

            if message.type == "Get GUI update":
                self.now_time = time()
                if self.first_session_render:
                    self.first_session_render = False
                    self.doing_fade_in = True
                    self.fade_in_start_time = self.now_time
                if self.analysing:
                    low_index = floor(self.current_division_num * np.size(self.tone_wave) / self.current_num_divisions)
                    high_index = floor((self.current_division_num + 1) * np.size(self.tone_wave) / self.current_num_divisions)
                    dynamics_score, accuracy_score = get_scores(low_index, high_index, self.recording_data_normalized, self.tone_wave_normalized, self.framerate)
                    self.dynamics_scores[self.current_num_divisions].append(dynamics_score)
                    self.accuracy_scores[self.current_num_divisions].append(accuracy_score)
                    self.load_percent = min(self.load_percent + (100.0 / self.number_of_ffts), 100.0)
                    self.current_division_num = self.current_division_num + 1
                    self.number_of_ffts_completed = self.number_of_ffts_completed + 1
                    if self.current_division_num == self.current_num_divisions:
                        self.current_division_num = 0
                        self.current_num_divisions = self.current_num_divisions + 1
                        self.dynamics_scores[self.current_num_divisions] = []
                        self.accuracy_scores[self.current_num_divisions] = []
                    if self.number_of_ffts == self.number_of_ffts_completed:
                        self.analysing = False
                        self.number_of_ffts_completed = None
                        self.accuracy_scores.pop(self.current_num_divisions)
                        self.dynamics_scores.pop(self.current_num_divisions)
                        self.current_num_divisions = self.current_num_divisions - 1
                    to_draw = [LoadBar(50.0, 95.0, 10.0, self.load_percent),
                               Text(50.0, 50.0, 95.0, 10.0, "Analysing... {}%"
                                    .format(round(self.load_percent, 1)), self.config.header)]
                else:
                    to_draw = [BackgroundBox(50, 43.75, 95, 82.5, 4.625 / 95),
                               Text(50.0, 10, 85.0, 10, "Analysis Results", self.config.header),
                               Text(50.0, 20.0, 85.0, 5.0, "{} by {}".format(self.current_tab.title, self.current_tab.artist), self.config.italic),
                               Text(50.0, 27.5, 40.0, 5.0, "Number of analysis segments: {}".format(self.current_num_divisions), self.config.italic),
                               ArrowButton(25, 27.5, 5, 5, self.decrease_num_analysis_segments, 3),
                               ArrowButton(75, 27.5, 5, 5, self.increase_num_analysis_segments, 1),
                               Text(50.0, 35.0, 85.0, 5.0, "Dynamic Accuracy:", self.config.regular),
                               AnalysisGraph(47.5, 85.0, 15, self.dynamics_scores[self.current_num_divisions], self.config.regular, self.config.italic, self.current_tab.length),
                               Text(50.0, 60, 95.0, 5.0, "Pitch / Tempo Accuracy:",
                                    self.config.regular),
                               AnalysisGraph(72.5, 85.0, 15, self.accuracy_scores[self.current_num_divisions], self.config.regular, self.config.italic, self.current_tab.length),
                               Button(25.625, 92.5, 46.25, 10, "Save Recording", self.config.regular, self.save_recording),
                               Button(74.375, 92.5, 46.25, 10, "Return", self.config.regular, self.return_to_menu)]

                if self.doing_fade_in:
                    if self.now_time - self.fade_in_start_time >= self.config.fade_length:
                        self.doing_fade_in = False
                    else:
                        to_draw.append(
                            Blackout(self.now_time - self.fade_in_start_time, self.config.fade_length))
                        for ii in range(len(to_draw)):
                            to_draw[ii].function = no_function
                elif self.doing_fade_out:
                    if self.now_time - self.fade_out_start_time >= self.config.fade_length:
                        self.doing_fade_out = False
                        self.outgoing_queue.put(Message(target="SongSelectStateManager",
                                                        source="AnalysisStateManager",
                                                        message_type="Get GUI update",
                                                        content={"events": []}))
                        self.first_session_render = True
                        self.skip_render = True
                    else:
                        to_draw.append(
                            Blackout(self.now_time - self.fade_out_start_time, self.config.fade_length, False))
                        for ii in range(len(to_draw)):
                            to_draw[ii].function = no_function
                if not self.skip_render:
                    self.outgoing_queue.put(Message(target="GUIEventBroker",
                                                    source="AnalysisStateManager",
                                                    message_type="render",
                                                    content=to_draw))
                self.skip_render = False

    def save_recording(self, event, renderable):
        if event.type == pygame.MOUSEBUTTONUP:
            datetime_info = datetime.now()
            filename = "../exports/{}-{}-{}_{}-{}-{}-{}.wav".format(datetime_info.year,
                                                                    datetime_info.month,
                                                                    datetime_info.day,
                                                                    datetime_info.hour,
                                                                    datetime_info.minute,
                                                                    datetime_info.second,
                                                                    datetime_info.microsecond)
            with wave.open(filename, "wb") as file:
                file.setnchannels(2)
                file.setsampwidth(np.dtype(self.original_sample_format).itemsize)
                file.setframerate(self.framerate)
                file.writeframes(self.recording_data_to_save.tobytes())

    def return_to_menu(self, event, renderable):
        if event.type == pygame.MOUSEBUTTONUP:
            self.doing_fade_out = True
            self.fade_out_start_time = self.now_time

    def decrease_num_analysis_segments(self, event, renderable):
        if event.type == pygame.MOUSEBUTTONUP:
            self.current_num_divisions = max(1, self.current_num_divisions - 1)

    def increase_num_analysis_segments(self, event, renderable):
        if event.type == pygame.MOUSEBUTTONUP:
            self.current_num_divisions = min(self.current_num_divisions + 1, self.precision_level)


def get_scores(low_index, high_index, recording_data_normalized, tone_wave_normalized, framerate):
    recording_amplitudes = np.abs(rfft(recording_data_normalized[low_index:high_index]))
    tone_amplitudes = np.abs(rfft(tone_wave_normalized[low_index:high_index]))
    frequencies = rfftfreq(high_index - low_index, 1 / int(framerate))
    difference_amplitudes = np.abs(recording_amplitudes - tone_amplitudes)

    difference_power = np.sum(difference_amplitudes)
    tone_power = np.sum(tone_amplitudes)
    recording_power = np.sum(recording_amplitudes)
    if tone_power == 0 and recording_power > 0:
        dynamics_score = 0.0
    elif tone_power == 0 and recording_power == 0:
        dynamics_score = 1.0
    else:
        dynamics_ratio = abs(recording_power / tone_power)
        dynamics_score = 1.0 / pow(log10(abs(dynamics_ratio - 1.0) + 10.0), 100.0)
    if recording_power == 0 and difference_power > 0:
        accuracy_score = 0.0
    elif recording_power == 0 and difference_power == 0:
        accuracy_score = 1.0
    else:
        accuracy_ratio = abs(difference_power / recording_power)
        accuracy_score = 1.0 - (1.0 / pow(log10(abs(accuracy_ratio - 1.0) + 10.0), 100.0))
    return dynamics_score, accuracy_score
