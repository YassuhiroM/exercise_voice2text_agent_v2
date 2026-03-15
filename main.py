"""Entry point with ESC key exit support."""

import os
from pynput import keyboard
from core.orchestrator import VoiceFlowOrchestrator
import threading

class GlobalHotkeyController:
    def __init__(self, orchestrator: VoiceFlowOrchestrator) -> None:
        self.orchestrator = orchestrator
        self._pressed = set()
        self._combo_down = False

    def on_press(self, key):
        # ESC to Exit (clean stop)
        if key == keyboard.Key.esc:
            print("\n[EXIT] Closing application...")
            return False  # stops listener per pynput docs
    
        self._pressed.add(key)
    
        # CTRL+ALT+SPACE combo (left keys only; you can extend to right keys later)
        if all(k in self._pressed for k in [keyboard.Key.ctrl_l, keyboard.Key.alt_l, keyboard.Key.space]):
            if not self._combo_down:
                self._combo_down = True
                # IMPORTANT: don't do long work in the callback thread
                threading.Thread(target=self.orchestrator.toggle, daemon=True).start()

    def on_release(self, key):
        self._pressed.discard(key)
        self._combo_down = False

STARTUP_HELP = """\
Voice2Text Agent
Turns your voice into polished text and pastes it where your cursor is.

How to use:
1) Hold CTRL + ALT + SPACE to start recording
2) Release to stop
3) Wait for Transcribing / Styling
4) The result is pasted automatically (Ctrl+V)

Controls:
- CTRL + ALT + SPACE: Push-to-talk record
- ESC: Exit
"""

def main():
    print(STARTUP_HELP)
    orchestrator = VoiceFlowOrchestrator()
    controller = GlobalHotkeyController(orchestrator)
    #print("Agent Active. CTRL+ALT+SPACE to Record | ESC to Exit")

    with keyboard.Listener(on_press=controller.on_press, on_release=controller.on_release) as listener:
        listener.join()

if __name__ == "__main__":
    main()
