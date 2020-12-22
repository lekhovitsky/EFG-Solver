from typing import List

from game.location import Location
from game.maze import Maze

from . import Action


class Move(Action):
    dx: int
    dy: int

    def __init__(self, dx: int, dy: int):
        assert abs(dx) + abs(dy) == 1
        self.dx = dx
        self.dy = dy

    def __str__(self) -> str:
        if self.dx == 1:
            return "Right"
        elif self.dy == 1:
            return "Down"
        elif self.dx == -1:
            return "Left"
        else:
            return "Up"

    @staticmethod
    def possible(maze: Maze, location: Location, visited: List[Location]) -> List['Move']:
        neighbors = maze.neighbors(location)
        return [Move(*n.sub(location)) for n in neighbors if n not in visited]
