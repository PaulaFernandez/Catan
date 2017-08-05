import unittest
import pickle
import game_state

class test_check_end_game(unittest.TestCase):
    def setUp(self):
        self.game = game_state.GameState()
        with open('test_check_end_game.pkl', 'rb') as input_file:
            self.game = pickle.load(input_file)

    def test_end_of_game(self):
        self.assertEqual(self.game.check_end_game(), "a21e5106-7466-11e7-8c08-d55eb5a6cb3f;2;8,7,10,7")

suite = unittest.TestLoader().loadTestsFromTestCase(test_check_end_game)
unittest.TextTestRunner(verbosity=2).run(suite)
    