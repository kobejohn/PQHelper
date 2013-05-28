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
# usually, just call the method and it gets everything from the game on screen
board = pqhelper.Board(board_string_8_choices)
player, opponent = pqhelper._state_investigator.generic_versus_actors()
pqhelper._state_investigator.get_versus = lambda: (board, player, opponent)

# Simulate two turns (with the versus module, you can simulate turn by turn)
summaries = pqhelper.summarize_versus_options(2)
for summary in summaries:
    print summary
