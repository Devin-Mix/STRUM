from Message import Message
from os import scandir
from queue import Queue
from Renderables import *
from Tab import Tab
from time import time


class SongSelectStateManager:
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
        self.scroll_time = 0.125
        self.tab_names = []
        self.skip_render = None
        self.song_list_index = 0
        self.scrolling = False
        self.last_scroll_start = None
        self.scroll_direction_is_up = True
        tab_scanner = scandir("../test")
        for scanned_object in tab_scanner:
            if scanned_object.is_file() and ".txt" in scanned_object.name:
                self.tab_names.append("../test/{}".format(scanned_object.name))
        self.tab_objects = []
        if not self.tab_names == []:
            for ii in range(4):
                self.tab_objects.append(Tab(self.tab_names[ii % len(self.tab_names)]))
        else:
            self.tab_objects = None
        self.button_functions = [self.select_tab_one,
                                 self.select_tab_two,
                                 self.select_tab_three,
                                 self.select_tab_four,
                                 self.select_tab_five]
        self.current_tab_object = None
        self.leaving_tab_object = None
        self.config = None

    def handle(self):
        if not self.incoming_queue.empty():
            message = self.incoming_queue.get()
            if message.type == "Config":
                self.config = message.content
            elif message.type == "Get GUI update":
                to_draw = [Button(2.5 + 10,
                                  2.5 + 5,
                                  20,
                                  10,
                                  "Back",
                                  20,
                                  7.5,
                                  self.config.regular,
                                  self.back)]
                if self.current_tab_object is not None:
                    to_draw.append(BackgroundBox(25,
                                                 50,
                                                 45,
                                                 70))
                    to_draw.append(Text(25,
                                        25,
                                        35,
                                        10,
                                        "{}".format(self.current_tab_object.title),
                                        self.config.header))
                    to_draw.append(Text(25,
                                        35,
                                        40,
                                        5,
                                        "{}".format(self.current_tab_object.artist),
                                        self.config.italic))
                    to_draw.append(Text(25,
                                        40,
                                        40,
                                        5,
                                        "{} BPM".format(self.current_tab_object.bpm),
                                        self.config.italic))
                    to_draw.append(Button(25,
                                          100 - 2.5 - 5,
                                          45,
                                          10,
                                          "Start",
                                          40,
                                          7.5,
                                          self.config.regular,
                                          self.start))
                    to_draw.append(Text(20,
                                        47.5,
                                        25,
                                        5,
                                        "Play studio track:",
                                        self.config.regular))
                    to_draw.append(CheckBox(35,
                                            47.5,
                                            5,
                                            5,
                                            self.toggle_song,
                                            self.config.play_song))
                    if self.config.play_tone:
                        if self.config.square_tone:
                            tone_style = "Square"
                        else:
                            tone_style = "Sine"
                    else:
                        tone_style = "Off"
                    to_draw.append(Text(25,
                                        55,
                                        40,
                                        5,
                                        "Tone wave style: {}".format(tone_style),
                                        self.config.regular))
                    to_draw.append(CheckBox(15,
                                            60,
                                            5,
                                            5,
                                            self.tone_wave_off,
                                            not self.config.play_tone))
                    to_draw.append(CheckBox(25,
                                            60,
                                            5,
                                            5,
                                            self.sine_tone_on,
                                            (not self.config.square_tone) and self.config.play_tone))
                    to_draw.append(CheckBox(35,
                                            60,
                                            5,
                                            5,
                                            self.square_tone_on,
                                            self.config.square_tone and self.config.play_tone))
                to_draw.append(ArrowButton(100 - 2.5 - (45 / 2),
                                           18.75,
                                           45,
                                           10,
                                           self.scroll_up,
                                           0))
                to_draw.append(ArrowButton(100 - 2.5 - (45 / 2),
                                           100 - 18.75,
                                           45,
                                           10,
                                           self.scroll_down,
                                           2))
                time_now = time()
                if self.scrolling and time_now - self.last_scroll_start > self.scroll_time:
                    self.scrolling = False
                    self.leaving_tab_object = None
                if self.scrolling:
                    if self.scroll_direction_is_up:
                        to_draw.append(FadeOutButton(100 - 2.5 - (45 / 2),
                                                     31.25,
                                                     45,
                                                     10,
                                                     self.leaving_tab_object.title,
                                                     40,
                                                     7.5,
                                                     self.config.italic,
                                                     self.button_functions[0],
                                                     time_now - self.last_scroll_start,
                                                     self.scroll_time))
                        to_draw.append(FadeInButton(100 - 2.5 - (45 / 2),
                                                    100 - 31.25,
                                                    45,
                                                    10,
                                                    self.tab_objects[-1].title,
                                                    40,
                                                    7.5,
                                                    self.config.italic,
                                                    self.button_functions[-1],
                                                    time_now - self.last_scroll_start,
                                                    self.scroll_time))
                        for ii in range(3):
                            to_draw.append(Button(100 - 2.5 - (45 / 2),
                                                  43.75 + (ii * 12.5) - (12.5 * (time_now - self.last_scroll_start) / self.scroll_time),
                                                  45,
                                                  10,
                                                  self.tab_objects[ii].title,
                                                  40,
                                                  7.5,
                                                  self.config.italic,
                                                  self.button_functions[ii]))
                    else:
                        to_draw.append(FadeInButton(100 - 2.5 - (45 / 2),
                                                    31.25,
                                                    45,
                                                    10,
                                                    self.tab_objects[0].title,
                                                    40,
                                                    7.5,
                                                    self.config.italic,
                                                    self.button_functions[0],
                                                    time_now - self.last_scroll_start,
                                                    self.scroll_time))
                        to_draw.append(FadeOutButton(100 - 2.5 - (45 / 2),
                                                     100 - 31.25,
                                                     45,
                                                     10,
                                                     self.leaving_tab_object.title,
                                                     40,
                                                     7.5,
                                                     self.config.italic,
                                                     self.button_functions[-1],
                                                     time_now - self.last_scroll_start,
                                                     self.scroll_time))
                        for ii in range(3):
                            to_draw.append(Button(100 - 2.5 - (45 / 2),
                                                  31.25 + (ii * 12.5) + (12.5 * (time_now - self.last_scroll_start) / self.scroll_time),
                                                  45,
                                                  10,
                                                  self.tab_objects[ii + 1].title,
                                                  40,
                                                  7.5,
                                                  self.config.italic,
                                                  self.button_functions[ii]))
                else:
                    for ii in range(4):
                        to_draw.append(Button(100 - 2.5 - (45 / 2),
                                              31.25 + (ii * 12.5),
                                              45,
                                              10,
                                              self.tab_objects[ii].title,
                                              40,
                                              7.5,
                                              self.config.italic,
                                              self.button_functions[ii]))
                if not self.skip_render:
                    self.outgoing_queue.put(Message(source="SongSelectStateManager",
                                                    target="GUIEventBroker",
                                                    message_type="render",
                                                    content=to_draw))
                self.skip_render = False

    def back(self, event, renderable):
        if event.type == pygame.MOUSEBUTTONUP:
            self.outgoing_queue.put(Message(source="SongSelectStateManager",
                                            target="TitleScreenStateManager",
                                            message_type="Get GUI update",
                                            content=None))
            self.skip_render = True

    def scroll_down(self, event, renderable):
        if event.type == pygame.MOUSEBUTTONUP:
            if not self.scrolling:
                self.song_list_index -= 1
                if self.song_list_index < 0:
                    self.song_list_index = len(self.tab_names) - 1
                self.scrolling = True
                self.last_scroll_start = time()
                self.scroll_direction_is_up = False
                self.leaving_tab_object = self.tab_objects[-1]
                self.tab_objects[1:] = self.tab_objects[0:3]
                self.tab_objects[0] = Tab(self.tab_names[self.song_list_index])

    def scroll_up(self, event, renderable):
        if event.type == pygame.MOUSEBUTTONUP:
            if not self.scrolling:
                self.song_list_index += 1
                if self.song_list_index == len(self.tab_names):
                    self.song_list_index = 0
                self.scrolling = True
                self.last_scroll_start = time()
                self.scroll_direction_is_up = True
                self.leaving_tab_object = self.tab_objects[0]
                self.tab_objects = self.tab_objects[1:]
                self.tab_objects.append(Tab(self.tab_names[self.song_list_index]))

    def select_tab_one(self, event, renderable):
        if event.type == pygame.MOUSEBUTTONUP:
            self.current_tab_object = self.tab_objects[0]

    def select_tab_two(self, event, renderable):
        if event.type == pygame.MOUSEBUTTONUP:
            self.current_tab_object = self.tab_objects[1]

    def select_tab_three(self, event, renderable):
        if event.type == pygame.MOUSEBUTTONUP:
            self.current_tab_object = self.tab_objects[2]

    def select_tab_four(self, event, renderable):
        if event.type == pygame.MOUSEBUTTONUP:
            self.current_tab_object = self.tab_objects[3]

    def select_tab_five(self, event, renderable):
        if event.type == pygame.MOUSEBUTTONUP:
            self.current_tab_object = self.tab_objects[4]

    def start(self, event, renderable):
        if event.type == pygame.MOUSEBUTTONUP:
            self.outgoing_queue.put(Message(source="SongSelectStateManager",
                                            target="RecordingStateManager",
                                            message_type="Start recording session",
                                            content={"tab_file": self.current_tab_object}))
            self.skip_render = True

    def square_tone_on(self, event, renderable):
        if event.type == pygame.MOUSEBUTTONUP:
            self.config.square_tone = True
            self.config.play_tone = True

    def sine_tone_on(self, event, renderable):
        if event.type == pygame.MOUSEBUTTONUP:
            self.config.square_tone = False
            self.config.play_tone = True

    def toggle_song(self, event, renderable):
        if event.type == pygame.MOUSEBUTTONUP:
            self.config.play_song = not self.config.play_song

    def tone_wave_off(self, event, renderable):
        if event.type == pygame.MOUSEBUTTONUP:
            self.config.play_tone = False