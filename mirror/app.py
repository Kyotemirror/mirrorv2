import os, sys, json, pygame
from state import MirrorState

def load_config():
    root = os.path.dirname(os.path.dirname(__file__))
    with open(os.path.join(root, "config.json")) as f:
        return json.load(f)

class MirrorApp:
    def __init__(self):
        pygame.init()
        pygame.font.init()

        self.config = load_config()
        d = self.config["display"]

        flags = pygame.FULLSCREEN if d["fullscreen"] else 0
        self.screen = pygame.display.set_mode((d["width"], d["height"]), flags)
        pygame.mouse.set_visible(False)

        self.clock = pygame.time.Clock()
        self.fps = d["fps"]
        self.state = MirrorState(self.config)
        self.running = True

    def run(self):
        print("✅ Mirror app started")
        try:
            while self.running:
                dt = self.clock.tick(self.fps) / 1000.0
                for e in pygame.event.get():
                    if e.type == pygame.QUIT:
                        self.running = False
                    elif e.type == pygame.KEYDOWN and e.key in (pygame.K_ESCAPE, pygame.K_q):
                        self.running = False

                self.state.update(dt)
                self.state.draw(self.screen)
                pygame.display.flip()

        finally:
            pygame.quit()
            sys.exit(0)

if __name__ == "__main__":
    MirrorApp().run()
