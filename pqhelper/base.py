from collections import deque
import random

import numpy

from treenode import TreeNode


class State(object):
    """Simulates the possibilities of a PQ game.

    Attributes represent a single state:
    For example, the board, number of actions remaining and the results of
    all valid swaps.

    Simulation produces a tree representing one set of possibilities for a game.
    Tree Structure:
    state  --->  transition  ->  state
             ->  ...
             ->  transition  ->  state

    Tree State Assumptions:
    - Each state has (0+) transitions as children in the tree
    - Each state that is a leaf has not been simulated yet

    Tree Transition Assumptions:
    - Each transition has (0 or 1) state as its child in the tree
    - Each transition that is a leaf is an "end of turn" transition
    """
    def __init__(self, board=None, turn=1, actions_remaining=1):
        self._type = 'state'
        self._board = board or Board()
        self._turn = turn
        self._actions_remaining = actions_remaining
        self._node = SimNode(self)

    # Core attributes
    @property
    def board(self):
        """This is non-settable to avoid unexpected behavior."""
        return self._board

    @property
    def turn(self):
        """This is non-settable to avoid unexpected behavior."""
        return self._turn

    @property
    def actions_remaining(self):
        """This is non-settable to avoid unexpected behavior."""
        return self._actions_remaining

    @property
    def type(self):
        return self._type

    # Delegated tree behavior
    def attach(self, other):
        """Attach other state or transition as a child to self."""
        self._node.graft_child(other._node)

    def children(self):
        """Return a tuple copy of the children in self."""
        return tuple(child.main for child in self._node.children)

    @property
    def parent(self):
        """Return the parent of self."""
        return self._node.parent.main

    def _leaves_within_depth(self, absolute_turn_depth):
        """Generate exactly the leaves within the tree rooted at self that
        are within the absolute turn depth."""
        for leaf in self._node.leaves:
            try:  # handle states
                turn = leaf.main.turn
            except AttributeError:  # handle transitions (no "turn" attribute)
                turn = leaf.parent.main.turn
            if turn <= absolute_turn_depth:
                yield leaf.main

    # Core behavior
    def end_of_turns(self, absolute_turn_depth=1, random_fill=False):
        """Yield each qualifying EOT found within the tree rooted at self.
        Complete all and only simulation to EOT within absolute_turn_depth.

        Arguments:
        absolute_turn_depth: no simulation will be done below this depth
        random_fill: instruct the simulation to fill the board with random
            tiles after each execution or not.
        """
        # tracking for unprocessed states and end of turns
        states = deque()
        eots = deque()
        # start with a set of qualifying leaves in the tree rooted at self
        leaves_within_depth = list(self._leaves_within_depth(absolute_turn_depth))
        for leaf in leaves_within_depth:

            print 'start leaf: '


            # decide how to handle the current set of qualifying leaves
            # -------------------------------------------------------------
            if leaf.type == 'state':
                states.append(leaf)
            elif leaf.type == 'end of turn':
                eots.append(leaf)
            elif leaf.type == 'mana drain':
                continue  # special case: ignore manadrain
            else:
                raise ValueError('Unexpectedly found a leaf that is not an'
                                 ' end of turn and not a state:\n{}'
                                 ''.format(leaf))
            # -------------------------------------------------------------
            # continue simulating until everything within turn limit is done
            while eots or states:
                # achieve basically depth-first simulation by trying EOT first
                try:
                    eot = eots.pop()
                    new_turn_state = State(board=eot.parent.board.copy(),
                                           turn=eot.parent.turn + 1,
                                           actions_remaining=1)
                    states.append(new_turn_state)
                    continue  # done with this state
                except IndexError:
                    pass
                # get and qualify state to work on
                state = states.pop()
                if state.turn > absolute_turn_depth:
                    continue  # ignore this state
                # # # # # # # # # todo: Start atomic change. rollback if error
                # handle EOT states
                if state.actions_remaining <= 0:
                    new_eot = EOT()
                    state.attach(new_eot)
                    eots.append(new_eot)
                    yield new_eot
                    continue  # no further simulation for this state
                # handle swaps
                for swap_pair in state.board.potential_swaps():
                    result_board, destroyed_groups = state.board.execute_once(swap=swap_pair,
                                                                              random_fill=random_fill)
                    # finish this swap if it was invalid
                    if not destroyed_groups:
                        continue
                    # attach the transition
                    swap = Swap(swap_pair)
                    state.attach(swap)
                    # attach the result state
                    bonus_action = any(len(group) >= 4
                                       for group in destroyed_groups)
                    result_state = State(board=result_board,
                                         turn=state.turn,
                                         actions_remaining=state.actions_remaining - 1 + bonus_action)
                    swap.attach(result_state)
                    # handle any chain reactions
                    potential_chain_reaction = result_state
                    while potential_chain_reaction:
                        result_board, destroyed_groups = potential_chain_reaction.board.execute_once(random_fill=random_fill)
                        # finish this chain reaction if it was invalid
                        if not destroyed_groups:
                            states.append(potential_chain_reaction)
                            break
                        # attach the transition
                        chain = ChainReaction()
                        potential_chain_reaction.attach(chain)
                        # attach the result state
                        bonus_action = any(len(group) >= 4
                                           for group in destroyed_groups)
                        result_state = State(board=result_board,
                                             turn=potential_chain_reaction.turn,
                                             actions_remaining=potential_chain_reaction.actions_remaining + bonus_action)
                        swap.attach(result_state)
                        # prepare to try for another chain reaction
                        potential_chain_reaction = result_state
                #at this point all swaps have been tried
                #if nothing was valid, it's a manadrain
                if not tuple(state.children()):
                    manadrain = ManaDrain()
                    state.attach(manadrain)
                    yield manadrain
                    continue  # no further simulation for this state
                # handle spells
                pass
                # # # # # # # # #todo:      End atomic change

    # Special methods
    def __str__(self):
        indent = '    '
        line_list = list()
        line_list.append('State:')
        line_list.append(indent + '{} : turn'.format(self.turn))
        line_list.append(indent + '{} : actions remaining'
                         ''.format(self.actions_remaining))
        line_list.append(indent + '{} : children'.format(len(self.children())))
        line_list.append(indent + 'board:')
        line_list.extend(indent + indent + line for line
                         in str(self.board).splitlines())
        return '\n    '.join(line_list)

    def __repr__(self):
        return str(self)


