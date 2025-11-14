from typing import Optional

from fakemidi.fakemidi import FakeMidi


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
            GlobalCtx._initialized = True

