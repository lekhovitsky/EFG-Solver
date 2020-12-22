import itertools
from typing import Tuple, List

from game.location import Location

from . import Action


class Allocation(Action):
    indexes: Tuple[int]

    def __init__(self, indexes: Tuple[int]):
        self.indexes = indexes

    def __str__(self):
        return f"Allocate({','.join(map(str, self.indexes))})"

    @staticmethod
    def possible(num_bandits: int,
                 dangers: List[Location],
                 bandits: List[Location],
                 agent: Location
                 ) -> List['Allocation']:
        indexes: List[int] = list(range(len(dangers)))
        if not bandits:
            return list(map(Allocation, itertools.combinations(indexes, num_bandits)))
        else:
            # determine the index of agent
            agent_index = -1
            if agent in dangers:
                agent_index = dangers.index(agent)

            # determine current indexes of bandits
            current_indexes = tuple([dangers.index(bandit) for bandit in bandits])

            # add possible permutations
            possible = []
            for candidate_indexes in itertools.combinations(indexes, num_bandits):
                if agent_index in candidate_indexes:
                    continue
                if len(set(current_indexes).difference(set(candidate_indexes))) > 1:
                    continue
                possible.append(Allocation(candidate_indexes))
            return possible
