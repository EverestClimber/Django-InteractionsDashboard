from enum import Enum


class ChoiceEnum(Enum):
    @classmethod
    def choices(cls):
        return [(c.name, c.value) for c in cls]
