import pickle
import pygame
import sys
from soundManager import *
from asteroids import *
import random
import numpy as np
import json
from datetime import datetime

class Agent():

    def __init__(self, game):
        self.game = game
        self.Q_table = {}
        self.update_table = {}
        print("initializing agent")

    # hash observation into a string
    def hash(self, obs, debug=False):

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
                
        state = obs
        ship_pos = state['ship']['position']
        ship_heading = state['ship']['heading']
        alien_pos = state['alien']
        rocks = state['rocks']

        state_hash_str = ""

        # Normalize ship heading
        ship_heading_mag = math.sqrt(ship_heading.x ** 2 + ship_heading.y ** 2)
        ship_heading_norm = Vector2d(
            ship_heading.x / ship_heading_mag if ship_heading_mag != 0 else 0,
            ship_heading.y / ship_heading_mag if ship_heading_mag != 0 else 0,
        )

        # Rock danger ahead
        rock_danger = 0
        rock_in_view = 0

        if rocks:
            for rock in rocks.values():
                rel_pos = Vector2d(rock['position'].x - ship_pos.x, rock['position'].y - ship_pos.y)
                distance = math.sqrt(rel_pos.x**2 + rel_pos.y**2)
                rel_pos_norm = Vector2d(
                    rel_pos.x / distance if distance != 0 else 0,
                    rel_pos.y / distance if distance != 0 else 0,
                )
                direction_similarity = np.dot([rel_pos_norm.x, rel_pos_norm.y], [ship_heading_norm.x, ship_heading_norm.y])

                if distance < 30 and direction_similarity > 0.9:
                    rock_danger = 1
                    

                if rock_danger == 0 and direction_similarity > 0.7 and distance < 150:
                    rock_in_view = 1

        state_hash_str += str(rock_danger)
        state_hash_str += str(rock_in_view)

        if debug:
            print("Rock danger ahead:", rock_danger)
            print("Rock in view:", rock_in_view)


        # Rock in the ship’s line of fire
        # rock_in_view = 0
        # if not rock_danger and rocks:
        #     for rock in rocks.values():
        #         rel_pos = Vector2d(rock['position'].x - ship_pos.x, rock['position'].y - ship_pos.y)
        #         distance = math.sqrt(rel_pos.x**2 + rel_pos.y**2)
        #         rel_pos_norm = Vector2d(
        #             rel_pos.x / max(distance, 1e-6),
        #             rel_pos.y / max(distance, 1e-6),
        #         )

        #         direction_similarity = np.dot([rel_pos_norm.x, rel_pos_norm.y], [ship_heading_norm.x, ship_heading_norm.y])
        #         print(f"[Rock View Check] Distance: {distance:.2f}, Similarity: {direction_similarity:.2f}")

        #         if direction_similarity > 0.7:
        #             print("[Rock View Check] ✅ Rock detected in view!")
        #             rock_in_view = 1
        #             break
        # state_hash_str += str(rock_in_view)
        # if debug:
        #     print("Rock in cone:", rock_in_view)

        # Rock proximity
        rock_prox = 0
        min_dist = float('inf')
        if rock_danger == 1:
            rock_prox = 2
        else:
            if rocks:
                min_dist = min([
                    math.sqrt((rock['position'].x - ship_pos.x) ** 2 + (rock['position'].y - ship_pos.y) ** 2)
                    for rock in rocks.values()
                ])
                if min_dist <= 75:
                    rock_prox = 2   
                elif min_dist <= 150:
                    rock_prox = 1
                else:
                    rock_prox = 0
        # print(f"[Rock Proximity Check] Min Distance: {min_dist:.2f}, Proximity Level: {rock_prox}")

        state_hash_str += str(rock_prox)
        if debug:
            print("Rock proximity (0=farthest, 2=closest):", rock_prox)

        # Alien present
        alien_present = 1 if alien_pos else 0
        state_hash_str += str(alien_present)
        if debug:
            print("Alien present:", alien_present)

        # Alien in view
        alien_in_view = 0
        if alien_pos:
            rel_pos = Vector2d(alien_pos.x - ship_pos.x, alien_pos.y - ship_pos.y)
            alien_dist = math.sqrt(rel_pos.x**2 + rel_pos.y**2)
            rel_pos_norm = Vector2d(
                rel_pos.x / alien_dist if alien_dist != 0 else 0,
                rel_pos.y / alien_dist if alien_dist != 0 else 0,
            )
            direction_similarity = np.dot([rel_pos_norm.x, rel_pos_norm.y], [ship_heading_norm.x, ship_heading_norm.y])
            if direction_similarity > 0.7:  
                alien_in_view = 1
        state_hash_str += str(alien_in_view)
        if debug:
            print("Alien in view:", alien_in_view)

        # Alien proximity
        alien_prox = 0
        if alien_pos:
            alien_distance = math.sqrt((alien_pos.x - ship_pos.x) ** 2 + (alien_pos.y - ship_pos.y) ** 2)
            if alien_distance < 200:
                alien_prox = 1
        state_hash_str += str(alien_prox)
        if debug:
            print("Alien proximity:", alien_prox)

        # Bullet threat (placeholder)
        bullet_threat = 0
        state_hash_str += str(bullet_threat)
        if debug:
            print("Bullet threat:", bullet_threat)

        if debug:
            print("Hashed state:", state_hash_str)
        return state_hash_str

    
    def play(self):
        args = sys.argv[1:]
        if len(args) > 0:
            # load a specific q_table file
            filename = args[0]
        elif len(args) == 0:
            # load the most recent q_table
            filename = "./q_tables/" + self.get_latest_q_table()
            with open(filename, "rb") as f:
                q_table = pickle.load(f)
                self.Q_table = q_table
                print(self.Q_table) 

        print("🚀 Initializing pygame...")
        pygame.init()

        print("🔊 Initializing sound manager...")
        initSoundManager()

        print("🎮 Initializing game...")
        self.game.initialiseGame()

        actions = ['up', 'left', 'right', 'fire']
        action = actions[3] # default first action to fire
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
            
            obs, reward, done = self.game.step(action)
            state_hash = self.hash(obs)
            print("🔑 State Hash:", state_hash)

            # select action for next round based off of current state
            if state_hash in self.Q_table:
                action_idx = np.argmax(self.Q_table[state_hash])
            else:
                # if for some reason we've never gotten to state_hash in training, then pick a random action.
                action_idx = random.randint(0, len(actions)-1)
            action = actions[action_idx]
            print("Action:", action)

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

    def q_learning(self, num_episodes=10000, gamma=0.95, epsilon=1, decay_rate=0.999, history_range=40, GUI=False):
        if GUI==True:
            print("🚀 Initializing pygame...")
            pygame.init()

            print("🔊 Initializing sound manager...")
            initSoundManager()

            clock = pygame.time.Clock()
            frame_count = 0

        actions = ['up', 'left', 'right', 'fire']
        num_actions = len(actions)
        hist = []

        for i in range(num_episodes):
            obs, reward, done = self.game.initialiseGame()
        
            for j in range(history_range):
                rand_action = random.choice(actions)
                obs, reward, done = self.game.step(rand_action)
                # print(f"Action: {rand_action}, Reward: {reward}")

                # reward = random.randint(-100, 100)
                hist.append([self.hash(obs), reward, actions.index(rand_action)])

            # init subsequent rewards into the first loop
            subsequent_rewards = sum(map(lambda arr: arr[1], hist[:-1]))

            while not done:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        done = True

                snapshot = hist.pop(0)
                hash = snapshot[0]
                first_action_idx = snapshot[2]

                if hash not in self.Q_table:
                    self.Q_table[hash] = np.zeros(num_actions)
                    self.update_table[hash] = np.zeros(num_actions)

                eta = 1 / (1 + self.update_table[hash][first_action_idx])
                # update subsequent_rewards
                subsequent_rewards -= snapshot[1]
                subsequent_rewards += hist[-1][1]
                self.Q_table[hash][first_action_idx] = (1 - eta) * self.Q_table[hash][first_action_idx] + eta * subsequent_rewards
                self.update_table[hash][first_action_idx] += 1

                next_action = np.argmax(self.Q_table[hash])

                if np.random.rand() < epsilon:
                    next_action = random.randint(0, num_actions - 1)  # Explore: Random action
                else:
                    # Chase and shoot rock logic
                    if '1' in hash[0]:  # Rock danger detected
                        next_action = random.choice([1, 2, 0])  # Left, Right, or Up
                    elif hash[1] == '1' and hash[2] in ['1', '2']:  # Rock in view and close
                        next_action = 3  # Fire
                    elif hash[1] == '1':  # Rock in view but not close
                        next_action = random.choice([1, 2])  # Left or Right to adjust aim
                    elif hash[2] == '1':  # Rock mid-range, chase it
                        next_action = 0  # Thrust (up)
                    else:
                        next_action = np.argmax(self.Q_table[hash])


                obs, reward, done = self.game.step(actions[next_action])
                # print(f"Next Action: {actions[next_action]}, Reward: {reward}")
                # reward = random.randint(-100, 100)
                new_hash = self.hash(obs)
                hist.append([new_hash, reward, next_action])

                epsilon *= decay_rate
                epsilon = max(0.1, epsilon) 

                # Render the game state
                if GUI==True:
                    self.game.stage.screen.fill((10, 10, 10))
                    self.game.stage.moveSprites()
                    self.game.stage.drawSprites()
                    self.game.stage.displayScore(game.score)
                    pygame.display.flip()

                    # print(f"Frame {frame_count}: {next_action}")
                    # print("--------------")

                    frame_count += 1
                    clock.tick(30)

                    # if frame_count > 5000:
                    #     done = True
                    #     print(self.Q_table)
                    #     print(self.update_table)

            print(self.Q_table)

        pygame.quit()
        print("🛑 Game session ended.")

        # save q table so we can use it
        now = datetime.now()
        formatted_date_time = now.strftime("%Y-%m-%d-%H:%M:%S") 
        filename = f'q_table_{formatted_date_time}.pickle'
        with open(filename, "wb") as f:
            pickle.dump(self.Q_table, f)


    def get_latest_q_table(self):
        try:
            contents = os.listdir("./q_tables")
            contents.sort(reverse=True)
            return contents[0]
        except Exception as e:
            return f"Error: {e}"

if __name__ == "__main__":
    game = Asteroids()
    agent = Agent(game)
    # uncomment to train:
    agent.q_learning(num_episodes = 1000, GUI=True)
    # uncomment to play with trained model:
    # agent.play()