import unittest

from mock import patch

from pqhelper.base import State, Actor
from pqhelper.base import _Transition, Swap, ChainReaction, EOT, ManaDrain
from pqhelper.base import Board, Tile


class Test_Actor(unittest.TestCase):
    def test___init___default_name_is_player(self):
        actor = Actor()
        self.assertEqual(actor.name, 'player')

    def test___init___accepts_name_of_player_or_opponent(self):
        try:
            player = Actor('player')
            opponent = Actor('opponent')
        except Exception as e:
            self.fail('Expected creation of actors with names player and'
                      'nopponent to work but got this error:\n{}'.format(e))
        self.assertEqual(player.name, 'player')
        self.assertEqual(opponent.name, 'opponent')

    def test___init___raises_ValueError_if_name_not_valid(self):
        invalid_name = 'invalid'
        self.assertRaises(ValueError, Actor, **{'name': invalid_name})

    def test_copy_returns_a_new_actor_with_the_same_name(self):
        actor_name_spec = 'opponent'
        actor = Actor(actor_name_spec)
        actor_copy = actor.copy()
        self.assertIsNot(actor_copy, actor)
        self.assertEqual(actor_copy.name, actor_name_spec)

    def test_consume_tiles_is_a_placeholder_in_base_class(self):
        actor = Actor()
        skull = Tile('s')
        tile_groups = [[skull, skull, skull]]
        try:
            actor.consume_tiles(tile_groups)
        except Exception as e:
            self.fail('Expected consume_tiles to run with no problems'
                      ' but got this exception:\n{}'.format(e))

    def test_apply_attack_is_a_placeholder_in_base_class(self):
        actor = Actor()
        any_attack_value = 10
        try:
            actor.apply_attack(any_attack_value)
        except Exception as e:
            self.fail('Expected apply_attack to run with no problems'
                      ' but got this exception:\n{}'.format(e))


