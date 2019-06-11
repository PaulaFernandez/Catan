import pickle
from os import listdir, remove
from random import choice
import numpy as np
import sys
from keras.optimizers import SGD

from model import Residual_CNN
import config

def train_network(agent, train_phase):
    if train_phase[0] == 'start':
        net = Residual_CNN(config.REG_CONST, config.LEARNING_RATE, config.INPUT_START_DIM, config.OUTPUT_START_DIM, config.HIDDEN_CNN_LAYERS)
        net_str = 's'
    elif train_phase[0] == 'general':
        net = Residual_CNN(config.REG_CONST, config.LEARNING_RATE, config.INPUT_DIM, config.OUTPUT_DIM, config.HIDDEN_CNN_LAYERS)
        net_str = 'g'
        
    net.read(agent, net_str)

    #validation_file = choice(listdir('validation_states'))
    #with open('validation_states\\' + validation_file, 'rb') as input_file:
    #    validation = pickle.load(input_file)

    min_val_error = 10000.0
    for i in range(config.TRAINING_LOOPS):
        print ("Iteration #" + str(i))
        
        game_file = choice(listdir('train_states'))
        with open('train_states\\' + game_file, 'rb') as input_file:
            game_memory = pickle.load(input_file)
        remove('train_states\\' + game_file)
            
        hist = net.fit(game_memory['batch_states'], game_memory['batch_targets'], config.EPOCHS, 2, 0.0, 32)
        
        #metric = hist.history['val_loss'][config.EPOCHS - 1]
            
        #if metric < min_val_error:
        #    min_val_error = metric
        net.write(agent, net_str)
            
        print ("Min Loss: " + str(min_val_error))