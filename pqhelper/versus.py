from pqhelper import base as _base


class _State(_base.State):
    _use_random_fill = True
    pass  # eventually actor will be customized and placed here


def _create_simulation_root(board_string,
                            player_string=None, opponent_string=None):
    """Create the root to be used in building the simulation tree."""
    board = _State.Board(board_string)
    player = _State.Actor(player_string or 'player')
    opponent = _State.Actor(opponent_string or 'opponent')
    return _State(board=board,
                  turn=1, actions_remaining=1,
                  player=player, opponent=opponent)


def _expand_simulation(root, turns=1):
    """Build the simulation tree within the turn limit given."""
    # list makes the generator complete the simulation to the given turn
    list(root.end_of_turns(absolute_turn_depth=turns))
    return root

# def scored_actions(board_string, player_string, opponent_string):
#     pass
#
# def _continue_simulation(state, turns=2):
#     pass


if __name__ == '__main__':
    pass
