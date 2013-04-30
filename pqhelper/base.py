from collections import deque
import random

import numpy

from treenode import TreeNode


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
    for __tile_type, __weight in _random_weights.items():
        _random_distribution += (__tile_type,) * __weight

    _singletons = dict()

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
    def is_experience(self):
        return True if self._type == 'x' else False

    def is_money(self):
        return True if self._type == 'm' else False

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

    @classmethod
    def singleton(cls, tile_type):
        try:
            tile = cls._singletons[tile_type]
        except KeyError:
            tile = cls._singletons[tile_type] = cls(tile_type)
        return tile


class Board(object):
    """Behaves like a PQ board."""
    # Customizeable class attributes
    Tile = Tile

    def __init__(self, board_string=None):
        # setup the core ndarray that stores the 8x8 grid of tiles
        grid_shape = (8, 8)
        self._array = numpy.ndarray(shape=grid_shape, dtype=object)
        if board_string is None:
            blank = self.Tile.singleton('.')
            self._array.fill(blank)
        else:
            for row, row_string in enumerate(board_string.split()):
                for col, tile_character in enumerate(row_string):
                    self._array[row, col] = self.Tile.singleton(tile_character)

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
        blank = self.Tile.singleton('.')
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
                a[position] = self.Tile.random_tile()

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
        return self.__class__(str(self))

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


