import pygame
from math import pi



def no_function(event, renderable):
    return

class StringLine:
    def __init__(self, width_percent, y_percent):
        if 0.0 <= width_percent <= 100.0:
            self.width_percent = float(width_percent)
        else:
            raise ValueError("width_percent out of bounds for StringLine renderable ({})".format(width_percent))
        if 0.0 <= y_percent <= 100.0:
            self.y_percent = float(y_percent)
        else:
            raise ValueError("y_percent out of bounds for StringLine renderable ({})".format(y_percent))
        self.bounding_box = None
        self.function = no_function

    # Expects a resolution in the format (x_resolution, y_resolution)
    def draw(self, screen, config):
        if not type(screen) == pygame.surface.Surface:
            raise TypeError("Unexpected argument type for Renderables.StringLine.draw() (Expected pygame.surface."
                            "Surface, got {})".format(type(screen)))
        else:
            start_x = ((100.0 - self.width_percent) / 200) * screen.get_width()
            end_x = screen.get_width() - start_x
            y = screen.get_height() * self.y_percent / 100
            self.bounding_box = pygame.draw.line(screen,
                                                 "black",
                                                 (start_x, y),
                                                 (end_x, y))
            return self


class FallingChord:
    def __init__(self, chord, now_time, config, final_fret_offset, tuning):
        tuning_differences = [tuning[ii] - config.user_tuning[ii] for ii in range(6)]
        remaining_fall_time = chord[1] - now_time
        self.y_offset = (95 - (25 * config.recording_vertical_scale)) - (
                    (90 - (25 * config.recording_vertical_scale)) *
                    remaining_fall_time / config.recording_fall_time)
        self.to_draw = []
        for jj in range(6):
            self.to_draw.append(StringLine(95, self.y_offset + jj * 5 * config.recording_vertical_scale))
        for string_number in range(len(chord[0].play_string)):
            if chord[0].play_string[string_number]:
                fret_number = chord[0].string_fret[string_number] + tuning_differences[string_number]
                if 0 <= fret_number <= config.fret_count:
                    fret_offset = 0.0
                    for kk in range(fret_number):
                        fret_offset = ((95.0 - fret_offset) / 17.817) + fret_offset
                    fret_offset = 2.5 + (95 * fret_offset / final_fret_offset)
                    self.to_draw.append(FretMark(fret_offset, self.y_offset + (5 - string_number) * 5 *
                                        config.recording_vertical_scale))

    def draw(self, screen, config):
        s = pygame.Surface((screen.get_width(), screen.get_height()))
        s.fill(config.chroma_key)
        s.set_colorkey(config.chroma_key, pygame.RLEACCEL)
        s.set_alpha(round(255 * min(1, (self.y_offset - 5.0) / 50)), pygame.RLEACCEL)
        for ii in self.to_draw:
            ii.draw(s, config)
        screen.blit(s, (0, 0))

class FretLine:
    def __init__(self, x_percent, height_percent):
        if 0.0 <= x_percent <= 100.0:
            self.x_percent = x_percent
        else:
            raise ValueError("x_percent out of bounds for FretLine renderable ({})".format(x_percent))
        if 0.0 <= height_percent <= 95.0:
            self.height_percent = height_percent
        else:
            raise ValueError("height_percent out of bounds for FretLine renderable ({})".format(height_percent))
        self.bounding_box = None
        self.function = no_function

    def draw(self, screen, config):
        if not type(screen) == pygame.surface.Surface:
            raise TypeError("Unexpected argument type for Renderables.FretLine.draw() (Expected pygame.surface.Surface,"
                            " got {})".format(type(screen)))
        else:
            start_y = (95.0 - self.height_percent) * screen.get_height() / 100
            end_y = 0.95 * screen.get_height()
            x = self.x_percent * screen.get_width() / 100
            self.bounding_box = pygame.draw.line(screen,
                                                 "white",
                                                 (x, start_y),
                                                 (x, end_y))
            return self


class FretMark:
    def __init__(self, x_percent, y_percent):
        if 0.005 <= x_percent <= 99.995:
            self.x_percent = x_percent
        else:
            raise ValueError("x_percent out of bounds for FretMark renderable ({})".format(x_percent))
        if 0.005 <= y_percent <= 99.995:
            self.y_percent = y_percent
        else:
            raise ValueError("height_percent out of bounds for FretMark renderable ({})".format(y_percent))
        self.bounding_box = None
        self.function = no_function

    def draw(self, screen, config):
        if not type(screen) == pygame.surface.Surface:
            raise TypeError("Unexpected argument type for Renderables.FretMark.draw() (Expected pygame.surface.Surface,"
                            " got {})".format(type(screen)))
        else:
            x = self.x_percent * screen.get_width() / 100.0
            y = self.y_percent * screen.get_height() / 100.0
            self.bounding_box = pygame.draw.circle(screen,
                                                   "white",
                                                   (x, y),
                                                   0.01 * max(screen.get_width(), screen.get_height()))
            return self


