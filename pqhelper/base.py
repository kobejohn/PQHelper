import random

import numpy

from treenode import TreeNode


class Game(object):
    """Simulates the possibilities of a PQ game."""
    # Initialization and core attributes
    def __init__(self, use_random_fill):
        """Initialize a new game simulation container.

        Arguments:
        use_random_fill: True/False indicating to randomly fill boards or not.
        """
        self.random_fill = use_random_fill

    # Run simulation
    def ends_of_turn(self, root=None, root_eot=None):
        """Simulate a complete turn and generate each end of turn reached in
        the simulation.

        Arguments:
        Exactly one of:
            root: a start state with no parent
            or
            root_eot: an EOT or ManaDrain transition in the simulation
        """
        # basic confirmation of valid arguments
        self._argument_gauntlet(root_eot, root)
        # setup the starting state
        if root:
            start_state = root
        else:
            start_state = State(root_eot.parent.board.copy(),
                                root_eot.parent.player.copy(),
                                root_eot.parent.opponent.copy(),
                                root_eot.parent.turn + 1, 1)
            root_eot.graft_child(start_state)
        # track states that are stable - i.e. no remaining chain reactions
        ready_for_action = [start_state]
        # simulate all actions for each state until reaching EOTs
        while ready_for_action:
            ready_state = ready_for_action.pop()
            # handle states that have run out of actions (end of turn)
            if ready_state.actions_remaining <= 0:
                root_eot = self._simulated_EOT(ready_state)
                yield root_eot
                continue  # no more simulation for an EOT
            # handle swaps when there are actions remaining
            for swap_result in self._simulated_swap_results(ready_state):
                # handle any chain reactions
                if swap_result.actions_remaining \
                        >= ready_state.actions_remaining:
                    already_used_bonus = True
                else:
                    already_used_bonus = False
                chain_result = self._simulated_chain_result(swap_result,
                                                            already_used_bonus)
                # chain results may be filtered so test first
                if chain_result:
                    ready_for_action.append(chain_result)
            #at this point all swaps have been tried
            #if nothing was valid, it's a manadrain
            if not tuple(ready_state.children):
                mana_drain_eot = self._simulated_mana_drain(ready_state)
                yield mana_drain_eot
                continue
            # if something was valid, now spells can be simulated
            else:
                pass

    # Internal methods
    def _argument_gauntlet(self, eot, root):
        # confirm exactly one argument received
        if (root and eot) or (not root and not eot):
            raise TypeError('Provide exactly one of root or eot')
        # confirm root looks like a real root
        if root and root.parent is not None:
            raise ValueError('Received something for root that does not seem to'
                             ' be a root state:\n{}'.format(root))
        # confirm eot looks like a real eot
        if eot and not isinstance(eot, EOT):
            raise TypeError('Received something for eot that does not seem to'
                            ' be an EOT transition:\n{}'.format(eot))

    def _simulated_swap_results(self, stable_state):
        for swap_pair in stable_state.board.potential_swaps():
            result_board, destroyed_groups = \
                stable_state.board.execute_once(swap=swap_pair,
                                                random_fill=self.random_fill)
            # ignore invalid swaps
            if not destroyed_groups:
                continue  # discard this swap if it was invalid
            # attach valid swap and result state
            swap = Swap(swap_pair)
            stable_state.graft_child(swap)
            bonus_action = any(len(group) >= 4
                               for group in destroyed_groups)
            cls = stable_state.__class__
            result_state = cls(board=result_board,
                               turn=stable_state.turn,
                               actions_remaining=
                               stable_state.actions_remaining
                               - 1 + bonus_action,
                               player=stable_state.player.copy(),
                               opponent=stable_state.opponent.copy())
            # update the player and opponent
            attack = \
                result_state.active.apply_tile_groups(destroyed_groups)
            result_state.passive.apply_attack(attack)
            swap.graft_child(result_state)
            # hook for capture game optimizations. does nothing in base
            if self._disallow_state(result_state):
                result_state.graft_child(Filtered())
                continue  # no more simulation for this filtered state
            yield result_state

    def _simulated_chain_result(self, potential_chain, already_used_bonus):
        """Simulate any chain reactions.

        Arguments:
        potential_chain: a state to be tested for chain reactions
        already_used_bonus: boolean indicating whether a bonus turn was already
            applied during this action

        Return: final result state or None (if state is filtered out in capture)

        Note that if there is no chain reaction, the final result is the
        same as the original state received.
        """
        while potential_chain:
            result_board, destroyed_groups = \
                potential_chain.board.execute_once(random_fill=
                                                   self.random_fill)
            # yield the state if nothing happened during execution (chain done)
            if not destroyed_groups:
                # hook for capture game optimizations. no effect in base
                if self._disallow_state(potential_chain):
                    potential_chain.graft_child(Filtered())
                    return None  # no more simulation for this filtered state
                # yield this state as the final result of the chain
                return potential_chain
            # attach the transition
            chain = ChainReaction()
            potential_chain.graft_child(chain)
            # attach the result state
            if already_used_bonus:
                # disallow bonus action if already applied
                bonus_action = 0
            else:
                # allow bonus action once and then flag as used
                bonus_action = any(len(group) >= 4
                                   for group in destroyed_groups)
                already_used_bonus = True
            cls = potential_chain.__class__
            chain_result = cls(board=result_board,
                               turn=potential_chain.turn,
                               actions_remaining=
                               potential_chain.actions_remaining + bonus_action,
                               player=potential_chain.player.copy(),
                               opponent=potential_chain.opponent.copy())
            # update the player and opponent
            base_attack = \
                chain_result.active.apply_tile_groups(destroyed_groups)
            chain_result.passive.apply_attack(base_attack)
            chain.graft_child(chain_result)
            # prepare to try for another chain reaction
            potential_chain = chain_result

    def _disallow_state(self, state):
        """Hook for capture game optimizations."""
        if state:
            pass  # just to satisfy my IDE. sorry.
        return False

    def _simulated_EOT(self, state):
        """Simulate a normal or mana drain EOT and return it."""
        # determine if this is a manadrain or just end of turn
        is_manadrain = True  # default mana drain until valid swap found
        for swap_pair in state.board.potential_swaps():
            result_board, destroyed_groups = \
                state.board.execute_once(swap=swap_pair,
                                         random_fill=self.random_fill)
            if destroyed_groups:
                is_manadrain = False
                break  # stop when the first valid swap found
        # attach appropriate EOT or ManaDrain
        if is_manadrain:
            end = self._simulated_mana_drain(state)
        else:
            end = EOT(False)
            state.graft_child(end)
        return end

    def _simulated_mana_drain(self, mana_drain_state):
        """Apply mana drain effects to this state, attach a mana drain EOT
        and return the mana drain EOT."""
        # clear all mana
        mana_drain_state.player.apply_mana_drain()
        mana_drain_state.opponent.apply_mana_drain()
        # force change of turn
        mana_drain_state.actions_remaining = 0
        # randomize the board if this game uses random fill
        if self.random_fill:
            random_start_board = mana_drain_state.board.random_start_board()
            mana_drain_state.board = random_start_board
        # attach the mana drain EOT
        mana_drain = EOT(True)
        mana_drain_state.graft_child(mana_drain)
        return mana_drain


