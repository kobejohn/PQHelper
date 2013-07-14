from pqhelper import base


class Advisor(object):
    def __init__(self):
        self._current_completed_turn = 0
        self._root = None
        self._game = base.Game(True)

    @property
    def current_completed_turn(self):
        return self._current_completed_turn

    def reset(self, board, player, opponent, extra_actions):
        total_actions = 1 + extra_actions
        self._root = base.State(board, player, opponent,
                                1, total_actions)
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
        summaries.sort(key=lambda summary: summary.score, reverse=True)
        return summaries

    def _summarize_action(self, root_action):
        """Return a dictionary with various information about this root_action.

        Note:
        Scoring assumes that each actor makes the "best" choices in their turn
        based on the simulation available.
        """
        def is_target_node(node):
            return isinstance(node, base.EOT) or (node is root_action)
        # store per-turn results from the bottom up.
        realistic_ends_by_node = dict()
        for node in root_action.post_order_nodes():  # bottom up to this action
            # only work with EOT or the root action
            if not is_target_node(node):
                continue
            # by the time this node is reached, the results of all children
            # have been stored under it in realistic_ends (except leaves)
            # so choose the best of the available results and send it
            # up to the next valid node
            try:  # get the results stored previously in the deeper turn
                realistic_ends = realistic_ends_by_node[node]
            except KeyError:  # leaves are own realistic end
                realistic_ends = [node]
            # identify the "best" end for this node
            if node is root_action:
                active = node.parent.active
                passive = node.parent.passive
            else:
                active = node.parent.passive
                passive = node.parent.active
            ends_by_score = dict()
            for realistic_end in realistic_ends:
                # determine the relative score. i.e. if delta is positive
                # then the end result is better for active than passive
                relative_score = self._relative_score(node, realistic_end,
                                                      active, passive)
                ends_by_score[relative_score] = realistic_end
            best_end = ends_by_score[max(ends_by_score.keys())]
            # done after determining realistic result for root action
            if node is root_action:
                return self._summarize_result(root_action, best_end)
            # not done: place best end on the parent EOT's list of possibilities
            parent = node.parent
            while parent:
                if is_target_node(parent):
                    break
                parent = parent.parent  # keep moving up until target found
            # at this point the parent is either root_action or another EOT
            realistic_ends_by_node.setdefault(parent, list()).append(best_end)
        pass  # the algorithm should never reach this point...

    def _relative_score(self, start_eot, end_eot, active, passive):
        """Return the balance of perception between the two nodes.
        A positive score indicates the result is relatively better for active.
        """
        active_start = self._score_eot_for_actor(start_eot, active)
        passive_start = self._score_eot_for_actor(start_eot, passive)
        active_end = self._score_eot_for_actor(end_eot, active)
        passive_end = self._score_eot_for_actor(end_eot, passive)
        return (active_end - passive_end) - (active_start - passive_start)

    def _score_eot_for_actor(self, eot, actor):
        """Have the actor evaluate the end of turn for itself only."""
        # currently just simple sum of own attributes
        # could be much more sophisticated in both analysis (e.g. formulas)
        # and breadth of items analyzed (e.g. require other actor, the board)
        end_state = eot.parent
        a = {'player': end_state.player,
             'opponent': end_state.opponent}[actor.name]
        # simple prioritization without regard to character attributes
        health = a.health * 2
        r, g, b, y = a.r, a.g, a.b, a.y
        x, m = 0.5 * a.x, 0.5 * a.m
        return sum((health, r, g, b, y, x, m))

    def _summarize_result(self, root_action, leaf_eot):
        """Return a dict with useful information that summarizes this action."""
        root_board = root_action.parent.board
        action_detail = root_action.position_pair
        score = self._relative_score(root_action, leaf_eot,
                                     root_action.parent.player,
                                     root_action.parent.opponent)
        # mana drain info
        total_leaves = 0
        mana_drain_leaves = 0
        for leaf in root_action.leaves():
            total_leaves += 1
            if leaf.is_mana_drain:
                mana_drain_leaves += 1
        summary = base.Summary(root_board, action_detail, score,
                               mana_drain_leaves, total_leaves)
        return summary


if __name__ == '__main__':
    pass
