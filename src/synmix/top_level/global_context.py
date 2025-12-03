from typing import NamedTuple, Optional

from synmix.fakemidi.fakemidi import FakeMidi
from synmix.inputs.midi import MIDI_BUTTEN_CLICK, MIDI_DEC_VALUE, MIDI_INC_VALUE


class TimeParams(NamedTuple):
    offset: float
    speed: float


DEFAULT_TIME_PARAMS = TimeParams(0.0, 1.0)

# Time adjustment constants
TIME_OFFSET_STEP = 0.3
TIME_SPEED_STEP = 0.5
TIME_SPEED_HOLD_INTERVAL = 0.15


class GlobalCtx:
    """
    Singleton object that holds global context shared across the application
    """

    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        # Only initialize if it's the first time
        if not GlobalCtx._initialized:
            self.fake_midi: Optional[FakeMidi] = None
            self.starting_scene_name: Optional[str] = None
            self.time_params: TimeParams = DEFAULT_TIME_PARAMS
            self.shared_values: dict = {}

            # Time adjustment state
            self.time_offset_step = TIME_OFFSET_STEP
            self.time_speed_step = TIME_SPEED_STEP
            self._last_time = 0.0
            self._increase_speed_active = False
            self._decrease_speed_active = False
            self._increase_hold_accumulator = 0.0
            self._decrease_hold_accumulator = 0.0

            GlobalCtx._initialized = True

    def reset_time_params(self):
        self.time_params = DEFAULT_TIME_PARAMS

    def update_last_time(self, time: float):
        """Update the last time value for time adjustments"""
        self._last_time = time

    def adjust_time_offset(self, value: int | None):
        """Adjust time offset based on MIDI input"""
        if value == MIDI_INC_VALUE:
            delta = self.time_offset_step
        elif value == MIDI_DEC_VALUE:
            delta = -self.time_offset_step
        else:
            return

        current = self.time_params or DEFAULT_TIME_PARAMS
        print(f"Update time offset to {current.offset + delta}")
        self._set_time_params(TimeParams(current.offset + delta, current.speed))

    def handle_increase_speed_button(self, value: int | None):
        """Handle increase speed button press/release"""
        is_pressed = value == MIDI_BUTTEN_CLICK
        self._increase_speed_active = is_pressed
        if not is_pressed:
            self._increase_hold_accumulator = 0.0
            return

        if is_pressed:
            self._update_time_speed(self.time_speed_step)

    def handle_decrease_speed_button(self, value: int | None):
        """Handle decrease speed button press/release"""
        is_pressed = value == MIDI_BUTTEN_CLICK
        self._decrease_speed_active = is_pressed
        if not is_pressed:
            self._decrease_hold_accumulator = 0.0
            return

        self._update_time_speed(-self.time_speed_step)

    def _update_time_speed(self, delta: float):
        """Update time speed with delta change"""
        if delta == 0:
            return

        current = self.time_params or DEFAULT_TIME_PARAMS
        new_speed = max(-10.0, min(10.0, current.speed + delta))

        if new_speed == current.speed:
            return

        current_time = self._last_time if self._last_time is not None else 0.0
        new_offset = current.offset + current_time * (current.speed - new_speed)
        print(f"Update time speed to {new_speed}")
        self._set_time_params(TimeParams(new_offset, new_speed))

    def _set_time_params(self, new_params: TimeParams):
        """Set new time parameters"""
        self.time_params = new_params

    def get_adjusted_time(self, base_time: float) -> float:
        """Get adjusted time based on current time parameters"""
        params = self.time_params or DEFAULT_TIME_PARAMS
        return params.offset + (base_time * params.speed)

    def apply_speed_hold(self, frame_time: float):
        """Apply speed hold logic for continuous speed adjustment"""
        if frame_time <= 0:
            return

        if self._increase_speed_active:
            self._increase_hold_accumulator += frame_time
            while self._increase_hold_accumulator >= TIME_SPEED_HOLD_INTERVAL:
                self._update_time_speed(self.time_speed_step)
                self._increase_hold_accumulator -= TIME_SPEED_HOLD_INTERVAL

        if self._decrease_speed_active:
            self._decrease_hold_accumulator += frame_time
            while self._decrease_hold_accumulator >= TIME_SPEED_HOLD_INTERVAL:
                self._update_time_speed(-self.time_speed_step)
                self._decrease_hold_accumulator -= TIME_SPEED_HOLD_INTERVAL
