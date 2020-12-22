# EFG-Solver

Sequence form LP solver for imperfect information zero-sum extensive form games. 
Contains implementation of a solver applied to a specific maze problem described in [1].

There are two main entry points of the program:
* `game_tree.py` reads a game specification and outputs the game representation in a format compatible with Gambit [2].
* `game_lp.py` reads a game specification and outputs the value of the game for a given player. Linear programs are solved using the Gurobi optimizer [3].

## References:
1. Problem specification and examples: https://cw.fel.cvut.cz/wiki/courses/be4m36mas/assignment2-game
2. Gambit project: http://www.gambit-project.org/
3. Gurobi optimizer: https://www.gurobi.com/resource/modeling-with-the-gurobi-python-interface/
