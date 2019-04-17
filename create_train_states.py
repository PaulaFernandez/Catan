import pickle
from os import listdir
from random import choice
from mcts_ai import MCTS_AI
import numpy as np

import config

num_states_start = 16    

def create_sets(type, batch_size, i, states_per_loop, train_net, train_head):
    states = {}
    dummy_ai = MCTS_AI(0, [None, None], 0, 0)

    for j in range(states_per_loop):
        states[j] = {'states': [],
                     'target_probs': [],
                     'target_results': []}

    for b in range(batch_size):
        game_file = choice(listdir(type))
        
        with open(type + '\\' + game_file, 'rb') as input_file:
            game_memory = pickle.load(input_file)
            
        if train_net == 'start':
            move_num = np.random.randint(num_states_start, size = states_per_loop)
        else:
            move_num = np.random.randint(num_states_start, len(game_memory.game_results), size = states_per_loop)
            
        for j in range(states_per_loop):
            if train_head == 'value':
                perspective = np.random.randint(4, size = 1)[0]
            else:
                perspective = game_memory.states[move_num[j]][0]
                
            if train_net == 'start':
                nn = dummy_ai.build_start_nn_input(game_memory.states[move_num[j]][1], perspective)
            else:
                nn = dummy_ai.build_nn_input(game_memory.states[move_num[j]][1], perspective, determined = 1)
            
            p_order = (4 + perspective - game_memory.states[move_num[j]][0]) % 4
            
            states[j]['states'].append(nn[0])
            
            if train_net == 'start':
                states[j]['target_probs'].append(game_memory.states[move_num[j]][2])
            else:
                if isinstance(game_memory.states[move_num[j]][2], int) < config.OUTPUT_DIM:
                    states[j]['target_probs'].append([0] * config.OUTPUT_DIM)
                else:
                    states[j]['target_probs'].append(game_memory.states[move_num[j]][2])
                             
            states[j]['target_results'].append([game_memory.game_results[move_num[j]][p_order]])
    
    for j in range(states_per_loop):    
        file_output = {}
        file_output['batch_states'] = np.array(states[j]['states'])
        file_output['batch_targets'] = [np.array(states[j]['target_results']), np.array(states[j]['target_probs'])]
        
        if type == 'training':
            with open('train_states\\states' + str(states_per_loop * i + j) + '.pkl', 'wb') as output_file:
                pickle.dump(file_output, output_file, -1)
        else:
            with open('validation_states\\states' + str(states_per_loop * i + j) + '.pkl', 'wb') as output_file:
                pickle.dump(file_output, output_file, -1)