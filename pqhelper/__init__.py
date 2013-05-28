import base
import capture
import versus


_state_investigator = base.StateInvestigator()
_versus_advisor = versus.Advisor()
Board = base.Board  # top level access for convenience
Actor = base.Actor  # top level access for convenience


def summarize_versus_options(turns=1):
    board, player, opponnet = _state_investigator.get_versus()
    if board is None:
        return tuple()
    _versus_advisor.reset(board, player, opponnet)
    for i in range(turns):
        _versus_advisor.simulate_next_turn()
    summaries = _versus_advisor.sorted_current_summaries()
    return summaries


def solve_capture():
    board = _state_investigator.get_capture()
    if board is None:
        return tuple()
    steps = capture.capture(board)
    return steps


if __name__ == '__main__':
    pass