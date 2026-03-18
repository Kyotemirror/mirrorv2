import pygame
import sys

from state import MirrorState
from config import CONFIG  # make sure this exists

# ============================================================
# Screen configuration for 3.5" GPIO LCD
# ============================================================
WIDTH, HEIGHT = 480, 320
FPS = 30


class MirrorApp:
    def __init__(self):
        # ----------------------------------------------------
        # Initialize pygame
        # ----------------------------------------------------
        pygame.init()
        pygame.font.init()

        # ----------------------------------------------------
        # Create display (fullscreen, no window frame)
        # Best practice for Raspberry Pi GPIO LCDs
        # ----------------------------------------------------
        self.screen = pygame.display.set_mode(
            (WIDTH, HEIGHT),
            pygame.FULLSCREEN | pygame.NOFRAME
        )

        pygame.display.set_caption("Smart Mirror")

        # ----------------------------------------------------
        # Timing
        # ----------------------------------------------------
        self.clock = pygame.time.Clock()

        # ----------------------------------------------------
        # App state
        # ----------------------------------------------------
        self.state = MirrorState(CONFIG)
        self.running = True

        # Optional: hide mouse cursor for mirror display
        pygame.mouse.set_visible(False)

    # ========================================================
    # Main loop
    # ========================================================
    def run(self):
        print("✅ Mirror app started")

        try:
            while self.running:
                self.handle_events()
                self.update()
                self.draw()

                pygame.display.flip()
                self.clock.tick(FPS)

        except KeyboardInterrupt:
            # Allow Ctrl+C exit when running via SSH
            print("⌨️  Keyboard interrupt received")

        finally:
            self.shutdown()

    # ========================================================
    # Event handling
    # ========================================================
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            # Optional hard exit keys (useful during development)
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_q):
                    self.running = False

            # Forward all other events to the active state
            if hasattr(self.state, "handle_event"):
                self.state.handle_event(event)

    # ========================================================
    # Update logic
    # ========================================================
    def update(self):
        self.state.update()

    # ========================================================
    # Rendering
    # ========================================================
    def draw(self):
        # Clear screen (black background)
        self.screen.fill((0, 0, 0))

        # Let the state render itself
        self.state.draw(self.screen)

    # ========================================================
    # Cleanup
    # ========================================================
    def shutdown(self):
        print("🛑 Mirror app stopped")
        pygame.quit()
        sys.exit(0)


# ============================================================
# Entry point
# ============================================================
if __name__ == "__main__":
    app = MirrorApp()
    app.run()
