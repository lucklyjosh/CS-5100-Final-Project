from soundManager import *
from asteroids import *

class Agent():

    def __init__(self):
        # game initialized at bottom of file after Agent declaration
        obs, reward, done = game.initialiseGame()
        self.instructions = {}
        print(obs)

    # TODO: take in values and hash them into binary string, each slot representing situation of the state.
    # return binary string
    def hash(self):
        print("hello world")
    
    def play(self):
        self.game.playGame()

    def q_learning(self, num_episodes=10000, gamma=0.9, epsilon=1, decay_rate=0.999):
        obs, reward, done = game.initialiseGame()
        print(obs)

        history = {}

        # store history of 10 episodes. use last 9 episodes to calculate/update reward for first episode.
        # for i in range(num_episodes):
        #     if i < 9:
        #         continue
        #     else:
        #         target_episode = history[0]

    def obj_func():
        print("hello world")


initSoundManager()
game = Asteroids()
agent = Agent()
agent.q_learning()