class Actor(object):
    def __init__(self, actor_string='player'):
        name, attr_current_max_sets = self._parse_actor_string(actor_string)
        # apply name
        if not name in ('player', 'opponent'):
            raise ValueError('Expected name to be "player" or "opponent"')
        self._name = name
        # apply attributes with current and max
        self._attributes_to_copy = list()
        for name, current, max_ in attr_current_max_sets:
            self._set_property_current_max(name, current, max_)
            self._attributes_to_copy.append(name)

    def _set_property_current_max(self, name, current, max_):
        internal_name = '_' + name
        internal_max_name = internal_name + '_max'
        # create and apply the attribute as a property with set limits
        fget = lambda self_: getattr(self_, internal_name)
        fset = lambda self_, value:\
            setattr(self_, internal_name,
                    max(0, min(value, getattr(self, internal_max_name))))
        setattr(self.__class__, name, property(fget=fget, fset=fset))
        # set the current and max values
        setattr(self, internal_max_name, max_)
        setattr(self, name, current)

    def _parse_actor_string(self, s):
        """Return the parts of an actor string

        name: string name of the actor
        attr_current_maxes: list of tuples
            - string attribute name
            - non-negative integer current value
            - non-negative integer max value
        """
        lines = s.strip().splitlines()
        name = lines[0]
        attr_current_maxes = list()
        for line in lines[1:]:
            attr, current_and_max = (x.strip() for x in line.split(':'))
            current, max_ = (int(x.strip()) for x in current_and_max.split('/'))
            if current < 0 or max_ < 0:
                raise ValueError('current and max must be non-negative')
            attr_current_maxes.append((attr, current, max_))
        return name, attr_current_maxes

    def apply_tile_groups(self, tile_groups):
        """Apply the tiles to self and return an attack value.

        Stub for specific game types
        """
        attack_value = 0  # stub
        return attack_value

    def apply_attack(self, attack_value):
        """Apply the attack value to self.

        Stub for specific game types
        """
        pass

    @property
    def name(self):
        return self._name

    def copy(self):
        return self.__class__(str(self))

    def __str__(self):
        lines = [self.name]
        for attr in self._attributes_to_copy:
            max_attr = '_' + attr + '_max'
            lines.append('{}: {}/{}'.format(attr,
                                            getattr(self, attr),
                                            getattr(self, max_attr)))
        return '\n'.join(lines)


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
    # Parts Classes that can be customized in specific game types
    Tile = Tile
    Board = Board
    Actor = Actor
    _random_fill = False

    def __init__(self, board=None, turn=1, actions_remaining=1,
                 player=None, opponent=None):
        self._type = 'state'
        self._board = board or self.Board()
        self._turn = turn
        self._actions_remaining = actions_remaining
        self.player = player or self.Actor('player')
        self.opponent = opponent or self.Actor('opponent')
        self._node = _SimNode(self)

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

    @property
    def active(self):
        return self.player if self.turn % 2 else self.opponent

    @property
    def passive(self):
        return self.opponent if self.turn % 2 else self.player

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
        try:
            return self._node.parent.main
        except AttributeError:  # no parent
            return None

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
    def end_of_turns(self, absolute_turn_depth=1):
        """Yield each qualifying EOT found within the tree rooted at self.
        Complete all and only simulation to EOT within absolute_turn_depth.

        Arguments:
        absolute_turn_depth: no simulation will be done below this depth
        random_fill: instruct the simulation to fill the board with random
            tiles after each execution or not.
        """
        # tracking for unprocessed states and end of turns
        ready_for_action_stack = deque(leaf.main for leaf in self._node.leaves)
        # continue simulating until everything within turn limit is done
        while ready_for_action_stack:
            next_job = ready_for_action_stack.pop()
            # get a state to simulate or continue to the next job
            if next_job.type == 'mana drain':
                continue  # ignore mana drains
            elif next_job.type == 'state' and not tuple(next_job.children()):
                # this state is ready to be simulated
                if next_job.turn > absolute_turn_depth:
                    continue  # ignore states over the turn limit
                state = next_job
            elif next_job.type == 'end of turn':
                last_state = next_job.parent
                # ignore end of turns at the turn limit
                if last_state.turn + 1 > absolute_turn_depth:
                    continue
                # the next turn is within the turn limit so simulate it
                state = self.__class__(board=last_state.board.copy(),
                                       turn=last_state.turn + 1,
                                       actions_remaining=1,
                                       player=last_state.player.copy(),
                                       opponent=last_state.opponent.copy())
                # attach the new turn to the previous turn
                next_job.attach(state)
            else:
                raise ValueError('Expected an unsimulated state or some kind of'
                                 'end of turn transition in the job stack but'
                                 'found: {}'.format(next_job))

            # # # # # # # # # # # # # # # # # # # # # # # # # # #
            #  Begin atomic changes
            # # # # # # # # # # # # # # # # # # # # # # # # # # #

            # handle states that are ready but have no actions remaining
            if state.actions_remaining <= 0:
                # determine if this is a manadrain or just end of turn
                is_manadrain = True
                for swap_pair in state.board.potential_swaps():
                    result_board, destroyed_groups = \
                        state.board.execute_once(swap=swap_pair,
                                                 random_fill=self._random_fill)
                    if destroyed_groups:
                        is_manadrain = False
                        break  # stop when the first valid swap found
                # attach appropriate EOT or ManaDrain
                if is_manadrain:
                    end = ManaDrain()
                else:
                    end = EOT()
                    ready_for_action_stack.append(end)
                state.attach(end)
                yield end
                continue  # no further simulation for this state
            # handle swaps
            for swap_pair in state.board.potential_swaps():
                result_board, destroyed_groups = \
                    state.board.execute_once(swap=swap_pair,
                                             random_fill=self._random_fill)
                if not destroyed_groups:
                    continue  # discard this swap if it was invalid
                # attach the transition
                swap = Swap(swap_pair)
                state.attach(swap)
                # attach the result state
                bonus_action = any(len(group) >= 4
                                   for group in destroyed_groups)
                used_bonus_action = False
                if bonus_action:
                    used_bonus_action = True
                result_state = self.__class__(board=result_board,
                                              turn=state.turn,
                                              actions_remaining=
                                              state.actions_remaining
                                              - 1 + bonus_action,
                                              player=state.player.copy(),
                                              opponent=state.opponent.copy())
                # update the player and opponent
                base_attack = \
                    result_state.active.apply_tile_groups(destroyed_groups)
                result_state.passive.apply_attack(base_attack)
                swap.attach(result_state)
                # hook for capture game optimizations. does nothing in base
                if self._disallow_state(state):
                    filtered = Filtered()
                    result_state.attach(filtered)
                    continue  # no more simulation for this filtered state
                # handle any chain reactions
                potential_chain = result_state
                while potential_chain:
                    result_board, destroyed_groups = \
                        potential_chain.board.execute_once(random_fill=
                                                           self._random_fill)
                    # when chain reaction is done, submit it to the job stack
                    if not destroyed_groups:
                        # hook for capture game optimizations. no effect in base
                        if self._disallow_state(potential_chain):
                            filtered = Filtered()
                            potential_chain.attach(filtered)
                            break  # no more simulation for this filtered state
                        ready_for_action_stack.append(potential_chain)
                        break
                    # attach the transition
                    chain = ChainReaction()
                    potential_chain.attach(chain)
                    # attach the result state
                    if used_bonus_action:
                        bonus_action = 0
                    else:
                        bonus_action = any(len(group) >= 4
                                           for group in destroyed_groups)
                        used_bonus_action = True
                    result_state = \
                        self.__class__(board=result_board,
                                       turn=potential_chain.turn,
                                       actions_remaining=
                                       potential_chain.actions_remaining
                                       + bonus_action,
                                       player=potential_chain.player.copy(),
                                       opponent=potential_chain.opponent.copy())
                    # update the player and opponent
                    base_attack = \
                        result_state.active.apply_tile_groups(destroyed_groups)
                    result_state.passive.apply_attack(base_attack)
                    chain.attach(result_state)
                    # prepare to try for another chain reaction
                    potential_chain = result_state
            #at this point all swaps have been tried
            #if nothing was valid, it's a manadrain
            if not tuple(state.children()):
                manadrain = ManaDrain()
                state.attach(manadrain)
                yield manadrain  # manadrain is a type of end of turn
                continue  # no further simulation for this state
            # handle spells only if this was not a manadrain
            pass
            # # # # # # # # # # # # # # # # # # # # # # # # # # #
            #  End atomic changes
            # # # # # # # # # # # # # # # # # # # # # # # # # # #

    def _disallow_state(self, state):
        return False

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
        self._node = _SimNode(main=self)

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
        try:
            return self._node.parent.main
        except AttributeError:  # no parent
            return None


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
    def __init__(self, alternative_name=None):
        name = alternative_name or 'end of turn'
        super(EOT, self).__init__(name)


class ManaDrain(EOT):
    def __init__(self):
        super(ManaDrain, self).__init__('mana drain')


class Filtered(_Transition):
    def __init__(self):
        super(Filtered, self).__init__('filtered')


class _SimNode(TreeNode):
    """Provide node behavior for States and Transitions."""
    def __init__(self, main):
        super(_SimNode, self).__init__(main=main)


if __name__ == "__main__":
    pass
