from abc import ABC, abstractmethod
from typing import Tuple


class ValueController(ABC):
    def __init__(self, *args, **kwargs):
        super().__init__()
        self.value = kwargs.get('initial_value', 0.0)

    def set_value(self, value: float):
        self.value = value

    @abstractmethod
    def expose_functions(self) -> Tuple[callable]:
        pass


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


class RangedController(IncDecController):
    def increase(self):
        self.value = min(self.value + self.step, self.max_value)

    def decrease(self):
        self.value = max(self.value - self.step, self.min_value)


class CyclicController(IncDecController):
    def increase(self):
        self.value += self.step
        if self.value > self.max_value:
            self.value = self.min_value + (self.value - self.max_value)
    
    def decrease(self):
        self.value -= self.step
        if self.value < self.min_value:
            self.value = self.max_value - (self.min_value - self.value)
