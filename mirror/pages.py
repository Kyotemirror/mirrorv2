import pygame
from datetime import datetime

from weather import WeatherWidget
from news import RssNewsProvider
from quotes import QuotesProvider


def build_pages(config):
    order = config.get("pages", {}).get("order", ["time", "weather", "news", "quotes"])
    pages = []
    for name in order:
        if name == "time":
            pages.append(TimePage(config))
        elif name == "weather" and config.get("weather", {}).get("enabled", False):
            pages.append(WeatherPage(config))
        elif name == "news" and config.get("news", {}).get("enabled", False):
            pages.append(NewsPage(config))
        elif name == "quotes" and config.get("quotes", {}).get("enabled", False):
            pages.append(QuotesPage(config))
    return pages


class PageManager:
    def __init__(self, config, pages):
        self.config = config
        self.pages = pages or [TimePage(config)]
        self.idx = 0
        self.elapsed = 0.0
        self.switch_interval = float(config.get("pages", {}).get("switch_interval", 60))

    def update(self, dt):
        self.elapsed += dt
        if self.elapsed >= self.switch_interval:
            self.elapsed = 0.0
            self.idx = (self.idx + 1) % len(self.pages)

        self.pages[self.idx].update(dt)

    def draw(self, screen, content_rect):
        self.pages[self.idx].draw(screen, content_rect)

    def current_ticker_text(self):
        return self.pages[self.idx].ticker_text()


# -------------------------
# Pages
# -------------------------

class TimePage:
    def __init__(self, config):
        self.config = config
        colors = config.get("colors", {})
        self.text_color = tuple(colors.get("text", [192, 192, 192]))

        ccfg = config.get("clock", {})
        self.clock_font = pygame.font.SysFont(None, int(ccfg.get("font_size", 72)))
        self.date_font = pygame.font.SysFont(None, int(ccfg.get("date_font_size", 32)))

        self.time_text = ""
        self.date_text = ""

        self._time_surf = None
        self._date_surf = None
        self._last_minute = None
        self._last_day = None

    def update(self, dt):
        now = datetime.now()
        minute_key = now.strftime("%Y-%m-%d %H:%M")
        day_key = now.strftime("%Y-%m-%d")

        if minute_key != self._last_minute:
            self.time_text = now.strftime("%I:%M %p").lstrip("0")
            self._time_surf = self.clock_font.render(self.time_text, True, self.text_color)
            self._last_minute = minute_key

        if day_key != self._last_day:
            self.date_text = now.strftime("%A, %b %d")
            self._date_surf = self.date_font.render(self.date_text, True, self.text_color)
            self._last_day = day_key

    def draw(self, screen, rect):
        if self._date_surf:
            drect = self._date_surf.get_rect(center=(rect.centerx, rect.centery - 50))
            screen.blit(self._date_surf, drect)

        if self._time_surf:
            trect = self._time_surf.get_rect(center=rect.center)
            screen.blit(self._time_surf, trect)

    def ticker_text(self):
        now = datetime.now()
        return now.strftime("Time • %I:%M %p  •  %A, %b %d").replace(" 0", " ")


class WeatherPage:
    def __init__(self, config):
        self.config = config
        self.weather = WeatherWidget(config)

        colors = config.get("colors", {})
        self.text_color = tuple(colors.get("text", [192, 192, 192]))
        self.big_font = pygame.font.SysFont(None, 64)

    def update(self, dt):
        self.weather.update()

    def draw(self, screen, rect):
        # Draw animated icon + small text via widget (top-left)
        self.weather.draw(screen)

        # Big center summary (temp)
        temp = getattr(self.weather, "temperature", "--")
        desc = getattr(self.weather, "description", "")
        big = self.big_font.render(temp, True, self.text_color)
        brect = big.get_rect(center=rect.center)
        screen.blit(big, brect)

        if desc:
            small = pygame.font.SysFont(None, 28).render(desc, True, self.text_color)
            srect = small.get_rect(center=(rect.centerx, brect.bottom + 20))
            screen.blit(small, srect)

    def ticker_text(self):
        temp = getattr(self.weather, "temperature", "--")
        desc = getattr(self.weather, "description", "")
        return f"Weather • {temp} • {desc}".strip()


class NewsPage:
    def __init__(self, config):
        self.config = config
        self.news = RssNewsProvider(config)

        colors = config.get("colors", {})
        self.text_color = tuple(colors.get("text", [192, 192, 192]))
        self.title_font = pygame.font.SysFont(None, 40)
        self.item_font = pygame.font.SysFont(None, 26)

    def update(self, dt):
        self.news.update()

    def draw(self, screen, rect):
        title = self.title_font.render("News", True, self.text_color)
        screen.blit(title, (rect.left + 16, rect.top + 12))

        headlines = self.news.headlines[:5] if self.news.headlines else ["News unavailable"]
        y = rect.top + 58
        for h in headlines:
            surf = self.item_font.render("• " + h, True, self.text_color)
            screen.blit(surf, (rect.left + 16, y))
            y += surf.get_height() + 6
            if y > rect.bottom - 20:
                break

    def ticker_text(self):
        return self.news.get_ticker_text(prefix="News • ")


class QuotesPage:
    def __init__(self, config):
        self.config = config
        self.quotes = QuotesProvider(config)

        colors = config.get("colors", {})
        self.text_color = tuple(colors.get("text", [192, 192, 192]))
        self.font = pygame.font.SysFont(None, 34)

    def update(self, dt):
        self.quotes.update()

    def draw(self, screen, rect):
        q = self.quotes.current_quote() or "No quotes loaded"
        # Simple wrap (manual)
        lines = wrap_text(q, self.font, rect.width - 40)
        y = rect.centery - (len(lines) * 18)
        for line in lines:
            surf = self.font.render(line, True, self.text_color)
            srect = surf.get_rect(center=(rect.centerx, y))
            screen.blit(surf, srect)
            y += 36

    def ticker_text(self):
        q = self.quotes.current_quote() or "No quotes loaded"
        return f"Quote • {q}"


def wrap_text(text, font, max_width):
    words = text.split()
    lines = []
    cur = ""
    for w in words:
        test = (cur + " " + w).strip()
        if font.size(test)[0] <= max_width:
            cur = test
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines
