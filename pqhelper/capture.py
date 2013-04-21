from pqhelper import base as _base


class Board(_base.Board):
    pass  # no changes


class State(_base.State):
    def _disallow_state(self, state):
        """Disallow states that are not useful to continue simulating."""
        dissallow_methods = (self.__duplicate_board, self.__impossible_by_count)
        return any(dissallow(state) for dissallow in dissallow_methods)

    def __duplicate_board(self, state):
        """Disallow any board that has been simulated elsewhere."""
        # get or create the solution space
        try:
            duplicate_tree = self.__duplicate_tree
        except AttributeError:
            duplicate_tree = self.__duplicate_tree = _DuplicateTree()
        return duplicate_tree.find_or_graft(state.board)

    def __impossible_by_count(self, state):
        """Disallow any board that has insufficient tile count to solve."""
        # count all the tile types and name them for readability
        counts = {tile_type: 0 for tile_type in _base.Tile._all_types}
        standard_wildcard_type = '2'
        for p in state.board.positions():
            # count all wildcards as one value
            tile_type = state.board[p]._type
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


class _DuplicateTree(_base.TreeNode):
    def __init__(self, tile=None):
        super(_DuplicateTree, self).__init__(tile=tile)

    def find_or_graft(self, board):
        node = self
        for row in range(8):
            for col in range(8):
                tile = board[row, col]
                for child in node._children:
                    if child.tile == tile:
                        node = child
                        break  # found an existing match
                else:
                    # no existing matches found so attach it
                    # it already can't be a duplicate so stop here
                    child = _DuplicateTree(tile)
                    node.graft_child(child)
                    return False
        return True  # finally return True if all tiles were grafted previously



if __name__ == '__main__':
    pass
