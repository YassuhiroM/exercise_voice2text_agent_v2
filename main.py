"""Entry point: global push-to-talk (Ctrl+Alt+Space) + ESC to exit (Windows)."""

import threading

import keyboard
from dotenv import load_dotenv

load_dotenv()

from core.orchestrator import VoiceFlowOrchestrator

SHOW_STARTUP_HELP = False
HOTKEY_COMBO = "ctrl+alt+space"
HOTKEY_LABEL = "CTRL + ALT + SPACE"

# Keys whose release signals the end of a push-to-talk session
_COMBO_RELEASE_KEYS = frozenset([
    "ctrl", "left ctrl", "right ctrl",
    "alt", "left alt", "right alt",
    "space",
])

STARTUP_HELP = f"""\
Voice2Text Agent
Converts your voice into friendly, polished text and pastes it automatically.

Quick use:
1) Hold {HOTKEY_LABEL} to record (push-to-talk)
2) Release to stop and process
3) Paste happens automatically (Ctrl+V is sent for you)

Exit:
- Press ESC to quit
"""


class GlobalHotkeyController:
    """
    Push-to-talk semantics using the 'keyboard' package with hotkey suppression.

    The Ctrl+Alt+Space combo is registered with suppress=True so it is consumed
    by this app and never forwarded to Windows or other applications (which was
    the root cause of the Explorer 'no app associated' dialog).

      - All three keys held  → start recording (toggle)
      - Any combo key released → stop / process (toggle)
    """

    def __init__(self, orchestrator: VoiceFlowOrchestrator) -> None:
        self.orchestrator = orchestrator
        self._combo_down = False
        self._lock = threading.Lock()

    def _start_async_toggle(self) -> None:
        threading.Thread(target=self.orchestrator.toggle, daemon=True).start()

    def on_hotkey_press(self) -> None:
        """Called by keyboard.add_hotkey when Ctrl+Alt+Space is fully pressed."""
        with self._lock:
            if not self._combo_down:
                self._combo_down = True
                self._start_async_toggle()

    def on_any_release(self, event: keyboard.KeyboardEvent) -> None:
        """Called on every key release; only acts when a combo key is released."""
        with self._lock:
            if self._combo_down and event.name.lower() in _COMBO_RELEASE_KEYS:
                self._combo_down = False
                self._start_async_toggle()


def main() -> None:
    if SHOW_STARTUP_HELP:
        print(STARTUP_HELP)

    orchestrator = VoiceFlowOrchestrator()
    controller = GlobalHotkeyController(orchestrator)

    print("Voice2Text Agent running (ESC to exit).")

    # suppress=True prevents Ctrl+Alt+Space from reaching Windows / Explorer,
    # eliminating the 'no app associated' Explorer.EXE error dialogs.
    keyboard.add_hotkey(HOTKEY_COMBO, controller.on_hotkey_press, suppress=True)
    keyboard.on_release(controller.on_any_release)

    keyboard.wait("esc")

    if orchestrator.recorder.is_recording:
        orchestrator.recorder.stop()

    print("\n[EXIT] Closing Voice2Text Agent...")


if __name__ == "__main__":
    main()
