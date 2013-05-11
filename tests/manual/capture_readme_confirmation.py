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
solution = capture.capture(catapult)
for solution_step in solution:
    print solution_step
