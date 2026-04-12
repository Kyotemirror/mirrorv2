import time
import requests
import xml.etree.ElementTree as ET


class RssNewsProvider:
    def __init__(self, config):
        ncfg = config.get("news", {})
        self.enabled = bool(ncfg.get("enabled", False))
        self.rss_url = ncfg.get("rss_url")
        self.update_interval = int(ncfg.get("update_interval", 900))
        self.max_items = int(ncfg.get("max_items", 10))

        self.last_update = 0
        self.headlines = []

        if self.enabled:
            self.fetch()

    def fetch(self):
        if not self.rss_url:
            return
        try:
            r = requests.get(self.rss_url, timeout=6)
            r.raise_for_status()
            root = ET.fromstring(r.text)
            items = root.findall(".//item")[: self.max_items]

            headlines = []
            for it in items:
                title = it.findtext("title")
                if title:
                    headlines.append(title.strip())

            if headlines:
                self.headlines = headlines
                self.last_update = time.time()
        except Exception as e:
            print("📰 RSS fetch failed:", e)

    def update(self):
        if not self.enabled:
            return
        if time.time() - self.last_update > self.update_interval:
            self.fetch()

    def get_ticker_text(self, prefix=""):
        if not self.enabled or not self.headlines:
            return (prefix + "News unavailable").strip()
        return prefix + "  •  ".join(self.headlines)
