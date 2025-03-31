# CS-5100-Final-Project
CS 5100 Final Project

#### Trello Board
https://trello.com/b/qxq6IEZ3/cs5100-final-project

### How to run:
Navigate to:  
`cd asteroids-master/src` 

To play normally with the keyboard:  
`python3 asteroids.py`  
and uncomment the following from the bottom of `asteroids.py`: 
```
# initSoundManager()  
# game = Asteroids()  # create object game from class Asteroids
# game.playGame()
```

To have the agent play:  
`python3 agent.py`  
To train the agent, uncomment in `agent.py`:
```
# agent.q_learning(num_episodes = n, GUI=True)
```  
To make the agent play with a Q Table, uncomment in `agent.py`:
```
# agent.play()
``` 

To have the agent play with a **specific** Q Table:  
`python3 agent.py ./q_tables/q_table_filename.pickle` 


### Credits:
Asteroids pygame environment borrowed and adapted from: https://github.com/TheBeachLab/asteroids