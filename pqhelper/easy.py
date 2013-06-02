from pqhelper import base, capture, versus


# these parts are heavy so keep one common object for the module
_state_investigator = base.StateInvestigator()


def versus_summaries(turns=2, sims_to_average=2, async_results_q=None):
    """Return summaries of the likely resutls of each available action..

    Arguments:
    - turns: how many turns to simulate.
        - in 2013, 1 is fast (seconds), 2 is slow (seconds), 3 who knows
    - sims_to_average: how many times to run the simulation
        to get more representative average results of each action.
    - async_results_q: provide a multiprocessing Queue on which
        the summaries of each turn will be placed. this is an asynchronous
        alternative to waiting for the final return value
    """
    board, player, opponent = _state_investigator.get_versus()
    if board is None:
        return tuple()
    averaged_summaries = list()  # default return value is empty
    # keep a separate advisor for each simulation to average
    advisors = list()
    for i in range(sims_to_average):
        advisor = versus.Advisor()
        advisor.reset(board, player, opponent)
        advisors.append(advisor)
    # provide async sim results per turn; final results as return value
    for turn in range(turns):
        # store    {action: list of results from each simulation}
        summaries_by_action = dict()
        for i in range(sims_to_average):
            advisor = advisors[i]
            advisor.simulate_next_turn()
            for s in advisor.sorted_current_summaries():
                summaries_by_action.setdefault(s.action, list()).append(s)
        # now all sims and analysis for this turn have been completed
        averaged_summaries = list()
        for action, summaries in summaries_by_action.items():
            board = summaries[0].board  # any board. they are all the same
            action = summaries[0].action  # any action. they are all the same
            score_sum = sum(s.score for s in summaries)
            score_avg = score_sum / len(summaries)
            manadrain_sum = sum(s.mana_drain_leaves for s in summaries)
            leaves_sum = sum(s.total_leaves for s in summaries)
            avg_summary = base.Summary(board, action, score_avg,
                                       manadrain_sum, leaves_sum)
            averaged_summaries.append(avg_summary)
        averaged_summaries.sort(key=lambda s: s.score, reverse=True)
        # option to provide the results asynchronouslys
        if not async_results_q is None:
            async_results_q.put(averaged_summaries)
    return averaged_summaries


def capture_solution():
    board = _state_investigator.get_capture()
    if board is None:
        return tuple()
    steps = capture.capture(board)
    return steps


if __name__ == '__main__':
    pass
