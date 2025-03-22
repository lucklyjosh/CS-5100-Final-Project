import pygame
import sys
from soundManager import *
from asteroids import *
import random

class Agent():

    def __init__(self, game):
        self.game = game
        print("initializing agent")

    # TODO: take in values and hash them into binary string, each slot representing situation of the state.
    # return binary string
    def hash(self):
        print("hello world")
    
    def play(self):
            print("🚀 Initializing pygame...")
            pygame.init()

            print("🔊 Initializing sound manager...")
            initSoundManager()

            print("🎮 Initializing game...")
            self.game.initialiseGame()

            actions = ['up', 'left', 'right', 'fire']
            clock = pygame.time.Clock()

            print("🖥️ Checking screen surface...")
            if not self.game.stage.screen:
                print("❌ Screen surface is None!")
            else:
                print("✅ Screen initialized:", self.game.stage.screen.get_size())
                print("✅ Display driver:", pygame.display.get_driver())

            running = True
            frame_count = 0
            while running:
                
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False

                action = random.choice(actions)
                obs, reward, done = self.game.step(action)

                # Render the game state
                print("🔄 Rendering frame...")
                self.game.stage.screen.fill((10, 10, 10))
                self.game.stage.moveSprites()
                self.game.stage.drawSprites()
                self.game.stage.displayScore(game.score)
                pygame.display.flip()
                print("✅ Frame rendered.")

                print(f"Frame {frame_count}: {action}")
                print("Ship:", obs['ship']['position'].x, obs['ship']['position'].y)
                print("Rock:", obs['rocks'][0]['position'].x, obs['rocks'][0]['position'].y)
                print("--------------")

                frame_count += 1
                clock.tick(60)

                if done or frame_count > 300:
                    running = False

            pygame.quit()
            print("🛑 Game session ended.")



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


if __name__ == "__main__":
    game = Asteroids()
    agent = Agent(game)
    agent.play()