import time
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
print 'Trying to solve the catapult board:\n{}'.format(catapult)
start = time.time()
solution = capture.capture(catapult)
elapsed = time.time() - start
print 'Solution found in {}s:\n{}'.format(elapsed, '\n'.join(str(swap) for swap
                                                             in solution))
