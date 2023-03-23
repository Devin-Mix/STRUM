import pygame
from math import ceil

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

    # Expects a resolution in the format (x_resolution, y_resolution)
    def draw(self, screen):
        if not type(screen) == pygame.surface.Surface:
            raise TypeError("Unexpected argument type for Renderables.StringLine.draw() (Expected pygame.surface."
                            "Surface, got {})".format(type(screen)))
        else:
            start_x = ((100.0 - self.width_percent) / 200) * screen.get_width()
            end_x = screen.get_width() - start_x
            y = screen.get_height() * self.y_percent / 100
            s = pygame.Surface((screen.get_width(), screen.get_height()), pygame.SRCALPHA)
            pygame.draw.line(s,
                             (255, 255, 255, 255 * min(1.0, (self.y_percent - 5.0) / 90.0)),
                             (start_x, y),
                             (end_x, y))
            screen.blit(s, (0, 0))


class FretLine:
    def __init__(self, x_percent, height_percent):
        if 0.0 <= x_percent <= 100.0:
            self.x_percent = x_percent
        else:
            raise ValueError("x_percent out of bounds for FretLine renderable ({})".format(x_percent))
        if 0.0 <= height_percent <= 100.0:
            self.height_percent = height_percent
        else:
            raise ValueError("height_percent out of bounds for FretLine renderable ({})".format(height_percent))

    def draw(self, screen):
        if not type(screen) == pygame.surface.Surface:
            raise TypeError("Unexpected argument type for Renderables.FretLine.draw() (Expected pygame.surface.Surface,"
                            " got {})".format(type(screen)))
        else:
            start_y = (95.0 - self.height_percent) * screen.get_height() / 100
            end_y = 0.95 * screen.get_height()
            x = self.x_percent * screen.get_width() / 100
            pygame.draw.line(screen,
                             "white",
                             (x, start_y),
                             (x, end_y))


class FretMark:
    def __init__(self, x_percent, y_percent):
        if 0.0 <= x_percent <= 100.0:
            self.x_percent = x_percent
        else:
            raise ValueError("x_percent out of bounds for FretMark renderable ({})".format(x_percent))
        if 0.0 <= y_percent <= 100.0:
            self.y_percent = y_percent
        else:
            raise ValueError("height_percent out of bounds for FretMark renderable ({})".format(y_percent))

    def draw(self, screen):
        if not type(screen) == pygame.surface.Surface:
            raise TypeError("Unexpected argument type for Renderables.FretMark.draw() (Expected pygame.surface.Surface,"
                            " got {})".format(type(screen)))
        else:
            x = self.x_percent * screen.get_width() / 100.0
            y = self.y_percent * screen.get_height() / 100.0
            s = pygame.Surface((screen.get_width(), screen.get_height()), pygame.SRCALPHA)
            pygame.draw.circle(s,
                               (255, 255, 255, 255 * min(1.0, (self.y_percent - 5.0) / 90.0)),
                               (x, y),
                               0.01 * screen.get_width())
            screen.blit(s, (0, 0))


class FadingFretMark:
    def __init__(self, x_percent, y_percent, birth_time, time_to_live, time_now):
        if 0.0 <= x_percent <= 100.0:
            self.x_percent = x_percent
        else:
            raise ValueError("x_percent out of bounds for FretMark renderable ({})".format(x_percent))
        if 0.0 <= y_percent <= 100.0:
            self.y_percent = y_percent
        else:
            raise ValueError("height_percent out of bounds for FretMark renderable ({})".format(y_percent))
        # TODO: Need type checking here for safety
        self.birth_time = birth_time
        self.time_to_live = time_to_live
        self.time_now = time_now

    def draw(self, screen):
        if not type(screen) == pygame.surface.Surface:
            raise TypeError("Unexpected argument type for Renderables.FadingFretMark.draw() (Expected "
                            "pygame.surface.Surface, got {})".format(type(screen)))
        else:
            x = self.x_percent * screen.get_width() / 100.0
            y = self.y_percent * screen.get_height() / 100.0
            s = pygame.Surface((screen.get_width(), screen.get_height()), pygame.SRCALPHA)
            alpha = 255 * (1 - ((self.time_now - self.birth_time)/self.time_to_live))
            pygame.draw.circle(s,
                               (255, 255, 255, alpha),
                               (x, y),
                               0.01 * screen.get_width())
            screen.blit(s, (0, 0))

    def is_alive(self):
        return (1 - ((self.time_now - self.birth_time)/self.time_to_live)) > 0

    def update_time(self, time_now):
        self.time_now = time_now
        return self

class LoadBar:
    def __init__(self, y_percent, width_percent, height_percent, load_percent):
        if 0.0 <= y_percent + height_percent <= 100.0:
            self.y_percent = y_percent
            self.height_percent = height_percent
        else:
            raise ValueError("Height plus offset out of bounds for Renderables.LoadBar ({})".format(y_percent + height_percent))
        if 0.0 <= width_percent <= 100.0:
            self.width_percent = width_percent
        else:
            raise ValueError("Width out of bounds for Renderables.LoadBar ({})".format(width_percent))
        if 0.0 <= load_percent <= 100.0:
            self.load_percent = load_percent
        else:
            raise ValueError("Load percent out of bounts for Renderables.LoadBar ({})".format(load_percent))

    def draw(self, screen):
        if not type(screen) == pygame.surface.Surface:
            raise TypeError("Unexpected argument type for Renderables.LoadBar.draw() (Expected "
                            "pygame.surface.Surface, got {})".format(type(screen)))
        else:
            x = (50.0 - (self.width_percent / 2.0)) * screen.get_width() / 100.0
            width = (self.width_percent * screen.get_width() / 100.0) * (self.load_percent / 100.0)
            height = self.height_percent * screen.get_height() / 100.0
            y = self.y_percent * screen.get_height() / 100.0
            pygame.draw.rect(screen, "white", pygame.Rect(x, y, width, height))

