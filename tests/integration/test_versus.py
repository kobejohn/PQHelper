import unittest

from pqhelper.base import State
from pqhelper.versus import Advisor, Board, Actor


class Test_Advisor(unittest.TestCase):
    # Common test data
    board_string_3_valid_swaps = '........\n' \
                                 '........\n' \
                                 '........\n' \
                                 '........\n' \
                                 '........\n' \
                                 '8..*..g.\n' \
                                 '8..s..g.\n' \
                                 'xr.xs.xg'

    # Attributes
    def test_current_completed_turn_is_get_only(self):
        advisor = Advisor()
        self.assertRaises(AttributeError,
                          setattr, *(advisor, 'current_completed_turn', 10))

    def test_current_completed_turn_is_zero_by_default(self):
        advisor = Advisor()
        self.assertEqual(advisor.current_completed_turn, 0)

    # Setup and Maintenance of the simulation
    def test_reset_sets_a_new_internal_root(self):
        advisor = Advisor()
        # patch the root to some value
        original_root = advisor._root = 'fake root'
        # confirm reset changes the root and it's not None
        advisor.reset(Board(),
                      generic_actor('player'), generic_actor('opponent'))
        self.assertIsNot(advisor._root, original_root,
                         'Unexpectedly found the same root after resetting:'
                         '\n{}'.format(original_root))
        self.assertIsNotNone(advisor._root,
                             'Unexpectedly found "None" as the root after'
                             ' resetting')

    def test_reset_sets_the_current_completed_turn_to_zero(self):
        advisor = Advisor()
        # set a fake original value
        advisor._current_completed_turn = 2
        advisor.reset(Board(),
                      generic_actor('player'), generic_actor('opponent'))
        # confirm reset of the current turn indicator
        completed_turn = advisor.current_completed_turn
        self.assertEqual(completed_turn, 0,
                         'Unexpectedly found {} instead of zero for the'
                         'current completed turn value after resetting'
                         'the advisor'.format(completed_turn))

    # Run the versus simulation one turn at a time
    def test_simulate_next_turn_produces_correct_tree_internally(self):
        advisor = generic_advisor(self.board_string_3_valid_swaps)
        # turn 1: 3 leaves
        advisor.simulate_next_turn()
        leaf_count = len(list(advisor._root.leaves))
        self.assertEqual(leaf_count, 3)
        # turn 2: 6 leaves
        advisor.simulate_next_turn()
        leaf_count = len(list(advisor._root.leaves))
        self.assertEqual(leaf_count, 6)

    def test_simulate_next_turn_increments_current_turn_if_simulated(self):
        board_string_two_moves = '........\n' \
                                 '........\n' \
                                 '........\n' \
                                 '........\n' \
                                 '........\n' \
                                 'r.....*.\n' \
                                 '3.....s.\n' \
                                 'xr....xs'
        advisor = generic_advisor(board_string_two_moves)
        # turn 0
        self.assertEqual(advisor.current_completed_turn, 0)
        # turn 1, 2: increments with simulation
        advisor.simulate_next_turn()
        self.assertEqual(advisor.current_completed_turn, 1)
        advisor.simulate_next_turn()
        self.assertEqual(advisor.current_completed_turn, 2)
        # turn 3: nothing to simulate so does not increment
        advisor.simulate_next_turn()
        self.assertEqual(advisor.current_completed_turn, 2)

    # Summaries: general
    def test_current_summaries_generates_empty_sequence_for_None_root(self):
        advisor = Advisor()
        advisor._root = None  # just to be sure
        summaries_for_None = list(advisor.sorted_current_summaries())
        empty_sequence = tuple()
        self.assertSequenceEqual(summaries_for_None, empty_sequence)

    # Summaries: action details
    def test_current_summaries_generates_correct_swap_choices(self):
        advisor = generic_advisor(self.board_string_3_valid_swaps)
        # sim and confirm chocies for turn 1
        advisor.simulate_next_turn()
        summaries_turn_1 = advisor.sorted_current_summaries()
        swaps_turn_1 = [summary['action'] for summary in summaries_turn_1]
        swaps_spec = (((7, 0), (7, 1)),
                      ((7, 3), (7, 4)),
                      ((7, 6), (7, 7)))
        self.assertItemsEqual(swaps_turn_1, swaps_spec,
                              'Unexpectedly received these swaps:\n{}\n'
                              'instead of the expected swaps:\n{}'
                              ''.format(swaps_turn_1, swaps_spec))

    def test_current_summaries_generates_same_choices_each_turn(self):
        advisor = generic_advisor(self.board_string_3_valid_swaps)
        # sim and store choices for turn 1
        advisor.simulate_next_turn()
        summaries_turn_1 = advisor.sorted_current_summaries()
        swaps_turn_1 = [summary['action'] for summary in summaries_turn_1]
        # sim and store choices for turn 2
        advisor.simulate_next_turn()
        summaries_turn_2 = advisor.sorted_current_summaries()
        swaps_turn_2 = [summary['action'] for summary in summaries_turn_2]
        # confirm the choices are the same between turn 1 and turn 2
        self.assertItemsEqual(swaps_turn_1, swaps_turn_2,
                              'Unexpectedly found different root choices'
                              'on turn 1:\n{}\nand turn 2:\n{}'
                              ''.format(swaps_turn_1, swaps_turn_2))

    # Summaries: scoring
    def test_current_summaries_generates_correct_scoring(self):
        surprise_board_string = '........\n' \
                                '........\n' \
                                '........\n' \
                                '........\n' \
                                '........\n' \
                                'r.....r.\n' \
                                '2.....r.\n' \
                                'sr.**.xr'
        flexible_value = (500, 1000)
        flexible_player = generic_actor(name='player',
                                        r=flexible_value,
                                        g=flexible_value,
                                        health=flexible_value)
        flexible_opponent = generic_actor(name='opponent',
                                          r=flexible_value,
                                          g=flexible_value,
                                          health=flexible_value)
        advisor = generic_advisor(board_string=surprise_board_string,
                                  player=flexible_player,
                                  opponent=flexible_opponent)
        left_swap = ((7, 0), (7, 1))
        right_swap = ((7, 6), (7, 7))
        # Simulate 1 turn and confirm relative scoring
        advisor.simulate_next_turn()
        # with only one turn simulated, 4 reds seems better than 3
        ordered_swaps_turn_1_spec = (left_swap,  # 4 reds 2 * (1 + 1)
                                     right_swap)  # 3 reds
        summaries_turn_1 = advisor.sorted_current_summaries()
        ordered_swaps_turn_1 = [summary['action']
                                for summary in summaries_turn_1]
        self.assertSequenceEqual(ordered_swaps_turn_1,
                                 ordered_swaps_turn_1_spec,
                                 'After turn 1, expected to get this order'
                                 ' of swaps based on the scoring:\n{}'
                                 '\nbut got this order:\n{}'
                                 ''.format(ordered_swaps_turn_1_spec,
                                           ordered_swaps_turn_1))
        # with two turns simulated, 4 reds actually opened up a great move
        # for the opponent. so the 3 red move is scored higher
        advisor.simulate_next_turn()
        ordered_swaps_turn_2_spec = (right_swap, left_swap)
        summaries_turn_2 = advisor.sorted_current_summaries()
        ordered_swaps_turn_2 = [summary['action']
                                for summary in summaries_turn_2]
        self.assertSequenceEqual(ordered_swaps_turn_2,
                                 ordered_swaps_turn_2_spec,
                                 'After turn 2, expected to get this order'
                                 ' of swaps based on the scoring:\n{}'
                                 '\nbut got this order:\n{}'
                                 ''.format(ordered_swaps_turn_2_spec,
                                           ordered_swaps_turn_2))

    def test_current_summaries_generates_different_scoring_each_turn(self):
        advisor = generic_advisor(self.board_string_3_valid_swaps)
        # sim and store scoring for turn 1
        advisor.simulate_next_turn()
        summaries_turn_1 = advisor.sorted_current_summaries()
        overalls_turn_1 = [summary['overall']
                           for summary in summaries_turn_1]
        # sim and store scoring for turn 2
        advisor.simulate_next_turn()
        summaries_turn_2 = advisor.sorted_current_summaries()
        overalls_turn_2 = [summary['overall']
                           for summary in summaries_turn_2]
        # confirm the scoring is different between turn 1 and turn 2
        items_were_equal = True
        try:
            self.assertItemsEqual(overalls_turn_1, overalls_turn_2)
        except AssertionError:
            items_were_equal = False  # ok! the items shouldn't be equal
        if items_were_equal:
            self.fail('Expected the scoring for different turns to be different'
                      'but got the same:\n{}'.format(overalls_turn_1))


def generic_advisor(board_string, player=None, opponent=None,
                    random_fill=False):
    advisor = Advisor()
    player = player or generic_actor('player')
    opponent = opponent or generic_actor('opponent')
    advisor.reset(Board(board_string), player, opponent)
    # patch the game not to do random fills
    advisor._game.random_fill = random_fill
    return advisor


def generic_actor(name=None, health=None,
                  r=None, g=None, b=None, y=None,
                  x=None, m=None, h=None, c=None):
    """Simple factory to keep tests focused."""
    base = (50, 100)
    health = health or base
    r = r or base
    g = g or base
    b = b or base
    y = y or base
    x = x or base
    m = m or base
    h = h or base
    c = c or base
    return Actor(name, health, r, g, b, y, x, m, h, c)


if __name__ == '__main__':
    unittest.main()