class Test_State(unittest.TestCase):
    # Test Parameters
    _board_string_two_paths = '........\n' \
                              '........\n' \
                              'g......g\n' \
                              'g......g\n' \
                              's......s\n' \
                              's......s\n' \
                              'xg....gx\n' \
                              'rsrryysy'

    # Customizable Class attributes
    def test_class_holds_references_to_classes_of_Tile_Board_and_Actor(self):
        try:
            getattr(State, 'Tile')
            getattr(State, 'Board')
            getattr(State, 'Actor')
        except Exception as e:
            self.fail('Expected to find classes for the parts that state'
                      ' uses but got this error: {}'.format(e))

    # Instantiaion
    def test___init___accepts_optional_board(self):
        board = Board(self._board_string_two_paths)
        state = State(board=board)
        self.assertEqual(str(state.board), self._board_string_two_paths)

    def test___init___accepts_optional_turn(self):
        state = State(turn=2)
        self.assertEqual(state.turn, 2)

    def test___init___accepts_optional_actions_remaining(self):
        state = State(actions_remaining=2)
        self.assertEqual(state.actions_remaining, 2)

    def test___init___accepts_optional_player_and_opponent(self):
        try:
            State(player='player', opponent='opponent')
        except Exception as e:
            self.fail('Expected to be able to provide player and opponent'
                      ' arguments but got this error:\n{}'.format(e))

    # Generating end_of_turns (core behavior)
    def test_end_of_turns_produces_exactly_EOTs_within_turn_depth(self):
        board = Board(self._board_string_two_paths)
        state = State(board)
        eots = list(state.end_of_turns(absolute_turn_depth=1))
        eot_board_strings = [str(eot.parent.board) for eot in eots]
        # confirm that the real boards match the specification
        # one is swap on left side, other is swap on right side
        eot_board_strings_spec = ['........\n'
                                  '........\n'
                                  'g......g\n'
                                  'g......g\n'
                                  's......s\n'
                                  's......s\n'
                                  'x.....gx\n'
                                  'sg..yysy',

                                  '........\n'
                                  '........\n'
                                  'g......g\n'
                                  'g......g\n'
                                  's......s\n'
                                  's......s\n'
                                  'xg.....x\n'
                                  'rsrr..gs']
        self.assertItemsEqual(eot_board_strings, eot_board_strings_spec,
                              'Expected to produce exactly EOTs within the'
                              ' turn limit:\n{}\n'
                              'but got this:\n{}'
                              ''.format('\n'.join(eot_board_strings_spec),
                                        '\n'.join(eot_board_strings)))

    def test_end_of_turns_does_no_simulation_below_absolute_turn_depth(self):
        board = Board(self._board_string_two_paths)
        state = State(board)
        turn_limit = 2
        # use list to make sure all the results are generated / sim is done
        list(state.end_of_turns(absolute_turn_depth=2))
        leaves = [node.main for node in state._node.leaves]
        for leaf in leaves:
            if isinstance(leaf, State):
                self.assertLessEqual(leaf.turn, turn_limit)
            elif isinstance(leaf, _Transition):
                self.assertLessEqual(leaf.parent.turn, turn_limit)

    def test_end_of_turns_produces_depth_before_breadth(self):
        board = Board(self._board_string_two_paths)
        state = State(board)
        enough_turns_to_complete_either_side = 5
        eots = state.end_of_turns(absolute_turn_depth=
                                  enough_turns_to_complete_either_side)
        eots = list(eots)
        board_sequence = [str(eot.parent.board) for eot in eots]
        # confirm that end of one set of actions comes before beginning of other
        left_start = '........\n' \
                     '........\n' \
                     'g......g\n' \
                     'g......g\n' \
                     's......s\n' \
                     's......s\n' \
                     'x.....gx\n' \
                     'sg..yysy'
        left_end = '........\n' \
                   '........\n' \
                   '.......g\n' \
                   '.......g\n' \
                   '.......s\n' \
                   '.......s\n' \
                   '......gx\n' \
                   '.x..yysy'
        right_start = '........\n' \
                      '........\n' \
                      'g......g\n' \
                      'g......g\n' \
                      's......s\n' \
                      's......s\n' \
                      'xg.....x\n' \
                      'rsrr..gs'
        right_end = '........\n' \
                    '........\n' \
                    'g.......\n' \
                    'g.......\n' \
                    's.......\n' \
                    's.......\n' \
                    'xg......\n' \
                    'rsrr..x.'
        left_start_index = board_sequence.index(left_start)
        left_end_index = board_sequence.index(left_end)
        right_start_index = board_sequence.index(right_start)
        right_end_index = board_sequence.index(right_end)
        left_end_before_right_start = left_end_index < right_start_index
        right_end_before_left_start = right_end_index < left_start_index
        self.assertTrue(left_end_before_right_start
                        or right_end_before_left_start,
                        'Expected to see one side of swaps done before the'
                        ' other starts but got this:\n{}'
                        ''.format('\n'.join(board_sequence)))

    @patch.object(State, '_disallow_state')
    def test_end_of_turns_stops_bad_states_with_Filtered(self, mock_disallow):
        mock_disallow.return_value = True  # disallow all states
        board = Board(self._board_string_two_paths)
        state = State(board)
        enough_turns_to_go_beyond_filtered = 2
        eots = state.end_of_turns(absolute_turn_depth=
                                  enough_turns_to_go_beyond_filtered)
        eots = list(eots)
        # confirm that all results were filtered and tagged
        self.assertTrue(all(eot.type == 'filtered' for eot in eots))

    def test_active_passive_are_player_opponent_for_even_and_vice_versa(self):
        chain_reaction_first = '........\n' \
                               '........\n' \
                               '........\n' \
                               '........\n' \
                               '.......r\n' \
                               '.......s\n' \
                               '......xs\n' \
                               '...xxrsr'
        player = Actor('player')
        opponent = Actor('opponent')
        root = State(Board(chain_reaction_first),
                     player=player, opponent=opponent)
        # get the end of turn with empty board (chain reaction + second swap)
        enough_turns = 3
        list(root.end_of_turns(enough_turns))
        # confirm that each state has the appropriate active actor
        for node in root._node.in_order_nodes:
            if node.main.type != 'state':
                continue
            state = node.main
            if state.turn % 2:  # odd
                self.assertEqual(state.active.name, 'player')
                self.assertEqual(state.passive.name, 'opponent')
            else:  # even
                self.assertEqual(state.active.name, 'opponent')
                self.assertEqual(state.passive.name, 'player')

    # Convenience methods
    def test__leaves_within_depth_produces_exactly_leaves_within_depth(self):
        depth = 2
        root, leaves_within_depth, leaves_below_depth \
            = self.produce_fake_simulation()
        leaf_ids = [id(leaf) for leaf in root._leaves_within_depth(depth)]
        # Safety confirmation that there are some leaves below depth 2 to ignore
        if not leaves_below_depth:
            self.fail('Expected to get a simulation with leaves below the'
                      ' target depth but did not.')
        # Confirm that the depth 2 leaves exactly match specification
        leaf_ids_spec = [id(leaf) for leaf in leaves_within_depth]
        self.assertItemsEqual(leaf_ids, leaf_ids_spec)

    # Tree behavior
    def test_attach_attaches_children(self):
        state = State()
        transition = _Transition()
        try:
            state.attach(transition)
        except Exception as e:
            self.fail('Unexpected problem attaching a child to a state:'
                      '\n{}'.format(e))

    def test_children_provides_children(self):
        state = State()
        transition = _Transition()
        state.attach(transition)
        children_ids = [id(child) for child in state.children()]
        children_ids_spec = [id(transition)]
        self.assertItemsEqual(children_ids, children_ids_spec)

    def test_parent_provides_parent(self):
        state = State()
        transition = _Transition()
        transition.attach(state)
        parent_id = id(state.parent)
        parent_id_spec = id(transition)
        self.assertEqual(parent_id, parent_id_spec)

    def test_parent_provides_None_if_no_parent(self):
        state = State()
        self.assertIsNone(state.parent)

    # Special methods
    def test___str___shows_the_core_data_of_state_and_number_of_children(self):
        board_string_spec = self._board_string_two_paths
        board = Board(board_string_spec)
        turn = 2
        actions_remaining = 3
        state = State(board=board, turn=turn,
                      actions_remaining=actions_remaining)
        transition_1 = _Transition()
        transition_2 = _Transition()
        state.attach(transition_1)
        state.attach(transition_2)
        state_string = str(state)
        # confirm board
        for line in board_string_spec.splitlines():
            self.assertIn(line, state_string)
        # confirm turn
        turn_string_spec = '{} : turn'.format(turn)
        self.assertIn(turn_string_spec, state_string)
        # confirm actions remaining
        ar_string_spec = '{} : actions remaining'.format(actions_remaining)
        self.assertIn(ar_string_spec, state_string)
        # confirm number of children
        children_string_spec = '{} : children'.format(2)
        self.assertIn(children_string_spec, state_string)

    def produce_fake_simulation(self):
        """Produce a fake simulation.

        Return: root, leaves_within_depth_2, leaves_below_depth_2
        """
        # create a tree with:
        #   - level 2 leaves: 1 EOT, 1 state
        #   - level 3 leaves: 1 EOT, 1 state
        # make all the parts
        root_t1 = State(turn=1)  # any state is fine
        a_transition_t1 = ChainReaction()  # any transition is fine
        a_state_t2 = State(turn=2)
        a_transition_t2 = ChainReaction()
        a_state_t3 = State(turn=3)
        a_transition_t3 = ChainReaction()  # level 3 transition leaf
        b_transition_t1 = ChainReaction()
        b_state_t2 = State(turn=2)
        b_transition_t2 = ChainReaction()
        b_state_t3 = State(turn=3)  # level 3 state leaf
        c_transition_t1 = ChainReaction()
        c_state_t2 = State(turn=2)
        c_transition_t2 = ChainReaction()  # level 2 transition leaf
        d_transition_t1 = ChainReaction()
        d_state_t2 = State(turn=2)  # level 2 state leaf
        # build level 1 (no leaves)
        root_t1.attach(a_transition_t1)
        root_t1.attach(b_transition_t1)
        root_t1.attach(c_transition_t1)
        root_t1.attach(d_transition_t1)
        # build level 2 (c and d are leaves)
        a_transition_t1.attach(a_state_t2)
        b_transition_t1.attach(b_state_t2)
        c_transition_t1.attach(c_state_t2)
        d_transition_t1.attach(d_state_t2)
        a_state_t2.attach(a_transition_t2)
        b_state_t2.attach(b_transition_t2)
        c_state_t2.attach(c_transition_t2)
        # build level 3 (a and b are leaves)
        a_transition_t2.attach(a_state_t3)
        b_transition_t2.attach(b_state_t3)
        a_state_t3.attach(a_transition_t3)
        leaves_within_2 = (c_transition_t2, d_state_t2)
        leaves_below_2 = (a_transition_t3, b_state_t3)
        return root_t1, leaves_within_2, leaves_below_2