class Tile(object):
    """Behaves like a PQ Tile."""
    _all_types = ('r', 'g', 'b', 'y',  # colors
                  's', '*',            # skulls
                  'x', 'm', '.',       # experience, money, blank
                  'h', 'c',            # anvil(h), scroll(c)
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
                'h': ('h',),
                'c': ('c',),
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

    # distribution used to generate a random tile
    # keep computation simple by having no random skullbombs, wildcards, special
    _random_weights = {'r': 2,
                       'g': 2,
                       'b': 2,
                       'y': 2,
                       's': 2,
                       'x': 2,
                       'm': 2}
    _random_distribution = list()
    for __tile_type, __weight in _random_weights.items():
        _random_distribution += (__tile_type,) * __weight

    # storage for class singletons
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

    def is_skull(self):
        return True if self._type == 's' else False

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
    def __init__(self, board_string=None):
        # setup the core ndarray that stores the 8x8 grid of tiles
        grid_shape = (8, 8)
        self._array = numpy.ndarray(shape=grid_shape, dtype=object)
        if board_string is None:
            blank = Tile.singleton('.')
            self._array.fill(blank)
        else:
            board_string = board_string.strip()
            for row, row_string in enumerate(board_string.split()):
                row_string = row_string.strip()
                for col, tile_character in enumerate(row_string):
                    self._array[row, col] = Tile.singleton(tile_character)

    # Class methods
    @classmethod
    def random_start_board(cls):
        """Produce a full, stable start board with random tiles."""
        board = cls()
        board._random_fill()
        destructions = True  # prime the loop
        while destructions:
            board, destructions = board.execute_once()
            board._random_fill()
        return board

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
        blank = Tile.singleton('.')
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

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        """Equal only when all tiles in self and other are equal."""
        return numpy.all(self._array == other._array)

    def __ne__(self, other):
        return not self.__eq__(other)

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
    def __init__(self, name, health, r, g, b, y, x, m, h, c):
        """Provide current and max as a tuple for each of health, etc."""
        self.name = name
        self._health, self.health_max = health
        self._r, self.r_max = r
        self._g, self.g_max = g
        self._b, self.b_max = b
        self._y, self.y_max = y
        self._x, self.x_max = x
        self._m, self.m_max = m
        self._h, self.h_max = h
        self._c, self.c_max = c

    def copy(self):
        """Return a copy of this actor with the same attribute values."""
        health = self.health, self.health_max
        r = self.r, self.r_max
        g = self.g, self.g_max
        b = self.b, self.b_max
        y = self.y, self.y_max
        x = self.x, self.x_max
        m = self.m, self.m_max
        h = self.h, self.h_max
        c = self.c, self.c_max
        return self.__class__(self.name, health, r, g, b, y, x, m, h, c)

    def apply_mana_drain(self):
        """Clear current mana values."""
        self.r = self.g = self.b = self.y = 0

    def apply_tile_groups(self, tile_groups):
        """Increase mana, xp, money, anvils and scrolls based on tile groups."""
        self_increase_types = ('r', 'g', 'b', 'y', 'x', 'm', 'h', 'c')
        attack_types = ('s', '*')
        total_attack = 0
        for tile_group in tile_groups:
            group_type = None
            type_count = 0
            type_multiplier = 1
            for tile in tile_group:
                # try to get the group type
                if not group_type:
                    # try to set the group type to a non-wildcard type
                    if tile._type in self_increase_types:
                        group_type = tile._type
                    elif tile._type in attack_types:
                        group_type = 's'  # always use base skull
                # handle special case of wildcard
                if tile.is_wildcard():
                    type_multiplier *= int(tile._type)
                    continue  # done with this tile
                # handle special case of skullbomb / skull
                elif tile.is_skullbomb():
                    total_attack += 5
                    continue
                elif tile.is_skull():
                    total_attack += 1
                    continue
                # handle standard case of normal tiles
                else:
                    type_count += 1
            # TypeError if no group type
            if group_type is None:
                raise TypeError('Could not determine the main type for this'
                                'group of tiles: {}'.format(tile_group))
            # adjust self value
            if type_count:
                new_value = type_count * type_multiplier
                original = getattr(self, group_type)
                setattr(self, group_type, original + new_value)
        # return any attack value
        return total_attack

    def apply_attack(self, attack_value):
        """Apply the attack to health."""
        self.health -= attack_value

    def __limit_range(self, value, minimum, maximum):
        return max(minimum, min(maximum, value))

    @property
    def health(self):
        return self._health

    @health.setter
    def health(self, value):
        self._health = self.__limit_range(value, 0, self.health_max)

    @property
    def r(self):
        return self._r

    @r.setter
    def r(self, value):
        self._r = self.__limit_range(value, 0, self.r_max)

    @property
    def g(self):
        return self._g

    @g.setter
    def g(self, value):
        self._g = self.__limit_range(value, 0, self.g_max)

    @property
    def b(self):
        return self._b

    @b.setter
    def b(self, value):
        self._b = self.__limit_range(value, 0, self.b_max)

    @property
    def y(self):
        return self._y

    @y.setter
    def y(self, value):
        self._y = self.__limit_range(value, 0, self.y_max)

    @property
    def x(self):
        return self._x

    @x.setter
    def x(self, value):
        self._x = self.__limit_range(value, 0, self.x_max)

    @property
    def m(self):
        return self._m

    @m.setter
    def m(self, value):
        self._m = self.__limit_range(value, 0, self.m_max)

    @property
    def h(self):
        return self._h

    @h.setter
    def h(self, value):
        self._h = self.__limit_range(value, 0, self.h_max)

    @property
    def c(self):
        return self._c

    @c.setter
    def c(self, value):
        self._c = self.__limit_range(value, 0, self.c_max)


class State(TreeNode):
    def __init__(self, board, player, opponent, turn, actions_remaining):
        super(State, self).__init__()
        self.board = board
        self.player = player
        self.opponent = opponent
        self.turn = turn
        self.actions_remaining = actions_remaining

    # Additional turn information
    @property
    def active(self):
        """Return player when turn is odd; opponent when even."""
        return self.player if self.turn % 2 else self.opponent

    @property
    def passive(self):
        """Return player when turn is even; opponent when odd."""
        return self.opponent if self.turn % 2 else self.player

    # Special methods
    def __str__(self):
        indent = ' ' * 4
        line_list = list()
        line_list.append('State:')
        line_list.append(indent + '{} : turn'.format(self.turn))
        line_list.append(indent + '{} : actions remaining'
                         ''.format(self.actions_remaining))
        line_list.append(indent + '{} : children'.format(len(self.children)))
        line_list.append(indent + 'board:')
        line_list.extend(indent + indent + line for line
                         in str(self.board).splitlines())
        return '\n    '.join(line_list)

    def __repr__(self):
        return str(self)


# Transitions
class BaseTransition(TreeNode):
    def __str__(self):
        parts = str(self.__class__).split('.')
        class_name = parts[-1][:-2]
        children = ' (children: {})'.format(len(self.children))
        return class_name + children

    def __repr__(self):
        return self.__str__()


class Swap(BaseTransition):
    def __init__(self, position_pair):
        super(Swap, self).__init__()
        self._position_pair = position_pair

    def __str__(self):
        base = super(Swap, self).__str__()
        return base + ': {}'.format(self._position_pair)

    @property
    def position_pair(self):
        return self._position_pair


class ChainReaction(BaseTransition):
    pass


class EOT(BaseTransition):
    def __init__(self, is_mana_drain):
        super(EOT, self).__init__()
        self.is_mana_drain = is_mana_drain

    def __str__(self):
        s = super(EOT, self).__str__()
        if self.is_mana_drain:
            s += ' (mana drain)'
        return s


class Filtered(BaseTransition):
    pass


if __name__ == "__main__":
    pass
