import os
import pygame

from pages import PageManager, build_pages
from ticker import TickerBar


class MirrorState:
    def __init__(self, config):
        self.config = config

        colors = config.get("colors", {})
        self.bg_color = tuple(colors.get("background", [0, 0, 0]))

        self.pages = build_pages(config)
        self.page_manager = PageManager(config, self.pages)

        self.ticker = TickerBar(config)

        # Logos
        self.logo_cfg = config.get("logos", {})
        self.logo_left = None
        self.logo_right = None
        if self.logo_cfg.get("enabled", True):
            self._load_logos()

    def _load_logos(self):
        def load_logo(path):
            logo = pygame.image.load(path).convert_alpha()
            max_width = int(self.logo_cfg.get("max_width", 160))
            if logo.get_width() > max_width:
                scale = max_width / logo.get_width()
                logo = pygame.transform.smoothscale(
                    logo,
                    (int(logo.get_width() * scale), int(logo.get_height() * scale))
                )
            logo.set_alpha(int(self.logo_cfg.get("alpha", 180)))
            return logo

        try:
            left_path = self.logo_cfg.get("left")
            right_path = self.logo_cfg.get("right")

            if left_path and os.path.exists(os.path.join(os.path.dirname(os.path.dirname(__file__)), left_path)):
                self.logo_left = load_logo(os.path.join(os.path.dirname(os.path.dirname(__file__)), left_path))

            if right_path and os.path.exists(os.path.join(os.path.dirname(os.path.dirname(__file__)), right_path)):
                self.logo_right = load_logo(os.path.join(os.path.dirname(os.path.dirname(__file__)), right_path))

        except Exception as e:
            print("Logo load failed:", e)

    def update(self, dt):
        self.page_manager.update(dt)

        # Set ticker text from current page (page-specific ticker)
        ticker_text = self.page_manager.current_ticker_text()
        self.ticker.set_text(ticker_text)

        self.ticker.update(dt)

    def draw(self, screen):
        screen.fill(self.bg_color)

        # Draw current page in a content area above ticker
        content_rect = screen.get_rect().copy()
        if self.ticker.enabled:
            content_rect.height -= self.ticker.height

        self.page_manager.draw(screen, content_rect)

        # Draw logos near bottom (above ticker)
        self._draw_logos(screen, content_rect)

        # Draw ticker last (always on top)
        self.ticker.draw(screen)

    def _draw_logos(self, screen, content_rect):
        if not (self.logo_left or self.logo_right):
            return

        spacing = int(self.logo_cfg.get("spacing", 10))
        bottom_margin = int(self.logo_cfg.get("bottom_margin", 6))

        if self.logo_left and self.logo_right:
            total_width = self.logo_left.get_width() + spacing + self.logo_right.get_width()
            max_height = max(self.logo_left.get_height(), self.logo_right.get_height())

            group_rect = pygame.Rect(0, 0, total_width, max_height)
            group_rect.midbottom = (content_rect.centerx, content_rect.bottom - bottom_margin)

            left_rect = self.logo_left.get_rect()
            left_rect.bottomleft = group_rect.bottomleft

            right_rect = self.logo_right.get_rect()
            right_rect.bottomleft = (left_rect.right + spacing, left_rect.bottom)

            screen.blit(self.logo_left, left_rect)
            screen.blit(self.logo_right, right_rect)

        else:
            logo = self.logo_right or self.logo_left
            rect = logo.get_rect()
            rect.midbottom = (content_rect.centerx, content_rect.bottom - bottom_margin)
            screen.blit(logo, rect)
