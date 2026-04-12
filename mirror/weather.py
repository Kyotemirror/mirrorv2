import pygame
import time
import requests


class WeatherWidget:
    def __init__(self, config):
        weather_cfg = config.get("weather", {})
        color_cfg = config.get("colors", {})

        self.enabled = weather_cfg.get("enabled", False)
        self.latitude = weather_cfg.get("latitude")
        self.longitude = weather_cfg.get("longitude")
        self.units = weather_cfg.get("units", "fahrenheit")
        self.update_interval = weather_cfg.get("update_interval", 900)

        self.text_color = tuple(color_cfg.get("text", [255, 255, 255]))
        self.font = pygame.font.SysFont(None, weather_cfg.get("font_size", 28))

        self.last_update = 0
        self.temperature = "--"
        self.description = ""

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

            r = requests.get(url, timeout=5)
            r.raise_for_status()
            data = r.json()["current_weather"]

            self.temperature = f"{int(data['temperature'])}°"
            self.description = self._weather_code_to_text(data["weathercode"])

            self.temp_surf = self.font.render(
                self.temperature, True, self.text_color
            )
            self.desc_surf = self.font.render(
                self.description, True, self.text_color
            )

            self.last_update = time.time()

        except Exception as e:
            print("🌦 Weather fetch failed:", e)

    def update(self):
        if not self.enabled:
            return

        if time.time() - self.last_update > self.update_interval:
            self.fetch_weather()

    def draw(self, screen):
        if not self.enabled or not self.temp_surf:
            return

        margin = 12

        screen.blit(self.temp_surf, (margin, margin))
        screen.blit(
            self.desc_surf,
            (margin, margin + self.temp_surf.get_height() + 4)
        )

    def _weather_code_to_text(self, code):
        # Open‑Meteo weather codes
        mapping = {
            0: "Clear",
            1: "Mostly Clear",
            2: "Partly Cloudy",
            3: "Overcast",
            45: "Fog",
            48: "Fog",
            51: "Light Drizzle",
            53: "Drizzle",
            55: "Heavy Drizzle",
            61: "Light Rain",
            63: "Rain",
            65: "Heavy Rain",
            71: "Light Snow",
            73: "Snow",
            75: "Heavy Snow",
            80: "Showers",
            81: "Rain Showers",
            82: "Heavy Showers",
            95: "Thunderstorm"
        }
        return mapping.get(code, "Weather")