class Test_Transitions(unittest.TestCase):
    def test___init__gives_a_name_to_the_transition(self):
        type_spec = 'test'
        transition = _Transition(type_spec)
        self.assertEqual(transition.type, type_spec)

    def test_attach_attaches_children(self):
        transition = _Transition()
        state = State()
        try:
            transition.attach(state)
        except Exception as e:
            self.fail('Unexpected problem attaching a child to a transition:'
                      '\n{}'.format(e))

    def test_children_provides_children(self):
        transition = _Transition()
        state = State()
        transition.attach(state)
        children_ids = [id(child) for child in transition.children()]
        children_ids_spec = [id(state)]
        self.assertItemsEqual(children_ids, children_ids_spec)

    def test_parent_provides_parent(self):
        transition = _Transition()
        state = State()
        state.attach(transition)
        parent_id = id(transition.parent)
        parent_id_spec = id(state)
        self.assertEqual(parent_id, parent_id_spec)

    def test_parent_provides_None_if_no_parent(self):
        transition = _Transition()
        self.assertIsNone(transition.parent)

    def test_Swap_type_name_is_swap(self):
        swap = Swap(((0, 0), (0, 1)))
        self.assertEqual(swap.type, 'swap')

    def test_Swap___init___takes_a_pair_of_coordinates(self):
        position_pair_spec = ((0, 0), (0, 1))
        swap = Swap(position_pair_spec)
        self.assertEqual(swap.position_pair, position_pair_spec)

    def test_ChainReaction_type_name_is_chain_reaction(self):
        chainreaction = ChainReaction()
        self.assertEqual(chainreaction.type, 'chain reaction')

    def test_EOT_type_name_is_eot(self):
        eot = EOT()
        self.assertEqual(eot.type, 'end of turn')

    def test_ManaDrain_type_name_is_mana_drain(self):
        manadrain = ManaDrain()
        self.assertEqual(manadrain.type, 'mana drain')


