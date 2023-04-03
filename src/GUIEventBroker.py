import pyaudio
import pygame
import Renderables
import wave
from math import floor
from Message import Message
import numpy as np
from queue import Queue
from Tab import pa_data_type_to_np
from time import time


class GUIEventBroker:

    def __init__(self, incoming_queue, outgoing_queue):
        if not isinstance(incoming_queue, Queue):
            raise TypeError("Invalid incoming_queue type for GUIEventBroker (expected queue.Queue, got {})".
                            format(type(incoming_queue)))
        elif not isinstance(outgoing_queue, Queue):
            raise TypeError("Invalid outgoing_queue type for GUIEventBroker (expected queue.Queue, got {})"
                            .format(type(incoming_queue)))
        else:
            self.incoming_queue = incoming_queue
            self.outgoing_queue = outgoing_queue

            # TODO: Replace with configuration from either a file or another state manager
            # A default set of config values could potentially be used in lieu of "real" values as well
            self.current_source = None
            self.last_frame_time = time()
            self.this_frame_time = self.last_frame_time
            self.average_frame_time = None
            self.frame_lengths = []
            self.p = pyaudio.PyAudio()
            self.playback_file = None
            self.playback_file_name = None
            self.out_stream = None
            self.playback_frame_duration = None
            self.playback_frames = None
            self.playback_pos = None
            self.playback_frame_num_bytes = None
            self.play_to_pos = None
            self.playback_format = None
            self.tab_object = None
            self.playback_num_channels = None
            self.playback_framerate = None
            self.tone_wave = None
            self.in_stream = None
            self.recording_data = None
            self.out_stream_done = None
            self.sending_recording = None
            self.input_latency = None
            self.recording_start_time = None
            self.playback_start_time = None
            self.gui_start_time = time()
            self.config = None
            self.screen = None

    def handle(self):
        if not self.incoming_queue.empty():
            message = self.incoming_queue.get()
            if message.type == "Config":
                self.config = message.content
            elif message.type == "render":
                if self.screen is None:
                    pygame.init()
                    self.screen = pygame.display.set_mode(self.config.resolution, pygame.RESIZABLE)
                    pygame.display.set_caption("S.T.R.U.M.")
                self.current_source = message.source
                self.draw_background()
                interactables = []
                # GUI event broker expects a list of Renderable objects in message content
                # Objects should be provided in the order in which they should be rendered
                for render_object in message.content:
                    if not type(render_object) in Renderables.available:
                        raise TypeError("Invalid render object type (got {})".format(type(render_object)))
                    else:
                        interactable_to_add = render_object.draw(self.screen, self.config)
                        if interactable_to_add is not None:
                            # Using a tuple here makes the pygame.rect.Rect returned hashable
                            interactables.append((interactable_to_add, render_object))
                pygame.display.flip()
                events = pygame.event.get()
                for event in events:
                    if event.type == pygame.QUIT:
                        self.quit()
                    elif event.type in (pygame.MOUSEBUTTONUP, pygame.MOUSEMOTION):
                        for interactable in interactables:
                            if interactable[0].bounding_box.collidepoint(event.pos[0], event.pos[1]):
                                interactable[1].function(event)
                self.outgoing_queue.put(Message(target=self.current_source,
                                                source="GUIEventBroker",
                                                message_type="Get GUI update",
                                                content=None))
                self.this_frame_time = time()
                self.frame_lengths.append(self.this_frame_time - self.last_frame_time)
                if len(self.frame_lengths) > 50:
                    self.frame_lengths.pop(0)
                self.average_frame_time = sum(self.frame_lengths) / len(self.frame_lengths)
                self.last_frame_time = self.this_frame_time
            elif message.type == "Prime playback":
                self.playback_file_name = message.content["song_file"]
                self.tab_object = message.content["tab_object"]
                self.playback_file = wave.open(self.playback_file_name, "rb")
                self.playback_frames = self.playback_file.readframes(self.playback_file.getnframes())
                self.playback_framerate = self.playback_file.getframerate()
                self.playback_frame_duration = 1.0 / float(self.playback_framerate)
                self.playback_format = self.p.get_format_from_width(self.playback_file.getsampwidth())
                self.playback_frame_num_bytes = int(len(self.playback_frames) / self.playback_file.getnframes())
                self.playback_num_channels = self.playback_file.getnchannels()
                self.tone_wave = self.tab_object.get_tone_wave(self.playback_framerate, self.playback_format,
                                                               self.config, self.playback_num_channels)
                if not self.config.play_song and self.config.play_tone:
                    self.playback_frames = self.tone_wave
                elif self.config.play_song and self.config.play_tone:
                    self.mix_tone(0.5)
                elif not self.config.play_song and not self.config.play_tone:
                    self.playback_frames = bytes()

                self.playback_pos = 0
                self.play_to_pos = 0
                self.out_stream_done = False
                self.sending_recording = False
                self.out_stream = self.p.open(format=self.playback_format,
                                              channels=self.playback_num_channels,
                                              rate=self.playback_framerate,
                                              output=True,
                                              stream_callback=self.playback_callback,
                                              start=False)
                self.playback_file.close()
            elif message.type == "Start playback":
                self.out_stream.start_stream()
            elif message.type == "Prime recording":
                # Recording should only start after playback has begun in order to use playback parameters
                self.in_stream = self.p.open(channels=2,
                                             input=True,
                                             stream_callback=self.recording_callback,
                                             rate=self.playback_framerate,
                                             format=self.playback_format,
                                             start=False)
                self.input_latency = self.in_stream.get_input_latency()
            elif message.type == "Start recording":
                self.in_stream.start_stream()
            elif message.type == "Update playback":
                play_to_time = message.content
                self.play_to_pos = floor(play_to_time / self.playback_frame_duration) * self.playback_frame_num_bytes
                positional_lag = self.playback_pos - self.play_to_pos
                # Resync if audio is drifting too far outside of tolerance
                if abs(positional_lag) > 8000:
                    self.playback_pos = self.play_to_pos
                    # print("Resync ({})".format(positional_lag))
            elif message.type == "Send recording":
                self.sending_recording = True
                while not self.out_stream_done:
                    pass
                self.sending_recording = None
                self.out_stream.close()
                self.out_stream = None
                self.in_stream.close()
                self.in_stream = None
                self.outgoing_queue.put(Message(target="AnalysisStateManager",
                                                source="GUIEventBroker",
                                                message_type="Start analysis",
                                                content={"latency": self.input_latency,
                                                         "data": self.recording_data,
                                                         "recording_start_time": self.recording_start_time,
                                                         "playback_start_time": self.playback_start_time,
                                                         "tone_wave": self.tone_wave,
                                                         "sample_rate": self.playback_framerate,
                                                         "sample_format": pa_data_type_to_np(self.playback_format),
                                                         "tab": message.content,
                                                         "original_sample_width": self.playback_frame_num_bytes}))
                self.input_latency = None
                self.recording_data = None
                self.recording_start_time = None
                self.playback_start_time = None
            elif message.type == "Quit":
                self.quit()

    def playback_callback(self, in_data, frame_count,  time_info, status):
        if self.playback_start_time is None:
            self.playback_start_time = time()
        if self.sending_recording:
            self.out_stream_done = True
            return bytes(), pyaudio.paComplete
        bytes_count = frame_count * self.playback_frame_num_bytes
        playback_buffer = self.playback_frames[self.playback_pos:min(self.playback_pos + bytes_count,
                                                                     len(self.playback_frames))]
        self.playback_pos = self.playback_pos + bytes_count
        if self.playback_pos >= len(self.playback_frames):
            self.out_stream_done = True
        return playback_buffer, pyaudio.paContinue

    def recording_callback(self, in_data, frame_count, time_info, status):
        if self.recording_data is None:
            self.recording_start_time = time()
            self.recording_data = in_data
        else:
            self.recording_data = self.recording_data + in_data
        return None, pyaudio.paContinue

    def quit(self):
        pygame.quit()
        if self.out_stream is not None:
            self.out_stream.close()
        if self.in_stream is not None:
            self.in_stream.close()
        self.p.terminate()
        exit()

    def mix_tone(self, song_volume):
        signal_1 = np.frombuffer(self.playback_frames, pa_data_type_to_np(self.playback_format)).copy()
        signal_2 = np.frombuffer(self.tone_wave, pa_data_type_to_np(self.playback_format))
        signal_1[:np.size(signal_2)] = (signal_1[:np.size(signal_2)] * song_volume) + (signal_2 * (1 - song_volume))
        self.playback_frames = pa_data_type_to_np(self.playback_format)(signal_1).tobytes()

    def draw_background(self):
        self.screen.fill(self.config.rear_color)
        now_time = time() - self.gui_start_time
        x_vals = np.arange(0 + now_time, (2 * np.pi) + now_time, 2 * np.pi / self.screen.get_width())
        y_vals = (np.sin(x_vals) * self.screen.get_height() * 0.03) + (self.screen.get_height() * 0.35)
        points = np.stack([(x_vals - now_time) * (self.screen.get_width() / (2 * np.pi)), y_vals]).T
        points = np.append(points, [[self.screen.get_width() - 1, self.screen.get_height() - 1],
                            [0, self.screen.get_height() - 1]], 0)
        pygame.draw.polygon(self.screen, self.config.middle_color, points)
        x_vals = np.arange(0 + (now_time * 6), (4 * np.pi) + (now_time * 6), 4 * np.pi / self.screen.get_width())
        y_vals = (np.sin(x_vals) * self.screen.get_height() * 0.03) + (self.screen.get_height() * 0.45)
        points = np.stack([(x_vals - (now_time * 6)) * (self.screen.get_width() / (4 * np.pi)), y_vals]).T
        points = np.append(points, [[self.screen.get_width() - 1, self.screen.get_height() - 1],
                            [0, self.screen.get_height() - 1]], 0)
        pygame.draw.polygon(self.screen, self.config.front_color, points)
