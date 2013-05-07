import cProfile

from pqhelper import capture


def main():
    cProfile.run('test_solution(giant_rat)')


def test_solution(board_string):
    print capture.capture(board_string)

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