class Test_Board(unittest.TestCase):
    # Test Parameters
    _board_string_all_tiles = 'rgby....\n' \
                              '.xm.....\n' \
                              '..234567\n' \
                              '89......\n' \
                              '.s*.....\n' \
                              '........\n' \
                              '........\n' \
                              '........'

    _board_string_skull_bomb_reaction = '..*.....\n' \
                                        '...*....\n' \
                                        '....*...\n' \
                                        '.....*..\n' \
                                        '......*.\n' \
                                        '.......*\n' \
                                        '....gb*.\n' \
                                        '....r*y.'

    _board_string_simple_or_chain = '........\n' \
                                    '........\n' \
                                    '........\n' \
                                    '........\n' \
                                    'x......r\n' \
                                    'S......s\n' \
                                    'S......s\n' \
                                    'rs...rsr'

    # Customizable Class attributes
    def test_class_holds_references_to_classes_of_Tile_Board_and_Actor(self):
        try:
            Board.Tile
        except Exception as e:
            self.fail('Expected to find classes for the parts that board'
                      ' uses but got this error: {}'.format(e))

    # Instance creation
    def test___init___default_is_empty_board(self):
        board = Board()
        self.assertTrue(board.is_empty())

    def test___init___with_a_board_string_of_8x8_with_EOLs_works(self):
        board = Board(self._board_string_all_tiles)
        self.assertEqual(str(board), self._board_string_all_tiles)

    # Indexing and Shape of grid
    def test_indexing_works_for_grid_of_8_rows_and_8_columns(self):
        board = Board()
        test_tile = Tile('r')
        for row in range(8):
            for col in range(8):
                try:
                    board[row][col] = test_tile  # test writing
                    actual_tile = board[row][col]  # test reading
                except Exception as e:
                    self.fail('Indexing of row {} and column {} should have '
                              'worked but an error occured: {}'.format(row, col,
                                                                       e))
                self.assertIs(actual_tile, test_tile)

    def test_tuple_indexing_also_works(self):
        board = Board()
        test_tile = Tile('r')
        coordinate_tuple = (2, 2)
        try:
            board[coordinate_tuple] = test_tile
            actual_tile = board[coordinate_tuple]
        except Exception as e:
            self.fail('Indexing with the coordinate tuple {} should have '
                      'worked but an error occured: {}'.format(coordinate_tuple,
                                                               e))
        self.assertIs(actual_tile, test_tile)

    def test_indexing_outside_the_8x8_array_raises_IndexError(self):
        board = Board()
        bad_coordinate = (8, 7)
        self.assertRaises(IndexError, board.__getitem__, bad_coordinate)

    # Execution - execute_once (core behavior)
    def test_execute_once_returns_a_copy_not_original(self):
        board = Board()
        return_board, destroyed_tiles = board.execute_once()
        self.assertIsNot(return_board, board,
                         'Expected to receive a copy of board but received'
                         'the same board object instead.')

    def test_execute_once_simulates_swap(self):
        board_string = '........\n' \
                       '........\n' \
                       '........\n' \
                       '........\n' \
                       'x.......\n' \
                       's.......\n' \
                       's.......\n' \
                       'rs......'
        board = Board(board_string)
        swap = [(7, 0), (7, 1)]
        result, destroyed_groups = board.execute_once(swap=swap,
                                                      random_fill=False)
        # Combined test for clarity
        # 1) confirm the effects on the returned board
        result_board_spec = '........\n' \
                            '........\n' \
                            '........\n' \
                            '........\n' \
                            '........\n' \
                            '........\n' \
                            '........\n' \
                            'xr......'
        self.assertEqual(str(result), result_board_spec,
                         'Expected to receive a "fallen" version of changes:'
                         '\n{}\nbut received this:'
                         '\n{}'.format(result_board_spec, result))
        # 2) confirm the content of the returned groups
        skull = Tile('s')
        destroyed_groups_spec = [[skull, skull, skull]]
        self.assertItemsEqual(destroyed_groups, destroyed_groups_spec)

    def test_execute_once_does_not_execute_chain_reactions(self):
        board_string = '........\n' \
                       '........\n' \
                       '........\n' \
                       '........\n' \
                       '.......r\n' \
                       '.......s\n' \
                       '.......s\n' \
                       '.....rsr'
        board = Board(board_string)
        swap = [(7, 6), (7, 7)]
        result, destroyed_groups = board.execute_once(swap=swap,
                                                      random_fill=False)
        # Combined test for simplicity
        # 1) confirm the effects on the returned board
        result_spec = '........\n' \
                      '........\n' \
                      '........\n' \
                      '........\n' \
                      '........\n' \
                      '........\n' \
                      '........\n' \
                      '.....rrr'
        self.assertEqual(str(result), result_spec,
                         'Expected execution of the swap on this board\n{}\n'
                         'to result in this board\n{}\n'
                         'but received this\n{}'
                         ''.format(board, result_spec, result))
        # 2) confirm the content of the returned groups
        skull = Tile('s')
        destroyed_groups_spec = [[skull, skull, skull]]
        self.assertItemsEqual(destroyed_groups, destroyed_groups_spec,
                              'Expected execution of this board\n{}\n'
                              'to result in these destructions\n{}\n'
                              'but received this\n{}'
                              ''.format(board, destroyed_groups_spec,
                                        destroyed_groups))

    def test_execute_once_simulates_spells(self):
        board_string = '........\n' \
                       '........\n' \
                       '........\n' \
                       '........\n' \
                       'x.......\n' \
                       's.......\n' \
                       's.......\n' \
                       'rs......'
        board = Board(board_string)
        skull = Tile('s')
        red = Tile('r')
        # change the experience to skull --> 1 destroyed group (sss)
        spell_changes = [[(4, 0), skull]]
        # instantly destroy the red --> 1 destroyed group (r)
        spell_destructions = [(7, 0)]
        result, destroyed_groups = \
            board.execute_once(spell_changes=spell_changes,
                               spell_destructions=spell_destructions,
                               random_fill=False)
        # Combined test for simplicity
        # 1) confirm the effects on the returned board
        #remaining result should be just s at (7, 1)
        result_board_spec = '........\n' \
                            '........\n' \
                            '........\n' \
                            '........\n' \
                            '........\n' \
                            '........\n' \
                            '........\n' \
                            '.s......'
        self.assertEqual(str(result), result_board_spec,
                         'Expected to receive this result:'
                         '\n{}\nbut received this:'
                         '\n{}'.format(result_board_spec, result))
        # 2) confirm the content of the returned groups
        destroyed_groups_spec = [[skull, skull, skull],
                                 [red]]
        self.assertItemsEqual(destroyed_groups, destroyed_groups_spec)

    # Execution - execute_once with / without random fill (core behavior)
    def test_execute_once_with_random_fill_fills_empty_board(self):
        board = Board()
        if not board.is_empty():
            self.fail('Expected an empty board to start.')
        result_board, x = board.execute_once(random_fill=True)
        self.assertFalse(result_board.is_empty(),
                         'Expected to find a full board but found this:\n{}'
                         ''.format(result_board))

    def test_execute_once_without_random_fill_leaves_empty_board_empty(self):
        board = Board()
        if not board.is_empty():
            self.fail('Expected an empty board to start.')
        result_board, x = board.execute_once(random_fill=False)
        self.assertTrue(result_board.is_empty(),
                        'Expected to find a full board but found this:\n{}'
                        ''.format(result_board))

    # Execution - swap (core behavior)
    def test__swap_swaps_two_adjacent_positions(self):
        board_string = '........\n' \
                       '........\n' \
                       '........\n' \
                       '........\n' \
                       '........\n' \
                       '........\n' \
                       '........\n' \
                       'rs......'
        result_string = '........\n' \
                        '........\n' \
                        '........\n' \
                        '........\n' \
                        '........\n' \
                        '........\n' \
                        '........\n' \
                        'sr......'
        board = Board(board_string)
        swap = [(7, 0), (7, 1)]
        board._swap(swap)
        self.assertEqual(str(board), result_string,
                         'Expected to get the original board:'
                         '\n{}\n with the two tiles swapped'
                         ' but got this result board:'
                         '\n{}'.format(board_string, str(board)))

    def test__swap_does_nothing_if_swap_is_None(self):
        board_string = '........\n' \
                       '........\n' \
                       '........\n' \
                       '........\n' \
                       '........\n' \
                       '........\n' \
                       '........\n' \
                       'rs......'
        board = Board(board_string)
        board._swap(None)
        self.assertEqual(str(board), board_string)

    def test__swap_raises_ValueError_if_positions_are_not_adjacent(self):
        board = Board()
        # try a diagonal swap which should cause an error
        bad_swap = [(0, 0), (1, 1)]
        self.assertRaises(ValueError, board._swap, bad_swap)

    # Execution - change (core behavior)
    def test__change_changes_the_given_positions_to_the_given_tiles(self):
        board = Board()
        skull = Tile('s')
        green = Tile('g')
        changes = [[(0, 0), skull],
                   [(1, 1), green]]
        # Confirm that the pre-change board does not have the changes
        for position, tile_spec in changes:
            if board[position] == tile_spec:
                self.fail('Unexpectedly found one of the changes specified'
                          'by the test:\n{}\nin the pre-change board:'
                          '\n{}'.format((position, tile_spec), board))
        # Apply the changes
        board._change(changes)
        # Confirm that the post-change board has the changes
        for position, tile_spec in changes:
            self.assertEqual(board[position], tile_spec)

    # Execution - match (core behavior)
    def test__match_finds_simple_matches(self):
        simple_matches_board_string = 'r...yyyy\n' \
                                      'rs......\n' \
                                      'r*......\n' \
                                      '.s......\n' \
                                      '........\n' \
                                      '.......b\n' \
                                      '.......b\n' \
                                      'gggg...b'
        board = Board(simple_matches_board_string)
        matched_groups = list(board._match())
        matched_groups_spec = [[(0, 0), (1, 0), (2, 0)],  # red
                               [(0, 4), (0, 5), (0, 6), (0, 7)],  # yellow
                               [(1, 1), (2, 1), (3, 1)],  # skull / skullbomb
                               [(5, 7), (6, 7), (7, 7)],  # blue
                               [(7, 0), (7, 1), (7, 2), (7, 3)]]  # green
        self.assertItemsEqual(matched_groups, matched_groups_spec,
                              'Expected to get matches for all the tiles'
                              ' on this board:\n{}'
                              '\nlike this:\n{}'
                              '\nbut got this:\n{}'.format(board,
                                                           matched_groups_spec,
                                                           matched_groups))

    def test__match_finds_overlapping_matches(self):
        overlapping_matches_board_string = 'r.......\n' \
                                           'rrrr....\n' \
                                           'r.......\n' \
                                           '........\n' \
                                           '........\n' \
                                           '........\n' \
                                           '........\n' \
                                           '........'
        board = Board(overlapping_matches_board_string)
        matched_groups = list(board._match())
        matched_groups_spec = [[(0, 0), (1, 0), (2, 0)],  # vertical
                               [(1, 0), (1, 1), (1, 2), (1, 3)]]  # horizontal
        self.assertItemsEqual(matched_groups, matched_groups_spec,
                              'Expected to get overlapping matches on'
                              ' this board:\n{}'
                              '\nlike this:\n{}'
                              '\nbut got this:\n{}'.format(board,
                                                           matched_groups_spec,
                                                           matched_groups))

    def test__match_finds_wildcard_matches(self):
        wildcard_matches_board_string = '........\n' \
                                        'rr3.....\n' \
                                        'r3r.....\n' \
                                        'r33.....\n' \
                                        '3rr.....\n' \
                                        '3r3.....\n' \
                                        '33r.....\n' \
                                        '........'
        board = Board(wildcard_matches_board_string)
        matched_groups = list(board._match())
        # lots of matches:   6 short horizontal; 3 long vertical
        matched_groups_spec = [[(1, 0), (1, 1), (1, 2)],
                               [(2, 0), (2, 1), (2, 2)],
                               [(3, 0), (3, 1), (3, 2)],
                               [(4, 0), (4, 1), (4, 2)],
                               [(5, 0), (5, 1), (5, 2)],
                               [(6, 0), (6, 1), (6, 2)],
                               [(1, 0), (2, 0), (3, 0), (4, 0), (5, 0), (6, 0)],
                               [(1, 1), (2, 1), (3, 1), (4, 1), (5, 1), (6, 1)],
                               [(1, 2), (2, 2), (3, 2), (4, 2), (5, 2), (6, 2)]]
        self.assertItemsEqual(matched_groups, matched_groups_spec,
                              'Expected to get wildcard matches on'
                              ' this board:\n{}'
                              '\nlike this:\n{}'
                              '\nbut got this:\n{}'.format(board,
                                                           matched_groups_spec,
                                                           matched_groups))

    def test__match_ignores_matches_with_only_wildcards(self):
        wildcard_only_board_string = '.333....\n' \
                                     '.4......\n' \
                                     '.5......\n' \
                                     '.6......\n' \
                                     '........\n' \
                                     '........\n' \
                                     '........\n' \
                                     '........'
        board = Board(wildcard_only_board_string)
        matched_groups = list(board._match())
        matched_groups_spec = []  # empty. no matches
        self.assertItemsEqual(matched_groups, matched_groups_spec,
                              'Expected to get no matches on this board:\n{}'
                              '\nbut got this:'
                              '\n{}'.format(board, matched_groups))

    # Execution - destroy (core behavior)
    def test__destroy_empty_target_groups_returns_empty_destroyed_groups(self):
        board = Board(self._board_string_all_tiles)
        empty_position_groups = list()
        destroyed_tile_groups = board._destroy(empty_position_groups)
        no_destroyed_tile_groups = list()
        self.assertItemsEqual(destroyed_tile_groups, no_destroyed_tile_groups,
                              'Expected to find no destroyed tile groups but'
                              ' got {}'.format(no_destroyed_tile_groups))

    def test__destroy_simple_target_group_returns_same_destroyed_group(self):
        board = Board(self._board_string_all_tiles)
        simple_position_group = [(0, 0), (0, 1), (0, 2), (0, 3)]  # top row
        simple_position_groups = [simple_position_group]
        destroyed_tile_groups = board._destroy(simple_position_groups)
        destroyed_tile_group_spec = [Tile('r'), Tile('g'), Tile('b'), Tile('y')]
        destroyed_tile_groups_spec = [destroyed_tile_group_spec]
        self.assertItemsEqual(destroyed_tile_groups, destroyed_tile_groups_spec,
                              'Expected to find these destroyed groups:\n{}'
                              '\nbut found:'
                              '{}'.format(destroyed_tile_groups_spec,
                                          destroyed_tile_groups))

    def test__destroy_simple_target_group_destroys_exactly_targets(self):
        board = Board(self._board_string_all_tiles)
        simple_position_group = [(0, 0), (0, 1), (0, 2), (0, 3)]  # top row
        simple_position_groups = [simple_position_group]
        # Confirm first that the positions are not empty
        for position in simple_position_group:
            self.assertFalse(board[position].is_blank(),
                             'Expected position {} not to be blank before'
                             ' destruction but found blank.'.format(position))
        # Run destroy
        board._destroy(simple_position_groups)
        # Confirm after that the positions are now empty
        for position in simple_position_group:
            self.assertTrue(board[position].is_blank(),
                            'Expected position {} to be blank after'
                            ' destruction but found'
                            ' ({})'.format(position, board[position]))

    def test__destroy_skullbomb_chain_reaction_returns_tiles_separately(self):
        board = Board(self._board_string_skull_bomb_reaction)
        mid_chain_position_group = [(5, 7)]  # middle of skullbomb chain
        mid_chain_position_groups = [mid_chain_position_group]
        sb, r, g, b, y = Tile('*'), Tile('r'), Tile('g'), Tile('b'), Tile('y')
        destroyed_tile_groups_spec = [[sb]] * 8 + [[r], [g], [b], [y]]
        destroyed_tile_groups = board._destroy(mid_chain_position_groups)
        self.assertItemsEqual(destroyed_tile_groups, destroyed_tile_groups_spec,
                              'Expected to see all appropriate tiles in'
                              'separate groups like this:\n{}'
                              '\nbut found this:'
                              '\n{}'.format(destroyed_tile_groups_spec,
                                            destroyed_tile_groups))

    def test__destroy_skullbomb_chain_reaction_destroys_around_skullbombs(self):
        board = Board(self._board_string_skull_bomb_reaction)
        mid_chain_position_group = [(5, 7)]  # middle of skullbomb chain
        mid_chain_position_groups = [mid_chain_position_group]
        board._destroy(mid_chain_position_groups)
        self.assertTrue(board.is_empty(),
                        'Expected skullbomb chain reaction to destroy'
                        ' everything on this board:\n{}\nbut got this result:'
                        '\n{}'.format(self._board_string_skull_bomb_reaction,
                                      str(board)))

    # Execution - fall (core behavior)
    def test__fall_moves_tiles_down_as_far_as_possible(self):
        board = Board(self._board_string_all_tiles)
        board._fall()
        _board_string_all_tiles_fallen = '........\n' \
                                         '........\n' \
                                         '........\n' \
                                         '........\n' \
                                         '.gb.....\n' \
                                         '.xm.....\n' \
                                         'r92y....\n' \
                                         '8s*34567'
        self.assertEqual(str(board), _board_string_all_tiles_fallen,
                         'Expected these tiles:\n{}'
                         '\nto fall to the bottom like this:'
                         '\n{}\nbut got this:'
                         '\n{}'.format(self._board_string_all_tiles,
                                       _board_string_all_tiles_fallen,
                                       str(board)))

    # Execution - random_fill (core behavior)
    def test__random_fill_fills_an_empty_board(self):
        board = Board()
        if not board.is_empty():
            self.fail('Expected the starting board to be empty for testing but'
                      ' got this board:\n{}'.format(board))
        board._random_fill()
        for p in board.positions():
            self.assertFalse(board[p].is_blank())

    def test_existing_tiles_remain_after_random_fill(self):
        #prepare some positioned tiles
        tiles_with_position = ((Tile('r'), (7, 0)),
                               (Tile('g'), (6, 2)),
                               (Tile('b'), (7, 2)))
        #prepare the board
        board = Board()
        for tile, position in tiles_with_position:
            board[position] = tile
        #confirm existing tiles after random fill
        board._random_fill()
        for correct_tile, position in tiles_with_position:
            self.assertEqual(board[position], correct_tile)

    # Convenience methods
    def test_potential_swaps_returns_at_least_all_valid_swaps(self):
        board_string_two_valid_swaps = '........\n' \
                                       '........\n' \
                                       '........\n' \
                                       '........\n' \
                                       '........\n' \
                                       '........\n' \
                                       '....y...\n' \
                                       'rr.rgyy.'
        board = Board(board_string_two_valid_swaps)
        potential_swaps = list(board.potential_swaps())
        valid_swaps_spec = [((7, 2), (7, 3)),
                            ((6, 4), (7, 4))]
        for valid_swap_spec in valid_swaps_spec:
            self.assertIn(valid_swap_spec, potential_swaps,
                          'Expected to find this valid swap:\n{}'
                          '\nin the potential swaps result:\n{}'
                          '\nfor this board:\n{}'
                          '\nbut did not.'.format(valid_swap_spec,
                                                  potential_swaps,
                                                  board))

    def test_potential_swaps_ignores_blatantly_obvious_bad_swaps(self):
        # Combined test to keep specification compact
        # rr: same tiles
        board_string_bad_swaps = 'rr......\n' \
                                 '........\n' \
                                 's*......\n' \
                                 '........\n' \
                                 '........\n' \
                                 '....x...\n' \
                                 '...sgm..\n' \
                                 '....x...'
        # list of all the bad swaps that should not appear:
        bad_swaps_spec = [((0, 0), (0, 1)),  # rr: same tiles
                          ((2, 0), (2, 1)),  # s*: matching and no wildcard
                          ((6, 3), (6, 4))   # sg: surrounded by non-matches
                          ]
        board = Board(board_string_bad_swaps)
        potential_swaps = list(board.potential_swaps())
        for bad_swap_spec in bad_swaps_spec:
            self.assertNotIn(bad_swap_spec, potential_swaps,
                             'Unexpectedly found this bad swap:'
                             '\n{}\nin the list of potential swaps:'
                             '\n{}\nfor this board:'
                             '\n{}'.format(bad_swap_spec, potential_swaps,
                                           board))

    def test_copy_returns_a_board_with_a_different_underlying_array(self):
        b1 = Board()
        b2 = b1.copy()
        self.assertIsNot(b1._array, b2._array)

    def test_positions_provides_8x8_positions_as_row_column_tuples(self):
        board = Board()
        positions_spec = list()
        for row in range(8):
            for col in range(8):
                positions_spec.append((row, col))
        positions = list(board.positions())
        self.assertItemsEqual(positions, positions_spec,
                              'Expected to get all possible coordinates in an'
                              '8x8 grid:\n{}\nbut got'
                              ' this:\n{}'.format(positions_spec, positions))

    def test_is_empty_is_True_when_all_tiles_are_blanks(self):
        blank = Tile('.')
        board = Board()
        # make sure all positions are blank
        for position in board.positions():
            board[position] = blank
        self.assertTrue(board.is_empty())

    def test_str_returns_8x8_lines_with_EOL_showing_type_for_each_tile(self):
        board = Board(self._board_string_all_tiles)
        self.assertEqual(str(board), self._board_string_all_tiles)


