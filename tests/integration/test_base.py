import unittest
from os import path

from mock import patch
from investigators.visuals import cv2

from pqhelper.base import Actor, Board, Tile
from pqhelper.base import BaseTransition, Swap, ChainReaction, EOT, Filtered
from pqhelper.base import Game, State, StateInvestigator

from pqhelper.base import TreeNode

# silly workaround to avoid false warnings in PyCharm
patch.object = patch.object


class Test_StateInvestigator(unittest.TestCase):
    # Capture
    def test_get_capture_returns_None_if_game_can_not_be_found_on_screen(self):
        si = StateInvestigator()
        finder = si._game_finders['capture']
        with patch.object(finder, 'locate_in') as m_locate_in:
            m_locate_in.return_value = None
            board = si.get_capture()
        self.assertIsNone(board)

    def test_get_capture_returns_None_if_tile_can_not_be_identified(self):
        si = StateInvestigator()
        identifier = si._board_tools['tile_id']
        with patch.object(identifier, 'identify') as m_identify:
            m_identify.return_value = None
            board = si.get_capture()
        self.assertIsNone(board)

    def test_get_capture_returns_correct_capture_board(self):
        board_string_spec = '........\n'\
                            '........\n'\
                            '..mbgm..\n'\
                            '.mxgbrm.\n'\
                            'my*gb*gm\n'\
                            'yrrxrxxg\n'\
                            'ymxyyrmg\n'\
                            'ssxssrss'
        si = StateInvestigator()
        here = path.abspath(path.split(__file__)[0])
        screen_path = path.join(here, 'capture.png')
        screen = cv2.imread(screen_path)
        self.assertIsNotNone(screen)  # just to avoid confusing errors later
        with patch.object(si, '_screen_shot') as m_screen_shot:
            m_screen_shot.return_value = screen
            board = si.get_capture()
        self.assertEqual(str(board), board_string_spec)

    # Versus
    def test_get_versus_returns_None_if_game_can_not_be_found_on_screen(self):
        si = StateInvestigator()
        finder = si._game_finders['versus']
        with patch.object(finder, 'locate_in') as m_locate_in:
            m_locate_in.return_value = None
            board, player, opponent = si.get_versus()
        self.assertIsNone(board)
        self.assertIsNone(player)
        self.assertIsNone(opponent)

    def test_get_versus_returns_None_board_if_tile_can_not_be_identified(self):
        si = StateInvestigator()
        identifier = si._board_tools['tile_id']
        with patch.object(identifier, 'identify') as m_identify:
            m_identify.return_value = None
            board, player, opponent = si.get_versus()
        self.assertIsNone(board)

    def test_get_versus_returns_correct_board_player_and_opponent(self):
        si = StateInvestigator()
        here = path.abspath(path.split(__file__)[0])
        screen_path = path.join(here, 'versus.png')
        screen = cv2.imread(screen_path)
        self.assertIsNotNone(screen)  # just to avoid confusing errors later
        # get the versus parts
        with patch.object(si, '_screen_shot') as m_screen_shot:
            m_screen_shot.return_value = screen
            board, player, opponent = si.get_versus()
        # confirm that the board is correct
        board_string_spec = 'smrbmsgs\n'\
                            'bbyxxysm\n'\
                            'ysmggssm\n'\
                            's4*xssmg\n'\
                            'sbmsxgxx\n'\
                            'xmgssgms\n'\
                            'xsgmmsgs\n'\
                            'ggsxggxm'
        self.assertEqual(str(board), board_string_spec)
        # current specification is based on relative values rather than absolute
        # due to lack of character recognition on the StateInvestigator
        health_max_spec = 100
        health_tolerance = 20  # +/- 20%
        mana_max_spec = 40
        mana_tolerance = 8  # +/- 20%
        # confirm that the player is correct
        p_health_spec = health_max_spec * float(95) / 120  # max is appropriate
        p_g_spec = mana_max_spec * float(14) / 30  # max is approximate
        p_r_spec = mana_max_spec * float(29) / 40  # max is approximate
        p_y_spec = mana_max_spec * float(4) / 40  # max is approximate
        p_b_spec = mana_max_spec * float(7) / 30  # max is approximate
        self.assertAlmostEqual(player.health, p_health_spec,
                               delta=health_tolerance)
        self.assertAlmostEqual(player.g, p_g_spec, delta=mana_tolerance)
        self.assertAlmostEqual(player.r, p_r_spec, delta=mana_tolerance)
        self.assertAlmostEqual(player.y, p_y_spec, delta=mana_tolerance)
        self.assertAlmostEqual(player.b, p_b_spec, delta=mana_tolerance)
        self.assertEqual(player.health_max, health_max_spec)
        self.assertEqual(player.g_max, mana_max_spec)
        self.assertEqual(player.r_max, mana_max_spec)
        self.assertEqual(player.y_max, mana_max_spec)
        self.assertEqual(player.b_max, mana_max_spec)
        # confirm that the opponent is correct
        o_health_spec = health_max_spec * float(51) / 114  # max is approximate
        o_g_spec = mana_max_spec * float(8) / 30  # max is approximate
        o_r_spec = mana_max_spec * float(32) / 32  # max is approximate
        o_y_spec = mana_max_spec * float(15) / 28  # max is approximate
        o_b_spec = mana_max_spec * float(23) / 28  # max is approximate
        self.assertAlmostEqual(opponent.health, o_health_spec,
                               delta=health_tolerance)
        self.assertAlmostEqual(opponent.g, o_g_spec, delta=mana_tolerance)
        self.assertAlmostEqual(opponent.r, o_r_spec, delta=mana_tolerance)
        self.assertAlmostEqual(opponent.y, o_y_spec, delta=mana_tolerance)
        self.assertAlmostEqual(opponent.b, o_b_spec, delta=mana_tolerance)
        self.assertEqual(opponent.health_max, health_max_spec)
        self.assertEqual(opponent.g_max, mana_max_spec)
        self.assertEqual(opponent.r_max, mana_max_spec)
        self.assertEqual(opponent.y_max, mana_max_spec)
        self.assertEqual(opponent.b_max, mana_max_spec)

    def test_get_versus_returns_Nonex3_when_game_search_fails(self):
        si = StateInvestigator()
        finder = si._game_finders['versus']
        with patch.object(finder, 'locate_in') as m_locate_in:
            m_locate_in.return_value = None
            board, player, opponent = si.get_versus()
        self.assertIsNone(board)
        self.assertIsNone(player)
        self.assertIsNone(opponent)

    def test_get_versus_returns_board_None_when_board_extract_fails(self):
        si = StateInvestigator()
        identifier = si._board_tools['tile_id']
        with patch.object(identifier, 'identify') as m_identify:
            m_identify.return_value = None
            board, _, _ = si.get_versus()
        self.assertIsNone(board)

    def test_generic_versus_actors_produces_average_player_and_opponent(self):
        # this is a stopgap until actor investigation is implemented
        si = StateInvestigator()
        player, opponent = si.generic_versus_actors()
        health_spec, health_max_spec = 50, 100
        mana_spec, mana_max_spec = 20, 40
        unused_spec, unused_max_spec = 0, 0
        for actor in (player, opponent):
            self.assertEqual(actor.health, health_spec)
            self.assertEqual(actor.g, mana_spec)
            self.assertEqual(actor.r, mana_spec)
            self.assertEqual(actor.y, mana_spec)
            self.assertEqual(actor.b, mana_spec)
            self.assertEqual(actor.x, unused_spec)
            self.assertEqual(actor.m, unused_spec)
            self.assertEqual(actor.h, unused_spec)
            self.assertEqual(actor.c, unused_spec)
            self.assertEqual(actor.health_max, health_max_spec)
            self.assertEqual(actor.g_max, mana_max_spec)
            self.assertEqual(actor.r_max, mana_max_spec)
            self.assertEqual(actor.y_max, mana_max_spec)
            self.assertEqual(actor.b_max, mana_max_spec)
            self.assertEqual(actor.x_max, unused_max_spec)
            self.assertEqual(actor.m_max, unused_max_spec)
            self.assertEqual(actor.h_max, unused_max_spec)
            self.assertEqual(actor.c_max, unused_max_spec)


