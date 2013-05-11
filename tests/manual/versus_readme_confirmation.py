from pqhelper import versus

# First, make a board, player and opponent that make up the start state
board_string_8_choices = '''
                         gyrybrmg
                         xmxbgymm
                         sggybssm
                         mxsmxmmy
                         sybgbgys
                         xgyxygsg
                         gxmxgybb
                         mbbyssyx
                         '''
board = versus.Board(board_string_8_choices)
# Player / Opponent Actors are initialized by their current / maximum values
current_and_maximum = c_m = (50, 100)  # or whatever values for mana, etc.
player = versus.Actor('player', c_m, c_m, c_m, c_m, c_m, c_m, c_m, c_m, c_m)
opponent = versus.Actor('opponent', c_m, c_m, c_m, c_m, c_m, c_m, c_m, c_m, c_m)

# Now make the advisor which manages the internal simulation details
advisor = versus.Advisor()
advisor.reset(board, player, opponent)  # reset the simulation

# Simulate a single turn and get a sorted list of options
advisor.simulate_next_turn()
summaries = advisor.sorted_current_summaries()

# Print some details before going to turn 2
top_choice = summaries[0]
bottom_choice = summaries[-1]
print 'Original board:\n{}'.format(board)
print '{} swaps available'.format(len(summaries))
print 'Top choice after simulating 1 turn: {}'.format(top_choice)
print 'Bottom choice after simulating 1 turn: {}'.format(bottom_choice)

# Simulate a second turn and get a new sorted list of options
advisor.simulate_next_turn()
summaries = advisor.sorted_current_summaries()

# Print revised details after turn 2
top_choice = summaries[0]
bottom_choice = summaries[-1]
print 'Top choice after simulating 2 turns: {}'.format(top_choice)
print 'Bottom choice after simulating 2 turns: {}'.format(bottom_choice)
