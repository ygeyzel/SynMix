from abc import ABC, abstractmethod
from inputs.midi import MIDI_MAX_VALUE, MIDI_MIN_VALUE, MIDI_INC_VALUE, MIDI_DEC_VALUE 


controllers_registry = {}

def register_controller(name):
    def decorator(cls):
        controllers_registry[name] = cls
        return cls

    return decorator


@register_controller('ValueController')
class ValueController(ABC):
    def __init__(self, *args, **kwargs):
        super().__init__()
        self.value = kwargs.get('initial_value', 0.0)

    def __repr__(self):
        return f'{self.__class__.__name__}({self.__dict__})'

    def set_value(self, value: float):
        self.value = value

    @abstractmethod
    def control_value(self, in_value: int):
        pass


@register_controller('NormalizedController')
class NormalizedController(ValueController):
    def __init__(self, min_value, max_value, **kwargs):
        super().__init__(**kwargs)
        self.min_value = min_value
        self.max_value = max_value

    def control_value(self, in_value: int):
        normalized_value = self.min_value + (in_value - MIDI_MIN_VALUE) * (
            self.max_value - self.min_value) / (MIDI_MAX_VALUE - MIDI_MIN_VALUE)
        self.set_value(normalized_value)


@register_controller('IncDecController')
class IncDecController(ValueController):
    def __init__(self, min_value: float, max_value: float, step: float, inc_value: int = MIDI_INC_VALUE, dec_value: int = MIDI_DEC_VALUE, **kwargs):
        super().__init__(**kwargs)
        self.min_value = min_value
        self.max_value = max_value
        self.inc_value = inc_value
        self.dec_value = dec_value
        self.step = step

    @abstractmethod
    def increase(self):
        pass

    @abstractmethod
    def decrease(self):
        pass

    def control_value(self, in_value: int):
        if in_value == self.inc_value:
            self.increase()
        elif in_value == self.dec_value:
            self.decrease()


@register_controller('RangedController')
class RangedController(IncDecController):
    def increase(self):
        self.value = min(self.value + self.step, self.max_value)

    def decrease(self):
        self.value = max(self.value - self.step, self.min_value)


@register_controller('CyclicController')
class CyclicController(IncDecController):
    def increase(self):
        self.value += self.step
        if self.value > self.max_value:
            self.value = self.min_value + (self.value - self.max_value)

    def decrease(self):
        self.value -= self.step
        if self.value < self.min_value:
            self.value = self.max_value - (self.min_value - self.value)
