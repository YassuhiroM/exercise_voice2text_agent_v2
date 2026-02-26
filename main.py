"""Entry point with ESC key exit support."""

import os
from pynput import keyboard
from core.orchestrator import VoiceFlowOrchestrator

class GlobalHotkeyController:
    def __init__(self, orchestrator: VoiceFlowOrchestrator) -> None:
        self.orchestrator = orchestrator
        self._pressed = set()
        self._combo_down = False

    def on_press(self, key):
        # ESC to Exit
        if key == keyboard.Key.esc:
            print("\n🛑 Closing application...")
            os._exit(0)

        self._pressed.add(key)
        # Simple check for CTRL+ALT+SPACE
        if all(k in self._pressed for k in [keyboard.Key.ctrl_l, keyboard.Key.alt_l, keyboard.Key.space]):
            if not self._combo_down:
                self._combo_down = True
                self.orchestrator.toggle()

    def on_release(self, key):
        self._pressed.discard(key)
        self._combo_down = False

def main():
    orchestrator = VoiceFlowOrchestrator()
    controller = GlobalHotkeyController(orchestrator)
    print("Agent Active. CTRL+ALT+SPACE to Record | ESC to Exit")
    with keyboard.Listener(on_press=controller.on_press, on_release=controller.on_release) as listener:
        listener.join()

if __name__ == "__main__":
    main()
