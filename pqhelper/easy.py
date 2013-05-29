from pqhelper import base, capture, versus


# these parts are heavy so keep one common object for the module
_state_investigator = base.StateInvestigator()
_versus_advisor = versus.Advisor()


def versus_summaries(turns=2, sims_to_average=2):
    """Run several simulations and average the results."""
    board, player, opponent = _state_investigator.get_versus()
    if board is None:
        return tuple()
    summaries_by_action = dict()
    # simulate as many times as specified
    for i in range(sims_to_average):
        _versus_advisor.reset(board, player, opponent)
        for j in range(turns):
            _versus_advisor.simulate_next_turn()
        summaries = _versus_advisor.sorted_current_summaries()
        # group the summaries by the action for easy averaging later
        for summary in summaries:
            action = summary['action']
            summaries_by_action.setdefault(action, list()).append(summary)
    averaged_summaries = list()
    for action, summaries in summaries_by_action.items():
        new_summary = dict()
        new_summary['action'] = summaries[0]['action']
        score_sum = sum(summary['overall'] for summary in summaries)
        score_avg = score_sum / len(summaries)
        new_summary['overall'] = score_avg
        averaged_summaries.append(new_summary)
    averaged_summaries.sort(key=lambda s: s['overall'], reverse=True)
    return averaged_summaries


def capture_solution():
    board = _state_investigator.get_capture()
    if board is None:
        return tuple()
    steps = capture.capture(board)
    return steps


if __name__ == '__main__':
    pass
