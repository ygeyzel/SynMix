import threading
import time

import mido
import moderngl_window as mglw
from pyglet.window import key as pyglet_key

from synmix.fakemidi.fakemidi import FakeMidi


class MidiMonitor(threading.Thread):
    """Monitors MIDI output from the virtual controller and prints messages"""

    def __init__(self, port_name: str) -> None:
        super().__init__(daemon=True)
        self.port_name = port_name
        self.running = False
        self.input_port = None

    def run(self) -> None:
        """Main thread loop - listens for and prints MIDI messages"""
        # Wait a moment for the virtual output port to be created
        time.sleep(0.5)

        try:
            # Open virtual input to receive messages from the fake controller's output
            self.input_port = mido.open_input(self.port_name)
            self.running = True
            print(f"MIDI Monitor connected to '{self.port_name}'")
            print("=" * 60)
            print("Listening for MIDI messages... (Press keys to generate MIDI)")
            print("=" * 60)

            while self.running:
                for msg in self.input_port.iter_pending():
                    print(msg)
                time.sleep(0.01)  # Small delay to prevent busy-waiting

        except Exception as e:
            print(f"✗ Error in MIDI monitor: {e}")
        finally:
            if self.input_port:
                self.input_port.close()

    def stop(self) -> None:
        """Stop the monitoring thread"""
        self.running = False


class TestWindow(mglw.WindowConfig):
    """Simple moderngl window for testing the fake controller"""

    gl_version = (3, 3)
    title = "Fake MIDI Controller Test"
    window_size = (800, 600)
    resizable = True

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

        # Create fake controller
        print("Initializing Fake MIDI Controller...")
        self.fake_controller = FakeMidi()
        print(f"Created virtual MIDI output: '{self.fake_controller.output_name}'")

        # Start MIDI monitor in background thread
        self.midi_monitor = MidiMonitor(self.fake_controller.output_name)
        self.midi_monitor.start()

        # Setup frame counter for periodic updates
        self.frame_count = 0

    def on_render(self, time: float, frame_time: float) -> None:
        """Render loop - just clear to a dark background"""
        self.ctx.clear(0.1, 0.1, 0.15)

        # Process any pending key inputs periodically
        self.frame_count += 1
        if self.frame_count % 2 == 0:  # Process every other frame (~30Hz)
            self.fake_controller.handle_keys_input()

    def on_key_event(self, key, action, modifiers) -> None:
        """Handle keyboard events and forward to fake controller"""
        if key == pyglet_key.ESCAPE and action == self.wnd.keys.ACTION_PRESS:
            self.wnd.close()
            return

        if action == self.wnd.keys.ACTION_PRESS:
            self.fake_controller.on_key_press(key, modifiers)
        elif action == self.wnd.keys.ACTION_RELEASE:
            self.fake_controller.on_key_release(key)

    def on_close(self) -> None:
        """Cleanup when window closes"""
        print("\nShutting down...")
        self.midi_monitor.stop()
        if self.fake_controller.output:
            self.fake_controller.output.close()
        print("Cleanup complete")


if __name__ == "__main__":
    print("=" * 60)
    print("Fake MIDI Controller Test Script")
    print("=" * 60)

    # Run the test window
    mglw.run_window_config(TestWindow)