class FadingFretMark:
    def __init__(self, x_percent, y_percent, birth_time, time_to_live, time_now):
        if 0.005 <= x_percent <= 99.995:
            self.x_percent = x_percent
        else:
            raise ValueError("x_percent out of bounds for FretMark renderable ({})".format(x_percent))
        if 0.005 <= y_percent <= 99.995:
            self.y_percent = y_percent
        else:
            raise ValueError("height_percent out of bounds for FretMark renderable ({})".format(y_percent))
        # TODO: Need type checking here for safety
        if birth_time <= time_now < birth_time + time_to_live:
            self.birth_time = birth_time
            self.time_to_live = time_to_live
            self.time_now = time_now
        else:
            raise ValueError("time_now not bounded by birth_time and time_to_live for FretMark renderable ({}, {}, {})"
                             .format(time_now, birth_time, time_to_live))
        self.bounding_box = None
        self.function = no_function

    def draw(self, screen, config):
        if not type(screen) == pygame.surface.Surface:
            raise TypeError("Unexpected argument type for Renderables.FadingFretMark.draw() (Expected "
                            "pygame.surface.Surface, got {})".format(type(screen)))
        else:
            x = self.x_percent * screen.get_width() / 100.0
            y = self.y_percent * screen.get_height() / 100.0
            self.bounding_box = pygame.draw.circle(screen,
                                                   "white",
                                                   (x, y),
                                                   0.01 * max(screen.get_width(), screen.get_height()) * (1 - ((self.time_now - self.birth_time)/self.time_to_live)))
            return self


    def is_alive(self):
        return (1 - ((self.time_now - self.birth_time)/self.time_to_live)) > 0

    def update_time(self, time_now):
        self.time_now = time_now
        return self

class LoadBar:
    def __init__(self, y_percent, width_percent, height_percent, load_percent):
        if height_percent <= 0:
            raise ValueError("Height percent too low for Renderables.LoadBar ({})".format(height_percent))
        if width_percent <= 0:
            raise ValueError("Width percent too low for Renderables.LoadBar ({})".format(width_percent))
        if y_percent + (height_percent / 2) <= 100.0 and y_percent - (height_percent / 2) >= 0:
            self.y_percent = y_percent
            self.height_percent = height_percent
        else:
            raise ValueError("Height plus/minus offset out of bounds for Renderables.LoadBar ({})".format(y_percent + height_percent))
        if 0.0 <= width_percent <= 100.0:
            self.width_percent = width_percent
        else:
            raise ValueError("Width out of bounds for Renderables.LoadBar ({})".format(width_percent))
        if 0.0 <= load_percent <= 100.0:
            self.load_percent = load_percent
        else:
            raise ValueError("Load percent out of bounts for Renderables.LoadBar ({})".format(load_percent))
        self.function = no_function
        self.bounding_box = None

    def draw(self, screen, config):
        if not type(screen) == pygame.surface.Surface:
            raise TypeError("Unexpected argument type for Renderables.LoadBar.draw() (Expected "
                            "pygame.surface.Surface, got {})".format(type(screen)))
        else:
            x = (50.0 - (self.width_percent / 2.0)) * screen.get_width() / 100.0
            width = (self.width_percent * screen.get_width() / 100.0) * (self.load_percent / 100.0)
            height = self.height_percent * screen.get_height() / 100.0
            y = self.y_percent * screen.get_height() / 100.0
            self.bounding_box =  BackgroundBox(50 - ((self.width_percent / 2) * (1 - (self.load_percent / 100))),
                                               self.y_percent,
                                               self.width_percent * (self.load_percent / 100.0),
                                               self.height_percent).draw(screen, config).bounding_box
            return self

class Text:
    def __init__(self, x_percent, y_percent, max_width_percent, max_height_percent, text, font, align_center=True, color=None):
        if 0.0 <= x_percent <= 100.0:
            if (align_center and (
                    x_percent - (max_width_percent / 2.0) >= 0.0 and x_percent + (max_width_percent / 2.0) <= 100.0)) \
                    or (not align_center) and x_percent + max_width_percent <= 100.0:
                self.x_percent = x_percent
                self.max_width_percent = max_width_percent
            else:
                raise ValueError(
                    "max_width_percent too large in combination with x_percent for Renderables.Text (x_percent: {}, max_width_percent: {}, align_center: {})".format(
                        x_percent, max_width_percent, align_center))
        else:
            raise ValueError("x_percent out of bounds for Renderables.Text ({})".format(x_percent))
        if 0.0 <= y_percent <= 100.0:
            if (align_center and (
                    y_percent - (max_height_percent / 2.0) >= 0.0 and y_percent + (max_height_percent / 2.0) <= 100.0)) \
                    or (not align_center) and y_percent + max_height_percent <= 100.0:
                self.y_percent = y_percent
                self.max_height_percent = max_height_percent
            else:
                raise ValueError(
                    "max_height_percent too large in combination with y_percent for Renderables.Text (y_percent: {}, max_height_percent: {}, align_center: {})".format(
                        y_percent, max_height_percent, align_center))
        else:
            raise ValueError("y_percent out of bounds for Renderables.Text ({})".format(y_percent))
        if self.max_height_percent <= 0:
            raise ValueError("max_height_percent too small for Renderables.Text ({})".format(self.max_height_percent))
        if self.max_width_percent <= 0:
            raise ValueError("max_width_percent too small for Renderables.Text ({})".format(self.max_width_percent))
        self.text = "{}".format(text)
        if type(align_center) is bool:
            self.align_center = align_center
        else:
            raise TypeError("Invalid align_center type for Renderables.Text ({})".format(type(align_center)))
        if type(font) == pygame.freetype.Font:
            self.font = font
        else:
            raise TypeError("Invalid font type for Renderables.Text ({})".format(type(font)))
        self.color = color

    def draw(self, screen, config):
        if not type(screen) == pygame.surface.Surface:
            raise TypeError("Unexpected argument type for Renderables.Text.draw() (Expected "
                            "pygame.surface.Surface, got {})".format(type(screen)))
        else:
            if self.font.scalable:
                x = self.x_percent * screen.get_width() / 100.0
                y = self.y_percent * screen.get_height() / 100.0
                max_width = self.max_width_percent * screen.get_width() / 100.0
                max_height = self.max_height_percent * screen.get_height() / 100.0
                size = max(0.75 * max_height, 1)
                width = self.font.get_rect(self.text, size=size, style=pygame.freetype.STYLE_NORMAL).width
                while width > max_width:
                    size = size / 2
                    if size > 0.5:
                        width = self.font.get_rect(self.text, size=size, style=pygame.freetype.STYLE_NORMAL).width
                        if width < max_width:
                            while width < max_width:
                                size = size * 1.1
                                width = self.font.get_rect(self.text, size=size, style=pygame.freetype.STYLE_NORMAL).width
                            if width > max_width:
                                size = size / 1.1
                            width = self.font.get_rect(self.text, size=size, style=pygame.freetype.STYLE_NORMAL).width
                    else:
                        size = 1
                        break
                height = self.font.get_rect(self.text, size=size, style=pygame.freetype.STYLE_NORMAL).height
                self.font.fgcolor = pygame.color.Color(config.text_color, config.text_color, config.text_color)
                if self.align_center:
                    self.font.render_to(screen,
                                        (x - (width / 2.0), y - (height / 2.0)),
                                        self.text,
                                        fgcolor=self.color,
                                        size=size,
                                        style=pygame.freetype.STYLE_NORMAL)
                else:
                    self.font.render_to(screen,
                                        (x, y),
                                        self.text,
                                        fgcolor=self.color,
                                        size=size,
                                        style=pygame.freetype.STYLE_NORMAL)
            else:
                raise TypeError("Font {} not scalable".format(self.font))

