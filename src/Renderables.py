import pygame


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
            raise TypeError("Unexpected argument type for Renderables.StringLine.draw() (Expected pygame.display, got {})"
                            .format(type(screen)))
        else:
            start_x = ((100.0 - self.width_percent) / 200) * screen.get_width()
            end_x = screen.get_width() - start_x
            y = screen.get_height() * self.y_percent / 100
            pygame.draw.line(screen,
                             "white",
                             (start_x, y),
                             (end_x, y))

# Add available classes here for indexing by other modules
available = [StringLine]