import unittest
from mock import patch

from pqhelper.versus import _create_simulation_root, _expand_simulation


class Test_simulation(unittest.TestCase):
    # Test attributes
    board_string_3_valid_swaps = '........\n' \
                                 '........\n' \
                                 '........\n' \
                                 '........\n' \
                                 '........\n' \
                                 'r..g..b.\n' \
                                 'r..g..b.\n' \
                                 'xr.xg.xb'

    def test__create_simulation_root_returns_a_disconnected_state(self):
        root = _create_simulation_root(self.board_string_3_valid_swaps)
        self.assertFalse(root.parent)
        self.assertFalse(list(root.children()))

    def test__create_simulation_root_accepts_optional_player_and_opponent(self):
        try:
            _create_simulation_root(self.board_string_3_valid_swaps,
                                    player_string='player',
                                    opponent_string='opponent')
        except Exception as e:
            self.fail('Expected creation with player and opponent strings'
                      ' to work but got this exception:\n{}'.format(e))

    @patch('pqhelper.versus._State._random_fill', False)
    def test__expand_simulation_adds_3_actions_to_root(self):
        root = _create_simulation_root(self.board_string_3_valid_swaps)
        _expand_simulation(root, turns=1)
        self.assertEqual(len(tuple(root.children())), 3)

    @patch('pqhelper.versus._State._random_fill', False)
    def test__expand_simulation_results_in_all_leaves_within_turn_limit(self):
        turn_limit = 2
        root = _create_simulation_root(self.board_string_3_valid_swaps)
        _expand_simulation(root, turn_limit)
        leaves = tuple(leaf.main for leaf in root._node.leaves)
        for leaf in leaves:
            state = leaf.parent
            self.assertLessEqual(state.turn, turn_limit)

    @patch('pqhelper.versus._State._random_fill', False)
    def test__expand_simulation_completes_turns_up_to_turn_limit(self):
        turn_limit = 2
        root = _create_simulation_root(self.board_string_3_valid_swaps)
        _expand_simulation(root, turn_limit)
        leaves = tuple(leaf.main for leaf in root._node.leaves)
        # confirm expected number of leaves (3 actions first * 2 actions each)
        number_of_possibilities_after_2_turns = 3 * 2
        self.assertEqual(len(leaves), number_of_possibilities_after_2_turns)


if __name__ == '__main__':
    unittest.main()
