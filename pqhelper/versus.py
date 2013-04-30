from pqhelper import base as _base


class _Actor(_base.Actor):
    def __init__(self, actor_string=None, opponent=False):
        name = 'opponent' if opponent else 'player'
        actor_string = actor_string or '''
                                       {}
                                       health: 50/100
                                       r: 0/20
                                       g: 0/20
                                       b: 0/20
                                       y: 0/20
                                       '''.format(name)
        super(_Actor, self).__init__(actor_string=actor_string)

    def score_eot(self, eot):
        """Return a score for this end of turn based on how favorable it is
        for this actor. Higher numbers are better for self."""
        state = eot.parent
        final_self = {'player': state.player,
                      'opponent': state.opponent}[self.name]
        return sum((final_self.health,
                    final_self.r, final_self.g, final_self.b, final_self.y))

    def apply_tile_groups(self, tile_groups):
        """Apply the tiles to self and return an attack value."""
        attack_value = 0
        for tile_group in tile_groups:
            group_count = 0
            group_type = None
            wildcard_multiplier = 1  # start with no wildcard multiplier
            for tile in tile_group:
                # handle wildcards
                if tile.is_wildcard():
                    wildcard_multiplier += int(tile._type)
                    continue
                # handle skullbombs
                elif tile.is_skullbomb():
                    group_count += 5
                    group_type = _State.Tile('s')
                else:
                    group_count += 1
                    group_type = tile
            group_count *= wildcard_multiplier
            attack_value += self._consume_tiles(group_type, group_count)
        return attack_value

    def _consume_tiles(self, base_tile, count):
        """Accept any base tile (color, money, experience or skull) apply
        the given count of them to self and return an attack value."""
        base_type = base_tile._type
        # colors, money, experience
        if any((base_tile.is_color(),
                base_tile.is_money(),
                base_tile.is_experience())):
            original_value = getattr(self, base_type)
            setattr(self, base_type, original_value + count)
            attack_value = 0
        # skulls
        elif any((base_tile.is_skullbomb(),
                  base_tile.is_skull())):
            attack_value = count
        else:
            raise ValueError('Unexpected base tile type: {}'.format(base_type))
        return attack_value

    def apply_attack(self, attack_value):
        """Apply the attack value to self.

        Stub for specific game types
        """
        self.health -= attack_value

    def apply_manadrain(self):
        """Clear mana."""
        self.r, self.g, self.b, self.y = 0, 0, 0, 0


class _State(_base.State):
    _use_random_fill = True
    Actor = _Actor

    def __str__(self):
        base_str = super(_State, self).__str__()
        lines = list()
        lines.append(base_str)
        lines.append(str(self.player))
        lines.append(str(self.opponent))
        return '\n'.join(lines)

def realistic_choices(root):
    """Return a list of choices and the simulated final results of each choice,
    assuming that the player and opponent both make realistic choices
    along the way.
    """
    # store per-turn results from the bottom up. root results are under None
    realistic_results_by_EOT = {None: list()}
    for node in root._node.post_order_nodes:
        # only looking for EOT states (EOT or manadrain)
        if not isinstance(node.main, _base.EOT):
            continue
        eot = node.main
        # by the time this eot is reached, all its children have been handled
        # so get all the realistic results below it
        try:  # get the results stored previously in the higher turn
            realistic_results = realistic_results_by_EOT[eot]
        except KeyError:  # leaves will be empty and are own realistic result
            realistic_results = [_summarize_eot(eot)]
        # get the most realistic result for this eot
        is_players_turn = eot.parent.active is eot.parent.player
        realistic_result = sorted(realistic_results, reverse=is_players_turn)[0]
        # place the most realistic result on the parent EOT's list
        parent = eot.parent
        while parent:
            if isinstance(parent, _base.EOT):
                break  # stop when the parent EOT is found
            parent = parent.parent
        # at this point the parent is either None (root) or another EOT
        # so put the most realistic result of this EOT on the parent's list
        realistic_results_by_EOT.setdefault(parent,
                                            list()).append(realistic_result)
    return realistic_results_by_EOT[None]  # return the root's results


def _summarize_eot(eot):
    """Summarize the value of this EOT and the first step to get to it.

    Arguments:
    eot - an EOT / ManaDrain transition in a simulation tree.

    Return:
    a dict with the following items:
    - overall_score (higher numbers favor player, lower favor opponent)
    - root_action (the details of the root action that led to this state)
    """
    overall_score = _score_eot(eot)
    action_summary = _summarize_root_action(eot)
    return {'overall_score': overall_score,
            'root_action': action_summary}


def _score_eot(eot):
    """Return an overall score for this eot."""
    player = eot.parent.player
    opponent = eot.parent.opponent
    return player.score_eot(eot) - opponent.score_eot(eot)


def _summarize_root_action(eot):
    """Return a summary of the root action that led to this EOT.

    Action Summary Keys:
    - type
    - details
    """
    # find the action leading back to the root
    node = eot.parent
    child = eot
    while node.parent:  # search for the root
        child = node
        node = node.parent
    action = child  # at this point, node is root, child is the action
    return {'type': action.type,
            'details': action.position_pair}


def _create_simulation_root(board_string,
                            player_string=None, opponent_string=None):
    """Create the root to be used in building the simulation tree."""
    board = _State.Board(board_string)
    player = _State.Actor(player_string)
    opponent = _State.Actor(opponent_string, opponent=True)
    return _State(board=board,
                  turn=1, actions_remaining=1,
                  player=player, opponent=opponent)


def _expand_simulation(root, turns=1):
    """Build the simulation tree within the turn limit given."""
    # list makes the generator complete the simulation to the given turn
    list(root.end_of_turns(absolute_turn_depth=turns))
    return root


if __name__ == '__main__':
    pass
