# You can use your own implementation of game tree for testing.
# It should satisfy the original interfaces in game_tree.py
#
# The game tree implementation does not have to be the bandits game:
# you can use any game implementation, for example the simple poker.
# You have constructed the LP by hand at class, so you can check
# that for debugging.
#
# Note that the LP must support any EFG, especially including ones where
# the player makes multiple moves before it's opponent's turn.
#
# For automatic evaluation, test version of game_tree will be imported.
# In  your solution, submit only this file, i.e. game_lp.py
from typing import Dict

import gurobipy as gp

from game_tree import create_root
from game import Player, History, HistoryType

# Following packages are supported:
# Solvers:
# import gurobipy # == 8.1
# import cvxopt # == 1.2.3
#
# Matrix manipulation:
# import numpy as np


# Do not print anything besides the final output in your submission.
# Implement the LP as a function of the game tree.
#
# You MUST SPECIFY the LP as a function of the player! 
# I.e do NOT construct it only for player 0, and return the -value
# when asked for player 1 (do not use the zero-sum property
# for the value in the root). I.e. you are not allowed to make
# only one LP for both players, and find the value as `u_2(root) = -u_1(root)`.
#
# For each of the players you should have different sets of constraints,
# since they have different opponent infosets and player sequences.
# Within the constraints, you can of course use the fact that
# `u_2(z) = -u_1(z)` (where `z` is leaf in the tree), and you can specify
# the LP as maximization for both of the players.
#
# If you don't satisfy this, you will be heavily penalized.
#
# At the course webpage, we have calculated some testing game values for you.
# You can use them to check if your LP has been well specified.

def root_value(root: History, player: Player) -> float:
    """Create sequence-form LP from supplied EFG tree and solve it.

    Do not rely on any specifics of the original maze problem.
    Your LP should solve this problem for any EFG tree, if it is described
    by the original interface.

    The LP must be constructed for the given player:
    you should also compute the realization plan for that player.

    Return the expected utility in the root node for the player.
    So for the first player this will be the game value.

    Tip: Actions are ordered in the sense that that for two histories
       h,g in the same infoset it holds that h.actions() == g.actions().
       You can use action's index in the list for it's identification.
       Do not use str(action) or some other way of encoding the action based
       on your previous implementation.

       To identify **sequences** it is not enough to use the list of actions indices!
       Consider simple poker: first player can fold or bet.
       Folding in one Infoset_1  (player has card J) is however not the same thing
       as folding in Infoset_2 (player has card Q)!

       In class, we identified folding as f1 and f2, based on the fact from which
       infoset they came from.

    :param root: root history of the EFG tree
    :param player: zero-indexed player: first player has index 0,
                 second player has index 1
    :return: expected value in the root for given player
    """
    lp = SequentialFormLP(root, player)
    return lp.solve()


class SequentialFormLP:
    root: History
    player: Player

    # the LP itself
    model: gp.Model

    # r variables, one per player's sequence
    # represented as infoset-action pair
    r_vars: Dict[str, gp.Var] = {}

    # v variables, one per opponent's infoset
    v_vars: Dict[str, gp.Var] = {}

    # r constraints, one per player's infoset
    r_constr: Dict[str, gp.Constr] = {}
    r_constr_lhs: Dict[str, gp.LinExpr] = {}

    # v constraints, one per opponent's sequence
    # represented as infoset-action pair
    v_constr: Dict[str, gp.Constr] = {}
    v_constr_lhs: Dict[str, gp.LinExpr] = {}

    # NOTE:
    # players' sequences are encoded as strings I:a, where I is an index of the infoset and
    # a is an index of the taken action in the list of possible actions for this infoset.
    # this representation works because in the game with perfect for every infoset there's
    # exactly one sequence of actions of a player that leads to it.
    # root sequences are denoted with a "root" string.
    # also "root" is used as the name of a dummy infoset corresponding to an empty sequence
    # of a given player.

    def __init__(self, root: History, player: Player):
        self.root = root
        self.player = player
        self.model = gp.Model()

    def solve(self) -> float:
        self.r_vars["root"] = self.model.addVar(lb=0, ub=1, vtype=gp.GRB.CONTINUOUS, name="r(root)")
        self.r_constr_lhs["root"] = 1 - self.r_vars["root"]

        self.v_vars["root"] = self.model.addVar(lb=-gp.GRB.INFINITY, vtype=gp.GRB.CONTINUOUS, name="v(root)")
        self.v_constr_lhs["root"] = -self.v_vars["root"]

        self._process(self.root, "root", "root", 1.)

        for inf in self.r_constr_lhs:
            self._make_r_constr(inf)
        for seq in self.v_constr_lhs:
            self._make_v_constr(seq)

        self.model.setObjective(self.v_vars["root"], sense=gp.GRB.MAXIMIZE)

        self.model.update()
        self.model.optimize()
        return self.model.objVal

    def _process(self, history: History, player_seq: str, opponent_seq: str, chance: float):
        player: Player = history.player
        h_type: HistoryType = history.type()

        if h_type == HistoryType.terminal:
            sign = 1 if self.player == 0 else -1
            value = sign * chance * history.utility()
            self.v_constr_lhs[opponent_seq] += value * self.r_vars[player_seq]

        elif h_type == HistoryType.chance:
            for a in history.actions():
                next_chance = chance * history.chance_prob(a)
                self._process(history.child(a), player_seq, opponent_seq, next_chance)

        else:
            infoset: str = str(history.infoset().index())
            if player == self.player:
                # create a new r-constraint corresponding to the current infoset
                if infoset not in self.r_constr_lhs:
                    self.r_constr_lhs[infoset] = self.r_vars[player_seq]

                for i, a in enumerate(history.actions()):
                    next_seq = f"{infoset}:{i}"
                    # create a new r-variable corresponding to a given sequence extension
                    if next_seq not in self.r_vars:
                        self.r_vars[next_seq] = self.model.addVar(
                            ub=1, vtype=gp.GRB.CONTINUOUS, name=f"r({next_seq})")
                        self.r_constr_lhs[infoset] -= self.r_vars[next_seq]

                    self._process(history.child(a), next_seq, opponent_seq, chance)

            else:
                # create a new v-variable corresponding to the current infoset
                if infoset not in self.v_vars:
                    self.v_vars[infoset] = self.model.addVar(
                        lb=-gp.GRB.INFINITY, vtype=gp.GRB.CONTINUOUS, name=f"v({infoset})")
                    self.v_constr_lhs[opponent_seq] += self.v_vars[infoset]

                for i, a in enumerate(history.actions()):
                    next_seq = f"{infoset}:{i}"
                    # create a new v-constraint corresponding to a given sequence extension
                    if next_seq not in self.v_constr_lhs:
                        self.v_constr_lhs[next_seq] = -self.v_vars[infoset]

                    self._process(history.child(a), player_seq, next_seq, chance)

    def _make_r_constr(self, infoset: str):
        if infoset in self.r_constr:
            return
        self.r_constr[infoset] = self.model.addConstr(self.r_constr_lhs[infoset] == 0, name=f"r-constr {infoset}")
        self.model.update()

    def _make_v_constr(self, sequence: str):
        if sequence in self.v_constr:
            return
        self.v_constr[sequence] = self.model.addConstr(self.v_constr_lhs[sequence] >= 0, name=f"v-constr {sequence}")
        self.model.update()


# Do not modify code below.
def main():
    # read input specification in the body of this function
    root_history = create_root()
    # additionally specify for which player it should be solved
    player = int(input())

    print(root_value(root_history, Player(player)))


if __name__ == "__main__":
    main()
