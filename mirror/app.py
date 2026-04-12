import os
import sys
import json
import pygame

from state import MirrorState


def load_config():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(os.path.dirname(base_dir), "config.json")
    with open(config_path, "r") as f:
        return json.load(f)


class MirrorApp:
    def __init__(self):
        pygame.init()
        pygame.font.init()

        self.config = load_config()
        dcfg = self.config.get("display", {})

        width = int(dcfg.get("width", 480))
        height = int(dcfg.get("height", 320))
        fullscreen = bool(dcfg.get("fullscreen", True))

        flags = pygame.FULLSCREEN if fullscreen else 0
        self.screen = pygame.display.set_mode((width, height), flags)
        pygame.display.set_caption("Smart Mirror")
        pygame.mouse.set_visible(False)

        self.clock = pygame.time.Clock()
        self.fps = int(dcfg.get("fps", 25))

        self.state = MirrorState(self.config)
        self.running = True

    def run(self):
        print("✅ Mirror app started")
        try:
            while self.running:
                dt = self.clock.tick(self.fps) / 1000.0  # seconds

                pygame.event.pump()
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.running = False
                    elif event.type == pygame.KEYDOWN:
                        if event.key in (pygame.K_ESCAPE, pygame.K_q):
                            self.running = False

                self.state.update(dt)
                self.state.draw(self.screen)

                pygame.display.flip()

        except KeyboardInterrupt:
            pass
        finally:
            self.shutdown()

    def shutdown(self):
        print("🛑 Mirror app stopped")
        pygame.quit()
        sys.exit(0)


if __name__ == "__main__":
    MirrorApp().run()
