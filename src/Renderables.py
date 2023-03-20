import pygame
from time import time


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
    def __init__(self, x_percent, y_percent, birth_time, time_to_live):
        if 0.0 <= x_percent <= 100.0:
            self.x_percent = x_percent
        else:
            raise ValueError("x_percent out of bounds for FretMark renderable ({})".format(x_percent))
        if 0.0 <= y_percent <= 100.0:
            self.y_percent = y_percent
        else:
            raise ValueError("height_percent out of bounds for FretMark renderable ({})".format(y_percent))
        self.birth_time = birth_time
        self.time_to_live = time_to_live

    def draw(self, screen):
        if not type(screen) == pygame.surface.Surface:
            raise TypeError("Unexpected argument type for Renderables.FretMark.draw() (Expected pygame.surface.Surface,"
                            " got {})".format(type(screen)))
        else:
            x = self.x_percent * screen.get_width() / 100.0
            y = self.y_percent * screen.get_height() / 100.0
            s = pygame.Surface((screen.get_width(), screen.get_height()), pygame.SRCALPHA)
            pygame.draw.circle(s,
                               (255, 255, 255, 255 * (1 - ((time() - self.birth_time)/self.time_to_live))),
                               (x, y),
                               0.01 * screen.get_width())
            screen.blit(s, (0, 0))

    def is_dead(self):
        return (1 - ((time() - self.birth_time)/self.time_to_live)) > 0


# Add available classes here for indexing by other modules
available = [FretLine, FretMark, StringLine]
