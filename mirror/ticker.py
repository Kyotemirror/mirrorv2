import pygame

class TickerBar:
    def __init__(self, cfg):
        t = cfg["ticker"]
        self.enabled = t["enabled"]
        self.height = t["height"]
        self.speed = t["speed_px_per_sec"]
        self.pad = t["padding"]
        self.color = tuple(cfg["colors"]["text"])
        self.bg = tuple(cfg["colors"]["background"])
        self.font = pygame.font.SysFont(None, t["font_size"])
        self.text = ""
        self.surf = None
        self.x = 0

    def set_text(self, txt):
        if txt != self.text:
            self.text = txt
            self.surf = self.font.render(txt, True, self.color)
            self.x = 0

    def update(self, dt):
        if self.surf:
            self.x -= self.speed * dt

    def draw(self, s):
        if not self.surf: return
        w,h = s.get_size()
        y = h - self.height
        pygame.draw.rect(s, self.bg, (0,y,w,self.height))
        if self.x == 0: self.x = w + self.pad
        s.blit(self.surf, (self.x, y+(self.height-self.surf.get_height())//2))
        if self.x + self.surf.get_width() < 0:
            self.x = w + self.pad
