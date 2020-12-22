from enum import IntEnum
from typing import List

from game.location import Location


class Cell(IntEnum):
    FREE = 0
    OBSTACLE = 1


class Maze:
    data: List[List[Cell]]
    start: Location
    goal: Location
    golds: List[Location]
    dangers: List[Location]

    def __init__(self,
                 data: List[List[Cell]],
                 start: Location,
                 goal: Location,
                 golds: List[Location],
                 dangers: List[Location]):
        assert Maze.is_valid(data)
        self.data = data
        assert all([self.is_free(loc) for loc in [start, goal] + golds + dangers])
        self.start = start
        self.goal = goal
        self.golds = golds
        self.dangers = dangers

    @property
    def height(self) -> int:
        return len(self.data)

    @property
    def width(self) -> int:
        return len(self.data[0])

    def neighbors(self, location: Location) -> List[Location]:
        assert self.is_free(location)
        neighbors = []
        for dx, dy in [(1, 0), (0, 1), (-1, 0), (0, -1)]:
            loc = location.add(dx, dy)
            if self.contains(loc) and self.is_free(loc):
                neighbors.append(loc)
        return neighbors

    def contains(self, location: Location) -> bool:
        return 0 <= location.x < self.width and 0 <= location.y < self.height

    def is_free(self, location: Location) -> bool:
        assert self.contains(location)
        return self.data[location.y][location.x] == Cell.FREE

    @staticmethod
    def is_valid(data: List[List[int]]) -> bool:
        return data and data[0] and all([len(row) == len(data[0]) for row in data[1:]])
