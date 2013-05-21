import os

from investigators.visuals import cv2

_base = os.path.abspath(os.path.split(__file__)[0])

capture_template = cv2.imread(os.path.join(_base,
                                           'capture template 1280x960.png'))
versus_template = cv2.imread(os.path.join(_base,
                                          'versus template 1280x960.png'))

tile_templates = {'.': cv2.imread(os.path.join(_base, '..png')),
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
                  '4': cv2.imread(os.path.join(_base, '4.png'))}