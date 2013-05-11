from pqhelper import base

Actor = base.Actor  # for convenient access
Board = base.Board  # for convenient access


class Advisor(object):
    def __init__(self):
        self._current_completed_turn = 0
        self._root = None
        self._game = base.Game(True)

    @property
    def current_completed_turn(self):
        return self._current_completed_turn

    def reset(self, board, player, opponent):
        self._root = base.State(board, player, opponent, 1, 1)
        self._current_completed_turn = 0

    def simulate_next_turn(self):
        eots = list(self._game.ends_of_next_whole_turn(self._root))
        if eots:
            self._current_completed_turn += 1

    def sorted_current_summaries(self):
        # return empty sequence for empty root
        try:
            actions = tuple(self._root.children)
        except AttributeError:
            return tuple()
        summaries = list()
        for action in actions:
            summary = self._summarize_action(action)
            summaries.append(summary)
        # sort to the benefit of player (descending overall score)
        summaries.sort(key=lambda summary: summary['overall'], reverse=True)
        return summaries

    def _summarize_action(self, root_action):
        """Return a dictionary with various information about this root_action.

        Note:
        Scoring assumes that each actor makes the "best" choices in their turn
        based on the simulation available.
        """
        # store per-turn results from the bottom up.
        # this action's results will eventually be stored under action itself
        realistic_results_by_EOT = dict()
        for node in root_action.post_order_nodes:  # bottom up traversal
            # only work with EOT or the root action
            if not (isinstance(node, base.EOT) or (node is root_action)):
                continue
            # by the time this node is reached, all children have been scored
            # so get all the realistic results below it
            try:  # get the results stored previously in the deeper turn
                realistic_results = realistic_results_by_EOT[node]
            except KeyError:  # leaves are own realistic result
                realistic_results = [{'overall': self._score_eot(node)}]
            # get the most realistic result for the turn of this node
            was_players_turn = node.parent.active is node.parent.opponent
            min_max = max if was_players_turn else min
            realistic_result = min_max(realistic_results,
                                       key=lambda summary: summary['overall'])
            if node is root_action:
                break  # done after determining realistic result for root action
            # place the most realistic result on the parent EOT's list
            parent = node.parent
            while parent:
                if isinstance(parent, base.EOT) or (parent is root_action):
                    break
                parent = parent.parent  # keep moving up until EOT found
            # at this point the parent is either root_action or another EOT
            # so put the most realistic result of this EOT on the parent's list
            realistic_results_by_EOT.setdefault(parent,
                                                list()).append(realistic_result)
        # action_results = realistic_results_by_EOT[root_action]
        # best_summary = max(action_results, key=lambda score: score['overall'])
        # # add the root_action details to the summary at the end
        # best_summary['action'] = root_action.position_pair
        final_realistic_result = realistic_results_by_EOT[root_action][0]
        final_realistic_result['action'] = root_action.position_pair
        return final_realistic_result

    def _score_eot(self, eot):
        """Return a score for this eot."""
        player_score = self._score_for_actor(eot.parent.player)
        opponent_score = self._score_for_actor(eot.parent.opponent)
        return player_score - opponent_score

    def _score_for_actor(self, actor):
        """Have the actor self-evaluate all available information."""
        # currently just simple sum of own attributes
        # could be much more sophisticated in both analysis (e.g. formulas)
        # and breadth of items analyzed (e.g. require other actor, the board)
        a = actor
        return sum((a.health, a.r, a.g, a.b, a.y, a.x, a.m))


if __name__ == '__main__':
    pass
