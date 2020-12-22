from typing import List

from . import Action


class Chance(Action):
    HIT = 0
    MISS = 1

    value: int

    def __init__(self, v: int):
        assert v in (Chance.MISS, Chance.HIT)
        self.value = v

    def __str__(self) -> str:
        if self.value == Chance.MISS:
            return "Miss"
        else:
            return "Hit"

    @staticmethod
    def possible() -> List['Chance']:
        return [Chance(Chance.MISS), Chance(Chance.HIT)]