class _Transition(object):
    """Base class for all state-to-state transitions in a PQ simulation."""
    def __init__(self, type_name='base transition'):
        self._type = type_name
        self._node = SimNode(main=self)

    @property
    def type(self):
        return self._type

    # Delegated tree behavior
    def attach(self, other):
        """Attach other state or transition as a child to self."""
        self._node.graft_child(other._node)

    def children(self):
        """Return a tuple copy of the children in self."""
        return tuple(child.main for child in self._node.children)

    @property
    def parent(self):
        """Return the parent of self."""
        return self._node.parent.main


class Swap(_Transition):
    def __init__(self, position_pair):
        super(Swap, self).__init__('swap')
        self._position_pair = position_pair

    @property
    def position_pair(self):
        return self._position_pair


class ChainReaction(_Transition):
    def __init__(self):
        super(ChainReaction, self).__init__('chain reaction')


class EOT(_Transition):
    def __init__(self):
        super(EOT, self).__init__('end of turn')


class ManaDrain(_Transition):
    def __init__(self):
        super(ManaDrain, self).__init__('mana drain')


class Board(object):
    """Behaves like a PQ board."""
    def __init__(self, board_string=None):
        # setup the core ndarray that stores the 8x8 grid of tiles
        grid_shape = (8, 8)
        self._array = numpy.ndarray(shape=grid_shape, dtype=object)
        if board_string is None:
            blank = Tile('.')
            self._array.fill(blank)
        else:
            for row, row_string in enumerate(board_string.split()):
                for col, tile_character in enumerate(row_string):
                    self._array[row, col] = Tile(tile_character)

    # Execution Methods (Core behavior)
    def execute_once(self, swap=None,
                     spell_changes=None, spell_destructions=None,
                     random_fill=False):
        """Execute the board only one time. Do not execute chain reactions.

        Arguments:
        swap - pair of adjacent positions
        spell_changes - sequence of (position, tile) changes
        spell_destructions - sequence of positions to be destroyed

        Return: (copy of the board, destroyed tile groups)
        """
        bcopy = self.copy()  # work with a copy, not self
        total_destroyed_tile_groups = list()
        # swap if any
        bcopy._swap(swap)
        # spell changes if any
        bcopy._change(spell_changes)
        # spell destructions and record if any
        # first convert simple positions to groups
        spell_destructions = spell_destructions or tuple()
        destruction_groups = [[p] for p in spell_destructions]
        destroyed_tile_groups = bcopy._destroy(destruction_groups)
        total_destroyed_tile_groups.extend(destroyed_tile_groups)
        # execute one time only
        # look for matched groups
        matched_position_groups = bcopy._match()
        # destroy and record matched groups
        destroyed_tile_groups = bcopy._destroy(matched_position_groups)
        total_destroyed_tile_groups.extend(destroyed_tile_groups)
        bcopy._fall()
        if random_fill:
            bcopy._random_fill()
        return bcopy, total_destroyed_tile_groups

    def _swap(self, swap):
        """Simulate swapping as in PQ.

        swap should be a sequence of two positions with a square distance of
        exactly 1.

        Non-adjacent swaps cause a ValueError.
        """
        if swap is None:
            return
        p1, p2 = swap
        square_distance = abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])
        if square_distance != 1:
            raise ValueError('Positions unexpectedly not adjacent: square'
                             ' distance between {} and {} is'
                             ' {}'.format(p1, p2,
                                          square_distance))
        a = self._array
        a[p1], a[p2] = a[p2], a[p1]

    def _change(self, changes):
        """Apply the given changes to the board.

        changes: sequence of (position, new tile) pairs or None
        """
        if changes is None:
            return
        for position, new_tile in changes:
            self._array[position] = new_tile

    def _match(self, non_equivalent_positions=None):
        """Find all matches and generate a position group for each match.

        non_equivalent_positions should be None (no optimization) or a sequence
        of positions in which the matching behavior has changed. Then matching
        can be limited to those rows / columns

        """
        #optional optimization based on matching changes from the previous board
        #get all rows and columns that have a non equivalent mark
        if non_equivalent_positions:
            rows = [row for row, column in non_equivalent_positions]
            columns = [column for row, column in non_equivalent_positions]
            optimized_rows = set(rows)
            optimized_columns = set(columns)
        else:
            #disable optimized matching
            optimized_rows = None
            optimized_columns = None
        for match in self.__match_rows(optimized_rows):
            #match in rows
            yield match
        for match in self.__match_rows(optimized_columns,
                                       transpose=True):
            #match in columns and transpose coordinates
            yield match

    def __match_rows(self, optimized_lines=None, transpose=False):
        """Main functionality of _match, but works only on rows.
        Full matches are found by running this once with original board and
        once with a transposed board.

        Arguments:
        optimized_lines is an optional argument that identifies the lines
        that need to be matched.

        transpose indicates whether the match is looking at rows or columns

        """
        MIN_LENGTH = 3
        a = self._array
        if transpose:
            a = a.T
        rows = optimized_lines or range(8)
        # check for matches in each row separately
        for row in rows:
            NUM_COLUMNS = 8
            match_length = 1
            start_position = 0  # next tile pointer
            #set next start position as long as a match is still possible
            while start_position + MIN_LENGTH <= NUM_COLUMNS:
                group_type = a[row, start_position]
                # try to increase match length as long as there is room
                while start_position + match_length + 1 <= NUM_COLUMNS:
                    next_tile = a[row, start_position + match_length]
                    # if no match, stop looking for further matches
                    if not group_type.matches(next_tile):
                        break
                    # if group_type is wildcard, try to find a real type
                    if group_type.is_wildcard():
                        group_type = next_tile
                    match_length += 1
                #produce a matched position group if the current match qualifies
                if match_length >= MIN_LENGTH and not group_type.is_wildcard():
                    row_ = row
                    target_positions = [(row_, col_) for col_
                                        in range(start_position,
                                                 start_position + match_length)]
                    if transpose:
                        target_positions = [(col_, row_)
                                            for row_, col_ in target_positions]
                    yield target_positions
                #setup for continuing to look for matches after the current one
                start_position += match_length
                match_length = 1

    def _destroy(self, target_position_groups):
        """Destroy indicated position groups, handle any chain destructions,
        and return all destroyed groups."""
        target_position_groups = list(target_position_groups)  # work on a copy
        destroyed_tile_groups = list()
        blank = Tile('.')
        a = self._array
        while target_position_groups:  # continue as long as more targets exist
            # delay actual clearing of destroyed tiles until all claiming
            # groups have been stored (e.g. overlapping matches, bombs)
            clear_after_storing = list()
            new_target_position_groups = list()
            for target_position_group in target_position_groups:
                destroyed_tile_group = list()
                for target_position in target_position_group:
                    target_tile = a[target_position]
                    # no handling for blanks that appear in destruction
                    if target_tile.is_blank():
                        continue
                    destroyed_tile_group.append(target_tile)
                    clear_after_storing.append(target_position)
                    # skull bombs require further destructions
                    if target_tile.is_skullbomb():
                        new_positions = self.__skullbomb_radius(target_position)
                        # convert individual positions to position groups
                        new_position_groups = [(new_position,) for new_position
                                               in new_positions]
                        new_target_position_groups.extend(new_position_groups)
                if destroyed_tile_group:
                    destroyed_tile_groups.append(destroyed_tile_group)
            # Finally clear positions after all records have been made
            for position in clear_after_storing:
                a[position] = blank
            # Replace the completed target position groups with any new ones
            target_position_groups = new_target_position_groups
        return destroyed_tile_groups

    def __skullbomb_radius(self, position):
        """Generate all valid positions in the square around position."""
        #get the boundaries of the explosion
        sb_row, sb_col = position
        left = max(sb_row - 1, 0)  # standard radius or 0 if out of bounds
        right = min(sb_row + 1, 7)  # standard radius or 7 if out of bounds
        top = max(sb_col - 1, 0)
        bottom = min(sb_col + 1, 7)
        for explosion_row in xrange(left, right + 1):
            for explosion_col in xrange(top, bottom + 1):
                yield (explosion_row, explosion_col)

    def _fall(self):
        """Cause tiles to fall down to fill blanks below them."""
        a = self._array
        for column in [a[:, c] for c in range(a.shape[1])]:
            # find blanks and fill them with tiles above them
            target_p = column.shape[0] - 1  # start at the bottom
            fall_distance = 1  # increases every time a new gap is found
            while target_p - fall_distance >= 0:  # step up the target position
                if column[target_p].is_blank():
                    blank = column[target_p]  # move the blank
                    #find the next nonblank position
                    while target_p - fall_distance >= 0:
                        next_p = target_p - fall_distance
                        if column[next_p].is_blank():
                            fall_distance += 1
                        else:
                            break  # stop expanding blank space when nonblank
                    if target_p - fall_distance >= 0:
                        #move the nonblank position to the target if gap exists
                        source_position = target_p - fall_distance
                        column[target_p] = column[source_position]
                        column[source_position] = blank
                        #in any case, move on to the next target position
                target_p -= 1

    def _random_fill(self):
        """Fill the board with random tiles based on the Tile class."""
        a = self._array
        for position in self.positions():
            if a[position].is_blank():
                a[position] = Tile.random_tile()

    # Special Methods
    def __str__(self):
        """Represent the board basically as an 8x8 block of characters."""
        return '\n'.join([''.join(str(tile) for tile in row)
                          for row in self._array])

    # Convenience Methods
    def potential_swaps(self):
        """Generate a sequence of at least all valid swaps for this board.

        The built-in optimizer filters out many meaningless swaps, but not all.
        """
        a = self._array
        rows, cols = a.shape
        for this_position in self.positions():
            #produce horizontal swap for this position
            r, c = this_position
            if c < cols - 1:
                other_position = (r, c + 1)
                if self._swap_optimizer_allows(this_position, other_position):
                    yield (this_position, other_position)
            #produce vertical swap for this position. not DRY but meh.
            if r < rows - 1:
                other_position = (r + 1, c)
                if self._swap_optimizer_allows(this_position, other_position):
                    yield (this_position, other_position)

    def _swap_optimizer_allows(self, p1, p2):
        """Identify easily discarded meaningless swaps.

        This is motivated by the cost of millions of swaps being simulated.
        """
        # setup local shortcuts
        a = self._array
        tile1 = a[p1]
        tile2 = a[p2]
        # 1) disallow same tiles
        if tile1 == tile2:
            return False
        # 2) disallow matches unless a wildcard is involved
        if tile1.matches(tile2) and not any(t.is_wildcard()
                                            for t in (tile1, tile2)):
            return False
        # 3) disallow when both tiles (post-swap) are surrounded by non-matches
        center_other_pairs = ((p1, p2), (p2, p1))

        class MatchedTiles(Exception):
            pass
        try:
            for center_p, other_p in center_other_pairs:
                up_down_left_right = ((center_p[0] - 1, center_p[1]),
                                      (center_p[0] + 1, center_p[1]),
                                      (center_p[0],     center_p[1] - 1),
                                      (center_p[0],     center_p[1] + 1))
                post_swap_center_tile = a[other_p]
                for surrounding_p in up_down_left_right:
                    # ignore out of bounds positions
                    # and ignore the inner swap which is handled elsewhere
                    if any((not (0 <= surrounding_p[0] <= 7),  # out of bounds
                            not (0 <= surrounding_p[1] <= 7),  # out of bounds
                            surrounding_p == other_p)):  # inner swap
                        continue
                    surrounding_tile = a[surrounding_p]
                    if post_swap_center_tile.matches(surrounding_tile):
                        raise MatchedTiles()
        except MatchedTiles:
            pass  # if any match found, stop checking and pass this filter
        else:
            return False  # if no match is found, then this can be filtered
        return True  # return True if it couldn't be filtered

    def copy(self):
        """Generate an independent copy of self."""
        return Board(str(self))

    def positions(self):
        """Generate all positions as a tuple of (row,col)."""
        # if desired, use it[0].item() to reference the content of the cell
        it = numpy.nditer(self._array, flags=['multi_index', 'refs_ok'])
        while not it.finished:
            yield (it.multi_index[0], it.multi_index[1])
            it.iternext()

    def is_empty(self):
        return all(self._array[p].is_blank() for p in self.positions())

    # Delegated behavior to numpy.ndarray
    def __getitem__(self, item):
        return self._array[item]

    def __setitem__(self, key, value):
        self._array[key] = value


