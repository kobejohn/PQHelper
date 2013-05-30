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
pqhelper.easy._state_investigator.get_capture = lambda: pqhelper.Board(catapult)
solution = pqhelper.capture_solution()
for solution_step in solution:
    print solution_step.action
