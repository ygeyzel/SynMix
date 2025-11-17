from typing import NamedTuple, Optional

from fakemidi.fakemidi import FakeMidi


class TimeParams(NamedTuple):
    offset: float
    speed: float


DEFAULT_TIME_PARAMS = TimeParams(0.0, 1.0)


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
            GlobalCtx._initialized = True

    def reset_time_params(self):
        self.time_params = DEFAULT_TIME_PARAMS

