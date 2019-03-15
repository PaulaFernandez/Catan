import pickle
from os import listdir
from random import choice
import numpy as np

import config

states_per_loop = 4
number_of_sets = 400

for i in range(number_of_sets):
    print ("Iteration #" + str(i))
    states = {}

    for j in range(states_per_loop):
        states[j] = {'states': [],
                     'target_probs': [],
                     'target_results': []}

    for b in range(config.TRAIN_BATCH_SIZE):
        game_file = choice(listdir('games'))
        
        with open('games\\' + game_file, 'rb') as input_file:
            game_memory = pickle.load(input_file)
            
        move_num = np.random.randint(len(game_memory.game_results), size = states_per_loop)
        
        for j in range(states_per_loop):
            states[j]['states'].append(game_memory.states[move_num[j]][1][0])
            states[j]['target_probs'].append(game_memory.states[move_num[j]][2])
            states[j]['target_results'].append(game_memory.game_results[move_num[j]])
    
    for j in range(states_per_loop):    
        file_output = {}
        file_output['batch_states'] = np.array(states[j]['states'])
        file_output['batch_targets'] = [np.array(states[j]['target_results']), np.array(states[j]['target_probs'])]
        
        with open('train_states\\states' + str(states_per_loop * i + j) + '.pkl', 'wb') as output_file:
            pickle.dump(file_output, output_file, -1)