import pygame
from datetime import datetime


class MirrorState:
    def __init__(self, config):
        self.config = config

        # ✅ Safe colors (ignore config for now)
        self.bg_color = (0, 0, 0)
        self.text_color = (255, 255, 255)

        # ✅ Big readable font
        self.font = pygame.font.SysFont(None, 72)

        self.time_text = "STARTING"

    def update(self):
        self.time_text = datetime.now().strftime("%I:%M %p").lstrip("0")

    def draw(self, screen):
        # ✅ BRIGHT BACKGROUND PROOF
        screen.fill(self.bg_color)

        text_surface = self.font.render(
            self.time_text, True, self.text_color
        )

        rect = text_surface.get_rect(
            center=screen.get_rect().center
        )

        screen.blit(text_surface, rect)
