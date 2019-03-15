import pickle
from os import listdir, remove
from random import choice
import numpy as np
import sys

from model import Residual_CNN
import config

net = Residual_CNN(config.REG_CONST, config.LEARNING_RATE, config.INPUT_DIM, config.OUTPUT_DIM, config.HIDDEN_CNN_LAYERS)
net.read(sys.argv[1])

for i in range(config.TRAINING_LOOPS):
    print ("Iteration #" + str(i))

    batch_states = []
    batch_target_results = []
    batch_target_probs = []
    
    game_file = choice(listdir('train_states'))
    with open('train_states\\' + game_file, 'rb') as input_file:
        game_memory = pickle.load(input_file)
    remove('train_states\\' + game_file)
    
    # for b in range(config.TRAIN_BATCH_SIZE):
        # game_file = choice(listdir('games'))
        
        # with open('games\\' + game_file, 'rb') as input_file:
            # game_memory = pickle.load(input_file)
            
        # move_num = np.random.randint(len(game_memory.game_results))
        
        # batch_states.append(game_memory.states[move_num][1][0])
        # batch_target_probs.append(game_memory.states[move_num][2])
        # batch_target_results.append(game_memory.game_results[move_num])

    # batch_states = np.array(batch_states)
    # batch_targets = [np.array(batch_target_results), np.array(batch_target_probs)]
        
    net.fit(game_memory['batch_states'], game_memory['batch_targets'], config.EPOCHS, 2, 0.0, 32)

net.write(sys.argv[2])