class Tile(object):
    """Behaves like a PQ Tile."""
    _all_types = ('r', 'g', 'b', 'y',  # colors
                  's', '*',            # skulls
                  'x', 'm', '.',       # experience, money, blank
                  '2', '3', '4', '5', '6', '7', '8', '9')  # wildcards
    _matches = {'.': tuple(),  # blank matches nothing
                'r': ('r', '2', '3', '4', '5', '6', '7', '8', '9'),
                'g': ('g', '2', '3', '4', '5', '6', '7', '8', '9'),
                'b': ('b', '2', '3', '4', '5', '6', '7', '8', '9'),
                'y': ('y', '2', '3', '4', '5', '6', '7', '8', '9'),
                's': ('s', '*'),
                '*': ('s', '*'),
                'x': ('x',),
                'm': ('m',),
                '2': ('r', 'g', 'b', 'y',
                      '2', '3', '4', '5', '6', '7', '8', '9'),
                '3': ('r', 'g', 'b', 'y',
                      '2', '3', '4', '5', '6', '7', '8', '9'),
                '4': ('r', 'g', 'b', 'y',
                      '2', '3', '4', '5', '6', '7', '8', '9'),
                '5': ('r', 'g', 'b', 'y',
                      '2', '3', '4', '5', '6', '7', '8', '9'),
                '6': ('r', 'g', 'b', 'y',
                      '2', '3', '4', '5', '6', '7', '8', '9'),
                '7': ('r', 'g', 'b', 'y',
                      '2', '3', '4', '5', '6', '7', '8', '9'),
                '8': ('r', 'g', 'b', 'y',
                      '2', '3', '4', '5', '6', '7', '8', '9'),
                '9': ('r', 'g', 'b', 'y',
                      '2', '3', '4', '5', '6', '7', '8', '9')}
    _random_weights = {'r': 2,
                       'g': 2,
                       'b': 2,
                       'y': 2,
                       's': 2,
                       '*': 1,  # i.e. skullbomb half as likely as others
                       'x': 2,
                       'm': 2}
    _random_distribution = list()
    for tile_type, weight in _random_weights.items():
        _random_distribution += (tile_type,) * weight

    def __init__(self, type_character):
        if type_character in self._all_types:
            self._type = type_character
        else:
            raise ValueError('Provided type_character ({0}) is not one of the '
                             'allowed types: {1}'.format(type_character,
                                                         self._all_types))

    # Tile comparisons (core behavior)
    def matches(self, other):
        """Return True for tiles that would match in PQ and False otherwise."""
        return other._type in self._matches[self._type]

    # Random tile
    @classmethod
    def random_tile(cls):
        """Return a random tile based on _random_weights distribution."""
        random_type = random.choice(cls._random_distribution)
        return cls(random_type)

    # Special methods
    def __str__(self):
        return self._type

    def __repr__(self):
        return "Tile({})".format(repr(self._type))

    def __eq__(self, other):
        """Equality is equality of self and other tile types."""
        return self._type == other._type

    def __ne__(self, other):
        """Inequality is simply the opposite of equality."""
        return not (self == other)

    # Convenience methods
    def is_skullbomb(self):
        return True if self._type == '*' else False

    def is_blank(self):
        return True if self._type == '.' else False

    def is_wildcard(self):
        try:
            return int(self._type) in range(2, 10)
        except ValueError:
            return False

    def is_color(self):
        return self._type in ('r', 'g', 'b', 'y')


class SimNode(TreeNode):
    """Provide node behavior for States and Transitions."""
    def __init__(self, main):
        super(SimNode, self).__init__(main=main)


if __name__ == "__main__":
    pass
