from pqhelper import base


class _DuplicateTree(base.TreeNode):
    def __init__(self, tile=None):
        super(_DuplicateTree, self).__init__(tile=tile)

    def find_or_graft(self, board):
        """Build a tree with various tiles for each position...."""
        node = self
        exact_match = True  # assume same until find a difference
        # compare each position
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
                exact_match = False  # this will get set many times. no problem
        return exact_match


class Game(base.Game):
    _duplicate_root = _DuplicateTree()

    @classmethod
    def clear_duplicate_tree(cls):
        for child in cls._duplicate_root.children:
            child.trim()

    def _disallow_state(self, state):
        """Disallow states that are not useful to continue simulating."""
        dissallow_methods = (self.__duplicate_board, self.__impossible_by_count)
        return any(dissallow(state) for dissallow in dissallow_methods)

    def __duplicate_board(self, state):
        """Disallow any board that has been simulated elsewhere."""
        return self._duplicate_root.find_or_graft(state.board)

    def __impossible_by_count(self, state):
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


# def capture(board_string):
#     """Try to solve the board described by board_string.
#
#     Return tuple of swaps in the order required to solve the board.
#     """
#     _State.clear_duplicate_tree()
#     state = _State(_Board(board_string))
#     solution_sequence = list()
#     enough_turns = 20
#     for eot in state.end_of_turns(absolute_turn_depth=enough_turns):
#         if eot.parent.board.is_empty():
#             node = eot._node
#             while node:
#                 if node.main.type == 'swap':
#                     solution_sequence.append(node.main.position_pair)
#                 node = node.parent
#             break
#     _State.clear_duplicate_tree()
#     return tuple(reversed(solution_sequence))


if __name__ == '__main__':
    pass
