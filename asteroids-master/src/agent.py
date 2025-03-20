from soundManager import *
from asteroids import *
import random

class Agent():

    def __init__(self):
        print("initializing agent")

    # TODO: take in values and hash them into binary string, each slot representing situation of the state.
    # return binary string
    def hash(self):
        print("hello world")
    
    def play(self):
        game.initialiseGame()
        # game.playGame()
        # rotate_key = pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_x})
        actions = ['up', 'left', 'right']
        for i in range(10):
            action = random.choice(actions)
            print(action)
            obs, reward, done = game.step(action)
            print(obs['ship']['position'].x, obs['ship']['position'].y)
            print(obs['rocks'][0]['position'].x, obs['rocks'][0]['position'].y)
            print("--------------")

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
# agent.q_learning()
# game_thread = threading.Thread(target=game.playGame())
# game_thread.start()

agent.play()