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

        '''
        - are we in the trajectory of a rock? (will it hit us if we don't move)
        - is a rock in our cone of vision? (are we facing it and can we shoot it if we fire a bunch and tilt left/right)
        - how close is the closest rock to us?
            - 0 = outside first threshold (farthest)
            - 1 = inside first threshold (middle region)
            - 2 = inside second threshold (super close, uh oh, hyperspace now)
        - is alien present?
        - is the alien in our cone of vision?
        - how close is the alien to us?
            - 0 = outside threshold
            - 1 = inside threshold
        '''

        state = self.game.current_state
        ship_pos = state['ship']['position']
        ship_heading = state['ship']['heading']
        alien_pos = state['alien']
        rocks = state['rocks']

        hash_str = ""


        # Normalize ship heading
        ship_heading_mag = math.sqrt(ship_heading.x ** 2 + ship_heading.y ** 2)
        ship_heading_norm = Vector2d(
            ship_heading.x / ship_heading_mag if ship_heading_mag != 0 else 0,
            ship_heading.y / ship_heading_mag if ship_heading_mag != 0 else 0,
        )


        # Rock danger ahead
        rock_danger = 0
        for rock in rocks.values():
            
            rel_pos = Vector2d(rock['position'].x - ship_pos.x, rock['position'].y - ship_pos.y)
            distance = math.sqrt(rel_pos.x**2 + rel_pos.y**2)
            rel_pos_norm = Vector2d(
                rel_pos.x / distance if distance != 0 else 0,
                rel_pos.y / distance if distance != 0 else 0,
            )
            direction_similarity = rel_pos_norm.x * ship_heading_norm.x + rel_pos_norm.y * ship_heading_norm.y


            if distance < 200 and direction_similarity > 0.9:
                rock_danger = 1
                break
        hash_str += str(rock_danger)
        print("Rock danger ahead:", rock_danger)


        # Rock is in the ship’s line of fire
        rock_in_view = 0
        for rock in rocks.values():
            rel_pos = Vector2d(rock['position'].x - ship_pos.x, rock['position'].y - ship_pos.y)
            distance = math.sqrt(rel_pos.x**2 + rel_pos.y**2)
            rel_pos_norm = Vector2d(
                rel_pos.x / distance if distance != 0 else 0,
                rel_pos.y / distance if distance != 0 else 0,
            )
            direction_similarity = rel_pos_norm.x * ship_heading_norm.x + rel_pos_norm.y * ship_heading_norm.y


            if direction_similarity > 0.7:
                rock_in_view = 1
                break
        hash_str += str(rock_in_view)
        print("Rock in cone:", rock_in_view)


        #   Rock is in medium proximity
        min_dist = min([
            math.sqrt((rock['position'].x - ship_pos.x) ** 2 +
                    (rock['position'].y - ship_pos.y) ** 2)
            for rock in rocks.values()
        ])
        if min_dist < 75:
            rock_prox = 2
        elif min_dist < 150:
            rock_prox = 1
        else:
            rock_prox = 0
        hash_str += str(rock_prox)
        print("Rock proximity (0=farthest, 2=closest):", rock_prox)


        # Alien present
        alien_present = 1 if alien_pos else 0
        hash_str += str(alien_present)
        print("👾 Alien present:", alien_present)


        # Alien in view
        alien_in_view = 0
        if alien_pos:
            rel_pos = Vector2d(alien_pos.x - ship_pos.x, alien_pos.y - ship_pos.y)
            alien_dist = math.sqrt(rel_pos.x**2 + rel_pos.y**2)
            rel_pos_norm = Vector2d(
                rel_pos.x / alien_dist if alien_dist != 0 else 0,
                rel_pos.y / alien_dist if alien_dist != 0 else 0,
            )
            if rel_pos_norm.dot(ship_heading_norm) > 0.7:
                alien_in_view = 1
        hash_str += str(alien_in_view)
        print("Alien in view:", alien_in_view)


        # Alien proximity
        alien_prox = 0
        if alien_pos:
            alien_distance = math.sqrt((alien_pos.x - ship_pos.x) ** 2 +
                                    (alien_pos.y - ship_pos.y) ** 2)
            if alien_distance < 200:
                alien_prox = 1
        hash_str += str(alien_prox)
        print("📏 Alien proximity:", alien_prox)


        # Bullet threat(future enhancement placeholder)
        bullet_threat = 0
        hash_str += str(bullet_threat)
        print("Bullet threat:", bullet_threat)


        print("Hashed state:", hash_str)
        return hash_str
    
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
                print("Screen surface is None!")
            else:
                print("Screen initialized:", self.game.stage.screen.get_size())
                print("Display driver:", pygame.display.get_driver())

            running = True
            frame_count = 0
            while running:
                
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False

                action = random.choice(actions)
                obs, reward, done = self.game.step(action)
                hash_str = self.hash()
                print("🔑 State Hash:", hash_str)

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

                if done or frame_count > 3000:
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