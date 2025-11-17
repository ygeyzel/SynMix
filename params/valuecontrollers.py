from abc import ABC, abstractmethod
from random import uniform
from threading import Timer
from typing import Any, Callable, Dict, Iterable, Tuple

from inputs.buttons import ButtonType
from inputs.midi import MIDI_DEC_VALUE, MIDI_INC_VALUE, MIDI_MAX_VALUE, MIDI_MIN_VALUE, MAX_PITCH, MIN_PITCH


controllers_registry: Dict[str, Tuple[type['ValueController'], frozenset[ButtonType]]] = {}


def _normalize_supported_types(
        controller_name: str,
        supported_button_types: Iterable[ButtonType]) -> frozenset[ButtonType]:
    supported_set = frozenset(supported_button_types)
    if not supported_set:
        raise ValueError(
            f"Controller '{controller_name}' must declare at least one supported button type.")

    return supported_set


def register_controller(name: str, *supported_button_types: ButtonType) -> Callable[[type['ValueController']], type['ValueController']]:
    def decorator(cls: type['ValueController']) -> type['ValueController']:
        controllers_registry[name] = (
            cls, _normalize_supported_types(name, supported_button_types))
        return cls

    return decorator


class ValueController(ABC):
    def __init__(self, *args, **kwargs):
        super().__init__()
        self.initial_value = kwargs.get('initial_value', 0.0)
        self.value = self.initial_value

    def __repr__(self):
        return f'{self.__class__.__name__}({self.__dict__})'

    def set_value(self, value: Any):
        self.value = value

    def reset(self):
        """Reset the controller to its initial value"""
        self.value = self.initial_value

    @abstractmethod
    def control_value(self, in_value: int):
        pass

    @property
    def is_persistent(self) -> bool:
        return False


@register_controller('NormalizedController', ButtonType.KNOB)
class NormalizedController(ValueController):
    def __init__(self, min_value, max_value, **kwargs):
        super().__init__(**kwargs)
        self.min_value = min_value
        self.max_value = max_value

        is_pitch = kwargs.get('is_pitch', False)
        self.max_input_value = MAX_PITCH if is_pitch else MIDI_MAX_VALUE
        self.min_input_value = MIN_PITCH if is_pitch else MIDI_MIN_VALUE

    def control_value(self, in_value: int):
        normalized_value = self.min_value + (in_value - self.min_input_value) * (
            self.max_value - self.min_value) / (self.max_input_value - self.min_input_value)
        self.set_value(normalized_value)


@register_controller('LinearSegmentedController', ButtonType.KNOB)
class LinearSegmentedController(ValueController):
    def __init__(self, segments_points: Iterable[Tuple[float, float]], **kwargs):
        super().__init__(**kwargs)
        self.segments_points = sorted(segments_points, key=lambda point: point[0])
        self.num_segments = len(self.segments_points) - 1

    def control_value(self, in_value: int):
        segment_index = next((i for i, point in enumerate(self.segments_points)
                              if point[0] >= in_value), self.num_segments) - 1

        x0, y0 = self.segments_points[segment_index]
        x1, y1 = self.segments_points[segment_index + 1]
        value = y0 + (in_value - x0) * (y1 - y0) / (x1 - x0)

        self.set_value(value)


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


@register_controller('RangedController', ButtonType.SCROLLER)
class RangedController(IncDecController):
    def increase(self):
        self.value = min(self.value + self.step, self.max_value)

    def decrease(self):
        self.value = max(self.value - self.step, self.min_value)


@register_controller('CyclicController', ButtonType.SCROLLER)
class CyclicController(IncDecController):
    def increase(self):
        self.value += self.step
        if self.value > self.max_value:
            self.value = self.min_value + (self.value - self.max_value)

    def decrease(self):
        self.value -= self.step
        if self.value < self.min_value:
            self.value = self.max_value - (self.min_value - self.value)


@register_controller('ToggleController', ButtonType.CLICKABLE)
class ToggleController(ValueController):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.initial_value = False
        self.value = False

    def reset(self):
        """Reset the controller to its initial value"""
        self.value = False

    def control_value(self, in_value: int):
        if in_value == MIDI_MAX_VALUE:
            self.set_value(not self.value)


@register_controller('IsPressedController', ButtonType.CLICKABLE)
class IsPressedController(ValueController):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.initial_value = False
        self.value = False

    def reset(self):
        """Reset the controller to its initial value"""
        self.value = False

    def control_value(self, in_value: int):
        self.set_value(in_value == MIDI_MAX_VALUE)


@register_controller('PersistentTimerToggleController', ButtonType.CLICKABLE)
class PersistentTimerToggleController(ValueController):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.initial_value = False
        self.value = False

        self.min_time_to_reset = kwargs.get('min_time_to_reset', 10.0)
        self.max_time_to_reset = kwargs.get('max_time_to_reset', 600.0)

    def control_value(self, in_value: int):
        if in_value == MIDI_MAX_VALUE and not self.value:
            self.set_value(True)
            time_to_reset = uniform(self.min_time_to_reset, self.max_time_to_reset)
            Timer(time_to_reset, self.reset).start()

    @property
    def is_persistent(self) -> bool:
        return True

