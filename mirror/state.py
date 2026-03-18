import pygame
from datetime import datetime


class MirrorState:
    def __init__(self, config):
        self.config = config

        # Clock config
        clock_cfg = config["clock"]
        color_cfg = config["colors"]

        self.time_format = "%I:%M %p"  # 12-hour time with AM/PM
        self.font = pygame.font.SysFont(None, clock_cfg["font_size"])

        # Colors
        self.text_color = color_cfg["text"]
        self.bg_color = color_cfg["background"]

        self.time_text = ""

    def update(self):
        # Update the clock text
        self.time_text = datetime.now().strftime(self.time_format).lstrip("0")

    def draw(self, screen):
        # Clear background
        screen.fill(self.bg_color)

        # Render clock
        text_surface = self.font.render(
            self.time_text,
            True,
            self.text_color
        )

        # Position: top-right with margin
        margin = 10
        rect = text_surface.get_rect(
            topright=(screen.get_width() - margin, margin)
        )

        screen.blit(text_surface, rect)
