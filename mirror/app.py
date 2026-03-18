import pygame
import sys
import json

from state import MirrorState

WIDTH, HEIGHT = 480, 320
FPS = 30


def load_config(path="config.json"):
    with open(path, "r") as f:
        return json.load(f)


class MirrorApp:
    def __init__(self):
        pygame.init()
        pygame.font.init()

        self.screen = pygame.display.set_mode(
            (WIDTH, HEIGHT),
            pygame.FULLSCREEN | pygame.NOFRAME
        )
        pygame.display.set_caption("Smart Mirror")

        self.clock = pygame.time.Clock()

        # ✅ Load JSON config
        config = load_config()
        self.state = MirrorState(config)

        self.running = True
        pygame.mouse.set_visible(False)

    def run(self):
        print("✅ Mirror app started")
        try:
            while self.running:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.running = False
                    elif event.type == pygame.KEYDOWN:
                        if event.key in (pygame.K_ESCAPE, pygame.K_q):
                            self.running = False
                    else:
                        if hasattr(self.state, "handle_event"):
                            self.state.handle_event(event)

                self.state.update()
                self.state.draw(self.screen)

                pygame.display.flip()
                self.clock.tick(FPS)
        finally:
            self.shutdown()

    def shutdown(self):
        print("🛑 Mirror app stopped")
        pygame.quit()
        sys.exit(0)


if __name__ == "__main__":
    app = MirrorApp()
    app.run()
