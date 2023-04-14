from math import log
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
        tab_scanner = scandir("../tabs")
        for scanned_object in tab_scanner:
            if scanned_object.is_file() and ".txt" in scanned_object.name:
                self.tab_names.append("../tabs/{}".format(scanned_object.name))
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
        self.launch_recording = False
        self.launch_title_screen = False
        self.first_session_render = True

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
                                        32.5,
                                        40,
                                        5,
                                        "{}".format(self.current_tab_object.artist),
                                        self.config.italic))
                    to_draw.append(Text(25,
                                        37.5,
                                        40,
                                        5,
                                        "{} BPM".format(self.current_tab_object.bpm),
                                        self.config.italic))
                    tuning_indices = self.config.get_tuning_indices(self.current_tab_object.tuning)
                    to_draw.append(Text(25,
                                        42.5,
                                        40,
                                        5,
                                        "Tuning: {} {} {} {} {} {}".format(
                                            self.config.tones_flats_only[tuning_indices[0]],
                                            self.config.tones_flats_only[tuning_indices[1]],
                                            self.config.tones_flats_only[tuning_indices[2]],
                                            self.config.tones_flats_only[tuning_indices[3]],
                                            self.config.tones_flats_only[tuning_indices[4]],
                                            self.config.tones_flats_only[tuning_indices[5]],
                                        ),
                                        self.config.italic))
                    to_draw.append(Button(25,
                                          100 - 2.5 - 5,
                                          45,
                                          10,
                                          "Start",
                                          self.config.regular,
                                          self.start))
                    to_draw.append(Text(20,
                                        50,
                                        25,
                                        5,
                                        "Play studio track:",
                                        self.config.regular))
                    to_draw.append(CheckBox(35,
                                            50,
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
                                        57.5,
                                        40,
                                        5,
                                        "Tone wave style: {}".format(tone_style),
                                        self.config.regular))
                    to_draw.append(CheckBox(15,
                                            62.5,
                                            5,
                                            5,
                                            self.tone_wave_off,
                                            not self.config.play_tone))
                    to_draw.append(CheckBox(25,
                                            62.5,
                                            5,
                                            5,
                                            self.sine_tone_on,
                                            (not self.config.square_tone) and self.config.play_tone))
                    to_draw.append(CheckBox(35,
                                            62.5,
                                            5,
                                            5,
                                            self.square_tone_on,
                                            self.config.square_tone and self.config.play_tone))
                    to_draw.append(Text(25,
                                        70,
                                        40,
                                        5,
                                        "Playback speed: {}x".format(self.config.playback_speed_scale),
                                        self.config.regular))
                    to_draw.append(SlideBar(25,
                                            75,
                                            30,
                                            5,
                                            self.adjust_playback_speed_scale,
                                            100 * log(self.config.playback_speed_scale + 0.9, 10.9)))
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
                self.now_time = time()
                if self.first_session_render:
                    self.doing_fade_in = True
                    self.fade_in_start_time = self.now_time
                    self.first_session_render = False
                if self.scrolling and self.now_time - self.last_scroll_start > self.scroll_time:
                    self.scrolling = False
                    self.leaving_tab_object = None
                if self.scrolling:
                    if self.scroll_direction_is_up:
                        to_draw.append(FadeOutButton(100 - 2.5 - (45 / 2),
                                                     31.25,
                                                     45,
                                                     10,
                                                     self.leaving_tab_object.title,
                                                     self.config.italic,
                                                     self.button_functions[0],
                                                     self.now_time - self.last_scroll_start,
                                                     self.scroll_time))
                        if self.now_time > self.last_scroll_start:
                            to_draw.append(FadeInButton(100 - 2.5 - (45 / 2),
                                                        100 - 31.25,
                                                        45,
                                                        10,
                                                        self.tab_objects[-1].title,
                                                        self.config.italic,
                                                        self.button_functions[-1],
                                                        self.now_time - self.last_scroll_start,
                                                        self.scroll_time))
                        for ii in range(3):
                            to_draw.append(Button(100 - 2.5 - (45 / 2),
                                                  43.75 + (ii * 12.5) - (12.5 * (self.now_time - self.last_scroll_start) / self.scroll_time),
                                                  45,
                                                  10,
                                                  self.tab_objects[ii].title,
                                                  self.config.italic,
                                                  self.button_functions[ii]))
                    else:
                        if self.now_time > self.last_scroll_start:
                            to_draw.append(FadeInButton(100 - 2.5 - (45 / 2),
                                                        31.25,
                                                        45,
                                                        10,
                                                        self.tab_objects[0].title,
                                                        self.config.italic,
                                                        self.button_functions[0],
                                                        self.now_time - self.last_scroll_start,
                                                        self.scroll_time))
                        to_draw.append(FadeOutButton(100 - 2.5 - (45 / 2),
                                                     100 - 31.25,
                                                     45,
                                                     10,
                                                     self.leaving_tab_object.title,
                                                     self.config.italic,
                                                     self.button_functions[-1],
                                                     self.now_time - self.last_scroll_start,
                                                     self.scroll_time))
                        for ii in range(3):
                            to_draw.append(Button(100 - 2.5 - (45 / 2),
                                                  31.25 + (ii * 12.5) + (12.5 * (self.now_time - self.last_scroll_start) / self.scroll_time),
                                                  45,
                                                  10,
                                                  self.tab_objects[ii + 1].title,
                                                  self.config.italic,
                                                  self.button_functions[ii]))
                else:
                    for ii in range(4):
                        to_draw.append(Button(100 - 2.5 - (45 / 2),
                                              31.25 + (ii * 12.5),
                                              45,
                                              10,
                                              self.tab_objects[ii].title,
                                              self.config.italic,
                                              self.button_functions[ii]))
                if self.launch_recording or self.launch_title_screen:
                    if self.now_time >= self.fade_out_start_time + self.config.fade_length:
                        if self.launch_recording:
                            self.outgoing_queue.put(Message(source="SongSelectStateManager",
                                                            target="RecordingStateManager",
                                                            message_type="Start recording session",
                                                            content={"tab_file": self.current_tab_object}))
                        elif self.launch_title_screen:
                            self.outgoing_queue.put(Message(source="SongSelectStateManager",
                                                            target="TitleScreenStateManager",
                                                            message_type="Get GUI update",
                                                            content=None))
                        self.skip_render = True
                        self.launch_recording = False
                        self.launch_title_screen = False
                        self.first_session_render = True
                    else:
                        to_draw.append(
                            Blackout((self.now_time - self.fade_out_start_time), self.config.fade_length, False))
                        for ii in range(len(to_draw)):
                            to_draw[ii].function = no_function
                if self.doing_fade_in:
                    if self.now_time - self.fade_in_start_time >= self.config.fade_length:
                        self.doing_fade_in = False
                    else:
                        to_draw.append(Blackout((self.now_time - self.fade_in_start_time), self.config.fade_length))
                        for ii in range(len(to_draw)):
                            to_draw[ii].function = no_function
                if not self.skip_render:
                    self.outgoing_queue.put(Message(source="SongSelectStateManager",
                                                    target="GUIEventBroker",
                                                    message_type="render",
                                                    content=to_draw))
                self.skip_render = False

    def back(self, event, renderable):
        if event.type == pygame.MOUSEBUTTONUP:
            self.launch_title_screen = True
            self.fade_out_start_time = self.now_time

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
            self.launch_recording = True
            self.fade_out_start_time = self.now_time

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

    def adjust_playback_speed_scale(self, event, renderable):
        if type(renderable) == SlideBar and event.type == pygame.MOUSEMOTION and event.buttons[0]:
            cursor_position = ((event.pos[0] * self.config.resolution_scale * self.config.antialiasing_scale)
                               - renderable.start_x) / (renderable.end_x - renderable.start_x)
            self.config.playback_speed_scale = pow(10.9, cursor_position) - 0.9
            if self.config.playback_speed_scale < 1:
                self.config.playback_speed_scale = round(self.config.playback_speed_scale, 2)
            elif self.config.playback_speed_scale > 1:
                self.config.playback_speed_scale = round(self.config.playback_speed_scale, 1)
            if self.config.playback_speed_scale < 0.1:
                self.config.playback_speed_scale = 0.1
            elif self.config.playback_speed_scale > 10:
                self.config.playback_speed_scale = 10.0