class Text:
    def __init__(self, x_percent, y_percent, max_width_percent, max_height_percent, text, font, align_center=True):
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
        self.text = "{}".format(text)
        if type(align_center) is bool:
            self.align_center = align_center
        else:
            raise TypeError("Invalid align_center type for Renderables.Text ({})".format(type(align_center)))
        if type(font) == pygame.freetype.Font:
            self.font = font
        else:
            raise TypeError("Invalid font type for Renderables.Text ({})".format(type(font)))

    def draw(self, screen):
        if not type(screen) == pygame.surface.Surface:
            raise TypeError("Unexpected argument type for Renderables.Text.draw() (Expected "
                            "pygame.surface.Surface, got {})".format(type(screen)))
        else:
            if self.font.scalable:
                x = self.x_percent * screen.get_width() / 100.0
                y = self.y_percent * screen.get_height() / 100.0
                max_width = self.max_width_percent * screen.get_width() / 100.0
                max_height = self.max_height_percent * screen.get_height() / 100.0
                size = 0.75 * max_height
                width = self.font.get_rect(self.text, size=size, style=pygame.freetype.STYLE_NORMAL).width
                while width > max_width:
                    size = size * 0.99
                    width = self.font.get_rect(self.text, size=size, style=pygame.freetype.STYLE_NORMAL).width
                height = self.font.get_rect(self.text, size=size, style=pygame.freetype.STYLE_NORMAL).height
                if self.align_center:
                    self.font.render_to(screen,
                                        (x - (width / 2.0), y - (height / 2.0)),
                                        self.text,
                                        fgcolor="black",
                                        size=size,
                                        style=pygame.freetype.STYLE_NORMAL)
                else:
                    self.font.render_to(screen,
                                        (x, y),
                                        self.text,
                                        fgcolor="black",
                                        size=size,
                                        style=pygame.freetype.STYLE_NORMAL)
            else:
                raise TypeError("Font {} not scalable".format(self.font))

class AnalysisGraph:
    def __init__(self, y_percent, width_percent, height_percent, values, regular_font, italic_font, song_length):
        if 0.0 <= y_percent + height_percent <= 100.0:
            self.y_percent = y_percent
            self.height_percent = height_percent
        else:
            raise ValueError("Height plus offset out of bounds for Renderables.AnalysisGraph ({})".format(y_percent + height_percent))
        if 0.0 <= width_percent <= 100.0:
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

    def draw(self, screen):
        division_width = self.width_percent / len(self.values)
        main_height = self.height_percent * 0.35
        key_height = self.height_percent - (2.0 * main_height)
        for ii in range(len(self.values)):
            Text(50.0 - (self.width_percent / 2) + (ii * division_width) + (division_width / 2) + (0.025 * division_width),
                 self.y_percent - (self.height_percent / 2) + (main_height / 2) + (0.025 * main_height),
                 0.95 * division_width,
                 0.95 * main_height,
                 "{}%".format(round(100 * self.values[ii], 2)),
                 self.regular_font).draw(screen)
            pygame.draw.rect(screen,
                             "white",
                             pygame.Rect(screen.get_width() * (50.0 - (self.width_percent / 2) + (ii * division_width)) / 100,
                                         screen.get_height() * (self.y_percent - (self.height_percent / 2) + (2 * main_height) - (main_height * self.values[ii])) / 100,
                                         screen.get_width() * division_width / 100,
                                         ceil(self.values[ii] * main_height * screen.get_height() / 100)))
        pygame.draw.line(screen,
                         "white",
                         (screen.get_width() * (100 - self.width_percent) / 200, screen.get_height() * (
                                     self.y_percent - (0.5 * self.height_percent) + (2 * main_height)) / 100),
                         (screen.get_width() * (self.width_percent + ((100 - self.width_percent) / 2)) / 100, screen.get_height() * (
                                     self.y_percent - (0.5 * self.height_percent) + (2 * main_height)) / 100))
        seconds_per_timing_mark = 5
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
                Text(50.0 - (self.width_percent / 2) + next_mark_percent - (timing_mark_width / 2) + (0.025 * timing_mark_width),
                     self.y_percent + (self.height_percent / 2) - (key_height / 2) + (0.025 * key_height),
                     0.95 * timing_mark_width,
                     0.95 * key_height,
                     "{} - {}".format(as_time_string((next_mark_num - 1) * seconds_per_timing_mark), as_time_string(next_mark_num * seconds_per_timing_mark)),
                     self.regular_font).draw(screen)
            next_mark_percent = next_mark_percent + timing_mark_width
            next_mark_num = next_mark_num + 1


def as_time_string(seconds):
    minutes = round((seconds - (seconds % 60)) / 60)
    seconds = "{}".format(seconds % 60).rjust(2, "0")
    return "{}:{}".format(minutes, seconds)

# Add available classes here for indexing by other modules
available = [AnalysisGraph, FadingFretMark, FretLine, FretMark, LoadBar, StringLine, Text]
