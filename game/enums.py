from enum import IntEnum


class HistoryType(IntEnum):
    decision = 1
    chance = 2
    terminal = 3


class Player(IntEnum):
    agent = 0
    bandit = 1
    chance = 2
    terminal = 3