class Test_Game(unittest.TestCase):
    """Confirm that Game simulates a game of PQ."""
    # Test Parameters
    board_string_two_paths = '........\n'\
                             '........\n'\
                             'g......g\n'\
                             'g......g\n'\
                             's......s\n'\
                             's......s\n'\
                             'xg....gx\n'\
                             'rsrryysy'

    turn_1_eot_board_strings = ['........\n'
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

    turn_2_left_eot_board_strings = ['........\n'
                                     '........\n'
                                     '.......g\n'
                                     '.......g\n'
                                     '.......s\n'
                                     'g......s\n'
                                     'g.....gx\n'
                                     'xg..yysy',
                                     '........\n'
                                     '........\n'
                                     'g......g\n'
                                     'g......g\n'
                                     's......s\n'
                                     's......s\n'
                                     'x......x\n'
                                     'sg....gs']

    def test_Game_has_internal_indicator_to_random_fill_boards_or_not(self):
        game = generic_game()
        confirm_attribute(game, 'random_fill')

    # Run simulation of one turn for one state
    def test_ends_of_one_state_raises_TypeError_if_not_exactly_one_arg(self):
        game = generic_game()
        # fail for zero args
        generator = game.ends_of_one_state()
        self.assertRaises(TypeError, generator.next)
        # fail for two args
        root_state = generic_state()
        eot = EOT(False)
        generator = game.ends_of_one_state(root=root_state, root_eot=eot)
        self.assertRaises(TypeError, generator.next)

    def test_ends_of_one_state_raises_ValueError_for_non_root_state(self):
        game = generic_game()
        root_state = generic_state()
        child_state = generic_state()
        root_state.graft_child(child_state)
        generator = game.ends_of_one_state(root=child_state)
        self.assertRaises(ValueError, generator.next)

    def test_ends_of_one_state_raises_TypeError_for_non_eot_transition(self):
        game = generic_game()
        non_eot_transition = ChainReaction()
        generator = game.ends_of_one_state(root_eot=non_eot_transition)
        self.assertRaises(TypeError, generator.next)

    def test_ends_of_one_state_generates_all_leaves_as_EOT(self):
        game = generic_game()
        root = generic_state(board=Board(self.board_string_two_paths))
        # try to complete generation by converting to list
        ends_of_turn = list(game.ends_of_one_state(root))
        leaves = list(root.leaves)
        # confirm leaves === generated ends of turn
        self.assertItemsEqual(ends_of_turn, leaves)
        # confirm all supposed ends of turn are actually EOT
        for result in ends_of_turn:
            self.assertIsInstance(result, EOT)

    def test_ends_of_one_state_from_root_generates_2_branches(self):
        game = generic_game()
        root = generic_state(board=Board(self.board_string_two_paths))
        # try to complete generation by converting to list
        eots = list(game.ends_of_one_state(root=root))
        # confirm eots have correct boards
        end_boards = [str(eot.parent.board) for eot in eots]
        self.assertItemsEqual(end_boards, self.turn_1_eot_board_strings,
                              'Expected to get these end boards:\n{}\n{}\n'
                              'but got these:\n{}'
                              ''.format(self.turn_1_eot_board_strings[0],
                                        self.turn_1_eot_board_strings[1],
                                        '\n'.join(end_boards)))

    def test_ends_of_one_state_from_left_eot_generates_2_branches(self):
        game = generic_game()
        # simulate an eot
        last = generic_state(board=Board(self.turn_1_eot_board_strings[0]),
                             turn=1, actions_remaining=0)
        eot = EOT(False)
        last.graft_child(eot)
        # provide the eot to the simulation and confirm the results are correct
        eots = list(game.ends_of_one_state(root_eot=eot))
        end_boards = [str(eot.parent.board) for eot in eots]
        self.assertItemsEqual(end_boards,
                              self.turn_2_left_eot_board_strings,
                              'Expected to get these end boards:\n{}\n{}\n'
                              'but got these:\n{}'
                              ''.format(self.turn_2_left_eot_board_strings[0],
                                        self.turn_2_left_eot_board_strings[1],
                                        '\n'.join(end_boards)))
        
    def test_ends_of_one_state_generates_chain_reaction_result(self):
        chain_board_string = '........\n'\
                             '........\n'\
                             '........\n'\
                             '........\n'\
                             'x.......\n'\
                             'r.......\n'\
                             'r.......\n'\
                             'xrx.....'
        game = generic_game()
        root = generic_state(board=Board(chain_board_string))
        # run the simulation
        eots = list(game.ends_of_one_state(root=root))
        # confirm the following sequence
        # root_state -> swap -> result_state -> chain -> result_state -> eot
        tree_strings_spec = ('State', 'Swap', 'State', 'Chain', 'State', 'EOT')
        tree_strings = list()
        node = root
        while node:
            tree_strings.append(str(node))
            try:
                node = node.children[0]
            except IndexError:
                break
        self.assertEqual(len(tree_strings), len(tree_strings_spec))  # safety
        for s, s_spec in zip(tree_strings, tree_strings_spec):
            self.assertIn(s_spec, s)
        # confirm that the final board is empty (chain reaction succeeded
        leaf = eots[0]
        self.assertEqual(leaf.parent.board, Board())

    def test_ends_of_one_state_attaches_mana_drain_to_blank_root(self):
        game = generic_game(False)
        root = generic_state(board=Board())
        list(game.ends_of_one_state(root=root))
        eot = root.children[0]
        # confirm that there is only one new node
        self.assertEqual(len(root.children), 1)
        self.assertEqual(len(eot.children), 0)
        # confirm that the node is mana_drain
        self.assertTrue(eot.is_mana_drain)

    def test_ends_of_one_state_attaches_mana_drain_to_mana_drain_result(self):
        end_of_turn_is_mana_drain_board_string = '........\n'\
                                                 '........\n'\
                                                 '........\n'\
                                                 '........\n'\
                                                 '........\n'\
                                                 '........\n'\
                                                 '........\n'\
                                                 'rr.r....'
        game = generic_game(False)
        board = Board(end_of_turn_is_mana_drain_board_string)
        root = generic_state(board=board)
        eots = list(game.ends_of_one_state(root=root))
        eot = eots[0]
        # confirm that the node is mana_drain
        self.assertTrue(eot.is_mana_drain)

    def test_ends_of_one_state_sets_random_board_on_mana_drain_state(self):
        use_random_fill = True
        game = generic_game(use_random_fill)
        empty_board = Board()
        root = generic_state(board=empty_board)
        # run the simulation
        ends_of_turn = list(game.ends_of_one_state(root=root))
        last_state_board = ends_of_turn[0].parent.board
        # confirm that the end state is full
        for p, tile in last_state_board.positions_with_tile():
            tile = last_state_board[p]
            self.assertFalse(tile.is_blank(),
                             'Unexpectedly found a blank when the board'
                             ' should be full:\n{}'.format(last_state_board))
        # confirm that the end state is stable
        x, destructions = last_state_board.execute_once()
        self.assertFalse(destructions,
                         'Unexpectedly found destructions when the board'
                         ' should be stable')

    @patch('pqhelper.base.Game._disallow_state', lambda *args: True)
    def test_ends_of_one_state_attaches_Filtered_when_a_state_fails_test(self):
        game = generic_game(False)
        root = generic_state(board=Board(self.board_string_two_paths))
        list(game.ends_of_one_state(root=root))
        # confirm that the root was filtered and tagged
        leaf = list(root.leaves)[0]
        self.assertIsInstance(leaf, Filtered)

    @patch('pqhelper.base.Game._disallow_state',
           lambda self_, state: state.board.is_empty())
    def test_ends_of_one_state_attaches_Filtered_when_a_chain_fails_test(self):
        # the patch causes a failure only during the chain reaction part of sim
        chain_board_string = '........\n'\
                             '........\n'\
                             '........\n'\
                             '........\n'\
                             'x.......\n'\
                             'r.......\n'\
                             'r.......\n'\
                             'xrx.....'
        game = generic_game()
        root = generic_state(board=Board(chain_board_string))
        # run the simulation
        list(game.ends_of_one_state(root=root))
        # confirm that the leaf is filtered, not EOT
        leaf = list(root.leaves)[0]
        self.assertIsInstance(leaf, Filtered)

    def test_ends_of_one_state_simulates_bonus_action_for_match_of_4(self):
        bonus_action_board_string = '........\n'\
                                    '........\n'\
                                    '........\n'\
                                    '........\n'\
                                    '2.......\n'\
                                    '2.......\n'\
                                    'xrx.x...\n'\
                                    '2mm.s...'
        after_bonus_board_string = '........\n'\
                                   '........\n'\
                                   '........\n'\
                                   '........\n'\
                                   '........\n'\
                                   '........\n'\
                                   '........\n'\
                                   '.mm.s...'
        game = generic_game(False)
        root = generic_state(board=Board(bonus_action_board_string))
        eots = list(game.ends_of_one_state(root=root))
        last_state = eots[0].parent
        # confirm still on turn 1
        self.assertEqual(last_state.turn, 1)
        # confirm board that is possible only after an extra action
        self.assertEqual(str(last_state.board), after_bonus_board_string)

    def test_ends_of_one_state_simulates_tile_effects_on_actors(self):
        # this board has the same move available in the first and second turns
        # the move gives x to the active actor and damages the passive actor
        # the "m" tiles just allow the result not to be identified as mana drain
        board_string = '........\n'\
                       '........\n'\
                       '........\n'\
                       '..m.....\n'\
                       '..s.s...\n'\
                       '..s.s...\n'\
                       '..x.xm..\n'\
                       'xxsmsxx.'
        game = generic_game(False)
        # setup the root
        v = (base, maximum) = (50, 100)
        player = generic_actor('player', v, v, v, v, v, v, v, v, v)
        opponent = generic_actor('opponent', v, v, v, v, v, v, v, v, v)
        root = generic_state(board=Board(board_string),
                             player=player, opponent=opponent)
        # turn 1 values
        turn_1_player_high = ('x',)
        turn_1_player_same = ('health', 'r', 'g', 'b', 'y', 'm', 'h', 'c')
        turn_1_player_low = ()
        turn_1_opponent_high = ()
        turn_1_opponent_same = ('r', 'g', 'b', 'y', 'x', 'm', 'h', 'c')
        turn_1_opponent_low = ('health',)
        # turn 2 values
        turn_2_both_high = ('x',)
        turn_2_both_same = ('r', 'g', 'b', 'y', 'm', 'h', 'c')
        turn_2_both_low = ('health',)

        def confirm_values(turn, actor, highs, sames, lows):
            for high in highs:
                new_value = getattr(actor, high)
                self.assertGreater(new_value, base,
                                   'Expected {} to be greater than {} for {}'
                                   ' on turn {} but got {}.'
                                   ''.format(high, base, actor.name,
                                             turn, new_value))
            for same in sames:
                new_value = getattr(actor, same)
                self.assertEqual(new_value, base,
                                 'Expected {} to be equal to {} for {}'
                                 ' on turn {} but got {}.'
                                 ''.format(same, base, actor.name,
                                           turn, new_value))
            for low in lows:
                new_value = getattr(actor, low)
                self.assertLess(new_value, base,
                                'Expected {} to be less than {} for {}'
                                ' on turn {} but got {}.'
                                ''.format(low, base, actor.name,
                                          turn, new_value))
        # turn 1: confirm player gains exp and opponent loses health
        eots = list(game.ends_of_one_state(root=root))
        one_eot = eots[0]  # either eot is fine since the results are the same
        confirm_values(1, one_eot.parent.player,
                       turn_1_player_high,
                       turn_1_player_same,
                       turn_1_player_low)
        confirm_values(1, one_eot.parent.opponent,
                       turn_1_opponent_high,
                       turn_1_opponent_same,
                       turn_1_opponent_low)
        # turn 2: confirm opposite happens
        eots = list(game.ends_of_one_state(root_eot=one_eot))
        one_eot = eots[0]  # either eot is fine since the results are the same
        confirm_values(2, one_eot.parent.player,
                       turn_2_both_high,
                       turn_2_both_same,
                       turn_2_both_low)
        confirm_values(2, one_eot.parent.opponent,
                       turn_2_both_high,
                       turn_2_both_same,
                       turn_2_both_low)

    # Breadth-First whole turn simulation
    def test_ends_of_whole_next_turn_raises_ValueError_for_non_root(self):
        # confirm node with parent fails
        game = generic_game()
        root = generic_state()
        child = generic_state()
        root.graft_child(child)
        self.assertRaises(ValueError, game.ends_of_next_whole_turn(child).next)

    def test_ends_of_whole_next_turn_generates_all_results_per_turn(self):
        game = generic_game()
        root = generic_state(board=Board(self.board_string_two_paths))
        # generate each level and confirm counts at the end of each
        # this was confirmed on paper. each side of the board has only
        # one way to be swapped each turn, so has an easy pattern
        results_per_turn_spec = {1: 2,
                                 2: 4,
                                 3: 8,
                                 4: 14,
                                 5: 20,
                                 6: 20,
                                 7: 0}  # ignores mana drains
        eots = tuple()  # just to satisfy the IDE
        # check each turn
        for i in range(1, len(results_per_turn_spec) + 1):
            eots = list(game.ends_of_next_whole_turn(root))
            eot_len = len(eots)
            eot_len_spec = results_per_turn_spec[i]
            self.assertEqual(eot_len, eot_len_spec,
                             'Unexpectedly found {} results for turn {}'
                             ' instead of expected {} results.'
                             ''.format(eot_len, i, eot_len_spec))
        # confirm content of final ends of turn all the same mana drain
        final_board_string = '........\n'\
                             '........\n'\
                             '........\n'\
                             '........\n'\
                             '........\n'\
                             '........\n'\
                             '........\n'\
                             '.x....x.'
        for eot in root.leaves:
            self.assertEqual(str(eot.parent.board), final_board_string,
                             'Unexpectedly got this end of turn board:\n{}'
                             '\nbut was expecting this one:\n{}'
                             ''.format(str(eot.parent.board),
                                       final_board_string))

    # Depth-First continuous simulation
    def test_all_ends_of_turn_raises_ValueError_for_non_root(self):
        # confirm node with parent fails
        game = generic_game()
        root = generic_state()
        child = generic_state()
        root.graft_child(child)
        self.assertRaises(ValueError, game.all_ends_of_turn(child).next)

    def test_all_ends_of_turn_generates_all_possible_ends_of_turn(self):
        game = generic_game()
        root = generic_state(board=Board(self.board_string_two_paths))
        # generate all ends of turn and confirm the total number
        # this was confirmed on paper. each side of the board has only
        # one way to be swapped each turn, so has an easy pattern
        results_per_turn_spec = {1: 2,
                                 2: 4,
                                 3: 8,
                                 4: 14,
                                 5: 20,
                                 6: 20}
        eots = list(game.all_ends_of_turn(root))
        eot_len = len(eots)
        eot_len_spec = sum(results_per_turn_spec.values())
        self.assertEqual(eot_len, eot_len_spec,
                         'Unexpectedly found {} total results instead of {} for'
                         'this board:\n{}'.format(eot_len, eot_len_spec,
                                                  self.board_string_two_paths))
        # confirm that the final board appears 20 times
        final_board_string = '........\n'\
                             '........\n'\
                             '........\n'\
                             '........\n'\
                             '........\n'\
                             '........\n'\
                             '........\n'\
                             '.x....x.'
        final_eots = filter(lambda x: x.is_mana_drain,
                            eots)
        for final_eot in final_eots:
            self.assertEqual(str(final_eot.parent.board), final_board_string,
                             'Unexpectedly got this end of turn board:\n{}'
                             '\nbut was expecting this one:\n{}'
                             ''.format(str(final_eot.parent.board),
                                       final_board_string))


class Test_State(unittest.TestCase):
    # Simulation tree behavior
    def test_State_is_instance_of_TreeNode_for_tree_behavior(self):
        state = generic_state()
        self.assertIsInstance(state, TreeNode)

    # Primary attributes
    def test_State_has_a_board(self):
        state = generic_state()
        confirm_attribute(state, 'board')

    def test_State_has_a_player_and_opponent(self):
        # Combined spec for simplicity
        state = generic_state()
        confirm_attribute(state, 'player')
        confirm_attribute(state, 'opponent')

    def test_State_has_turn_and_actions_remaining(self):
        # Combined spec for simplicity
        state = generic_state()
        confirm_attribute(state, 'turn')
        confirm_attribute(state, 'actions_remaining')

    # extra turn information
    def test_for_odd_state_active_passive_is_player_opponent(self):
        odd_state = generic_state(turn=3)
        self.assertIs(odd_state.active, odd_state.player)
        self.assertIs(odd_state.passive, odd_state.opponent)

    def test_for_even_state_active_passive_is_opponent_player(self):
        even_state = generic_state(turn=4)
        self.assertIs(even_state.passive, even_state.player)
        self.assertIs(even_state.active, even_state.opponent)

    # special methods
    def test_State_has_a_human_readable_string_with_primary_attributes(self):
        state = generic_state()
        required_strings = ('State', 'turn', 'actions remaining', 'board',
                            'children')
        state_string = str(state)
        for required_string in required_strings:
            self.assertIn(required_string, state_string)


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

    # Instance creation
    def test___init___default_is_empty_board(self):
        board = Board()
        self.assertTrue(board.is_empty())

    def test___init___with_a_board_string_of_8x8_with_EOLs_works(self):
        board = Board(self._board_string_all_tiles)
        self.assertEqual(str(board), self._board_string_all_tiles)

    # Class methods
    def test_random_start_board_produces_stable_full_board(self):
        board = Board.random_start_board()
        # Confirm it's full
        for p, tile in board.positions_with_tile():
            self.assertFalse(tile.is_blank(),
                             'Unexpectedly found a blank when the start board'
                             ' should be full:\n{}'.format(board))
        # Confirm it's stable
        x, destructions = board.execute_once()
        self.assertFalse(destructions,
                         'Unexpectedly found destructions when the start board'
                         ' should be stable')

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
        board._array.fill(Tile('.'))
        result_board, x = board.execute_once(random_fill=True)
        self.assertFalse(result_board.is_empty(),
                         'Expected to find a full board but found this:\n{}'
                         ''.format(result_board))

    def test_execute_once_without_random_fill_leaves_empty_board_empty(self):
        board = Board()
        board._array.fill(Tile('.'))
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
        board._array.fill(Tile('.'))
        board._random_fill()
        for p, tile in board.positions_with_tile():
            self.assertFalse(tile.is_blank())

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
        positions = [p for p, tile in board.positions_with_tile()]
        self.assertItemsEqual(positions, positions_spec,
                              'Expected to get all possible coordinates in an'
                              '8x8 grid:\n{}\nbut got'
                              ' this:\n{}'.format(positions_spec, positions))

    def test_is_empty_is_True_when_all_tiles_are_blanks(self):
        blank = Tile('.')
        board = Board()
        # make sure all positions are blank
        for p, tile in board.positions_with_tile():
            board[p] = blank
        self.assertTrue(board.is_empty())

    def test_str_returns_8x8_lines_with_EOL_showing_type_for_each_tile(self):
        board = Board(self._board_string_all_tiles)
        self.assertEqual(str(board), self._board_string_all_tiles)

    # Special methods
    def test___eq___returns_True_only_when_all_tiles_equal(self):
        board_1 = Board()
        board_2 = Board()
        self.assertEqual(board_1, board_2)


class Test_Tile(unittest.TestCase):
    # Test Parameters
    _color_types_spec = ('r', 'g', 'b', 'y')
    _wildcard_types_spec = tuple(str(x) for x in range(2, 10))
    _skull_types_spec = ('s', '*')
    _unique_types_spec = ('x', 'm', 'h', 'c')
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

    def test_classmethod_singleton_produces_singletons_for_each_type(self):
        for tile_type in self._all_types_spec:
            tile_1 = Tile.singleton(tile_type)
            tile_2 = Tile.singleton(tile_type)
            self.assertIs(tile_1, tile_2,
                          'singleton classmethod unexpectedly produced'
                          ' different objects for the same type: {}'
                          ''.format(tile_type))

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

    def test_matches_for_unique_types_is_True_for_same_type_only(self):
        for tile_type in self._unique_types_spec:
            tile = Tile(tile_type)
            for other_type in self._all_types_spec:
                other = Tile(other_type)
                if other_type == tile_type:
                    self.assertTrue(tile.matches(other),
                                    'Unique tile ({}) should match itself but'
                                    ' does not.'.format(tile_type))
                else:
                    self.assertFalse(tile.matches(other),
                                     'Unique tile ({}) unexpectedly matched'
                                     ' a different type ({})'
                                     ''.format(tile_type, other_type))

    # Random Tiles
    def test_random_tile_provides_a_random_tile_according_to_distribution(self):
        n = 1000  # size of sample for checking distribution
        tolerance = 0.05  # i.e. 5% error tolerance
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
    def test_is_experience_returns_true_for_experience_only(self):
        experience = Tile('x')
        self.assertTrue(experience.is_experience())
        # confirm failure of wrong types
        skull = Tile('s')
        self.assertFalse(skull.is_experience())

    def test_is_money_returns_true_for_money_only(self):
        money = Tile('m')
        self.assertTrue(money.is_money())
        # confirm failure of wrong types
        skull = Tile('s')
        self.assertFalse(skull.is_money())

    def test_is_skullbomb_returns_true_for_skullbomb_only(self):
        skullbomb = Tile('*')
        self.assertTrue(skullbomb.is_skullbomb())
        # confirm failure of wrong types
        skull = Tile('s')
        self.assertFalse(skull.is_skullbomb())

    def test_is_skull_returns_true_for_skull_only(self):
        skull = Tile('s')
        self.assertTrue(skull.is_skull())
        # confirm failure of wrong types
        red = Tile('r')
        self.assertFalse(red.is_skull())

    def test_is_blank_returns_true_for_blank_only(self):
        blank = Tile('.')
        self.assertTrue(blank.is_blank())
        # confirm failure of wrong types
        skull = Tile('s')
        self.assertFalse(skull.is_blank())

    def test_is_wildcard_returns_true_for_wildcard_only(self):
        wildcards = (Tile(str(x)) for x in range(2, 10))
        for wildcard in wildcards:
            self.assertTrue(wildcard.is_wildcard())
        # confirm failure of wrong types
        skull = Tile('s')
        self.assertFalse(skull.is_wildcard())

    def test_is_color_returns_true_for_color_only(self):
        colors = (Tile(c) for c in ('r', 'g', 'b', 'y'))
        for color in colors:
            self.assertTrue(color.is_color())
        # confirm failure of wrong types
        skull = Tile('s')
        self.assertFalse(skull.is_color())


class Test_Transitions(unittest.TestCase):
    def test_BaseTransition_is_instance_of_TreeNode_for_tree_behavior(self):
        base_transition = BaseTransition()
        self.assertIsInstance(base_transition, TreeNode)

    def test_EOT_indicates_whether_it_is_mana_drain_or_not(self):
        eot = EOT(True)
        confirm_attribute(eot, 'is_mana_drain')

    def test_Swap___init___takes_and_stores_a_position_pair(self):
        position_pair_spec = ((0, 0), (0, 1))
        swap = Swap(position_pair_spec)
        self.assertEqual(swap.position_pair, position_pair_spec)

    def test_Swap_position_pair_is_read_only(self):
        some_position_pair = ((0, 0), (0, 1))
        another_position_pair = ((0, 0), (0, 1))
        swap = Swap(some_position_pair)
        self.assertRaises(AttributeError,
                          setattr, swap, 'position_pair', another_position_pair)

    # Special methods
    def test_Transitions_have_a_human_readable_string(self):
        transition = BaseTransition()
        transition_str = str(transition)
        required_strings = ('BaseTransition', '(children:')
        for required_string in required_strings:
            self.assertIn(required_string, transition_str)


class Test_Actor(unittest.TestCase):
    # Common data
    __max_suffix = '_max'
    attributes_for_copy = ['name', 'health', 'health' + __max_suffix]
    for color_type in Test_Tile._color_types_spec:
        attributes_for_copy.append(color_type)
        attributes_for_copy.append(color_type + __max_suffix)
    for unique_type in Test_Tile._unique_types_spec:
        attributes_for_copy.append(unique_type)
        attributes_for_copy.append(unique_type + __max_suffix)

    def test_Actor_has_all_attributes_required_for_copy(self):
        # super combined spec because of connectedness with copy
        # confirms name, health, etc.
        actor = generic_actor()
        for attribute_name in self.attributes_for_copy:
            confirm_attribute(actor, attribute_name)

    def test_Actor_current_values_are_bound_by_zero_and_max(self):
        base_original, maximum = 0, 10
        base = (base_original, maximum)
        current_max_types = ('health', 'r', 'g', 'b', 'y', 'x', 'm', 'h', 'c')
        current_max_kwargs = {t: base for t in current_max_types}
        actor = generic_actor(**current_max_kwargs)
        # confirm nothing goes below zero
        for t in current_max_types:
            setattr(actor, t, -10)
            value = getattr(actor, t)
            self.assertGreaterEqual(value, 0)
        # confirm nothing goes above max
        for t in current_max_types:
            setattr(actor, t, maximum + 2)
            value = getattr(actor, t)
            self.assertLessEqual(value, maximum)

    def test_copy_returns_a_different_object_from_original(self):
        actor = generic_actor()
        actor_copy = actor.copy()
        self.assertIsNot(actor_copy, actor)

    def test_copy_of_actor_has_same_attributes(self):
        actor = generic_actor()
        actor_copy = actor.copy()
        for attribute_name in self.attributes_for_copy:
            copied_value = getattr(actor_copy, attribute_name)
            original_value = getattr(actor, attribute_name)
            self.assertEqual(copied_value, original_value,
                             'Unexpectedly found different value ({}) between'
                             ' actor ({}) and its copy ({})'
                             ''.format(attribute_name,
                                       original_value, copied_value))

    def test_apply_mana_drain_sets_current_mana_to_zero(self):
        mana_types = ('r', 'g', 'b', 'y')
        non_zero_mana = {mana_type: (50, 100) for mana_type in mana_types}
        actor = generic_actor(**non_zero_mana)
        # confirm before clearing just to be safe
        for mana_type in mana_types:
            mana_value = getattr(actor, mana_type)
            self.assertGreater(mana_value, 0,
                               'Unexpectedly found mana value of <= 0 for {}'
                               ' when preparing for mana drain test.'
                               ''.format(mana_type))
        # clear and confirm
        actor.apply_mana_drain()
        for mana_type in mana_types:
            mana_value = getattr(actor, mana_type)
            self.assertEqual(mana_value, 0,
                             'Unexpectedly got nonzero ({}) mana value for {}'
                             ' after applying mana drain.'
                             ''.format(mana_value, mana_type))

    def test_apply_tile_groups_ignores_wildcard_group_type(self):
        actor = generic_actor()
        # build a wildcard only group that has no group type
        wildcard = Tile('2')
        tile_groups = [(wildcard, wildcard, wildcard)]
        # apply the groups and confirm increase
        try:
            actor.apply_tile_groups(tile_groups)
        except Exception as e:
            self.fail('Unexpectedly got an error applying an all-wildcard'
                      ' group instead of ignoring it:\n{}'.format(e))

    def test_apply_tile_groups_increases_color_and_unique_current_values(self):
        base_value = 0
        base = (base_value, 100)
        actor = generic_actor(r=base, g=base, b=base, y=base,
                              x=base, m=base, h=base, c=base)
        # build a set of groups, one group of 3 tiles for each type
        color_and_unique_types = ('r', 'g', 'b', 'y', 'x', 'm', 'h', 'c')
        increase_spec = 3
        tile_groups = [(Tile(t),) * increase_spec
                       for t in color_and_unique_types]
        # apply the groups and confirm increase
        actor.apply_tile_groups(tile_groups)
        for t in color_and_unique_types:
            new_value = getattr(actor, t)
            self.assertGreaterEqual(new_value, base_value + increase_spec)

    def test_apply_tile_groups_multiplies_colors_by_wildcard_sum(self):
        base_value = 0
        base = (base_value, 100)
        actor = generic_actor(r=base, g=base, b=base, y=base)
        color_types = ('r', 'g', 'b', 'y')
        four = Tile('4')
        three = Tile('3')
        increase_spec = 7
        color_groups_with_wildcards = [(four, Tile(t), three)
                                       for t in color_types]
        actor.apply_tile_groups(color_groups_with_wildcards)
        for t in color_types:
            new_value = getattr(actor, t)
            self.assertGreaterEqual(new_value, base_value + increase_spec)

    def test_apply_tile_groups_returns_an_attack_for_skulls_or_skullbombs(self):
        actor = generic_actor()
        # build a set of groups, one group of 3 tiles for each type
        skull = Tile('s')
        skullbomb = Tile('*')
        tile_groups = [(skull, skull, skullbomb)]
        # apply the skulls and confirm the attack value
        attack_value = actor.apply_tile_groups(tile_groups)
        attack_value_spec = 1 + 1 + 5
        self.assertGreaterEqual(attack_value, attack_value_spec)

    def test_apply_attack_affects_current_health(self):
        base = 50
        actor = generic_actor(health=(base, 100))
        attack = 10
        # apply the attack and confirm that the health changed
        actor.apply_attack(attack)
        # assert:    base-attack <= health <= base
        self.assertLess(actor.health, base)
        self.assertGreaterEqual(actor.health, base - attack)


# Helpers and simple factories
def confirm_attribute(obj, attribute_name):
    try:
        getattr(obj, attribute_name)
        return
    except AttributeError:
        pass
    # do this outside of the try block to retain context
    raise AttributeError('Unexpectedly failed to access {} on {}.'
                         ''.format(attribute_name, obj))


def generic_game(use_random_fill=False):
    """Simple factory to help keep tests focused."""
    return Game(use_random_fill)


def generic_state(board=None, player=None, opponent=None,
                  turn=1, actions_remaining=1):
    """Simple factory to help keep tests short and focused."""
    board = board or Board()
    player = player or generic_actor(name='player')
    opponent = opponent or generic_actor(name='opponent')
    return State(board, player, opponent,
                 turn, actions_remaining)


def generic_actor(name=None, health=None,
                  r=None, g=None, b=None, y=None,
                  x=None, m=None, h=None, c=None):
    """Simple factory to keep tests focused."""
    # use a generator to ensure accuracy when checking values
    def different_current_max():
        current, maximum = 50, 100
        while True:
            current += 1
            maximum += 1
            yield current, maximum
    val_gen = different_current_max()
    health = health or val_gen.next()
    r = r or val_gen.next()
    g = g or val_gen.next()
    b = b or val_gen.next()
    y = y or val_gen.next()
    x = x or val_gen.next()
    m = m or val_gen.next()
    h = h or val_gen.next()
    c = c or val_gen.next()
    return Actor(name, health, r, g, b, y, x, m, h, c)


if __name__ == '__main__':
    unittest.main()
