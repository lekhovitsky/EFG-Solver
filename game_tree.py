from typing import List, Optional, Tuple

from game import History, HistoryType, Infoset, Location, Maze, Cell


def read() -> Tuple[Maze, int, float]:
    maze_data: List[List[Cell]] = []
    start: Optional[Location] = None
    goal: Optional[Location] = None
    golds: List[Location] = []
    dangers: List[Location] = []

    M = int(input())
    N = int(input())
    assert M and N

    for y in range(M):
        row = input()
        assert len(row) == N

        maze_row = []
        for x, s in enumerate(row):
            assert s in "#-SDGE"
            maze_row.append(Cell.OBSTACLE if s == "#" else Cell.FREE)

            loc = Location(x, y)
            if s == "S":
                assert start is None, "There only can be one start location"
                start = loc
            elif s == "D":
                assert goal is None, "There only can be one goal location"
                goal = loc
            elif s == "G":
                golds.append(loc)
            elif s == "E":
                dangers.append(loc)

        maze_data.append(maze_row)

    assert start and goal, "Start or goal location not specified"
    assert start != goal, "Start and goal locations must be different"
    maze = Maze(maze_data, start, goal, golds, dangers)

    num_bandits = int(input())
    assert 0 < num_bandits <= len(dangers)

    hit_chance = float(input())
    assert 0 <= hit_chance <= 1, "Come on..."

    return maze, num_bandits, hit_chance


def create_root() -> History:
    maze, num_bandits, hit_chance = read()
    Infoset.init(num_bandits, num_dangers=len(maze.dangers))
    return History(maze, num_bandits, hit_chance)


def export_gambit(root_history: History) -> str:
    players = ' '.join([f"\"Pl{i}\"" for i in range(2)])
    ret = f"EFG 2 R \"\" {{ {players} }} \n"

    terminal_idx = 1
    chance_idx = 1

    def build_tree(history, depth):
        nonlocal ret, terminal_idx, chance_idx

        ret += " " * depth  # add nice spacing

        if history.type() == HistoryType.terminal:
            util = history.utility()
            ret += f"t \"{history}\" {terminal_idx} \"\" "
            ret += f"{{ {util}, {-util} }}\n"
            terminal_idx += 1
            return

        if history.type() == HistoryType.chance:
            ret += f"c \"{history}\" {chance_idx} \"\" {{ "
            ret += " ".join([f"\"{str(action)}\" {history.chance_prob(action):.3f}"
                             for action in history.actions()])
            ret += " } 0\n"
            chance_idx += 1

        else:  # player node
            player = int(history.current_player()) + 1  # cannot be indexed from 0
            infoset = history.infoset()
            ret += f"p \"{history}\" {player} {infoset.index()} \"\" {{ "
            ret += " ".join([f"\"{str(action)}\"" for action in history.actions()])
            ret += " } 0\n"

        for action in history.actions():
            child = history.child(action)
            build_tree(child, depth + 1)

    build_tree(root_history, 0)
    return ret


if __name__ == '__main__':
    print(export_gambit(create_root()))
