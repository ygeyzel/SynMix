from synmix.inputs.buttons import Button
from synmix.params.valuecontrollers import ValueController


class Param:
    def __init__(
        self, name: str, buttons: tuple[Button, ...], controller: ValueController
    ) -> None:
        """buttons all drive the param, e.g. one control mirrored on two channels."""
        self.name = name
        self.buttons = buttons
        self.controller = controller

    def __repr__(self) -> str:
        return f"Param({self.name}, {self.buttons}, {self.controller})"

    @property
    def value(self) -> float:
        return self.controller.value

    @property
    def is_reset_on_scene_change(self) -> bool:
        return not self.controller.is_persistent

    def control_param(self, value: float) -> None:
        self.controller.control_value(value)
