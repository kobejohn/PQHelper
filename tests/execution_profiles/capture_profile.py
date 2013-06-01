import cProfile

from pqhelper import capture
from pqhelper.base import Board


def main():
    cProfile.run('test_solution(catapult)')


def test_solution(board_string):
    board = Board(board_string)
    for summary in capture.capture(board):
        print summary.action


orc_lord = '''
........
........
.x.ss.x.
.s.ss.s.
.gxggxg.
.sxggxs.
ssyssy*s
sysyysys'''

skeleton = '''
..*..*..
.gm..mg.
.ms..sm.
.rs..sr.
.ggmmgg.
.rsggsr.
.rsrrsr.
ssgssgss'''

giant_rat = '''
...mm...
..mrym..
.mgyrgm.
mygrygym
ryxssxyr
rxgbbgxr
xygssgyx
rybssbyr'''

griffon = '''
.r..s...
.b.sy...
.b.yys..
.r.yxg.g
.g.x*b.r
.g.xxb.r
rybyxygy
ygyxybyr'''

catapult = '''
........
........
..mbgm..
.mxgbrm.
my*gb*gm
yrrxrxxg
ymxyyrmg
ssxssrss'''

easy = '''
........
........
........
........
.......x
....xx.r
....rr.r
..rryyry'''


if __name__ == '__main__':
    main()