class AnalysisGraph:
    def __init__(self, y_percent, width_percent, height_percent, values, regular_font, italic_font, song_length):
        if height_percent <= 0:
            raise ValueError("Height too small for Renderables.AnalysisGraph ({})".format(height_percent))
        if width_percent <= 0:
            raise ValueError("Width too small for Renderables.AnalysisGraph ({})".format(width_percent))
        if 0.0 <= y_percent - height_percent and y_percent + height_percent <= 100.0:
            self.y_percent = y_percent
            self.height_percent = height_percent
        else:
            raise ValueError("Height plus offset out of bounds for Renderables.AnalysisGraph ({})".format(y_percent + height_percent))
        if 0.0 <= 50 - (width_percent / 2) and 50 + (width_percent / 2) <= 100.0:
            self.width_percent = width_percent
        else:
            raise ValueError("Width out of bounds for Renderables.AnalysisGraph ({})".format(width_percent))
        self.values = values
        if type(regular_font) == pygame.freetype.Font:
            self.regular_font = regular_font
        else:
            raise TypeError("Invalid regular font type for Renderables.AnalysisGraph ({})".format(type(regular_font)))
        if type(italic_font) == pygame.freetype.Font:
            self.italic_font = italic_font
        else:
            raise TypeError("Invalid italic font type for Renderables.AnalysisGraph ({})".format(type(italic_font)))
        self.song_length = song_length

    def draw(self, screen, config):
        division_width = self.width_percent / len(self.values)
        main_height = self.height_percent * 0.35
        key_height = self.height_percent - (2.0 * main_height)
        points = [(screen.get_width() * (50.0 - (self.width_percent / 2)) / 100,
                   screen.get_height() * (self.y_percent - (self.height_percent / 2) + (2 * main_height)) / 100)]
        for ii in range(len(self.values)):
            Text(50.0 - (self.width_percent / 2) + (ii * division_width) + (division_width / 2) + (0.025 * division_width),
                 self.y_percent - (self.height_percent / 2) + (main_height / 2) + (0.025 * main_height),
                 0.95 * division_width,
                 0.95 * main_height,
                 "{}%".format(round(100 * self.values[ii], 2)),
                 self.regular_font).draw(screen, config)

            points.append((screen.get_width() * (50.0 - (self.width_percent / 2) + (ii * division_width)) / 100,
                           screen.get_height() * (self.y_percent - (self.height_percent / 2) + (2 * main_height) - (main_height * self.values[ii])) / 100))
            points.append((points[-1][0] + screen.get_width() * division_width / 100,
                           points[-1][1]))
            #pygame.draw.rect(screen,
            #                 "white",
            #                 pygame.Rect(screen.get_width() * (50.0 - (self.width_percent / 2) + (ii * division_width)) / 100,
            #                             screen.get_height() * (self.y_percent - (self.height_percent / 2) + (2 * main_height) - (main_height * self.values[ii])) / 100,
            #                             screen.get_width() * division_width / 100,
            #                             ceil(self.values[ii] * main_height * screen.get_height() / 100)))
        points.append((screen.get_width() * (50.0 + (self.width_percent / 2)) / 100,
                       points[0][1]))
        points.append(points[0])
        pygame.draw.polygon(screen,
                            "white",
                            points,
                            width=1)
        pygame.draw.line(screen,
                         "white",
                         (screen.get_width() * (100 - self.width_percent) / 200, screen.get_height() * (
                                     self.y_percent - (0.5 * self.height_percent) + (2 * main_height)) / 100),
                         (screen.get_width() * (self.width_percent + ((100 - self.width_percent) / 2)) / 100, screen.get_height() * (
                                     self.y_percent - (0.5 * self.height_percent) + (2 * main_height)) / 100))
        seconds_per_timing_mark = 5
        if self.song_length > seconds_per_timing_mark:
            num_timing_marks = (self.song_length - (self.song_length % seconds_per_timing_mark)) / seconds_per_timing_mark
            timing_mark_width = self.width_percent * ((self.song_length - (self.song_length % seconds_per_timing_mark)) / num_timing_marks) / self.song_length
            next_mark_percent = 0.0
            next_mark_num = 0
            while next_mark_percent <= self.width_percent:
                pygame.draw.line(screen,
                                 "white",
                                 (screen.get_width() * ((100 - self.width_percent) / 2 + next_mark_percent) / 100,
                                  screen.get_height() * (self.y_percent + (self.height_percent / 2) - key_height) / 100),
                                 (screen.get_width() * ((100 - self.width_percent) / 2 + next_mark_percent) / 100,
                                  screen.get_height() * (self.y_percent + (self.height_percent / 2) - (key_height / 2)) / 100))
                if next_mark_percent > 0.0:
                    Text(50.0 - (self.width_percent / 2) + next_mark_percent - (timing_mark_width / 2),
                         self.y_percent + (self.height_percent / 2) - (key_height / 2),
                         0.5 * timing_mark_width,
                         0.5 * key_height,
                         "{} - {}".format(as_time_string((next_mark_num - 1) * seconds_per_timing_mark), as_time_string(next_mark_num * seconds_per_timing_mark)),
                         self.regular_font).draw(screen, config)
                next_mark_percent = next_mark_percent + timing_mark_width
                next_mark_num = next_mark_num + 1

