import pygame

from Fonts import *
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
        self.header = header
        self.regular = regular
        self.italic = italic
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

    def handle(self):
        if not self.incoming_queue.empty():
            message = self.incoming_queue.get()
            if message.type == "Get GUI update":
                self.skip_render = False
                if message.content is not None and not message.content["events"] == []:
                    for event in message.content["events"]:
                        if event.type == pygame.MOUSEBUTTONUP:
                            for interactable in message.content["interactables"]:
                                if interactable[0].collidepoint(event.pos[0], event.pos[1]):
                                    interactable[1].function()
                to_draw = [Button(2.5 + 10,
                                  2.5 + 5,
                                  20,
                                  10,
                                  "Back",
                                  20,
                                  7.5,
                                  self.regular,
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
                                        self.header))
                    to_draw.append(Text(25,
                                        35,
                                        40,
                                        5,
                                        "{}".format(self.current_tab_object.artist),
                                        self.italic))
                    to_draw.append(Text(25,
                                        40,
                                        40,
                                        5,
                                        "{} BPM".format(self.current_tab_object.bpm),
                                        self.italic))
                    to_draw.append(Button(25,
                                          100 - 2.5 - 5,
                                          45,
                                          10,
                                          "Start",
                                          40,
                                          7.5,
                                          self.regular,
                                          self.start))
                to_draw.append(UpArrowButton(100 - 2.5 - (45 / 2),
                                             18.75,
                                             45,
                                             10,
                                             self.scroll_up))
                to_draw.append(DownArrowButton(100 - 2.5 - (45 / 2),
                                               100 - 18.75,
                                               45,
                                               10,
                                               self.scroll_down))
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
                                                     self.italic,
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
                                                    self.italic,
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
                                                  self.italic,
                                                  self.button_functions[ii]))
                    else:
                        to_draw.append(FadeInButton(100 - 2.5 - (45 / 2),
                                                    31.25,
                                                    45,
                                                    10,
                                                    self.tab_objects[0].title,
                                                    40,
                                                    7.5,
                                                    self.italic,
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
                                                     self.italic,
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
                                                  self.italic,
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
                                              self.italic,
                                              self.button_functions[ii]))
                if not self.skip_render:
                    self.outgoing_queue.put(Message(source="SongSelectStateManager",
                                                    target="GUIEventBroker",
                                                    message_type="render",
                                                    content=to_draw))

    def back(self):
        self.outgoing_queue.put(Message(source="SongSelectStateManager",
                                        target="TitleScreenStateManager",
                                        message_type="Get GUI update",
                                        content=None))
        self.skip_render = True

    def scroll_down(self):
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

    def scroll_up(self):
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

    def select_tab_one(self):
        self.current_tab_object = self.tab_objects[0]

    def select_tab_two(self):
        self.current_tab_object = self.tab_objects[1]

    def select_tab_three(self):
        self.current_tab_object = self.tab_objects[2]

    def select_tab_four(self):
        self.current_tab_object = self.tab_objects[3]

    def select_tab_five(self):
        self.current_tab_object = self.tab_objects[4]

    def start(self):
        self.outgoing_queue.put(Message(source="SongSelectStateManager",
                                        target="RecordingStateManager",
                                        message_type="Start recording session",
                                        content={"tab_file": self.current_tab_object}))
        self.skip_render = True