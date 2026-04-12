import pygame, datetime
from weather import WeatherWidget
from news import RssNewsProvider
from quotes import QuotesProvider

def build_pages(cfg):
    return [
        TimePage(cfg),
        WeatherPage(cfg),
        NewsPage(cfg),
        QuotesPage(cfg)
    ]

class PageManager:
    def __init__(self, cfg, pages):
        self.pages = pages
        self.idx = 0
        self.t = 0
        self.interval = cfg["pages"]["switch_interval"]

    def update(self, dt):
        self.t += dt
        if self.t >= self.interval:
            self.t = 0
            self.idx = (self.idx + 1) % len(self.pages)
        self.pages[self.idx].update(dt)

    def draw(self, screen, rect):
        self.pages[self.idx].draw(screen, rect)

    def ticker_text(self):
        return self.pages[self.idx].ticker()

class TimePage:
    def __init__(self, cfg):
        c = cfg["colors"]["text"]
        self.color = tuple(c)
        self.font = pygame.font.SysFont(None, cfg["clock"]["font_size"])
        self.datef = pygame.font.SysFont(None, cfg["clock"]["date_font_size"])

    def update(self, dt): pass

    def draw(self, s, r):
        now = datetime.datetime.now()
        t = self.font.render(now.strftime("%I:%M %p").lstrip("0"), True, self.color)
        d = self.datef.render(now.strftime("%A, %b %d"), True, self.color)
        s.blit(d, d.get_rect(center=(r.centerx, r.centery-48)))
        s.blit(t, t.get_rect(center=r.center))

    def ticker(self):
        return "Time • " + datetime.datetime.now().strftime("%I:%M %p").lstrip("0")

class WeatherPage:
    def __init__(self, cfg):
        self.weather = WeatherWidget(cfg)
        self.color = tuple(cfg["colors"]["text"])
        self.big = pygame.font.SysFont(None, 64)

    def update(self, dt):
        self.weather.update()

    def draw(self, s, r):
        self.weather.draw(s)
        t = self.big.render(self.weather.temperature, True, self.color)
        s.blit(t, t.get_rect(center=r.center))
        d = pygame.font.SysFont(None, 28).render(self.weather.description, True, self.color)
        s.blit(d, d.get_rect(center=(r.centerx, r.centery+40)))

    def ticker(self):
        return f"Weather • {self.weather.temperature} • {self.weather.description}"

class NewsPage:
    def __init__(self, cfg):
        self.news = RssNewsProvider(cfg)
        self.c = tuple(cfg["colors"]["text"])
        self.font = pygame.font.SysFont(None, 28)

    def update(self, dt): self.news.update()

    def draw(self, s, r):
        y = r.top
        for h in self.news.headlines[:4]:
            surf = self.font.render(h, True, self.c)
            s.blit(surf, (r.left, y))
            y += surf.get_height()+8

    def ticker(self):
        return "News • " + " • ".join(self.news.headlines)

class QuotesPage:
    def __init__(self, cfg):
        self.q = QuotesProvider(cfg)
        self.c = tuple(cfg["colors"]["text"])
        self.font = pygame.font.SysFont(None, 34)

    def update(self, dt): self.q.update()

    def draw(self, s, r):
        lines = self._wrap(self.q.current(), self.font, r.width-20)
        y = r.centery - len(lines)*18
        for l in lines:
            surf = self.font.render(l, True, self.c)
            s.blit(surf, surf.get_rect(center=(r.centerx,y)))
            y += 36

    def ticker(self):
        return "Quote • " + self.q.current()

    def _wrap(self, t, f, w):
        words, lines, cur = t.split(), [], ""
        for w2 in words:
            test = (cur+" "+w2).strip()
            if f.size(test)[0] <= w: cur = test
            else: lines.append(cur); cur = w2
        if cur: lines.append(cur)
        return lines
