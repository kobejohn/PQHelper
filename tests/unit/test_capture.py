import unittest

from pqhelper.capture import _State as State, _Board as Board, capture


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
        solution = capture(board_string)
        # confirm that the solution matches the specification
        solution_spec = (((7, 6), (7, 7)), ((7, 6), (7, 7)))
        self.assertSequenceEqual(solution, solution_spec)


class Test_Capture_State(unittest.TestCase):
    def setUp(self):
        State.clear_duplicate_tree()

    def test__disallow_state_disallows_duplicate_boards(self):
        board_string = '........\n' \
                       '........\n' \
                       '........\n' \
                       '........\n' \
                       '........\n' \
                       '........\n' \
                       '........\n' \
                       'ss......'
        state_1 = State(Board(board_string))
        state_2 = State(Board(board_string))
        self.assertTrue(state_1._disallow_state(state_2))

    def test__disallow_state_allows_skullbomb_with_enough_skulls(self):
        board_string = '........\n' \
                       '........\n' \
                       '........\n' \
                       '.......m\n' \
                       '........\n' \
                       '.......m\n' \
                       '.......m\n' \
                       'ss..*..m'
        state = State(Board(board_string))
        self.assertFalse(state._disallow_state(state))

    def test__disallow_state_allows_wildcard_with_enough_of_any_color(self):
        board_string = '........\n' \
                       '........\n' \
                       '........\n' \
                       '.......m\n' \
                       '........\n' \
                       '.......m\n' \
                       '.......m\n' \
                       'rr..4..m'
        state = State(Board(board_string))
        self.assertFalse(state._disallow_state(state))

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
        for board_string in board_strings:
            state = State(Board(board_string))
            self.assertTrue(state._disallow_state(state),
                            'This board unexpectedly passed impossible count:'
                            '\n{}'.format(board_string))


if __name__ == '__main__':
    unittest.main()
