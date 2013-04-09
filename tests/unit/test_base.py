import unittest

from pqhelper.base import Board, Tile


class Test_Base_Board(unittest.TestCase):
    # all_swaps --> list of changes representing all swaps on a board
    # execute_with_chainreactions(changes, destructions) --> total destroyed groups
    # _execute_once(changes = None, destructions = None) --> total destroyed groups
    # _apply changes (not groups)
    # _apply destructions (not groups) --> total destroyed groups
    # _match

    # Test Parameters
    _board_string_all_tiles = 'rgby....\n' \
                              '.xm.....\n' \
                              '..234567\n' \
                              '89......\n' \
                              '.s*.....\n' \
                              '........\n' \
                              '........\n' \
                              '........'

    _board_string_chain_reaction = '..*.....\n' \
                                   '...*....\n' \
                                   '....*...\n' \
                                   '.....*..\n' \
                                   '......*.\n' \
                                   '.......*\n' \
                                   '....gb*.\n' \
                                   '....r*y.'

    # Instance creation
    def test___init___default_is_empty_board(self):
        b = Board()
        self.assertTrue(b.is_empty())

    def test___init___with_a_board_string_of_8x8_with_EOLs_works(self):
        b = Board(self._board_string_all_tiles)
        self.assertEqual(str(b), self._board_string_all_tiles)

    # Indexing and Shape of grid
    def test_indexing_works_for_grid_of_8_rows_and_8_columns(self):
        b = Board()
        test_tile = Tile('r')
        for row in range(8):
            for col in range(8):
                try:
                    b[row][col] = test_tile  # test writing
                    actual_tile = b[row][col]  # test reading
                except Exception as e:
                    self.fail('Indexing of row {} and column {} should have '
                              'worked but an error occured: {}'.format(row, col,
                                                                       e))
                self.assertIs(actual_tile, test_tile)

    def test_tuple_indexing_also_works(self):
        b = Board()
        test_tile = Tile('r')
        coordinate_tuple = (2, 2)
        try:
            b[coordinate_tuple] = test_tile
            actual_tile = b[coordinate_tuple]
        except Exception as e:
            self.fail('Indexing with the coordinate tuple {} should have '
                      'worked but an error occured: {}'.format(coordinate_tuple,
                                                               e))
        self.assertIs(actual_tile, test_tile)

    def test_indexing_outside_the_8x8_array_raises_IndexError(self):
        b = Board()
        bad_coordinate = (8, 7)
        self.assertRaises(IndexError, b.__getitem__, bad_coordinate)

    # Execution (core behavior)
    def test__destroy_empty_target_groups_returns_empty_destroyed_groups(self):
        b = Board(self._board_string_all_tiles)
        empty_position_groups = list()
        destroyed_tile_groups = b._destroy(empty_position_groups)
        no_destroyed_tile_groups = list()
        self.assertItemsEqual(destroyed_tile_groups, no_destroyed_tile_groups,
                              'Expected to find no destroyed tile groups but'
                              ' got {}'.format(no_destroyed_tile_groups))

    def test__destroy_simple_target_group_returns_same_destroyed_group(self):
        b = Board(self._board_string_all_tiles)
        simple_position_group = [(0, 0), (0, 1), (0, 2), (0, 3)]  # top row
        simple_position_groups = [simple_position_group]
        destroyed_tile_groups = b._destroy(simple_position_groups)
        destroyed_tile_group_spec = [Tile('r'), Tile('g'), Tile('b'), Tile('y')]
        destroyed_tile_groups_spec = [destroyed_tile_group_spec]
        self.assertItemsEqual(destroyed_tile_groups, destroyed_tile_groups_spec,
                              'Expected to find these destroyed groups:\n{}'
                              '\nbut found:'
                              '{}'.format(destroyed_tile_groups_spec,
                                          destroyed_tile_groups))

    def test__destroy_simple_target_group_destroys_exactly_targets(self):
        b = Board(self._board_string_all_tiles)
        simple_position_group = [(0, 0), (0, 1), (0, 2), (0, 3)]  # top row
        simple_position_groups = [simple_position_group]
        # Confirm first that the positions are not empty
        for position in simple_position_group:
            self.assertFalse(b[position].is_blank(),
                             'Expected position {} not to be blank before'
                             ' destruction but found blank.'.format(position))
        # Run destroy
        b._destroy(simple_position_groups)
        # Confirm after that the positions are now empty
        for position in simple_position_group:
            self.assertTrue(b[position].is_blank(),
                            'Expected position {} to be blank after'
                            ' destruction but found ({})'.format(position,
                                                                 b[position]))

    def test__destroy_skullbomb_chain_reaction_returns_tiles_separately(self):
        board = Board(self._board_string_chain_reaction)
        mid_chain_position_group = [(5, 7)]  # middle of skullbomb chain
        mid_chain_position_groups = [mid_chain_position_group]
        sb, r, g, b, y = Tile('*'), Tile('r'), Tile('g'), Tile('b'), Tile('y')
        destroyed_tile_groups_spec = [[sb]] * 8 + [[r], [g], [b], [y]]
        destroyed_tile_groups = board._destroy(mid_chain_position_groups)
        self.assertItemsEqual(destroyed_tile_groups, destroyed_tile_groups_spec,
                              'Expected to see all appropriate tiles in'
                              'separate groups like this:\n{}'
                              '\nbut found this:'
                              '\n{}'.format(destroyed_tile_groups_spec,
                                            destroyed_tile_groups))

    def test__destroy_skullbomb_chain_reaction_destroys_around_skullbombs(self):
        b = Board(self._board_string_chain_reaction)
        mid_chain_position_group = [(5, 7)]  # middle of skullbomb chain
        mid_chain_position_groups = [mid_chain_position_group]
        b._destroy(mid_chain_position_groups)
        self.assertTrue(b.is_empty(),
                        'Expected skullbomb chain reaction to destroy'
                        ' everything on this board:\n{}\nbut got this'
                        ' result:\n{}'.format(self._board_string_chain_reaction,
                                              str(b)))

    def test__fall_moves_tiles_down_as_far_as_possible(self):
        b = Board(self._board_string_all_tiles)
        b._fall()
        _board_string_all_tiles_fallen = '........\n' \
                                         '........\n' \
                                         '........\n' \
                                         '........\n' \
                                         '.gb.....\n' \
                                         '.xm.....\n' \
                                         'r92y....\n' \
                                         '8s*34567'
        self.assertEqual(str(b), _board_string_all_tiles_fallen,
                         'Expected these tiles:\n{}'
                         '\nto fall to the bottom like this:'
                         '\n{}\nbut got this:'
                         '\n{}'.format(self._board_string_all_tiles,
                                       _board_string_all_tiles_fallen,
                                       str(b)))

    # Convenience methods
    def test_positions_provides_8x8_positions_as_row_column_tuples(self):
        b = Board()
        positions_spec = list()
        for row in range(8):
            for col in range(8):
                positions_spec.append((row, col))
        positions = list(b.positions())
        self.assertItemsEqual(positions, positions_spec,
                              'Expected to get all possible coordinates in an'
                              '8x8 grid:\n{}\nbut got'
                              ' this:\n{}'.format(positions_spec, positions))

    def test_is_empty_is_True_when_all_tiles_are_blanks(self):
        blank = Tile('.')
        b = Board()
        # make sure all positions are blank
        for position in b.positions():
            b[position] = blank
        self.assertTrue(b.is_empty())

    def test_str_returns_8x8_lines_with_EOL_showing_type_for_each_tile(self):
        b = Board(self._board_string_all_tiles)
        self.assertEqual(str(b), self._board_string_all_tiles)


