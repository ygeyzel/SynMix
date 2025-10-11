import argparse
import sys

import moderngl_window as mglw

from inputs.input_manager import MidiInputManager
from screen import Screen
from utils.fakemidi import FakeMidi 


MIDI_INPUT_SUBNAME = "Mixage"


if __name__ == "__main__":
    # Parse command line arguments (use parse_known_args to allow moderngl_window's args to pass through)
    parser = argparse.ArgumentParser(description='SynMix - Audio visualizer with MIDI control', add_help=False)
    parser.add_argument('--fakemidi', action='store_true', 
                        help='Use fake MIDI controller with keyboard input instead of real MIDI device')
    args, remaining = parser.parse_known_args()
    # Set class attribute based on argument
    fake_midi = FakeMidi() if args.fakemidi else None
    input_subname = fake_midi.output_name if fake_midi else MIDI_INPUT_SUBNAME
    input_manager = MidiInputManager(input_subname)

    # Update sys.argv to remove our custom arguments so moderngl_window can parse its own
    sys.argv = [sys.argv[0]] + remaining
    

    # Entry point: Create window and start the main rendering loop
    mglw.run_window_config(Screen)
