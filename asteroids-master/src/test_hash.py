import unittest
from agent import Agent
from asteroids import Asteroids
from util.vector2d import Vector2d

class TestAgentHash(unittest.TestCase):

    def setUp(self):
        """ Initialize agent and game before each test """
        self.game = Asteroids()
        self.agent = Agent(self.game)
        self.game.initialiseGame()

    def mock_state(self, ship_pos, ship_heading, alien_pos=None, rocks=[]):
        """ Helper to mock a game state """
        self.game.current_state = {
            'ship': {'position': Vector2d(*ship_pos), 'heading': Vector2d(*ship_heading)},
            'alien': Vector2d(*alien_pos) if alien_pos else None,
            'rocks': {i: {'position': Vector2d(*rock[0]), 'heading': Vector2d(*rock[1])} for i, rock in enumerate(rocks)}
        }

    def assertHash(self, expected_hash):
        """ Helper to compare expected and actual hash with detailed print """
        actual_hash = self.agent.hash(self.game.current_state)
        print(f"Expected: {expected_hash}, Actual: {actual_hash}, Result: {'Pass' if actual_hash == expected_hash else 'Fail'}")
        self.assertEqual(actual_hash, expected_hash)

    def test_no_rocks_no_alien(self):
        """ Test case where no rocks or aliens exist """
        self.mock_state(ship_pos=(512, 384), ship_heading=(1, 0))
        self.assertHash("0000000")

    def test_rock_danger_ahead(self):
        """ Test case where a rock is directly in front and close to the ship """
        self.mock_state(ship_pos=(512, 384), ship_heading=(1, 0), rocks=[((530, 384), (0, 0))])
        self.assertHash("1020000") 

    def test_rock_in_view(self):
        """ Test case where a rock is in the cone of view but not directly ahead """
        self.mock_state(ship_pos=(512, 384), ship_heading=(1, 0), rocks=[((550, 400), (0, 0))])
        self.assertHash("0120000") 

    def test_alien_in_view_and_close(self):
        """ Test case with an alien nearby in view """
        self.mock_state(ship_pos=(512, 384), ship_heading=(1, 0), alien_pos=(600, 384))
        self.assertHash("0001110")

    def test_multiple_rocks(self):
        """ Test case with multiple rocks and one in close proximity """
        self.mock_state(ship_pos=(512, 384), ship_heading=(1, 0), rocks=[
            ((520, 384), (0, 0)),  # Close and in front, dangerous
            ((600, 420), (0, 0))   # Further away
        ])
        self.assertHash("1020000")


if __name__ == '__main__':
    unittest.main()