class Button:
    def __init__(self, x_percent, y_percent, width_percent, height_percent, text, font, function):
        if width_percent <= 0:
            raise ValueError("Width percent too small for Renderables.Button ({})".format(width_percent))
        if height_percent <= 0:
            raise ValueError("Height percent too small for Renderables.Button ({})".format(height_percent))
        if 0.0 <= y_percent - (height_percent / 2) and y_percent + (height_percent / 2) <= 100.0:
            self.y_percent = y_percent
            self.height_percent = height_percent
        else:
            raise ValueError(
                "Height plus offset out of bounds for Renderables.Button ({})".format(y_percent + height_percent))
        if 0.0 <= x_percent - (width_percent / 2) and x_percent + (width_percent / 2) <= 100.0:
            self.x_percent = x_percent
            self.width_percent = width_percent
        else:
            raise ValueError(
                "Width plus offset out of bounds for Renderables.Button ({})".format(x_percent + width_percent))
        self.text = "{}".format(text)
        self.text_width_percent = 0.8 * self.width_percent
        self.text_height_percent = 0.8 * self.height_percent
        if type(font) == pygame.freetype.Font:
            self.font = font
        else:
            raise TypeError("Invalid font type for Renderables.Button ({})".format(type(font)))
        self.function = function
        self.bounding_box = None

    def draw(self, screen, config):
        self.bounding_box = BackgroundBox(self.x_percent, self.y_percent, self.width_percent, self.height_percent).draw(screen, config).bounding_box
        Text(self.x_percent, self.y_percent, self.text_width_percent, self.text_height_percent, self.text, self.font).draw(screen, config)
        return self

class ArrowButton:
    def __init__(self, x_percent, y_percent, width_percent, height_percent, function, direction=0):
        if width_percent <= 0:
            raise ValueError("Width percent too small for Renderables.ArrowButton ({})".format(width_percent))
        if height_percent <= 0:
            raise ValueError("Height percent too small for Renderables.ArrowButton ({})".format(height_percent))
        if 0.0 <= y_percent - (height_percent / 2) and y_percent + (height_percent / 2) <= 100.0:
            self.y_percent = y_percent
            self.height_percent = height_percent
        else:
            raise ValueError(
                "Height plus offset out of bounds for Renderables.UpArrowButton ({})".format(y_percent + height_percent))
        if 0.0 <= x_percent - (width_percent / 2) and x_percent + (width_percent / 2) <= 100.0:
            self.x_percent = x_percent
            self.width_percent = width_percent
        else:
            raise ValueError(
                "Width plus offset out of bounds for Renderables.UpArrowButton ({})".format(x_percent + width_percent))
        self.function = function
        self.bounding_box = None
        if type(direction) == int and 0 <= direction <= 3:
            self.direction = direction
        else:
            raise ValueError("Invalid direction for Renderables.ArrowButton ({})".format(direction))

    def draw(self, screen, config):
        self.bounding_box = pygame.Rect((self.x_percent - (self.width_percent / 2)) * screen.get_width() / 100,
                                                      (self.y_percent - (self.height_percent / 2)) * screen.get_height() / 100,
                                                      screen.get_width() * self.width_percent / 100,
                                                      screen.get_height() * self.height_percent / 100)
        BackgroundBox(self.x_percent, self.y_percent, self.width_percent, self.height_percent).draw(screen, config)
        triangle_size = min(self.width_percent * 0.5, self.height_percent * 0.5)
        color = pygame.color.Color(config.text_color, config.text_color, config.text_color)
        if self.direction == 0:
            points = [
                [self.x_percent * screen.get_width() / 100,
                 (self.y_percent - (triangle_size / 2)) * screen.get_height() / 100],
                [(self.x_percent + (triangle_size / 2)) * screen.get_width() / 100,
                 (self.y_percent + (triangle_size / 2)) * screen.get_height() / 100],
                [(self.x_percent - (triangle_size / 2)) * screen.get_width() / 100,
                 (self.y_percent + (triangle_size / 2)) * screen.get_height() / 100]
            ]
        elif self.direction == 1:
            points = [
                [(self.x_percent + (triangle_size / 2)) * screen.get_width() / 100,
                 self.y_percent * screen.get_height() / 100],
                [(self.x_percent - (triangle_size / 2)) * screen.get_width() / 100,
                 (self.y_percent + (triangle_size / 2)) * screen.get_height() / 100],
                [(self.x_percent - (triangle_size / 2)) * screen.get_width() / 100,
                 (self.y_percent - (triangle_size / 2)) * screen.get_height() / 100]
            ]
        elif self.direction == 2:
            points = [
                [self.x_percent * screen.get_width() / 100,
                 (self.y_percent + (triangle_size / 2)) * screen.get_height() / 100],
                [(self.x_percent - (triangle_size / 2)) * screen.get_width() / 100,
                 (self.y_percent - (triangle_size / 2)) * screen.get_height() / 100],
                [(self.x_percent + (triangle_size / 2)) * screen.get_width() / 100,
                 (self.y_percent - (triangle_size / 2)) * screen.get_height() / 100]
            ]
        elif self.direction == 3:
            points = [
                [(self.x_percent - (triangle_size / 2)) * screen.get_width() / 100,
                 self.y_percent * screen.get_height() / 100],
                [(self.x_percent + (triangle_size / 2)) * screen.get_width() / 100,
                 (self.y_percent - (triangle_size / 2)) * screen.get_height() / 100],
                [(self.x_percent + (triangle_size / 2)) * screen.get_width() / 100,
                 (self.y_percent + (triangle_size / 2)) * screen.get_height() / 100]
            ]
        pygame.draw.polygon(screen, color, points)
        return self

