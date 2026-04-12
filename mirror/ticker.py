import pygame


class TickerBar:
    def __init__(self, config):
        tcfg = config.get("ticker", {})
        colors = config.get("colors", {})

        self.enabled = bool(tcfg.get("enabled", True))
        self.height = int(tcfg.get("height", 44))
        self.speed = float(tcfg.get("speed_px_per_sec", 70))
        self.padding = int(tcfg.get("padding", 12))

        self.text_color = tuple(colors.get("text", [192, 192, 192]))
        self.bg_color = tuple(colors.get("background", [0, 0, 0]))

        self.font = pygame.font.SysFont(None, int(tcfg.get("font_size", 26)))

        self.text = ""
        self.surf = None
        self.x = 0.0

    def set_text(self, text):
        text = text or ""
        if text != self.text:
            self.text = text
            self.surf = self.font.render(self.text, True, self.text_color)
            self.x = 0.0

    def update(self, dt):
        if not self.enabled or not self.surf:
            return
        self.x -= self.speed * dt

    def draw(self, screen):
        if not self.enabled or not self.surf:
            return

        w, h = screen.get_size()
        y = h - self.height

        # background bar (same black, but you can tint if you want)
        pygame.draw.rect(screen, self.bg_color, (0, y, w, self.height))

        # start position when new text
        if self.x == 0.0:
            self.x = w + self.padding

        yy = y + (self.height - self.surf.get_height()) // 2
        screen.blit(self.surf, (self.x, yy))

        # wrap when off-screen
        if self.x + self.surf.get_width() < 0:
            self.x = w + self.padding
