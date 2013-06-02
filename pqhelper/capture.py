from pqhelper import base


def capture(board):
    """Try to solve the board described by board_string.

    Return sequence of summaries that describe how to get to the solution.
    """
    game = Game()
    v = (0, 0)
    stub_actor = base.Actor('capture', v, v, v, v, v, v, v, v, v)
    root = base.State(board, stub_actor, stub_actor,
                      turn=1, actions_remaining=1)
    solution_node = None
    for eot in game.all_ends_of_turn(root):
        # check for a solution
        if eot.is_mana_drain:  # quick check before checking whole board
            if eot.parent.board.is_empty():
                solution_node = eot
                break
    # if solution found, build the list of swaps
    solution_sequence = list()  # empty sequence (no solution) by default
    if solution_node:
        node = solution_node
        while node:
            # record each swap in the path to the root
            if not isinstance(node, base.Swap):
                node = node.parent
                continue
            summary = base.Summary(node.parent.board, node.position_pair,
                                   None, None, None)
            solution_sequence.append(summary)
            node = node.parent
    return tuple(reversed(solution_sequence))


class Game(base.Game):
    def __init__(self):
        use_random_fill = False
        super(Game, self).__init__(use_random_fill)
        self._duplicate_root = _DuplicateTree()

    def _disallow_state(self, state):
        """Disallow states that are not useful to continue simulating."""
        disallow_methods = (self._is_duplicate_board,
                            self._is_impossible_by_count)
        for disallow_method in disallow_methods:
            if disallow_method(state):
                return True
        return False  # just to be explicit. allow if can't fail it

    def _is_duplicate_board(self, state):
        """Disallow any board that has been simulated elsewhere."""
        return self._duplicate_root.find_or_graft(state.board)

    def _is_impossible_by_count(self, state):
        """Disallow any board that has insufficient tile count to solve."""
        # count all the tile types and name them for readability
        counts = {tile_type: 0 for tile_type in base.Tile._all_types}
        standard_wildcard_type = '2'
        for p, tile in state.board.positions_with_tile():
            # count all wildcards as one value
            tile_type = tile._type
            try:
                int(tile_type)
                counts[standard_wildcard_type] += 1
            except ValueError:
                counts[tile_type] += 1
        skullbomb = counts['*']
        skull = counts['s']
        wildcard = counts[standard_wildcard_type]
        red = counts['r']
        green = counts['g']
        blue = counts['b']
        yellow = counts['y']
        exp = counts['x']
        money = counts['m']
        # always allow skullbomb with enough skulls
        if skullbomb and skullbomb + skull >= 3:
            return False
        # always allow wildcard with enough of one color
        if wildcard:
            if any(wildcard + color >= 3
                   for color in (red, green, blue, yellow)):
                return False
        # disallow simple cases since special cases didn't occur
        if any(tile and tile < 3 for tile in (red, green, blue, yellow,
                                              exp, money, skull)):
            return True
        # allow the state if counts seem ok
        return False


class _DuplicateTree(base.TreeNode):
    def __init__(self, tile=None):
        super(_DuplicateTree, self).__init__(tile=tile)

    def find_or_graft(self, board):
        """Build a tree with each level corresponding to a fixed position on
        board. A path of tiles is stored for each board. If any two boards
        have the same path, then they are the same board. If there is any
        difference, a new branch will be created to store that path.

        Return: True if board already exists in the tree; False otherwise

        """
        is_duplicate_board = True  # assume same until find a difference
        # compare each position
        node = self
        for p, new_tile in board.positions_with_tile():
            found_tile = False  # assume no tile in same position until found
            for child in node.children:
                if child.tile == new_tile:
                    # same tile found in this position --> continue this branch
                    node = child
                    found_tile = True
                    break
            if found_tile:
                pass  # go on to the next position
            else:
                # different tile --> start new branch and mark not exact match
                child = _DuplicateTree(new_tile)
                node.graft_child(child)
                node = child
                is_duplicate_board = False  # this will get set many times. ok
        return is_duplicate_board


if __name__ == '__main__':
    pass