class FadeInButton:
    def __init__(self, x_percent, y_percent, width_percent, height_percent, text, font, function, time_alive, lifespan):
        if width_percent <= 0:
            raise ValueError("Width percent too small for Renderables.FadeInButton ({})".format(width_percent))
        if height_percent <= 0:
            raise ValueError("Height percent too small for Renderables.FadeInButton ({})".format(height_percent))
        if time_alive >= lifespan:
            raise ValueError("Lifespan exceeded for Renderables.FadeInButton")
        if time_alive <= 0:
            raise ValueError("Renderables.FadeInButton created too soon; nothing to draw")
        if 0.0 <= y_percent - (height_percent / 2) and y_percent + (height_percent / 2) <= 100.0:
            self.y_percent = y_percent
            self.height_percent = height_percent
        else:
            raise ValueError(
                "Height plus offset out of bounds for Renderables.FadeInButton ({})".format(y_percent + height_percent))
        if 0.0 <= x_percent - (width_percent / 2) and x_percent + (width_percent / 2) <= 100.0:
            self.x_percent = x_percent
            self.width_percent = width_percent
        else:
            raise ValueError(
                "Width plus offset out of bounds for Renderables.FadeInButton ({})".format(x_percent + width_percent))
        self.text = "{}".format(text)
        if type(font) == pygame.freetype.Font:
            self.font = font
        else:
            raise TypeError("Invalid font type for Renderables.FadeInButton ({})".format(type(font)))
        self.function = function
        if time_alive <= lifespan:
            self.age_percent = time_alive / lifespan
        else:
            raise ValueError("Time alive exceeds lifespan for Renderables.FadeInButton ({}, {})".format(time_alive, lifespan))
        self.bounding_box = None

    def draw(self, screen, config):
        if not type(screen) == pygame.surface.Surface:
            raise TypeError("Unexpected argument type for Renderables.FadeInButton.draw() (Expected "
                            "pygame.surface.Surface, got {})".format(type(screen)))
        else:
            s = pygame.Surface((screen.get_width(), screen.get_height()))
            s.fill(config.chroma_key)
            s.set_colorkey(config.chroma_key, pygame.RLEACCEL)
            current_x_percent = self.x_percent + ((self.width_percent / 2) * (1 - self.age_percent))
            current_width_percent = self.width_percent * self.age_percent
            current_height_percent = self.height_percent * self.age_percent
            s.set_alpha(round(255 * self.age_percent, pygame.RLEACCEL))
            self.bounding_box = Button(current_x_percent, self.y_percent, current_width_percent, current_height_percent, self.text, self.font, self.function).draw(s, config).bounding_box
            screen.blit(s, (0, 0))
            return self

