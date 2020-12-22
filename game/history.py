from copy import deepcopy
from typing import List

from . import (
    Action, Move, Allocation, Chance, Maze,
    Player, HistoryType, Infoset, Location
)

UTILITY = 10.0


class History:
    history: List[Action] = []

    maze: Maze
    num_bandits: int
    hit_chance: float

    alarm: bool = True
    num_golds: int = 0
    player: Player = Player.bandit
    bandit_locations: List[Location] = []
    visited_locations: List[Location] = []

    def __init__(self, maze: Maze, num_bandits: int, hit_chance: float):
        self.maze = maze
        self.num_bandits = num_bandits
        self.hit_chance = hit_chance
        self.visited_locations.append(maze.start)

    def __str__(self) -> str:
        return ""

    def type(self) -> HistoryType:
        if self.player == Player.chance:
            return HistoryType.chance
        elif self.player == Player.terminal:
            return HistoryType.terminal
        else:
            return HistoryType.decision

    def current_player(self) -> Player:
        return self.player

    def infoset(self) -> Infoset:
        assert self.player in [Player.agent, Player.bandit]
        return Infoset(self.player, self._agent_location, self.bandit_locations, self.maze.dangers, self.history)

    def actions(self) -> List[Action]:
        assert self.player in [Player.agent, Player.bandit, Player.chance]
        if self.player == Player.agent:
            return Move.possible(self.maze, self._agent_location, self.visited_locations)
        elif self.player == Player.bandit:
            return Allocation.possible(self.num_bandits, self.maze.dangers, self.bandit_locations, self._agent_location)
        else:
            return Chance.possible()

    def utility(self) -> float:
        assert self.type() == HistoryType.terminal
        if self._agent_location == self.maze.goal:
            return UTILITY + self.num_golds
        return 0.

    def chance_prob(self, action: Action) -> float:
        assert self.type() == HistoryType.chance and isinstance(action, Chance)
        return self.hit_chance if action.value == Chance.HIT else 1 - self.hit_chance

    def child(self, action: Action) -> 'History':
        child = self._clone()
        child.history.append(action)

        if isinstance(action, Move):
            loc = child._agent_location.add(action.dx, action.dy)
            child.visited_locations.append(loc)

            if not Move.possible(child.maze, loc, child.visited_locations):
                child.player = Player.terminal

            elif loc == child.maze.goal:
                child.player = Player.terminal

            elif loc in child.maze.golds:
                child.num_golds += 1

            elif loc in child.maze.dangers:
                if loc in child.bandit_locations:
                    child.player = Player.chance
                elif child.alarm:
                    child.player = Player.bandit

        elif isinstance(action, Allocation):
            # disable alarm after the first reallocation
            if child.bandit_locations:
                child.alarm = False
            child.bandit_locations = [child.maze.dangers[i] for i in action.indexes]
            child.player = Player.agent

        elif isinstance(action, Chance):
            # disable alarm after the first attack
            child.alarm = False
            if action.value == Chance.HIT:
                child.player = Player.terminal
            else:
                child.player = Player.agent

        else:
            raise TypeError(f"Unknown action type: {action.__class__.__name__}")

        return child

    @property
    def _agent_location(self):
        return self.visited_locations[-1]

    def _clone(self) -> 'History':
        clone = History(self.maze, self.num_bandits, self.hit_chance)
        clone.player = self.player
        clone.alarm = self.alarm
        clone.num_golds = self.num_golds
        clone.history = deepcopy(self.history)
        clone.visited_locations = deepcopy(self.visited_locations)
        clone.bandit_locations = deepcopy(self.bandit_locations)
        return clone
