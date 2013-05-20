from pqhelper import capture

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
solution = capture.capture(capture.Board(catapult))
for solution_step in solution:
    print solution_step
