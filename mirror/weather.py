import pygame
import time
import math
import requests


class WeatherWidget:
    def __init__(self, config):
        wcfg = config.get("weather", {})
        ccfg = config.get("colors", {})

        self.enabled = bool(wcfg.get("enabled", False))
        self.latitude = wcfg.get("latitude")
        self.longitude = wcfg.get("longitude")
        self.units = wcfg.get("units", "fahrenheit")
        self.update_interval = int(wcfg.get("update_interval", 900))

        self.text_color = tuple(ccfg.get("text", [192, 192, 192]))
        self.font = pygame.font.SysFont(None, int(wcfg.get("font_size", 28)))

        self.last_update = 0
        self.temperature = "--"
        self.description = ""
        self.weather_code = 3

        self.temp_surf = None
        self.desc_surf = None

        if self.enabled:
            self.fetch_weather()

    def fetch_weather(self):
        if self.latitude is None or self.longitude is None:
            return
        try:
            url = (
                "https://api.open-meteo.com/v1/forecast"
                f"?latitude={self.latitude}"
                f"&longitude={self.longitude}"
                "&current_weather=true"
                f"&temperature_unit={self.units}"
                "&windspeed_unit=mph"
            )
            r = requests.get(url, timeout=6)
            r.raise_for_status()
            cw = r.json().get("current_weather", {})

            temp = cw.get("temperature")
            self.weather_code = int(cw.get("weathercode", 3))

            unit = "F" if self.units == "fahrenheit" else "C"
            if temp is not None:
                self.temperature = f"{int(round(temp))}°{unit}"
            else:
                self.temperature = "--"

            self.description = self._code_to_text(self.weather_code)

            self.temp_surf = self.font.render(self.temperature, True, self.text_color)
            self.desc_surf = self.font.render(self.description, True, self.text_color)

            self.last_update = time.time()

        except Exception as e:
            print("🌦 Weather fetch failed:", e)

    def update(self):
        if not self.enabled:
            return
        if time.time() - self.last_update > self.update_interval:
            self.fetch_weather()

    def draw(self, screen):
        if not self.enabled:
            return

        margin = 12
        icon_x = margin + 16
        icon_y = margin + 16

        self._draw_animated_icon(screen, icon_x, icon_y)

        text_x = margin + 44
        if self.temp_surf:
            screen.blit(self.temp_surf, (text_x, margin))
        if self.desc_surf and self.temp_surf:
            screen.blit(self.desc_surf, (text_x, margin + self.temp_surf.get_height() + 4))

    def _code_to_text(self, code):
        if code == 0:
            return "Clear"
        if code in (1, 2):
            return "Partly Cloudy"
        if code == 3:
            return "Overcast"
        if code in (45, 48):
            return "Fog"
        if code in (51, 53, 55):
            return "Drizzle"
        if code in (61, 63, 65, 80, 81, 82):
            return "Rain"
        if code in (71, 73, 75):
            return "Snow"
        if code in (95, 96, 99):
            return "Storm"
        return "Weather"

    def _icon_type(self, code):
        if code == 0:
            return "sun"
        if code in (1, 2):
            return "partly"
        if code == 3:
            return "cloud"
        if code in (45, 48):
            return "fog"
        if code in (51, 53, 55):
            return "drizzle"
        if code in (61, 63, 65, 80, 81, 82):
            return "rain"
        if code in (71, 73, 75):
            return "snow"
        if code in (95, 96, 99):
            return "storm"
        return "cloud"

    def _draw_animated_icon(self, screen, x, y):
        t = pygame.time.get_ticks() / 1000.0
        kind = self._icon_type(self.weather_code)

        if kind == "sun":
            self._draw_sun(screen, x, y, t)
        elif kind == "partly":
            self._draw_partly(screen, x, y, t)
        elif kind == "cloud":
            self._draw_cloud(screen, x, y, t)
        elif kind == "fog":
            self._draw_fog(screen, x, y, t)
        elif kind == "drizzle":
            self._draw_drizzle(screen, x, y, t)
        elif kind == "rain":
            self._draw_rain(screen, x, y, t)
        elif kind == "snow":
            self._draw_snow(screen, x, y, t)
        elif kind == "storm":
            self._draw_storm(screen, x, y, t)

    def _draw_sun(self, screen, x, y, t):
        c = self.text_color
        r = 12
        pulse = 1.0 + 0.05 * math.sin(t * 2.0)
        rr = int(r * pulse)
        pygame.draw.circle(screen, c, (x, y), rr, 2)

        for i in range(8):
            ang = i * (math.pi / 4) + t * 0.4
            inner = rr + 3
            outer = rr + 8 + 1.5 * math.sin(t * 2.0)
            x1 = x + math.cos(ang) * inner
            y1 = y + math.sin(ang) * inner
            x2 = x + math.cos(ang) * outer
            y2 = y + math.sin(ang) * outer
            pygame.draw.line(screen, c, (x1, y1), (x2, y2), 1)

    def _draw_cloud(self, screen, x, y, t):
        c = self.text_color
        drift = int(math.sin(t * 0.6) * 2)
        pygame.draw.circle(screen, c, (x - 10 + drift, y), 8, 2)
        pygame.draw.circle(screen, c, (x + drift, y - 4), 10, 2)
        pygame.draw.circle(screen, c, (x + 12 + drift, y), 8, 2)
        pygame.draw.rect(screen, c, (x - 18 + drift, y, 36, 12), 2)

    def _draw_partly(self, screen, x, y, t):
        self._draw_sun(screen, x - 10, y - 8, t)
        self._draw_cloud(screen, x + 6, y + 2, t)

    def _draw_fog(self, screen, x, y, t):
        c = self.text_color
        self._draw_cloud(screen, x, y - 6, t)
        wobble = int(math.sin(t * 0.8) * 3)
        for yy in (y + 8, y + 14, y + 20):
            pygame.draw.line(screen, c, (x - 18 + wobble, yy), (x + 18 + wobble, yy), 2)

    def _draw_drizzle(self, screen, x, y, t):
        c = self.text_color
        self._draw_cloud(screen, x, y - 6, t)
        for i in range(3):
            dx = -10 + i * 10
            phase = (t * 18 + i * 6) % 18
            yy = y + int(phase)
            pygame.draw.line(screen, c, (x + dx, yy), (x + dx, yy + 4), 1)

    def _draw_rain(self, screen, x, y, t):
        c = self.text_color
        self._draw_cloud(screen, x, y - 6, t)
        for i in range(4):
            dx = -14 + i * 9
            phase = (t * 22 + i * 7) % 22
            yy = y + int(phase)
            pygame.draw.line(screen, c, (x + dx, yy), (x + dx - 2, yy + 7), 1)

    def _draw_snow(self, screen, x, y, t):
        c = self.text_color
        self._draw_cloud(screen, x, y - 6, t)
        for i in range(5):
            dx = -16 + i * 8
            phase = (t * 10 + i * 4) % 18
            yy = y + int(phase)
            wobble = int(math.sin(t * 1.2 + i) * 1.5)
            pygame.draw.circle(screen, c, (x + dx + wobble, yy), 1)

    def _draw_storm(self, screen, x, y, t):
        self._draw_cloud(screen, x, y - 6, t)
        self._draw_rain(screen, x, y, t)
        c = self.text_color
        flash = (math.sin(t * 3.0) > 0.95)
        if flash:
            points = [(x + 4, y + 2), (x - 2, y + 14), (x + 6, y + 14), (x + 0, y + 26)]
            pygame.draw.lines(screen, c, False, points, 2)
