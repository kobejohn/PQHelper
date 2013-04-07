import unittest

from pqhelper.base import Tile


class Test_Base_Tile(unittest.TestCase):
    # Parameters
    _color_types_spec = ('r', 'g', 'b', 'y')
    _wildcard_types_spec = tuple(str(x) for x in range(2, 10))
    _skull_types_spec = ('s', '*')
    _unique_types_spec = ('x', 'm')
    _blank_type_spec = '.'
    _nonblank_types_spec = _color_types_spec + _wildcard_types_spec +\
                           _skull_types_spec + _unique_types_spec
    _all_types_spec = _nonblank_types_spec + (_blank_type_spec,)

    # Class attributes
    def test_base_valid_tile_types_are_exactly_specified_types(self):
        self.assertItemsEqual(Tile._all_types, self._all_types_spec)

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

    # Convenient type checkers
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
