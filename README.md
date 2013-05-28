PQHelper
========

PQHelper takes any on-screen game of Puzzle Quest(tm) and then gives the user
appropriate advice for each type of game (capture, versus, forge, research).


Status
======

It is completely function for capture and versus from the command line.
Game data for capture and versus are extracted from the screen (doesn't touch
the application directly).

- Capture solution: Solutions are relatively fast.
- Versus advice: Gives scored choices based on how many turns you simulate.
- Forge, Research: May be implemented.
- GUI: May be implemented.


Command Line Usage per Game Type
================

**Capture:**

    import pqhelper

    # Capture is very easy to use and relatively quick to find a solution.
    catapult = '''
               ........
               ........
               ..mbgm..
               .mxgbrm.
               my*gb*gm
               yrrxrxxg
               ymxyyrmg
               ssxssrss
               '''
    print 'Trying to capture the catapult:\n{}'.format(catapult)
    # patch the screen investigation system to just use the catapult
    # usually, just call the method and it gets everything from the game on screen
    pqhelper._state_investigator.get_capture = lambda: pqhelper.Board(catapult)
    solution = pqhelper.solve_capture()
    for solution_step in solution:
        print solution_step


**Versus:**

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


License:
========

MIT. See LICENSE.