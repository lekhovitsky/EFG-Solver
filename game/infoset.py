import itertools
from typing import List, Tuple, Dict

from game.actions import Action, Move, Allocation, Chance
from game.location import Location
from enums import Player


class Infoset:
    # code -> index mapping
    _codes: Dict[str, int]

    # index of a next created Infoset
    _current_idx: int

    # pre-computed list of all possible bandit allocations
    _allocations: List[Tuple[int]]

    @classmethod
    def init(cls, num_bandits: int, num_dangers: int):
        assert 0 < num_bandits <= num_dangers

        cls._codes = {}
        cls._current_idx = 1
        danger_indexes: List[int] = list(range(num_dangers))
        cls._allocations = list(itertools.combinations(danger_indexes, num_bandits))

    def __init__(self,
                 player: Player,
                 agent: Location,
                 bandits: List[Location],
                 dangers: List[Location],
                 history: List[Action]):
        self.player = player
        self.agent = agent
        self.bandits = bandits
        self.dangers = dangers
        self.history = history

    def __str__(self):
        return f"I{self.index()}"

    def index(self) -> int:
        code = self.encode()
        if Infoset._codes.get(code) is None:
            Infoset._codes[code] = Infoset._current_idx
            Infoset._current_idx += 1
        return Infoset._codes[code]

    def encode(self) -> str:
        if self.player == Player.bandit:
            return self._encode_bandit_history()
        else:
            return self._encode_agent_history()

    def _encode_bandit_history(self) -> str:
        # empty history (initial allocation node) is the only one in its infoset.
        # any other two bandit histories are in the same infoset if:
        # 1. initial bandit allocations are the same.
        # 2. alarm was triggered by the agent in the same empty dangerous place.

        # allocation node
        # ---------------
        if not self.bandits:
            return "bandit:root"

        # reallocation node
        # -----------------
        # get the index of the initial bandits allocation
        allocation = tuple([self.dangers.index(bandit) for bandit in self.bandits])
        allocation_index = self._allocations.index(allocation)

        # get the index of an empty dangerous place visited by the agent
        empty = [d for d in self.dangers if d not in self.bandits]
        empty_index = empty.index(self.agent)

        return f"bandit:A{allocation_index}E{empty_index}"

    def _encode_agent_history(self) -> str:
        # two agent histories are in the same infoset if:
        # 1. agent's actions sequences are exactly same
        # 2. non-agent's actions sequences are of the same type
        symbols: List[str] = []
        for action in self.history:
            if isinstance(action, Move):
                symbols.append(str(action)[0])  # {"U", "D", "L", "R"}
            elif isinstance(action, Allocation):
                symbols.append("A")
            elif isinstance(action, Chance):
                symbols.append("C")
            else:
                raise TypeError(f"Unknown action type: {action.__class__.__name__}")

        return f"agent:{''.join(symbols)}"
