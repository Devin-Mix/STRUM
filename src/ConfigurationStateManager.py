import pygame
from Fonts import *
from Message import Message
from queue import Queue
from Renderables import *
from time import time


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
            self.rear_color_saturation = 45
            self.middle_color_saturation = 70
            self.update_colors()
            self.text_color = 0
            self.intro_start_time = 1.0
            self.intro_length = 1.0
            self.fade_length = 0.25
            self.header = header
            self.italic = italic
            self.regular = regular
            self.transition_length = 1.0
            self.logo = pygame.image.load("../src/logo.svg")
            self.square_tone = False
            self.play_song = True
            self.play_tone = True
            self.playback_speed_scale = 1
            self.resolution_scale = 1
            self.do_resolution_scaling = False
            self.use_scale2x = False
            self.use_bilinear_filtering = True
            self.use_antialiasing = False
            self.antialiasing_scale = 1
            self.use_smooth_downscaling = True
            self.fullscreen = False
            self.skip_render = None
            self.fullscreen_resolution = None
            self.first_session_render = True
            self.doing_fade_in = False
            self.doing_fade_out = False
            self.fade_in_start_time = None
            self.current_page = 0
            self.user_tuning = [0, 0, 0, 0, 0, 0]
            self.key_select = 0
            self.tones = ["A", "A# / Bb", "B", "C", "C# / Db", "D", "D# / Eb", "E", "F", "F# / Gb", "G", "G# / Ab"]
            self.tones_flats_only = ["A", "Bb", "B", "C", "Db", "D", "Eb", "E", "F", "Gb", "G", "Ab"]
            self.default_tone_indices = [7, 0, 5, 10, 2, 7]
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
                    self.now_time = time()
                    if self.first_session_render:
                        self.doing_fade_in = True
                        self.fade_in_start_time = self.now_time
                        self.first_session_render = False
                    if self.resolution_scale < 1:
                        resolution_scale_text = "1/{}x".format(int(1 / self.resolution_scale))
                    else:
                        resolution_scale_text = "Native"
                    if self.antialiasing_scale > 1:
                        antialiasing_scale_text = "{}x".format(self.antialiasing_scale)
                    else:
                        antialiasing_scale_text = "Off"
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
                                      self.regular,
                                      self.back),
                               Button(65,
                                      7.5,
                                      20,
                                      10,
                                      "Display",
                                      self.regular,
                                      self.show_display_page),
                               Button(100 - 12.5,
                                      7.5,
                                      20,
                                      10,
                                      "Recording",
                                      self.regular,
                                      self.show_guitar_page)]
                    if self.current_page == 0:
                        to_draw = to_draw + [
                               Text(50,
                                    22.5,
                                    20,
                                    5,
                                    "UI Color: {}".format(self.hue),
                                    self.regular),
                               SlideBar(50,
                                        27.5,
                                        85,
                                        5,
                                        self.adjust_hue,
                                        self.hue / 3.60),
                               ArrowButton(37.5,
                                           22.5,
                                           5,
                                           4,
                                           self.subtract_hue_one,
                                           3),
                               ArrowButton(62.5,
                                           22.5,
                                           5,
                                           4,
                                           self.add_hue_one,
                                           1),
                               Text(50,
                                    35,
                                    30,
                                    5,
                                    "Middle saturation: {}".format(self.middle_color_saturation),
                                    self.regular),
                               SlideBar(50,
                                        40,
                                        85,
                                        5,
                                        self.adjust_middle_saturation,
                                        self.middle_color_saturation),
                               ArrowButton(30,
                                           35,
                                           5,
                                           4,
                                           self.subtract_middle_saturation_one,
                                           3),
                               ArrowButton(70,
                                           35,
                                           5,
                                           4,
                                           self.add_middle_saturation_one,
                                           1),
                               Text(50,
                                    47.5,
                                    30,
                                    5,
                                    "Rear saturation: {}".format(self.rear_color_saturation),
                                    self.regular),
                               SlideBar(50,
                                        52.5,
                                        85,
                                        5,
                                        self.adjust_rear_saturation,
                                        self.rear_color_saturation),
                               ArrowButton(30,
                                           47.5,
                                           5,
                                           4,
                                           self.subtract_rear_saturation_one,
                                           3),
                               ArrowButton(70,
                                           47.5,
                                           5,
                                           4,
                                           self.add_rear_saturation_one,
                                           1),
                               Text(50,
                                    60,
                                    30,
                                    5,
                                    "Text / Borders color: {}".format(self.text_color),
                                    self.regular),
                               SlideBar(50,
                                        65,
                                        85,
                                        5,
                                        self.adjust_text_color,
                                        100 * self.text_color / 255),
                               ArrowButton(30,
                                           60,
                                           5,
                                           4,
                                           self.subtract_text_color_one,
                                           3),
                               ArrowButton(70,
                                           60,
                                           5,
                                           4,
                                           self.add_text_color_one,
                                           1),
                               Text(20,
                                    72.5,
                                    25,
                                    5,
                                    "Internal resolution:",
                                    self.regular),
                               ArrowButton(10,
                                           77.5,
                                           5,
                                           4,
                                           self.half_resolution_scale,
                                           3),
                               Text(20,
                                    77.5,
                                    15,
                                    5,
                                    resolution_scale_text,
                                    self.regular),
                               ArrowButton(30,
                                           77.5,
                                           5,
                                           4,
                                           self.double_resolution_scale,
                                           1),
                               Text(20,
                                    85,
                                    25,
                                    5,
                                    "Antialiasing:",
                                    self.regular),
                               ArrowButton(10,
                                           90,
                                           5,
                                           5,
                                           self.half_antialiasing_scale,
                                           3),
                               Text(20,
                                    90,
                                    15,
                                    5,
                                    antialiasing_scale_text,
                                    self.regular),
                               ArrowButton(30,
                                           90,
                                           5,
                                           5,
                                           self.double_antialiasing_scale,
                                           1)
                           ]
                        if self.resolution_scale < 1:
                            if self.use_scale2x:
                                smooth_scaling_text = "Scale2x"
                            elif self.use_bilinear_filtering:
                                smooth_scaling_text = "Bilinear filtering"
                            else:
                                smooth_scaling_text = "Off"
                            # noinspection PyTypeChecker
                            to_draw = to_draw + [
                                Text(50,
                                     78.75,
                                     25,
                                     5,
                                     "Smooth upscaling:",
                                     self.regular),
                                Text(50,
                                     83.75,
                                     25,
                                     5,
                                     smooth_scaling_text,
                                     self.regular),
                                CheckBox(70,
                                         81.25,
                                         5,
                                         5,
                                         self.smooth_upscaling_off,
                                         not (self.use_scale2x or self.use_bilinear_filtering)),
                                CheckBox(80,
                                         81.25,
                                         5,
                                         5,
                                         self.bilinear_filtering_on,
                                         self.use_bilinear_filtering),
                                CheckBox(90,
                                         81.25,
                                         5,
                                         5,
                                         self.scale2x_on,
                                         self.use_scale2x)
                            ]
                        if self.use_antialiasing:
                            # noinspection PyTypeChecker
                            to_draw = to_draw + [
                                Text(50,
                                     90,
                                     25,
                                     5,
                                     "Smooth downscaling:",
                                     self.regular),
                                CheckBox(80,
                                         90,
                                         5,
                                         5,
                                         self.toggle_smooth_downscaling,
                                         self.use_smooth_downscaling)
                                ]
                        # noinspection PyTypeChecker
                        to_draw = to_draw + [
                            Text(50,
                                 72.5,
                                 15,
                                 5,
                                 "Fullscreen:",
                                 self.regular),
                            CheckBox(80,
                                     72.5,
                                     5,
                                     5,
                                     self.toggle_fullscreen,
                                     self.fullscreen)
                        ]
                    # TODO: Add guitar UI elements here: Guitar tuning
                    if self.current_page == 1:
                        tuning_indices = self.get_tuning_indices(self.user_tuning)
                        # noinspection PyTypeChecker
                        to_draw = to_draw + [
                            Text(50,
                                 22.5,
                                 30,
                                 5,
                                 "Fret Count: {}".format(self.fret_count),
                                 self.regular),
                            SlideBar(50,
                                     27.5,
                                     85,
                                     5,
                                     self.adjust_fret_count,
                                     100 * ((self.fret_count - 5) / 30)),
                            Text(50,
                                 35,
                                 30,
                                 5,
                                 "Fall Time: {}".format(self.recording_fall_time),
                                 self.regular),
                            SlideBar(50,
                                     40,
                                     85,
                                     5,
                                     self.adjust_recording_fall_time,
                                     100 * ((self.recording_fall_time - 1.0) / 7.0)),
                            Text(50,
                                 47.5,
                                 30,
                                 5,
                                 "Vertical Scale: {}".format(self.recording_vertical_scale),
                                 self.regular),
                            SlideBar(50,
                                     52.5,
                                     85,
                                     5,
                                     self.adjust_recording_vertical_scale,
                                     100 * ((self.recording_vertical_scale - 0.1) / 0.9)),
                            Text(50,
                                 60,
                                 85,
                                 5,
                                 "Tuning:",
                                 self.regular),
                            ArrowButton(18.75,
                                        67.5,
                                        10,
                                        5,
                                        self.add_e_low_one,
                                        0),
                            ArrowButton(31.25,
                                        67.5,
                                        10,
                                        5,
                                        self.add_a_one,
                                        0),
                            ArrowButton(43.75,
                                        67.5,
                                        10,
                                        5,
                                        self.add_d_one,
                                        0),
                            ArrowButton(56.25,
                                        67.5,
                                        10,
                                        5,
                                        self.add_g_one,
                                        0),
                            ArrowButton(68.75,
                                        67.5,
                                        10,
                                        5,
                                        self.add_b_one,
                                        0),
                            ArrowButton(81.25,
                                        67.5,
                                        10,
                                        5,
                                        self.add_e_high_one,
                                        0),
                            Text(18.75,
                                 75,
                                 10,
                                 5,
                                 self.tones[tuning_indices[0]],
                                 self.regular),
                            Text(31.25,
                                 75,
                                 10,
                                 5,
                                 self.tones[tuning_indices[1]],
                                 self.regular),
                            Text(43.75,
                                 75,
                                 10,
                                 5,
                                 self.tones[tuning_indices[2]],
                                 self.regular),
                            Text(56.25,
                                 75,
                                 10,
                                 5,
                                 self.tones[tuning_indices[3]],
                                 self.regular),
                            Text(68.75,
                                 75,
                                 10,
                                 5,
                                 self.tones[tuning_indices[4]],
                                 self.regular),
                            Text(81.25,
                                 75,
                                 10,
                                 5,
                                 self.tones[tuning_indices[5]],
                                 self.regular),
                            ArrowButton(18.75,
                                        82.5,
                                        10,
                                        5,
                                        self.subtract_e_low_one,
                                        2),
                            ArrowButton(31.25,
                                        82.5,
                                        10,
                                        5,
                                        self.subtract_a_one,
                                        2),
                            ArrowButton(43.75,
                                        82.5,
                                        10,
                                        5,
                                        self.subtract_d_one,
                                        2),
                            ArrowButton(56.25,
                                        82.5,
                                        10,
                                        5,
                                        self.subtract_g_one,
                                        2),
                            ArrowButton(68.75,
                                        82.5,
                                        10,
                                        5,
                                        self.subtract_b_one,
                                        2),
                            ArrowButton(81.25,
                                        82.5,
                                        10,
                                        5,
                                        self.subtract_e_high_one,
                                        2)
                        ]
                    if self.doing_fade_out:
                        if self.now_time - self.fade_out_start_time >= self.fade_length:
                            self.outgoing_queue.put(Message(source="SongSelectStateManager",
                                                            target="TitleScreenStateManager",
                                                            message_type="Get GUI update",
                                                            content=None))
                            self.skip_render = True
                            self.first_session_render = True
                            self.doing_fade_out = False
                        else:
                            to_draw.append(Blackout((self.now_time - self.fade_out_start_time), self.fade_length, False))
                            for ii in range(len(to_draw)):
                                to_draw[ii].function = no_function
                    if self.doing_fade_in:
                        if self.now_time - self.fade_in_start_time >= self.fade_length:
                            self.doing_fade_in = False
                        else:
                            to_draw.append(
                                Blackout((self.now_time - self.fade_in_start_time), self.fade_length))
                            for ii in range(len(to_draw)):
                                to_draw[ii].function = no_function
                    if not self.skip_render:
                        self.outgoing_queue.put(Message(source="ConfigurationStateManager",
                                                        target="GUIEventBroker",
                                                        message_type="render",
                                                        content=to_draw))
                self.skip_render = False

    def update_colors(self):
        self.rear_color.hsva = (self.hue, self.rear_color_saturation, 100)
        self.middle_color.hsva = (self.hue, self.middle_color_saturation, 100)
        self.front_color.hsva = (self.hue, 100, 100)

    def back(self, event, renderable):
        if event.type == pygame.MOUSEBUTTONUP:
            self.doing_fade_out = True
            self.fade_out_start_time = self.now_time

    def show_display_page(self, event, renderable):
        if event.type == pygame.MOUSEBUTTONUP:
            self.current_page = 0

    def show_guitar_page(self, event, renderable):
        if event.type == pygame.MOUSEBUTTONUP:
            self.current_page = 1

    def adjust_hue(self, event, renderable):
        if type(renderable) == SlideBar and event.type == pygame.MOUSEMOTION and event.buttons[0]:
            self.hue = round(360 * ((event.pos[0] * self.resolution_scale * self.antialiasing_scale) - renderable.start_x) / (renderable.end_x - renderable.start_x))
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

    def adjust_middle_saturation(self, event, renderable):
        if type(renderable) == SlideBar and event.type == pygame.MOUSEMOTION and event.buttons[0]:
            self.middle_color_saturation = round(100 * ((event.pos[0] * self.resolution_scale * self.antialiasing_scale) - renderable.start_x) / (renderable.end_x - renderable.start_x))
            if self.middle_color_saturation < 0:
                self.middle_color_saturation = 0
            elif self.middle_color_saturation > 100:
                self.middle_color_saturation = 100
            self.update_colors()

    def subtract_middle_saturation_one(self, event, renderable):
        if event.type == pygame.MOUSEBUTTONUP:
            self.middle_color_saturation = max(self.middle_color_saturation - 1, 0)
            self.update_colors()

    def add_middle_saturation_one(self, event, renderable):
        if event.type == pygame.MOUSEBUTTONUP:
            self.middle_color_saturation = min(self.middle_color_saturation + 1, 100)
            self.update_colors()

    def subtract_rear_saturation_one(self, event, renderable):
        if event.type == pygame.MOUSEBUTTONUP:
            self.rear_color_saturation = max(self.rear_color_saturation - 1, 0)
            self.update_colors()

    def add_rear_saturation_one(self, event, renderable):
        if event.type == pygame.MOUSEBUTTONUP:
            self.rear_color_saturation = min(self.rear_color_saturation + 1, 100)
            self.update_colors()

    def adjust_rear_saturation(self, event, renderable):
        if type(renderable) == SlideBar and event.type == pygame.MOUSEMOTION and event.buttons[0]:
            self.rear_color_saturation = round(100 * ((event.pos[0] * self.resolution_scale * self.antialiasing_scale) - renderable.start_x) / (renderable.end_x - renderable.start_x))
            if self.rear_color_saturation < 0:
                self.rear_color_saturation = 0
            elif self.rear_color_saturation > 100:
                self.rear_color_saturation = 100
            self.update_colors()

    def adjust_text_color(self, event, renderable):
        if type(renderable) == SlideBar and event.type == pygame.MOUSEMOTION and event.buttons[0]:
            self.text_color = round(255 * ((event.pos[0] * self.resolution_scale * self.antialiasing_scale) - renderable.start_x) / (renderable.end_x - renderable.start_x))
            if self.text_color < 0:
                self.text_color = 0
            elif self.text_color > 255:
                self.text_color = 255

    def adjust_recording_vertical_scale(self, event, renderable):
        if type(renderable) == SlideBar and event.type == pygame.MOUSEMOTION and event.buttons[0]:
            self.recording_vertical_scale = round(0.1 + (0.9 * ((event.pos[0] * self.resolution_scale * self.antialiasing_scale) - renderable.start_x) / (renderable.end_x - renderable.start_x)), 2)
            if self.recording_vertical_scale < 0.1:
                self.recording_vertical_scale = 0.1
            elif self.recording_vertical_scale > 1.0:
                self.recording_vertical_scale = 1.0

    def adjust_recording_fall_time(self, event, renderable):
        if type(renderable) == SlideBar and event.type == pygame.MOUSEMOTION and event.buttons[0]:
            self.recording_fall_time = round(1.0 + (7.0 * ((event.pos[0] * self.resolution_scale * self.antialiasing_scale) - renderable.start_x) / (renderable.end_x - renderable.start_x)), 1)
            if self.recording_fall_time < 1.0:
                self.recording_fall_time = 1.0
            elif self.recording_fall_time > 8.0:
                self.recording_fall_time = 8.0

    def adjust_fret_count(self, event, renderable):
        if type(renderable) == SlideBar and event.type == pygame.MOUSEMOTION and event.buttons[0]:
            self.fret_count = round(5 + (30 * ((event.pos[0] * self.resolution_scale * self.antialiasing_scale) - renderable.start_x) / (renderable.end_x - renderable.start_x)))
            if self.fret_count < 5:
                self.fret_count = 5
            elif self.fret_count > 35:
                self.fret_count = 35

    def add_e_low_one(self, event, renderable):
        if event.type == pygame.MOUSEBUTTONUP:
            self.user_tuning[0] = self.user_tuning[0] + 1

    def subtract_e_low_one(self, event, renderable):
        if event.type == pygame.MOUSEBUTTONUP:
            self.user_tuning[0] = self.user_tuning[0] - 1

    def add_a_one(self, event, renderable):
        if event.type == pygame.MOUSEBUTTONUP:
            self.user_tuning[1] = self.user_tuning[1] + 1

    def subtract_a_one(self, event, renderable):
        if event.type == pygame.MOUSEBUTTONUP:
            self.user_tuning[1] = self.user_tuning[1] - 1

    def add_d_one(self, event, renderable):
        if event.type == pygame.MOUSEBUTTONUP:
            self.user_tuning[2] = self.user_tuning[2] + 1

    def subtract_d_one(self, event, renderable):
        if event.type == pygame.MOUSEBUTTONUP:
            self.user_tuning[2] = self.user_tuning[2] - 1

    def add_g_one(self, event, renderable):
        if event.type == pygame.MOUSEBUTTONUP:
            self.user_tuning[3] = self.user_tuning[3] + 1

    def subtract_g_one(self, event, renderable):
        if event.type == pygame.MOUSEBUTTONUP:
            self.user_tuning[3] = self.user_tuning[3] - 1

    def add_b_one(self, event, renderable):
        if event.type == pygame.MOUSEBUTTONUP:
            self.user_tuning[4] = self.user_tuning[4] + 1

    def subtract_b_one(self, event, renderable):
        if event.type == pygame.MOUSEBUTTONUP:
            self.user_tuning[4] = self.user_tuning[4] - 1

    def add_e_high_one(self, event, renderable):
        if event.type == pygame.MOUSEBUTTONUP:
            self.user_tuning[5] = self.user_tuning[5] + 1

    def subtract_e_high_one(self, event, renderable):
        if event.type == pygame.MOUSEBUTTONUP:
            self.user_tuning[5] = self.user_tuning[5] - 1

    def subtract_selected_key_one(self, event, renderable):
        if event.type == pygame.MOUSEBUTTONUP:
            self.user_tuning[self.key_select] = self.user_tuning[self.key_select] - 1

    def add_selected_key_one(self, event, renderable):
        if event.type == pygame.MOUSEBUTTONUP:
            self.user_tuning[self.key_select] = self.user_tuning[self.key_select] + 1

    def change_E_low_key(self, event, renderable):
        if event.type == pygame.MOUSEBUTTONUP:
            self.key_select = 0

    def change_A_key(self, event, renderable):
        if event.type == pygame.MOUSEBUTTONUP:
            self.key_select = 1

    def change_D_key(self, event, renderable):
        if event.type == pygame.MOUSEBUTTONUP:
            self.key_select = 2

    def change_G_key(self, event, renderable):
        if event.type == pygame.MOUSEBUTTONUP:
            self.key_select = 3

    def change_B_key(self, event, renderable):
        if event.type == pygame.MOUSEBUTTONUP:
            self.key_select = 4

    def change_E_high_key(self, event, renderable):
        if event.type == pygame.MOUSEBUTTONUP:
            self.key_select = 5

    def subtract_text_color_one(self, event, renderable):
        if event.type == pygame.MOUSEBUTTONUP:
            self.text_color = max(self.text_color - 1, 0)
            self.update_colors()

    def add_text_color_one(self, event, renderable):
        if event.type == pygame.MOUSEBUTTONUP:
            self.text_color = min(self.text_color + 1, 255)
            self.update_colors()

    def half_resolution_scale(self, event, renderable):
        if event.type == pygame.MOUSEBUTTONUP:
            self.resolution_scale = self.resolution_scale / 2
            if self.resolution_scale >= 1:
                self.resolution_scale = int(self.resolution_scale)
            self.do_resolution_scaling = not (self.resolution_scale == 1)

    def double_resolution_scale(self, event, renderable):
        if event.type == pygame.MOUSEBUTTONUP:
            self.resolution_scale = min(self.resolution_scale * 2, 1)
            self.do_resolution_scaling = not (self.resolution_scale == 1)

    def scale2x_on(self, event, renderable):
        if event.type == pygame.MOUSEBUTTONUP:
            self.use_scale2x = True
            self.use_bilinear_filtering = False

    def smooth_upscaling_off(self, event, renderable):
        if event.type == pygame.MOUSEBUTTONUP:
            self.use_scale2x = False
            self.use_bilinear_filtering = False

    def bilinear_filtering_on(self, event, renderable):
        if event.type == pygame.MOUSEBUTTONUP:
            self.use_bilinear_filtering = True
            self.use_scale2x = False

    def toggle_smooth_downscaling(self, event, renderable):
        if event.type == pygame.MOUSEBUTTONUP:
            self.use_smooth_downscaling = not self.use_smooth_downscaling

    def half_antialiasing_scale(self, event, renderable):
        if event.type == pygame.MOUSEBUTTONUP:
            self.antialiasing_scale = max(int(self.antialiasing_scale / 2), 1)
            if self.antialiasing_scale == 1:
                self.use_antialiasing = False

    def double_antialiasing_scale(self, event, renderable):
        if event.type == pygame.MOUSEBUTTONUP:
            self.antialiasing_scale = int(self.antialiasing_scale * 2)
            self.use_antialiasing = True

    def toggle_fullscreen(self, event, renderable):
        if event.type == pygame.MOUSEBUTTONUP:
            self.fullscreen = not self.fullscreen
            self.outgoing_queue.put(Message(source="ConfigurationStateManager",
                                            target="GUIEventBroker",
                                            message_type="Toggle fullscreen",
                                            content=None))

    def get_tuning_indices(self, tuning):
        tuning_indices = []
        for ii in range(len(tuning)):
            if tuning[ii] + self.default_tone_indices[ii] >= len(self.tones):
                tuning_indices.append((tuning[ii] + self.default_tone_indices[ii]) % len(self.tones))
            elif tuning[ii] + self.default_tone_indices[ii] < 0:
                tuning_indices.append(tuning[ii] + self.default_tone_indices[ii])
                while tuning_indices[-1] < 0:
                    tuning_indices[-1] = tuning_indices[-1] + len(self.tones)
            else:
                tuning_indices.append(tuning[ii] + self.default_tone_indices[ii])
        return tuning_indices
