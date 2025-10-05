from abc import ABC, abstractmethod
from typing import Tuple


controllers_registry = {}

def register_controller(name):
    def decorator(cls):
        controllers_registry[name] = cls
        return cls

    return decorator



class ValueController(ABC):
    def __init__(self, *args, **kwargs):
        super().__init__()
        self.value = kwargs.get('initial_value', 0.0)

    def __repr__(self):
        return f'{self.__class__.__name__}({self.__dict__})'

    def set_value(self, value: float):
        self.value = value

    @abstractmethod
    def expose_functions(self) -> Tuple[callable]:
        pass

@register_controller('IncDecController')
class IncDecController(ValueController):
    def __init__(self, min_value: float, max_value: float, step: float, **kwargs):
        super().__init__(**kwargs)
        self.min_value = min_value
        self.max_value = max_value
        self.step = step

    @abstractmethod
    def increase(self):
        pass

    @abstractmethod
    def decrease(self):
        pass

    def expose_functions(self) -> Tuple[callable]:
        return (self.increase, self.decrease)


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
