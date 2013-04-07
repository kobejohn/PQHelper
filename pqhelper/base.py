class Tile(object):
    """Behave like a PQ Tile."""
    _all_types = ('r', 'g', 'b', 'y',  # colors
                  's', '*',            # skulls
                  'x', 'm', '.',       # experience, money, blank
                  '2', '3', '4', '5', '6', '7', '8', '9')  # wildcards
    _matches = {'.': tuple(),  # blank matches nothing
                'r': ('r', '2', '3', '4', '5', '6', '7', '8', '9'),
                'g': ('g', '2', '3', '4', '5', '6', '7', '8', '9'),
                'b': ('b', '2', '3', '4', '5', '6', '7', '8', '9'),
                'y': ('y', '2', '3', '4', '5', '6', '7', '8', '9'),
                's': ('s', '*'),
                '*': ('s', '*'),
                'x': ('x',),
                'm': ('m',),
                '2': ('r', 'g', 'b', 'y',
                      '2', '3', '4', '5', '6', '7', '8', '9'),
                '3': ('r', 'g', 'b', 'y',
                      '2', '3', '4', '5', '6', '7', '8', '9'),
                '4': ('r', 'g', 'b', 'y',
                      '2', '3', '4', '5', '6', '7', '8', '9'),
                '5': ('r', 'g', 'b', 'y',
                      '2', '3', '4', '5', '6', '7', '8', '9'),
                '6': ('r', 'g', 'b', 'y',
                      '2', '3', '4', '5', '6', '7', '8', '9'),
                '7': ('r', 'g', 'b', 'y',
                      '2', '3', '4', '5', '6', '7', '8', '9'),
                '8': ('r', 'g', 'b', 'y',
                      '2', '3', '4', '5', '6', '7', '8', '9'),
                '9': ('r', 'g', 'b', 'y',
                      '2', '3', '4', '5', '6', '7', '8', '9')}

    def __init__(self, type_character):
        if type_character in self._all_types:
            self._type = type_character
        else:
            raise ValueError('Provided type_character ({0}) is not one of the '
                             'allowed types: {1}'.format(type_character,
                                                         self._all_types))

    def is_skullbomb(self):
        return True if self._type == '*' else False

    def is_blank(self):
        return True if self._type == '.' else False

    def is_wildcard(self):
        try:
            return int(self._type) in range(2, 10)
        except ValueError:
            return False

    def is_color(self):
        return self._type in ('r', 'g', 'b', 'y')

    def matches(self, other):
        """Return True for tiles that would match in PQ and False otherwise."""
        return other._type in self._matches[self._type]


if __name__ == "__main__":
    pass