class FadeOutButton:
    def __init__(self, x_percent, y_percent, width_percent, height_percent, text,
                 font, function, time_alive, lifespan):
        if width_percent <= 0:
            raise ValueError("Width percent too small for Renderables.FadeOutButton ({})".format(width_percent))
        if height_percent <= 0:
            raise ValueError("Height percent too small for Renderables.FadeOutButton ({})".format(height_percent))
        if time_alive > lifespan:
            raise ValueError("Lifespan exceeded for Renderables.FadeOutButton")
        if time_alive == lifespan:
            raise ValueError("Renderables.FadeOutButton created too late; nothing to draw")
        if 0.0 <= y_percent - (height_percent / 2) and y_percent + (height_percent / 2) <= 100.0:
            self.y_percent = y_percent
            self.height_percent = height_percent
        else:
            raise ValueError(
                "Height plus offset out of bounds for Renderables.FadeOutButton ({})".format(y_percent + height_percent))
        if 0.0 <= x_percent - (width_percent / 2) and x_percent + (width_percent / 2) <= 100.0:
            self.x_percent = x_percent
            self.width_percent = width_percent
        else:
            raise ValueError(
                "Width plus offset out of bounds for Renderables.FadeOutButton ({})".format(x_percent + width_percent))
        self.text = "{}".format(text)
        if type(font) == pygame.freetype.Font:
            self.font = font
        else:
            raise TypeError("Invalid font type for Renderables.FadeOutButton ({})".format(type(font)))
        self.function = function
        if time_alive <= lifespan:
            self.age_percent = time_alive / lifespan
        else:
            raise ValueError("Time alive exceeds lifespan for Renderables.FadeOutButton ({}, {})".format(time_alive, lifespan))
        self.bounding_box = None

    def draw(self, screen, config):
        if not type(screen) == pygame.surface.Surface:
            raise TypeError("Unexpected argument type for Renderables.FadeOutButton.draw() (Expected "
                            "pygame.surface.Surface, got {})".format(type(screen)))
        else:
            s = pygame.Surface((screen.get_width(), screen.get_height()))
            s.fill(config.chroma_key)
            s.set_colorkey(config.chroma_key, pygame.RLEACCEL)
            current_x_percent = self.x_percent + ((self.width_percent / 2) * self.age_percent)
            current_width_percent = self.width_percent * (1 - self.age_percent)
            current_height_percent = self.height_percent * (1 - self.age_percent)
            s.set_alpha(round(255 * (1 - self.age_percent)), pygame.RLEACCEL)
            self.bounding_box = Button(current_x_percent, self.y_percent, current_width_percent, current_height_percent, self.text, self.font, self.function).draw(s, config).bounding_box
            screen.blit(s, (0, 0))
            return self

class BackgroundBox:
    def __init__(self, x_percent, y_percent, width_percent, height_percent, edge_scale=0.1, function=no_function):
        if width_percent <= 0:
            raise ValueError("Width percent too small for Renderables.BackgroundBox ({})".format(width_percent))
        if height_percent <= 0:
            raise ValueError("Height percent too small for Renderables.BackgroundBox ({})".format(height_percent))
        if 0.0 <= y_percent - (height_percent / 2) and y_percent + (height_percent / 2) <= 100.0:
            self.y_percent = y_percent
            self.height_percent = height_percent
        else:
            raise ValueError(
                "Height plus offset out of bounds for Renderables.BackgroundBox ({})".format(
                    y_percent + height_percent))
        if 0.0 <= x_percent - (width_percent / 2) and x_percent + (width_percent / 2) <= 100.0:
            self.x_percent = x_percent
            self.width_percent = width_percent
        else:
            raise ValueError(
                "Width plus offset out of bounds for Renderables.BackgroundBox ({})".format(
                    x_percent + width_percent))
        self.edge_scale = edge_scale
        self.function = function
        self.bounding_box = None
    def draw(self, screen, config):
        self.bounding_box = pygame.Rect((self.x_percent - (self.width_percent / 2)) * screen.get_width() / 100,
                                   (self.y_percent - (self.height_percent / 2)) * screen.get_height() / 100,
                                   screen.get_width() * self.width_percent / 100,
                                   screen.get_height() * self.height_percent / 100)
        edge_width_x = round(self.bounding_box.width * self.edge_scale)
        edge_width_y = round(self.bounding_box.height * self.edge_scale)
        colors = (config.front_color, config.middle_color, config.rear_color)
        scales = (1.0, 2.0 / 3.0, 1.0 / 3.0)
        for ii in range(3):
            pygame.draw.ellipse(screen,
                                colors[ii],
                                pygame.rect.Rect(self.bounding_box.x + edge_width_x - (scales[ii] * edge_width_x),
                                                 self.bounding_box.y + edge_width_y - (scales[ii] * edge_width_y),
                                                 2.0 * edge_width_x * scales[ii],
                                                 2.0 * edge_width_y * scales[ii]))
            pygame.draw.ellipse(screen,
                                colors[ii],
                                pygame.rect.Rect(self.bounding_box.x + edge_width_x - (scales[ii] * edge_width_x),
                                                 self.bounding_box.y + self.bounding_box.height - edge_width_y - (scales[ii] * edge_width_y),
                                                 2.0 * edge_width_x * scales[ii],
                                                 2.0 * edge_width_y * scales[ii]))
            pygame.draw.ellipse(screen,
                                colors[ii],
                                pygame.rect.Rect(self.bounding_box.x + self.bounding_box.width - edge_width_x - (scales[ii] * edge_width_x),
                                                 self.bounding_box.y + edge_width_y - (scales[ii] * edge_width_y),
                                                 2.0 * edge_width_x * scales[ii],
                                                 2.0 * edge_width_y * scales[ii]))
            pygame.draw.ellipse(screen,
                                colors[ii],
                                pygame.rect.Rect(self.bounding_box.x + self.bounding_box.width - edge_width_x - (scales[ii] * edge_width_x),
                                                 self.bounding_box.y + self.bounding_box.height - edge_width_y - (scales[ii] * edge_width_y),
                                                 2.0 * edge_width_x * scales[ii],
                                                 2.0 * edge_width_y * scales[ii]))
            pygame.draw.rect(screen, colors[ii], pygame.Rect(self.bounding_box.x + edge_width_x,
                                                             self.bounding_box.y + edge_width_y - (edge_width_y * scales[ii]),
                                                             self.bounding_box.width - (2 * edge_width_x),
                                                             self.bounding_box.height - (
                                                                         2 * (edge_width_y - (edge_width_y * scales[ii])))))
            pygame.draw.rect(screen, colors[ii], pygame.Rect(self.bounding_box.x + edge_width_x - (edge_width_x * scales[ii]),
                                                             self.bounding_box.y + edge_width_y,
                                                             self.bounding_box.width - (
                                                                         2 * (edge_width_x - (edge_width_x * scales[ii]))),
                                                             self.bounding_box.height - (2 * edge_width_y)))
        pygame.draw.arc(screen,
                        pygame.color.Color(config.text_color, config.text_color, config.text_color),
                        pygame.rect.Rect(self.bounding_box.x,
                                         self.bounding_box.y,
                                         edge_width_x * 2,
                                         edge_width_y * 2),
                        pi / 2,
                        pi)
        pygame.draw.arc(screen,
                        pygame.color.Color(config.text_color, config.text_color, config.text_color),
                        pygame.rect.Rect(self.bounding_box.x + self.bounding_box.width - (2 * edge_width_x),
                                         self.bounding_box.y,
                                         edge_width_x * 2,
                                         edge_width_y * 2),
                        0,
                        pi / 2)
        pygame.draw.arc(screen,
                        pygame.color.Color(config.text_color, config.text_color, config.text_color),
                        pygame.rect.Rect(self.bounding_box.x + self.bounding_box.width - (2 * edge_width_x),
                                         self.bounding_box.y + self.bounding_box.height - (2 * edge_width_y),
                                         edge_width_x * 2,
                                         edge_width_y * 2),
                        3 * pi / 2,
                        2 * pi)
        pygame.draw.arc(screen,
                        pygame.color.Color(config.text_color, config.text_color, config.text_color),
                        pygame.rect.Rect(self.bounding_box.x,
                                         self.bounding_box.y + self.bounding_box.height - (2 * edge_width_y),
                                         edge_width_x * 2,
                                         edge_width_y * 2),
                        pi,
                        3 * pi / 2)
        pygame.draw.line(screen,
                         pygame.color.Color(config.text_color, config.text_color, config.text_color),
                         (self.bounding_box.x + edge_width_x, self.bounding_box.y),
                         (self.bounding_box.x + self.bounding_box.width - edge_width_x, self.bounding_box.y))
        pygame.draw.line(screen,
                         pygame.color.Color(config.text_color, config.text_color, config.text_color),
                         (self.bounding_box.x + edge_width_x, self.bounding_box.y + self.bounding_box.height),
                         (self.bounding_box.x + self.bounding_box.width - edge_width_x, self.bounding_box.y + self.bounding_box.height))
        pygame.draw.line(screen,
                         pygame.color.Color(config.text_color, config.text_color, config.text_color),
                         (self.bounding_box.x, self.bounding_box.y + edge_width_y),
                         (self.bounding_box.x, self.bounding_box.y + self.bounding_box.height - edge_width_y))
        pygame.draw.line(screen,
                         pygame.color.Color(config.text_color, config.text_color, config.text_color),
                         (self.bounding_box.x + self.bounding_box.width, self.bounding_box.y + edge_width_y),
                         (self.bounding_box.x + self.bounding_box.width, self.bounding_box.y + self.bounding_box.height - edge_width_y))
        return self

