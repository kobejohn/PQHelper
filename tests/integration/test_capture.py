import unittest

from pqhelper.base import Board, State, Actor
from pqhelper.capture import Game, capture


class Test_capture(unittest.TestCase):
    def test_capture_on_easy_board_returns_correct_solution(self):
        board_string = '........\n' \
                       '........\n' \
                       '........\n' \
                       '........\n' \
                       '.......x\n' \
                       '....xx.r\n' \
                       '....rr.r\n' \
                       '..rryyry'
        board = Board(board_string)
        solution = capture(board)
        solution_swaps = [summary.action for summary in solution]
        # confirm that the solution matches the specification
        solution_swaps_spec = (((7, 6), (7, 7)), ((7, 6), (7, 7)))
        self.assertSequenceEqual(solution_swaps, solution_swaps_spec,
                                 'Expected to get this solution:\n{}\nbut got'
                                 ' this:\n{}'
                                 ''.format(solution_swaps_spec, solution_swaps))


class Test_Capture_Game(unittest.TestCase):
    def test__disallow_state_allows_non_duplicate_boards(self):
        board_string_1 = '........\n' \
                         '........\n' \
                         '........\n' \
                         '........\n' \
                         '....m...\n' \
                         '....m...\n' \
                         '....s...\n' \
                         'ss..m..s'
        board_string_2 = '........\n' \
                         '........\n' \
                         '........\n' \
                         '........\n' \
                         '....m...\n' \
                         '....m...\n' \
                         'rr..s...\n' \
                         'ssr.m..s'
        game = generic_game()
        root = generic_state(board=Board(board_string_1))
        # simulate the game
        list(game.ends_of_one_state(root=root))
        # confirm that the game will now disallow a state with the same result
        non_duplicate_state = generic_state(board=Board(board_string_2))
        self.assertFalse(game._disallow_state(non_duplicate_state),
                         'Unexpectedly filtered a non-duplicate board:\n{}'
                         ''.format(non_duplicate_state))

    def test__disallow_state_disallows_duplicate_boards(self):
        board_string = '........\n' \
                       '........\n' \
                       '........\n' \
                       '........\n' \
                       '....m...\n' \
                       '....m...\n' \
                       '....s...\n' \
                       'ss..m..s'
        result_board_string = '........\n' \
                              '........\n' \
                              '........\n' \
                              '........\n' \
                              '........\n' \
                              '........\n' \
                              '........\n' \
                              'ss..s..s'
        game = generic_game()
        root = generic_state(board=Board(board_string))
        # simulate the game
        list(game.ends_of_one_state(root=root))
        # confirm that the game will now disallow a state with the same result
        test_state = generic_state(board=Board(result_board_string))
        self.assertTrue(game._disallow_state(test_state),
                        'Duplicate board unexpectedly passed duplicate'
                        ' detector. This board:\n{}\nshould have been detected'
                        'as a duplicate within the simulation of this start'
                        'board:\n{}'.format(result_board_string, board_string))

    def test__disallow_state_allows_skullbomb_with_enough_skulls(self):
        board_string = '........\n' \
                       '........\n' \
                       '........\n' \
                       '.......m\n' \
                       '........\n' \
                       '.......m\n' \
                       '.......m\n' \
                       'ss..*..m'
        game = generic_game()
        state = generic_state(Board(board_string))
        self.assertFalse(game._disallow_state(state),
                         'Unexpectedly failed state that has at least one'
                         ' skullbomb and enough total skulls to explode it:\n{}'
                         ''.format(state.board))
        self.assertFalse(game._is_impossible_by_count(state),
                         'Unexpectedly failed state that has at least one'
                         ' skullbomb and enough total skulls to explode it:\n{}'
                         ''.format(state.board))

    def test__disallow_state_allows_wildcard_with_enough_of_any_color(self):
        board_string = '........\n' \
                       '........\n' \
                       '........\n' \
                       '.......m\n' \
                       '........\n' \
                       '.......m\n' \
                       '.......m\n' \
                       'rr..4..m'
        game = generic_game()
        state = generic_state(Board(board_string))
        self.assertFalse(game._disallow_state(state),
                         'Unexpectedly failed state that has at least one'
                         ' wildcard and enough of any color to use it:\n{}'
                         ''.format(state.board))
        self.assertFalse(game._is_impossible_by_count(state),
                         'Unexpectedly failed state that has at least one'
                         ' wildcard and enough of any color to use it:\n{}'
                         ''.format(state.board))

    def test__disallow_state_disallows_too_few_x_m_s_or_color(self):
        # combined specification for simplicity
        board_strings = ('........\n'
                         '........\n'
                         '........\n'
                         '.......m\n'
                         '........\n'
                         '.......m\n'
                         '.......m\n'
                         'xx.....m',

                         '........\n'
                         '........\n'
                         '........\n'
                         '.......x\n'
                         '........\n'
                         '.......x\n'
                         '.......x\n'
                         'mm.....x',

                         '........\n'
                         '........\n'
                         '........\n'
                         '.......m\n'
                         '........\n'
                         '.......m\n'
                         '.......m\n'
                         'ss.....m',

                         '........\n'
                         '........\n'
                         '........\n'
                         '.......m\n'
                         '........\n'
                         '.......m\n'
                         '.......m\n'
                         'rr.....m')
        game = generic_game()
        for board_string in board_strings:
            state = generic_state(board=Board(board_string))
            self.assertTrue(game._disallow_state(state),
                            'This board unexpectedly passed impossible count:'
                            '\n{}'.format(board_string))
            self.assertTrue(game._is_impossible_by_count(state),
                            'This board unexpectedly passed impossible count:'
                            '\n{}'.format(board_string))


def generic_game():
    """Simple factory to help keep tests focused."""
    return Game()


def generic_state(board=None, turn=1, actions_remaining=1):
    """Simple factory to help keep tests short and focused."""
    board = board or Board()
    v = (0, 0)
    one_actor = Actor('capture', v, v, v, v, v, v, v, v, v)
    return State(board, one_actor, one_actor, turn, actions_remaining)


if __name__ == '__main__':
    unittest.main()
