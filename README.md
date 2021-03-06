PQHelper
========

PQHelper takes any on-screen game of Puzzle Quest(tm) and then gives the user
appropriate advice for each type of game (capture, versus, forge, research).

[![Screenshot](https://raw.github.com/kobejohn/PQHelper/master/screenshot.png)](http://youtu.be/00LsM4rMIcc)


Status
======

It is completely functional for capture and versus with a GUI or from
the command line. Game data for capture and versus are extracted from
the screen (doesn't touch the application directly).

- GUI: Working.
- Capture solution: Solutions are relatively fast.
- Versus advice: Tries to simulate 2 turns, but will give results of 1 if
  it times out. Note: "turn" includes any extra "actions" due to web, 4-block
  matches, etc. It currently extracts player/opponent health and mana
  to make scoring more accurate.
- Forge, Research: May be implemented.


GUI Usage
=========

    import pqhelper
    pqhelper.GUI()


Installation
============

Currently, windows only. Might work with wine in Linux.

    pip install pqhelper

If you don't have a compiler on your windows box, it will probably die on you.
You can install the
numpy requirement [here](http://sourceforge.net/projects/numpy/files/NumPy/).
For me, I have to open the executable with 7-zip and easy_install one
of the installers to get it into a virtualenv. Otherwise I believe
it goes only to the root python installation.

You will also need [OpenCV]() but that is such a pain that I've included
a working precompiled windows library (cv2.pyd) with the distribution so you
don't have to worry about it.


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
    # usually, just call the method with no arguments and it gets everything
    # from the game on screen for you
    from pqhelper.base import Board
    pqhelper.easy._state_investigator.get_capture = lambda: Board(catapult)
    # this is all you have to do when it's on the screen:
    solution = pqhelper.capture_solution()
    for solution_step in solution:
        print solution_step.action


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


License:
========

MIT. See LICENSE.