class Blackout:
    def __init__(self, age=None, lifespan=None, fade_out=True, function=no_function):
        self.age = age
        self.lifespan = lifespan
        self.fade_out = fade_out
        self.bounding_box = None
        self.function = function
    def draw(self, screen, config):
        self.bounding_box = pygame.Rect(0, 0, screen.get_width(), screen.get_height())
        if self.age is not None and self.lifespan is not None:
            s = pygame.Surface((screen.get_width(), screen.get_height()))
            s.set_colorkey(config.chroma_key, pygame.RLEACCEL)
            if self.fade_out:
                s.set_alpha(255 - round(255 * self.age / self.lifespan), pygame.RLEACCEL)
            else:
                s.set_alpha(round(255 * self.age / self.lifespan), pygame.RLEACCEL)
            s.fill(pygame.color.Color(config.text_color, config.text_color, config.text_color))
            screen.blit(s, (0, 0))
        else:
            screen.fill(pygame.color.Color(config.text_color, config.text_color, config.text_color))
        return self

class TitleText:
    def __init__(self, fade_percent):
        if 0 <= fade_percent <= 1:
            self.fade_percent = fade_percent
        else:
            raise ValueError("fade_percent out of bounds for Renderables.TitleText ({})".format(fade_percent))
    def draw(self, screen, config):
        s = pygame.Surface((screen.get_width(), screen.get_height()))
        s.fill(config.chroma_key)
        s.set_colorkey(config.chroma_key, pygame.RLEACCEL)
        s.set_alpha(round(255 * self.fade_percent), pygame.RLEACCEL)
        Text(50, 45, 100, 10, "Team S.T.R.U.M.", config.header, color="white").draw(s, config)
        Text(50, 52.5, 100, 5, "presents", config.italic, color="white").draw(s, config)
        screen.blit(s, (0, 0))

