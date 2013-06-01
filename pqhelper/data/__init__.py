import os

from investigators.visuals import cv2

_base = os.path.abspath(os.path.split(__file__)[0])

capture_template = cv2.imread(os.path.join(_base,
                                           'capture template 1280x960.png'))
versus_template = cv2.imread(os.path.join(_base,
                                          'versus template 1280x960.png'))

tile_templates = {'.': cv2.imread(os.path.join(_base, '_.png')),
                  'r': cv2.imread(os.path.join(_base, 'r.png')),
                  'g': cv2.imread(os.path.join(_base, 'g.png')),
                  'b': cv2.imread(os.path.join(_base, 'b.png')),
                  'y': cv2.imread(os.path.join(_base, 'y.png')),
                  'x': cv2.imread(os.path.join(_base, 'x.png')),
                  'm': cv2.imread(os.path.join(_base, 'm.png')),
                  's': cv2.imread(os.path.join(_base, 's.png')),
                  '*': cv2.imread(os.path.join(_base, '@.png')),
                  'c': cv2.imread(os.path.join(_base, 'c.png')),
                  'h': cv2.imread(os.path.join(_base, 'h.png')),
                  '2': cv2.imread(os.path.join(_base, '2.png')),
                  '3': cv2.imread(os.path.join(_base, '3.png')),
                  '4': cv2.imread(os.path.join(_base, '4.png')),
                  '5': cv2.imread(os.path.join(_base, '5.png')),
                  '6': cv2.imread(os.path.join(_base, '6.png')),
                  '7': cv2.imread(os.path.join(_base, '7.png')),
                  '8': cv2.imread(os.path.join(_base, '8.png'))}
