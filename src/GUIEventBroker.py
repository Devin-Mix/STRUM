import pyaudio
import pygame
import Renderables
import wave
from math import floor
from Message import Message
from queue import Queue
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
            self.config = {"resolution": (640, 480),
                           "background color": "blue"}
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

            pygame.init()
            self.screen = pygame.display.set_mode(self.config["resolution"])
            pygame.display.set_caption("S.T.R.U.M.")

    def handle(self):
        if not self.incoming_queue.empty():
            message = self.incoming_queue.get()
            if message.type == "render":
                self.current_source = message.source
                self.screen.fill(self.config["background color"])
                # GUI event broker expects a list of Renderable objects in message content
                # Objects should be provided in the order in which they should be rendered
                for render_object in message.content:
                    if not type(render_object) in Renderables.available:
                        raise TypeError("Invalid render object type (got {})".format(type(render_object)))
                    else:
                        render_object.draw(self.screen)
                pygame.display.flip()
                events = pygame.event.get()
                for event in events:
                    if event.type == pygame.QUIT:
                        self.quit()
                self.outgoing_queue.put(Message(target=self.current_source,
                                                source="GUIEventBroker",
                                                message_type="Get GUI update",
                                                content=events))
                self.this_frame_time = time()
                self.frame_lengths.append(self.this_frame_time - self.last_frame_time)
                if len(self.frame_lengths) > 50:
                    self.frame_lengths.pop(0)
                self.average_frame_time = sum(self.frame_lengths) / len(self.frame_lengths)
                self.last_frame_time = self.this_frame_time
            elif message.type == "Start playback":
                self.playback_file_name = message.content
                self.playback_file = wave.open(self.playback_file_name, "rb")
                self.playback_frame_duration = 1.0 / float(self.playback_file.getframerate())
                self.out_stream = self.p.open(format=self.p.get_format_from_width(self.playback_file.getsampwidth()),
                                              channels=self.playback_file.getnchannels(),
                                              rate=self.playback_file.getframerate(),
                                              output=True)
            elif message.type == "Update playback":
                play_to_time = message.content
                play_to_pos = floor(play_to_time / self.playback_frame_duration)
                if play_to_pos > 0:
                    while self.playback_file.tell() <= play_to_pos:
                        self.out_stream.write(self.playback_file.readframes(pow(2, 0)))
            elif message.type == "Quit":
                self.quit()

    def quit(self):
        pygame.quit()
        if self.playback_file is not None:
            self.playback_file.close()
        if self.out_stream is not None:
            self.out_stream.close()
        self.p.terminate()
        exit()