class Logo:
    def __init__(self, x_percent, y_percent, width_percent, height_percent, rotational_angle):
        if 0.0 <= y_percent - (height_percent / 2) and y_percent + (height_percent / 2) <= 100.0:
            self.y_percent = y_percent
            self.height_percent = height_percent
        else:
            raise ValueError(
                "Height plus offset out of bounds for Renderables.Logo ({})".format(
                    y_percent + height_percent))
        if 0.0 <= x_percent - (width_percent / 2) and x_percent + (width_percent / 2) <= 100.0:
            self.x_percent = x_percent
            self.width_percent = width_percent
        else:
            raise ValueError(
                "Width plus offset out of bounds for Renderables.Logo ({})".format(
                    x_percent + width_percent))
        self.rotational_angle = rotational_angle
    def draw(self, screen, config):
        if (self.width_percent / self.height_percent) > (config.logo.get_width() / config.logo.get_height()):
            scaler = (self.height_percent * screen.get_height()) / (100 * config.logo.get_height())
        else:
            scaler = (self.width_percent * screen.get_width()) / (100 * config.logo.get_width())
        scaled_logo = pygame.transform.rotozoom(config.logo, self.rotational_angle, scaler)
        scaled_logo = pygame.mask.from_surface(scaled_logo)\
            .to_surface(setcolor=pygame.color.Color(config.text_color, config.text_color, config.text_color),
                        unsetcolor=None)
        x_px = (self.x_percent * screen.get_width() / 100) - (scaled_logo.get_width() / 2)
        y_px = (self.y_percent * screen.get_height() / 100) - (scaled_logo.get_height() / 2)
        screen.blit(scaled_logo, (x_px, y_px))

class CheckBox:
    def __init__(self, x_percent, y_percent, width_percent, height_percent, function, value_set):
        if 0.0 <= y_percent - (height_percent / 2) and y_percent + (height_percent / 2) <= 100.0:
            self.y_percent = y_percent
            self.height_percent = height_percent
        else:
            raise ValueError(
                "Height plus offset out of bounds for Renderables.CheckBox ({})".format(y_percent + height_percent))
        if 0.0 <= x_percent - (width_percent / 2) and x_percent + (width_percent / 2) <= 100.0:
            self.x_percent = x_percent
            self.width_percent = width_percent
        else:
            raise ValueError(
                "Width plus offset out of bounds for Renderables.CheckBox ({})".format(x_percent + width_percent))
        if type(value_set) == bool:
            self.value_set = value_set
        else:
            raise TypeError("Invalid type for Renderables.CheckBox.set ({})".format(type(set)))
        self.function = function
        self.bounding_box = None

    def draw(self, screen, config):
        rect_side_length = min(self.width_percent * screen.get_width() / 100, self.height_percent * screen.get_height() / 100)
        self.bounding_box = pygame.Rect((self.x_percent * screen.get_width() / 100) - (rect_side_length / 2),
                                   (self.y_percent * screen.get_height() / 100) - (rect_side_length / 2),
                                   rect_side_length, rect_side_length)
        pygame.draw.ellipse(screen, config.front_color, self.bounding_box)
        pygame.draw.ellipse(screen, config.middle_color, self.bounding_box.scale_by(0.9, 0.9))
        pygame.draw.ellipse(screen, config.rear_color, self.bounding_box.scale_by(0.8, 0.8))
        if self.value_set:
            pygame.draw.ellipse(screen, pygame.color.Color(config.text_color, config.text_color, config.text_color), self.bounding_box.scale_by(0.7, 0.7))
        return self

class SlideBar:
    def __init__(self, x_percent, y_percent, width_percent, height_percent, function, cursor_percent):
        if 0.0 <= y_percent - (height_percent / 2) and y_percent + (height_percent / 2) <= 100.0:
            self.y_percent = y_percent
            self.height_percent = height_percent
        else:
            raise ValueError(
                "Height plus offset out of bounds for Renderables.SlideBar ({})".format(y_percent + height_percent))
        if 0.0 <= x_percent - (width_percent / 2) and x_percent + (width_percent / 2) <= 100.0:
            self.x_percent = x_percent
            self.width_percent = width_percent
        else:
            raise ValueError(
                "Width plus offset out of bounds for Renderables.SlideBar ({})".format(x_percent + width_percent))
        if 0.0 <= cursor_percent <= 100.0:
            self.cursor_percent = cursor_percent
        else:
            raise ValueError(
                "cursor_percent out of bounds for Renderables.SlideBar ({})".format(cursor_percent))
        self.function = function
        self.bounding_box = None
        self.start_x = None
        self.end_x = None

    def draw(self, screen, config):
        cursor_radius = self.height_percent * screen.get_height() / 200
        self.start_x = ((self.x_percent - (self.width_percent / 2)) * screen.get_width() / 100) + cursor_radius
        y = self.y_percent * screen.get_height() / 100
        self.end_x = ((self.x_percent + (self.width_percent / 2)) * screen.get_width() / 100) - cursor_radius
        pygame.draw.line(screen, pygame.color.Color(config.text_color, config.text_color, config.text_color), (self.start_x, y), (self.end_x, y))
        self.line_width_percent = 100 * (self.end_x - self.start_x) / screen.get_width()
        cursor_x = (self.start_x + ((self.cursor_percent * self.line_width_percent / 100) * screen.get_width() / 100))
        self.bounding_box = pygame.draw.circle(screen, config.front_color, (cursor_x, y), cursor_radius)
        pygame.draw.circle(screen, config.middle_color, (cursor_x, y), cursor_radius * 0.9)
        pygame.draw.circle(screen, config.rear_color, (cursor_x, y), cursor_radius * 0.8)
        return self


def as_time_string(seconds):
    minutes = round((seconds - (seconds % 60)) / 60)
    seconds = "{}".format(seconds % 60).rjust(2, "0")
    return "{}:{}".format(minutes, seconds)

# Add available classes here for indexing by other modules
available = [AnalysisGraph, BackgroundBox, Blackout, Button, CheckBox, ArrowButton, FadingFretMark, FadeInButton, FadeOutButton, FallingChord, FretLine, FretMark, LoadBar, Logo, SlideBar, StringLine, Text, TitleText]