class Test_Tile(unittest.TestCase):
    # Test Parameters
    _color_types_spec = ('r', 'g', 'b', 'y')
    _wildcard_types_spec = tuple(str(x) for x in range(2, 10))
    _skull_types_spec = ('s', '*')
    _unique_types_spec = ('x', 'm')
    _blank_type_spec = '.'
    _nonblank_types_spec = \
        _color_types_spec +\
        _wildcard_types_spec +\
        _skull_types_spec +\
        _unique_types_spec
    _all_types_spec = _nonblank_types_spec + (_blank_type_spec,)

    # Class attributes
    def test_base_valid_tile_types_are_exactly_specified_types(self):
        self.assertItemsEqual(Tile._all_types, self._all_types_spec)

    # Special methods
    def test_str_returns_the_type_character(self):
        for tile_type in self._all_types_spec:
            tile = Tile(tile_type)
            self.assertEqual(tile_type, str(tile))

    def test___eq___returns_True_for_same_tile_type_only(self):
        for tile_type in self._all_types_spec:
            tile = Tile(tile_type)
            for other_tile_type in self._all_types_spec:
                other_tile = Tile(other_tile_type)
                if tile._type == other_tile._type:
                    self.assertTrue(tile == other_tile)
                else:
                    self.assertFalse(tile == other_tile)

    def test___ne___returns_False_for_same_tile_type_only(self):
        for tile_type in self._all_types_spec:
            tile = Tile(tile_type)
            for other_tile_type in self._all_types_spec:
                other_tile = Tile(other_tile_type)
                if tile._type == other_tile._type:
                    self.assertFalse(tile != other_tile)
                else:
                    self.assertTrue(tile != other_tile)

    # Instance creation
    def test___init___from_all_types_works(self):
        for all_type in self._all_types_spec:
            try:
                Tile(all_type)
            except Exception as e:
                self.fail('Unexpectedly failed to create a tile with "{0}"'
                          ' with error: {1}'.format(all_type, e))

    def test___init___from_non_allowed_type_raises_ValueError(self):
        inall_type = 'z'
        self.assertTrue(inall_type not in self._all_types_spec,
                        'Specification is using a valid character to test'
                        'invalid characters. Please fix the spec.')
        self.assertRaises(ValueError, Tile, inall_type)

    # Matching
    def test_matches_for_blank_is_False_for_all_types_including_blank(self):
        blank = Tile('.')
        for other_type in self._all_types_spec:
            other = Tile(other_type)
            self.assertFalse(blank.matches(other))

    def test_matches_for_color_is_True_for_same_color_and_wildcards_only(self):
        # Combined test for ease of understanding the specification
        # For each color, confirm same color True, wildcards True, others False
        for color_type in self._color_types_spec:
            color = Tile(color_type)
            for other_type in self._all_types_spec:
                other = Tile(other_type)
                if other_type == color_type:
                    self.assertTrue(color.matches(other),
                                    'Color ({0}) should match itself'
                                    ' but does not.'.format(color_type,
                                                            other_type))
                elif other.is_wildcard():
                    self.assertTrue(color.matches(other),
                                    'Color ({0}) should match wildcard ({1})'
                                    ' but does not.'.format(color_type,
                                                            other_type))
                else:
                    self.assertFalse(color.matches(other),
                                     'Color ({0}) should not match other ({1})'
                                     ' but it does.'.format(color_type,
                                                            other_type))

    def test_matches_for_wildcard_is_True_for_colors_and_wildcards_only(self):
        # Combined test for ease of understanding the specification
        # For each wildcard, confirm colors True, wildcards True, others False
        for wildcard_type in self._wildcard_types_spec:
            wildcard = Tile(wildcard_type)
            for other_type in self._all_types_spec:
                other = Tile(other_type)
                if other.is_color():
                    self.assertTrue(wildcard.matches(other),
                                    'Wildcard ({0}) should match color ({1})'
                                    ' but does not.'.format(wildcard_type,
                                                            other_type))
                elif other.is_wildcard():
                    self.assertTrue(wildcard.matches(other),
                                    'Wildcard ({0}) should match wildcard ({1})'
                                    ' but does not.'.format(wildcard_type,
                                                            other_type))
                else:
                    self.assertFalse(wildcard.matches(other),
                                     'Wildcard ({0}) should not match other'
                                     ' ({1}) but it does.'.format(wildcard_type,
                                                                  other_type))

    def test_matches_for_skull_is_True_for_skulls_and_skullbombs_only(self):
        # Combined test for ease of understanding the specification
        skull_type = 's'
        skull = Tile(skull_type)
        for other_type in self._all_types_spec:
            other = Tile(other_type)
            if other_type == skull_type:
                self.assertTrue(skull.matches(other),
                                'Skull should match itself but does not.')
            elif other.is_skullbomb():
                self.assertTrue(skull.matches(other),
                                'Skull should match skullbomb but does not.')
            else:
                self.assertFalse(skull.matches(other),
                                 'Skull should not match other ({0}) but'
                                 ' does.'.format(other_type))

    def test_matches_for_skullbomb_is_True_for_skulls_and_skullbombs_only(self):
        # Combined test for ease of understanding the specification
        skull_type = 's'
        skullbomb_type = '*'
        skullbomb = Tile(skullbomb_type)
        for other_type in self._all_types_spec:
            other = Tile(other_type)
            if other_type == skull_type:
                self.assertTrue(skullbomb.matches(other),
                                'Skullbomb should match skull but does not.')
            elif other.is_skullbomb():
                self.assertTrue(skullbomb.matches(other),
                                'Skullbomb should match itself but does not.')
            else:
                self.assertFalse(skullbomb.matches(other),
                                 'Skullbomb should not match other ({0}) but'
                                 ' does.'.format(other_type))

    def test_matches_for_experience_is_True_for_experience_only(self):
        experience_type = 'x'
        experience = Tile(experience_type)
        for other_type in self._all_types_spec:
            other = Tile(other_type)
            if other_type == experience_type:
                self.assertTrue(experience.matches(other),
                                'Experience should match itself but does not.')
            else:
                self.assertFalse(experience.matches(other),
                                 'Experience should not match other ({0})'
                                 ' but does.'.format(other_type))
                
    def test_matches_for_money_is_True_for_money_only(self):
        money_type = 'm'
        money = Tile(money_type)
        for other_type in self._all_types_spec:
            other = Tile(other_type)
            if other_type == money_type:
                self.assertTrue(money.matches(other),
                                'money should match itself but does not.')
            else:
                self.assertFalse(money.matches(other),
                                 'money should not match other ({0})'
                                 ' but does.'.format(other_type))

    # Random Tiles
    def test_random_tile_provides_a_random_tile_according_to_distribution(self):
        n = 10000  # size of sample for checking distribution
        tolerance = 0.05  # i.e. 1% error tolerance
        delta = round(n * tolerance)
        weights = Tile._random_weights
        total_weight = sum(weights.values())
        counts_spec = {tile_type: float(n * weights[tile_type]) / total_weight
                       for tile_type in weights.keys()}
        counts = {tile_type: 0 for tile_type in weights.keys()}
        for i in range(n):
            counts[Tile.random_tile()._type] += 1
        for tile_type, tile_count in counts.items():
            tile_count_spec = counts_spec[tile_type]
            self.assertAlmostEqual(tile_count, tile_count_spec, delta=delta)

    # Convenient methods
    def test_is_skullbomb_for_a_skullbomb_returns_True(self):
        skullbomb = Tile('*')
        self.assertTrue(skullbomb.is_skullbomb())

    def test_is_skullbomb_for_a_non_skullbomb_returns_False(self):
        skull = Tile('s')
        self.assertFalse(skull.is_skullbomb())

    def test_is_blank_for_a_blank_returns_True(self):
        blank = Tile('.')
        self.assertTrue(blank.is_blank())

    def test_is_blank_for_a_non_blank_returns_False(self):
        skull = Tile('s')
        self.assertFalse(skull.is_blank())

    def test_is_wildcard_for_a_wildcard_returns_True(self):
        wildcards = (Tile(str(x)) for x in range(2, 10))
        for wildcard in wildcards:
            self.assertTrue(wildcard.is_wildcard())

    def test_is_wildcard_for_a_non_wildcard_returns_False(self):
        skull = Tile('s')
        self.assertFalse(skull.is_wildcard())

    def test_is_color_for_a_color_returns_True(self):
        colors = (Tile(c) for c in ('r', 'g', 'b', 'y'))
        for color in colors:
            self.assertTrue(color.is_color())

    def test_is_color_for_a_non_color_returns_False(self):
        skull = Tile('s')
        self.assertFalse(skull.is_color())


if __name__ == '__main__':
    unittest.main()
