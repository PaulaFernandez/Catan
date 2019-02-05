import pickle
from os import listdir
from random import choice
import numpy as np

from model import Residual_CNN
import config

net = Residual_CNN(config.REG_CONST, config.LEARNING_RATE, config.INPUT_DIM, config.OUTPUT_DIM, config.HIDDEN_CNN_LAYERS)
net.read(config.CURRENT_AGENT)

for i in range(config.TRAINING_LOOPS):
    batch_states = []
    batch_target_results = []
    batch_target_probs = []
    for b in range(config.TRAIN_BATCH_SIZE):
        game_file = choice(listdir('games'))
        
        with open('games\\' + game_file, 'rb') as input_file:
            game_memory = pickle.load(input_file)
            
        move_num = np.random.randint(len(game_memory.game_results))
        
        batch_states.append(game_memory.states[move_num][1][0])
        batch_target_probs.append(game_memory.states[move_num][2])
        batch_target_results.append(game_memory.game_results[move_num])

    batch_states = np.array(batch_states)
    batch_targets = [np.array(batch_target_results), np.array(batch_target_probs)]
        
    net.fit(batch_states, batch_targets, config.EPOCHS, 2, 0.0, 32)

net.write(config.CURRENT_AGENT + 1)