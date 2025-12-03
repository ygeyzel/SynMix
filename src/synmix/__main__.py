"""
SynMix entry point - allows running as 'python -m synmix' or 'uv run synmix'
"""
import argparse
import sys

import moderngl_window as mglw

mglw.settings.WINDOW["class"] = "moderngl_window.context.glfw.Window"

from synmix.inputs.input_manager import MidiInputManager
from synmix.top_level.global_context import GlobalCtx
from synmix.top_level.screen import Screen
from synmix.fakemidi.fakemidi import FakeMidi


MIDI_INPUT_SUBNAME = "Mixage"


def main():
    """Main entry point for SynMix application"""
    # Parse command line arguments (use parse_known_args to allow moderngl_window's args to pass through)
    parser = argparse.ArgumentParser(
        description="SynMix - Audio visualizer with MIDI control", add_help=False
    )
    parser.add_argument(
        "--fakemidi",
        action="store_true",
        help="Use fake MIDI controller with keyboard input instead of real MIDI device",
    )
    parser.add_argument(
        "--start-scene", type=str, default=None, help="Name of the starting scene"
    )
    args, remaining = parser.parse_known_args()

    # Initialize global context
    global_ctx = GlobalCtx()
    if args.fakemidi:
        global_ctx.fake_midi = FakeMidi()
    if args.start_scene:
        global_ctx.starting_scene_name = args.start_scene

    # Setup input manager
    fake_midi = global_ctx.fake_midi
    input_subname = fake_midi.output_name if fake_midi else MIDI_INPUT_SUBNAME
    input_manager = MidiInputManager(input_subname)

    # Update sys.argv to remove our custom arguments so moderngl_window can parse its own
    sys.argv = [sys.argv[0]] + remaining

    # Entry point: Create window and start the main rendering loop
    mglw.run_window_config(Screen)


if __name__ == "__main__":
    main()
