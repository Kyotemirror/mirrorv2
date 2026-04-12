import os, pygame
from pages import build_pages, PageManager
from ticker import TickerBar

class MirrorState:
    def __init__(self, config):
        self.config = config
        self.bg = tuple(config["colors"]["background"])

        self.layout = {
            "margin": 24,
            "top_safe": 20,
            "bottom_safe": 12
        }

        self.pages = build_pages(config)
        self.manager = PageManager(config, self.pages)
        self.ticker = TickerBar(config)
        self._load_logos()

    def _load_logos(self):
        self.left = self.right = None
        cfg = self.config["logos"]
        root = os.path.dirname(os.path.dirname(__file__))

        def load(path):
            img = pygame.image.load(path).convert_alpha()
            w = cfg["max_width"]
            if img.get_width() > w:
                s = w / img.get_width()
                img = pygame.transform.smoothscale(img, (int(img.get_width()*s), int(img.get_height()*s)))
            img.set_alpha(cfg["alpha"])
            return img

        if cfg["enabled"]:
            lp = os.path.join(root, cfg["left"])
            rp = os.path.join(root, cfg["right"])
            if os.path.exists(lp): self.left = load(lp)
            if os.path.exists(rp): self.right = load(rp)

    def update(self, dt):
        self.manager.update(dt)
        self.ticker.set_text(self.manager.ticker_text())
        self.ticker.update(dt)

    def draw(self, screen):
        screen.fill(self.bg)

        rect = screen.get_rect()
        rect.inflate_ip(-self.layout["margin"]*2, -(self.layout["top_safe"]+self.layout["bottom_safe"]))
        rect.top += self.layout["top_safe"]
        rect.height -= self.ticker.height

        self.manager.draw(screen, rect)
        self._draw_logos(screen, rect)
        self.ticker.draw(screen)

    def _draw_logos(self, screen, rect):
        if self.left and self.right:
            spacing = self.config["logos"]["spacing"]
            total = self.left.get_width() + spacing + self.right.get_width()
            y = rect.bottom - self.config["logos"]["bottom_margin"]
            x = rect.centerx - total//2
            screen.blit(self.left, (x, y-self.left.get_height()))
            screen.blit(self.right,(x+self.left.get_width()+spacing, y-self.right.get_height()))
