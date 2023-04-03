import pygame
from Fonts import *
from Message import Message
from queue import Queue
from Renderables import *


class ConfigurationStateManager:
    def __init__(self, incoming_queue, outgoing_queue):
        if not isinstance(incoming_queue, Queue):
            raise TypeError(
                "Invalid incoming_queue type for ConfigurationStateManager (expected queue.Queue, got {})".
                format(type(incoming_queue)))
        elif not isinstance(outgoing_queue, Queue):
            raise TypeError(
                "Invalid outgoing_queue type for ConfigurationStateManager (expected queue.Queue, got {})"
                .format(type(incoming_queue)))
        else:
            self.incoming_queue = incoming_queue
            self.outgoing_queue = outgoing_queue
            # These defaults are arbitrary and should be better specified elsewhere
            self.resolution = (640, 480)
            self.recording_vertical_scale = 0.5
            self.fret_count = 30
            self.recording_fall_time = 1.0
            self.chroma_key = pygame.color.Color(50, 50, 50)
            self.hue = 270
            self.rear_color = pygame.color.Color(0)
            self.middle_color = pygame.color.Color(0)
            self.front_color = pygame.color.Color(0)
            self.update_colors()
            self.intro_start_time = 1.0
            self.intro_length = 1.0
            self.intro_fade_time = 1.0
            self.header = header
            self.italic = italic
            self.regular = regular
            self.transition_length = 1.0
            self.logo = pygame.image.load("logo.svg")
            self.square_tone = False
            self.play_song = True
            self.play_tone = True
            self.skip_render = None
            self.outgoing_queue.put(Message(target="AnalysisStateManager",
                                            source="ConfigurationStateManager",
                                            message_type="Config",
                                            content=self))
            self.outgoing_queue.put(Message(target="GUIEventBroker",
                                            source="ConfigurationStateManager",
                                            message_type="Config",
                                            content=self))
            self.outgoing_queue.put(Message(target="SongSelectStateManager",
                                            source="ConfigurationStateManager",
                                            message_type="Config",
                                            content=self))
            self.outgoing_queue.put(Message(target="TitleScreenStateManager",
                                            source="ConfigurationStateManager",
                                            message_type="Config",
                                            content=self))

    def handle(self):
        if not self.incoming_queue.empty():
            message = self.incoming_queue.get()
            if message.type == "Get config":
                self.outgoing_queue.put(Message(target=message.source,
                                                source="ConfigurationStateManager",
                                                message_type="Config",
                                                content=self))
            elif message.type == "Get GUI update":
                if not self.skip_render:
                    to_draw = [BackgroundBox(50,
                                             56.25,
                                             95,
                                             82.5,
                                             4.625 / 95),
                               Button(2.5 + 10,
                                      2.5 + 5,
                                      20,
                                      10,
                                      "Back",
                                      20,
                                      7.5,
                                      self.regular,
                                      self.back),
                               Text(12.5,
                                    22.5,
                                    10,
                                    5,
                                    "UI Color: {}".format(self.hue),
                                    self.regular),
                               SlideBar(55,
                                        22.5,
                                        55,
                                        5,
                                        self.adjust_hue,
                                        self.hue / 3.60),
                               ArrowButton(23.75,
                                           22.5,
                                           5,
                                           5,
                                           self.subtract_hue_one,
                                           3),
                               ArrowButton(90,
                                           22.5,
                                           5,
                                           5,
                                           self.add_hue_one,
                                           1)]
                    self.outgoing_queue.put(Message(source="ConfigurationStateManager",
                                                    target="GUIEventBroker",
                                                    message_type="render",
                                                    content=to_draw))
                self.skip_render = False

    def update_colors(self):
        self.rear_color.hsva = (self.hue, 45, 100)
        self.middle_color.hsva = (self.hue, 70, 100)
        self.front_color.hsva = (self.hue, 100, 100)

    def back(self, event, renderable):
        if event.type == pygame.MOUSEBUTTONUP:
            self.outgoing_queue.put(Message(source="SongSelectStateManager",
                                            target="TitleScreenStateManager",
                                            message_type="Get GUI update",
                                            content=None))
            self.skip_render = True

    def adjust_hue(self, event, renderable):
        if type(renderable) == SlideBar and event.type == pygame.MOUSEMOTION and event.buttons[0]:
            self.hue = round(360 * (event.pos[0] - renderable.start_x) / (renderable.end_x - renderable.start_x))
            if self.hue < 0:
                self.hue = 0
            elif self.hue > 360:
                self.hue = 360
            self.update_colors()
    def subtract_hue_one(self, event, renderable):
        if event.type == pygame.MOUSEBUTTONUP:
            self.hue = max(self.hue - 1, 0)
            self.update_colors()

    def add_hue_one(self, event, renderable):
        if event.type == pygame.MOUSEBUTTONUP:
            self.hue = min(self.hue + 1, 360)
            self.update_colors()