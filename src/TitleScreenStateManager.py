from math import pi, sin
from Message import Message
from queue import Queue
from Renderables import *
from time import time


class TitleScreenStateManager:
    def __init__(self, incoming_queue, outgoing_queue):
        if not isinstance(incoming_queue, Queue):
            raise TypeError("Invalid incoming_queue type for SongSelectStateManager (expected queue.Queue, got {})".
                            format(type(incoming_queue)))
        elif not isinstance(outgoing_queue, Queue):
            raise TypeError("Invalid outgoing_queue type for SongSelectStateManager (expected queue.Queue, got {})"
                            .format(type(incoming_queue)))
        else:
            self.incoming_queue = incoming_queue
            self.outgoing_queue = outgoing_queue
            self.config = None
            self.doing_intro = None
            self.intro_start_time = None
            self.intro_end_time = None
            self.fade_done = None
            self.skip_render = None

    def handle(self):
        if not self.incoming_queue.empty():
            message = self.incoming_queue.get()
            if message.type == "Config":
                self.config = message.content
            elif message.type == "Get GUI update":
                if not self.skip_render:
                    if self.doing_intro is None:
                        self.doing_intro = True
                        self.intro_start_time = time()
                    now_time = time() - self.intro_start_time
                    if self.doing_intro:
                        to_draw = [Blackout(function=self.skip_intro)]
                        if self.config.intro_start_time <= now_time < self.config.intro_start_time + self.config.intro_length:
                            to_draw.append(TitleText(1))
                        elif self.config.intro_start_time + self.config.intro_length <= now_time < self.config.intro_start_time + self.config.intro_length + self.config.intro_fade_time:
                            to_draw.append(TitleText(1 - ((now_time - (self.config.intro_start_time + self.config.intro_length)) / self.config.intro_fade_time)))
                        elif self.config.intro_start_time + self.config.intro_length + self.config.intro_fade_time <= now_time:
                            self.intro_end_time = now_time
                            self.doing_intro = False
                            self.fade_done = False
                    if not self.doing_intro:
                        to_draw = [Button(25.625, 92.5, 46.25, 10, "Config", 46.25, 7.5, self.config.regular, self.launch_config),
                                   Button(74.375, 92.5, 46.25, 10, "Song Select", 46.25, 7.5, self.config.regular, self.launch_song_select),
                                   Logo(50, 40, 95, 80, 5 * sin(1.5 * time()))]
                        if not self.fade_done and now_time - self.intro_end_time < self.config.transition_length:
                            to_draw.append(Blackout(now_time - self.intro_end_time, self.config.transition_length))
                        elif not self.fade_done:
                            self.fade_done = True
                    self.outgoing_queue.put(Message(source="TitleScreenStateManager",
                                                    target="GUIEventBroker",
                                                    message_type="render",
                                                    content=to_draw))
                self.skip_render = False

    def launch_config(self, event):
        if event.type == pygame.MOUSEBUTTONUP:
            self.outgoing_queue.put(Message(target="ConfigurationStateManager",
                                            source="TitleScreenStateManager",
                                            message_type="Get GUI update",
                                            content=None))
            self.skip_render = True

    def launch_song_select(self, event):
        if event.type == pygame.MOUSEBUTTONUP:
            self.outgoing_queue.put(Message(source="TitleScreenStateManager",
                                            target="SongSelectStateManager",
                                            message_type="Get GUI update",
                                            content=None))
            self.skip_render = True
    def skip_intro(self, event):
        if event.type == pygame.MOUSEBUTTONUP:
            if self.doing_intro is None or self.doing_intro or self.fade_done is None or not self.fade_done:
                 self.doing_intro = False
                 self.fade_done = True