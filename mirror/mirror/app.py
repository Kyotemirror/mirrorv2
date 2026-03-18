import time
from .state import MirrorState
from .config import Config

class MirrorApp:
    def __init__(self):
        self.config = Config()
        self.state = MirrorState(self.config)
        self.running = True

    def run(self):
        print("✅ Mirror service started")
        try:
            while self.running:
                self.state.update()
                time.sleep(1)
        except KeyboardInterrupt:
            self.shutdown()

    def shutdown(self):
        print("🛑 Mirror service stopped")
        self.running = False
