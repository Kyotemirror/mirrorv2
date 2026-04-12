import pygame
import time
import math
import requests


class WeatherWidget:
    """
    Weather widget using Open-Meteo (no API key) + animated vector icons (no images).
    - Supports config with latitude/longitude OR city name (uses Open-Meteo geocoding, no key).
    - Draws subtle animated icons suitable for a smart mirror.
    """

    def __init__(self, config):
        weather_cfg = config.get("weather", {})
        color_cfg = config.get("colors", {})

        self.enabled = weather_cfg.get("enabled", False)

        # Location options (no OpenWeather required)
        self.city = weather_cfg.get("city")  # optional: "Meridian"
        self.country = weather_cfg.get("country")  # optional: "US"
        self.latitude = weather_cfg.get("latitude")
        self.longitude = weather_cfg.get("longitude")

        # Units: "fahrenheit" or "celsius"
        self.units = weather_cfg.get("units", "fahrenheit")
        self.update_interval = int(weather_cfg.get("update_interval", 900))
        self.font = pygame.font.SysFont(None, int(weather_cfg.get("font_size", 28)))

        self.text_color = tuple(color_cfg.get("text", [255, 255, 255]))

        self.last_update = 0
        self.temperature = "--"
        self.description = ""
        self.weather_code = 3  # default to cloudy-ish

        # Cache rendered text surfaces (avoid rerender each frame)
        self.temp_surf = None
        self.desc_surf = None

        # If city provided and coords missing, resolve once (no key)
        if self.enabled:
            if (self.latitude is None or self.longitude is None) and self.city:
                self._resolve_city_to_coords()
            self.fetch_weather()

    # --------------------------
    # Data fetch (Open-Meteo)
    # --------------------------
    def _resolve_city_to_coords(self):
        """Resolve 'city' to lat/lon using Open-Meteo geocoding (no key)."""
        try:
            name = self.city
            if self.country:
                name = f"{self.city},{self.country}"

            url = (
                "https://geocoding-api.open-meteo.com/v1/search"
                f"?name={name}&count=1&language=en&format=json"
            )
            r = requests.get(url, timeout=6)
            r.raise_for_status()
            data = r.json()

            results = data.get("results") or []
            if results:
                self.latitude = results[0].get("latitude")
                self.longitude = results[0].get("longitude")

        except Exception as e:
            print("📍 Geocoding failed:", e)

    def fetch_weather(self):
        if not self.enabled:
            return
        if self.latitude is None or self.longitude is None:
            # Keep last known display
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
            code = cw.get("weathercode", 3)

            if temp is not None:
                unit_suffix = "F" if self.units == "fahrenheit" else "C"
                self.temperature = f"{int(round(temp))}°{unit_suffix}"
            else:
                self.temperature = "--"

            self.weather_code = int(code)
            self.description = self._code_to_text(self.weather_code)

            # Cache text surfaces
            self.temp_surf = self.font.render(self.temperature, True, self.text_color)
            self.desc_surf = self.font.render(self.description, True, self.text_color)

            self.last_update = time.time()

        except Exception as e:
            print("🌦 Weather fetch failed:", e)

    def update(self):
        if not self.enabled:
            return

        # Refresh data on interval
        if time.time() - self.last_update > self.update_interval:
            # If we still don't have coords but do have a city, try again occasionally
            if (self.latitude is None or self.longitude is None) and self.city:
                self._resolve_city_to_coords()
            self.fetch_weather()

    # --------------------------
    # Drawing
    # --------------------------
    def draw(self, screen):
        if not self.enabled:
            return

        margin = 12

        # Icon anchor (top-left)
        icon_x = margin + 16
        icon_y = margin + 16
        self._draw_animated_icon(screen, icon_x, icon_y)

        # Text
        text_x = margin + 44
        if self.temp_surf:
            screen.blit(self.temp_surf, (text_x, margin))
            if self.desc_surf:
                screen.blit(self.desc_surf, (text_x, margin + self.temp_surf.get_height() + 4))

    # --------------------------
    # Weather code mapping
    # --------------------------
    def _code_to_text(self, code: int) -> str:
        # Open-Meteo weather codes (simplified)
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
        if code in (61, 63, 65):
            return "Rain"
        if code in (80, 81, 82):
            return "Showers"
        if code in (71, 73, 75):
            return "Snow"
        if code in (95, 96, 99):
            return "Storm"
        return "Weather"

    def _icon_type(self, code: int) -> str:
        # Decide which icon family to draw
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

    # --------------------------
    # Animated vector icons (no images)
    # --------------------------
    def _draw_animated_icon(self, screen, x, y):
        t = pygame.time.get_ticks() / 1000.0  # seconds
        kind = self._icon_type(self.weather_code)

        # Subtle motion amplitude (mirror-friendly)
        if kind == "sun":
            self._draw_sun(screen, x, y, t)
        elif kind == "partly":
            self._draw_partly_cloudy(screen, x, y, t)
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
        else:
            self._draw_cloud(screen, x, y, t)

    def _draw_sun(self, screen, x, y, t):
        c = self.text_color
        r = 12
        pulse = 1.0 + 0.05 * math.sin(t * 2.0)
        rr = int(r * pulse)

        pygame.draw.circle(screen, c, (x, y), rr, 2)

        # Rays: slow rotation, minimal flicker
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
        drift = int(math.sin(t * 0.6) * 2)  # subtle drift

        # cloud composed of circles + base
        pygame.draw.circle(screen, c, (x - 10 + drift, y), 8, 2)
        pygame.draw.circle(screen, c, (x + drift, y - 4), 10, 2)
        pygame.draw.circle(screen, c, (x + 12 + drift, y), 8, 2)
        pygame.draw.rect(screen, c, (x - 18 + drift, y, 36, 12), 2)

    def _draw_partly_cloudy(self, screen, x, y, t):
        # sun behind cloud
        self._draw_sun(screen, x - 10, y - 8, t)
        self._draw_cloud(screen, x + 6, y + 2, t)

    def _draw_fog(self, screen, x, y, t):
        c = self.text_color
        self._draw_cloud(screen, x, y - 6, t)

        wobble = int(math.sin(t * 0.8) * 3)
        for i, yy in enumerate((y + 8, y + 14, y + 20)):
            pygame.draw.line(screen, c, (x - 18 + wobble, yy), (x + 18 + wobble, yy), 2)

    def _draw_drizzle(self, screen, x, y, t):
        self._draw_cloud(screen, x, y - 6, t)
        c = self.text_color

        # light drops (small)
        for i in range(3):
            dx = -10 + i * 10
            phase = (t * 18 + i * 6) % 18
            yy = y + int(phase)
            pygame.draw.line(screen, c, (x + dx, yy), (x + dx, yy + 4), 1)

    def _draw_rain(self, screen, x, y, t):
        self._draw_cloud(screen, x, y - 6, t)
        c = self.text_color

        for i in range(4):
            dx = -14 + i * 9
            phase = (t * 22 + i * 7) % 22
            yy = y + int(phase)
            pygame.draw.line(screen, c, (x + dx, yy), (x + dx - 2, yy + 7), 1)

    def _draw_snow(self, screen, x, y, t):
        self._draw_cloud(screen, x, y - 6, t)
        c = self.text_color

        for i in range(5):
            dx = -16 + i * 8
            phase = (t * 10 + i * 4) % 18
            yy = y + int(phase)
            wobble = int(math.sin(t * 1.2 + i) * 1.5)
            pygame.draw.circle(screen, c, (x + dx + wobble, yy), 1)

    def _draw_storm(self, screen, x, y, t):
        # cloud + rain + occasional lightning flash
        self._draw_cloud(screen, x, y - 6, t)
        self._draw_rain(screen, x, y, t)

        c = self.text_color
        # Flash roughly every few seconds (brief)
        flash = (math.sin(t * 3.0) > 0.95)

        if flash:
            points = [
                (x + 4, y + 2),
                (x - 2, y + 14),
                (x + 6, y + 14),
                (x + 0, y + 26),
            ]
            pygame.draw.lines(screen, c, False, points, 2)