class Test_Base_Tile(unittest.TestCase):
    # Test Parameters
    _color_types_spec = ('r', 'g', 'b', 'y')
    _wildcard_types_spec = tuple(str(x) for x in range(2, 10))
    _skull_types_spec = ('s', '*')
    _unique_types_spec = ('x', 'm')
    _blank_type_spec = '.'
    _nonblank_types_spec = \
        _color_types_spec +\
        _wildcard_types_spec +\
        _skull_types_spec +\
        _unique_types_spec
    _all_types_spec = _nonblank_types_spec + (_blank_type_spec,)

    # Class attributes
    def test_base_valid_tile_types_are_exactly_specified_types(self):
        self.assertItemsEqual(Tile._all_types, self._all_types_spec)

    # Special methods
    def test_str_returns_the_type_character(self):
        for tile_type in self._all_types_spec:
            tile = Tile(tile_type)
            self.assertEqual(tile_type, str(tile))

    def test___eq___returns_True_for_same_tile_type_only(self):
        for tile_type in self._all_types_spec:
            tile = Tile(tile_type)
            for other_tile_type in self._all_types_spec:
                other_tile = Tile(other_tile_type)
                if tile._type == other_tile._type:
                    self.assertTrue(tile == other_tile)
                else:
                    self.assertFalse(tile == other_tile)

    def test___ne___returns_False_for_same_tile_type_only(self):
        for tile_type in self._all_types_spec:
            tile = Tile(tile_type)
            for other_tile_type in self._all_types_spec:
                other_tile = Tile(other_tile_type)
                if tile._type == other_tile._type:
                    self.assertFalse(tile != other_tile)
                else:
                    self.assertTrue(tile != other_tile)

    # Instance creation
    def test___init___from_all_types_works(self):
        for all_type in self._all_types_spec:
            try:
                Tile(all_type)
            except Exception as e:
                self.fail('Unexpectedly failed to create a tile with "{0}"'
                          ' with error: {1}'.format(all_type, e))

    def test___init___from_non_allowed_type_raises_ValueError(self):
        inall_type = 'z'
        self.assertTrue(inall_type not in self._all_types_spec,
                        'Specification is using a valid character to test'
                        'invalid characters. Please fix the spec.')
        self.assertRaises(ValueError, Tile, inall_type)

    # Matching
    def test_matches_for_blank_is_False_for_all_types_including_blank(self):
        blank = Tile('.')
        for other_type in self._all_types_spec:
            other = Tile(other_type)
            self.assertFalse(blank.matches(other))

    def test_matches_for_color_is_True_for_same_color_and_wildcards_only(self):
        # Combined test for ease of understanding the specification
        # For each color, confirm same color True, wildcards True, others False
        for color_type in self._color_types_spec:
            color = Tile(color_type)
            for other_type in self._all_types_spec:
                other = Tile(other_type)
                if other_type == color_type:
                    self.assertTrue(color.matches(other),
                                    'Color ({0}) should match itself'
                                    ' but does not.'.format(color_type,
                                                            other_type))
                elif other.is_wildcard():
                    self.assertTrue(color.matches(other),
                                    'Color ({0}) should match wildcard ({1})'
                                    ' but does not.'.format(color_type,
                                                            other_type))
                else:
                    self.assertFalse(color.matches(other),
                                     'Color ({0}) should not match other ({1})'
                                     ' but it does.'.format(color_type,
                                                            other_type))

    def test_matches_for_wildcard_is_True_for_colors_and_wildcards_only(self):
        # Combined test for ease of understanding the specification
        # For each wildcard, confirm colors True, wildcards True, others False
        for wildcard_type in self._wildcard_types_spec:
            wildcard = Tile(wildcard_type)
            for other_type in self._all_types_spec:
                other = Tile(other_type)
                if other.is_color():
                    self.assertTrue(wildcard.matches(other),
                                    'Wildcard ({0}) should match color ({1})'
                                    ' but does not.'.format(wildcard_type,
                                                            other_type))
                elif other.is_wildcard():
                    self.assertTrue(wildcard.matches(other),
                                    'Wildcard ({0}) should match wildcard ({1})'
                                    ' but does not.'.format(wildcard_type,
                                                            other_type))
                else:
                    self.assertFalse(wildcard.matches(other),
                                     'Wildcard ({0}) should not match other'
                                     ' ({1}) but it does.'.format(wildcard_type,
                                                                  other_type))

    def test_matches_for_skull_is_True_for_skulls_and_skullbombs_only(self):
        # Combined test for ease of understanding the specification
        skull_type = 's'
        skull = Tile(skull_type)
        for other_type in self._all_types_spec:
            other = Tile(other_type)
            if other_type == skull_type:
                self.assertTrue(skull.matches(other),
                                'Skull should match itself but does not.')
            elif other.is_skullbomb():
                self.assertTrue(skull.matches(other),
                                'Skull should match skullbomb but does not.')
            else:
                self.assertFalse(skull.matches(other),
                                 'Skull should not match other ({0}) but'
                                 ' does.'.format(other_type))

    def test_matches_for_skullbomb_is_True_for_skulls_and_skullbombs_only(self):
        # Combined test for ease of understanding the specification
        skull_type = 's'
        skullbomb_type = '*'
        skullbomb = Tile(skullbomb_type)
        for other_type in self._all_types_spec:
            other = Tile(other_type)
            if other_type == skull_type:
                self.assertTrue(skullbomb.matches(other),
                                'Skullbomb should match skull but does not.')
            elif other.is_skullbomb():
                self.assertTrue(skullbomb.matches(other),
                                'Skullbomb should match itself but does not.')
            else:
                self.assertFalse(skullbomb.matches(other),
                                 'Skullbomb should not match other ({0}) but'
                                 ' does.'.format(other_type))

    def test_matches_for_experience_is_True_for_experience_only(self):
        experience_type = 'x'
        experience = Tile(experience_type)
        for other_type in self._all_types_spec:
            other = Tile(other_type)
            if other_type == experience_type:
                self.assertTrue(experience.matches(other),
                                'Experience should match itself but does not.')
            else:
                self.assertFalse(experience.matches(other),
                                 'Experience should not match other ({0})'
                                 ' but does.'.format(other_type))
                
    def test_matches_for_money_is_True_for_money_only(self):
        money_type = 'm'
        money = Tile(money_type)
        for other_type in self._all_types_spec:
            other = Tile(other_type)
            if other_type == money_type:
                self.assertTrue(money.matches(other),
                                'money should match itself but does not.')
            else:
                self.assertFalse(money.matches(other),
                                 'money should not match other ({0})'
                                 ' but does.'.format(other_type))

    # Convenient methods
    def test_is_skullbomb_for_a_skullbomb_returns_True(self):
        skullbomb = Tile('*')
        self.assertTrue(skullbomb.is_skullbomb())

    def test_is_skullbomb_for_a_non_skullbomb_returns_False(self):
        skull = Tile('s')
        self.assertFalse(skull.is_skullbomb())

    def test_is_blank_for_a_blank_returns_True(self):
        blank = Tile('.')
        self.assertTrue(blank.is_blank())

    def test_is_blank_for_a_non_blank_returns_False(self):
        skull = Tile('s')
        self.assertFalse(skull.is_blank())

    def test_is_wildcard_for_a_wildcard_returns_True(self):
        wildcards = (Tile(str(x)) for x in range(2, 10))
        for wildcard in wildcards:
            self.assertTrue(wildcard.is_wildcard())

    def test_is_wildcard_for_a_non_wildcard_returns_False(self):
        skull = Tile('s')
        self.assertFalse(skull.is_wildcard())

    def test_is_color_for_a_color_returns_True(self):
        colors = (Tile(c) for c in ('r', 'g', 'b', 'y'))
        for color in colors:
            self.assertTrue(color.is_color())

    def test_is_color_for_a_non_color_returns_False(self):
        skull = Tile('s')
        self.assertFalse(skull.is_color())


if __name__ == '__main__':
    unittest.main()
