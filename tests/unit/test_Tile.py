import unittest

from pqhelper import Tile

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Specifications
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

#method condition result
class Test_Tile(unittest.TestCase):
    def test___init__with_single_character_works(self):
        single_character = 'x'
        try:
            Tile(single_character)
        except Exception as e:
            self.fail('Tile creation should have succeeded, but got exception:'
                      '{0}'.format(e))


if __name__ == '__main__':
    unittest.main()
