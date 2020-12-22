from dataclasses import dataclass
from typing import Tuple


@dataclass
class Location:
    x: int
    y: int

    def add(self, dx: int, dy: int) -> 'Location':
        loc = Location(self.x + dx, self.y + dy)
        return loc

    def sub(self, other: 'Location') -> Tuple[int, int]:
        return self.x - other.x, self.y - other.y
