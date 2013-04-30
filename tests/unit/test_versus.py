import unittest
from mock import patch

from pqhelper.versus import realistic_choices, _summarize_eot
from pqhelper.versus import _score_eot, _summarize_root_action
from pqhelper.versus import _create_simulation_root, _expand_simulation


class Test_Scoring(unittest.TestCase):
    @patch('pqhelper.versus._State._random_fill', False)
    def setUp(self):
        # run a short simulation for testing; 6 leaves
        self.board_string_3_valid_swaps = '........\n' \
                                          '........\n' \
                                          '........\n' \
                                          '........\n' \
                                          '........\n' \
                                          'r..g..b.\n' \
                                          'r..g..b.\n' \
                                          'xr.xg.xb'
        self.root = _create_simulation_root(self.board_string_3_valid_swaps)

    def test_realistic_choices_returns_an_empty_sequence_for_root_only(self):
        choices = realistic_choices(self.root)
        self.assertSequenceEqual(choices, tuple())

    def test_realistic_choices_has_3_results(self):
        _expand_simulation(self.root, 1)
        choices = realistic_choices(self.root)
        self.assertEqual(len(choices), 3)

    def test__summarize_eot_provides_required_items(self):
        # Combined specification for simplicity
        _expand_simulation(self.root, 1)
        any_leaf = self.root._node.leaves.next().main
        summary = _summarize_eot(any_leaf)
        # confirm overall score
        keys_spec = ('overall_score', 'root_action')
        self.assertItemsEqual(summary.keys(), keys_spec)

    def test__score_eot_with_default_actors_scores_positive_for_1_turn(self):
        one_turn = 1
        _expand_simulation(self.root, one_turn)
        any_leaf = self.root._node.leaves.next().main
        score = _score_eot(any_leaf)
        self.assertGreater(score, 0)

    def test__score_eot_with_default_actors_scores_zero_for_2_turns(self):
        # default actors have same preferences so 3 of any color
        two_turns = 2
        _expand_simulation(self.root, two_turns)
        any_leaf = self.root._node.leaves.next().main
        score = _score_eot(any_leaf)
        self.assertEqual(score, 0)

    def test__summarize_root_action_returns_one_of_valid_swap_pairs(self):
        _expand_simulation(self.root, 1)
        any_leaf = self.root._node.leaves.next().main
        root_action_summary = _summarize_root_action(any_leaf)
        # confirm the type of the root action
        self.assertEqual(root_action_summary['type'], 'swap')
        # confirm the swap is one of the valid swaps
        valid_swap_pairs_spec = (((7, 0), (7, 1)),
                                 ((7, 3), (7, 4)),
                                 ((7, 6), (7, 7)))
        self.assertIn(root_action_summary['details'], valid_swap_pairs_spec)


class Test_Simulation(unittest.TestCase):
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
