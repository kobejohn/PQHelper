import pqhelper

# Versus has more parts (board, player, opponent) but easy to use.
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
print 'Analyzing the versus game:\n{}'.format(board_string_8_choices)
# patch the screen investigation system to use our own board, player, opponent
# usually, just call the method with no arguments and it gets everything
# from the game on screen for you
from pqhelper.base import Board
board = Board(board_string_8_choices)
player, opponent = pqhelper.easy._state_investigator.generic_versus_actors()
pqhelper.easy._state_investigator.get_versus = lambda: (board, player, opponent)

# Simulate two turns (with the versus module, you can simulate turn by turn)
# Also runs the same simulation twice to smooth out the effects of random drops
# This is all you have to do when it's on the screen:
summaries = pqhelper.versus_summaries(turns=2, sims_to_average=2)
for summary in summaries:
    print '--------------------'
    print summary.text
    print summary.action
