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

    if train_phase[1] == 'value':
        for l in net.model.layers:
            prefix = l.name.split("_")[0]
            if prefix == 'policy':
                l.trainable = False
                
        net.model.compile(loss={'value_head': 'mean_squared_error', 'policy_head': 'mean_squared_error'},
                optimizer=SGD(lr=config.LEARNING_RATE, momentum = config.MOMENTUM),	
                loss_weights={'value_head': 0.01, 'policy_head': 0.99}	
                )
    elif train_phase[1] == 'policy':
        for l in net.model.layers:
            prefix = l.name.split("_")[0]
            if prefix != 'policy':
                l.trainable = False
                
        net.model.compile(loss={'value_head': 'mean_squared_error', 'policy_head': 'mean_squared_error'},
                optimizer=SGD(lr=config.LEARNING_RATE, momentum = config.MOMENTUM),	
                loss_weights={'value_head': 0.99, 'policy_head': 0.01}	
                )
        
    net.read(agent, net_str)

    validation_file = choice(listdir('validation_states'))
    with open('validation_states\\' + validation_file, 'rb') as input_file:
        validation = pickle.load(input_file)

    min_val_error = 10000.0
    for i in range(config.TRAINING_LOOPS):
        print ("Iteration #" + str(i))

        batch_states = []
        batch_target_results = []
        batch_target_probs = []
        
        game_file = choice(listdir('train_states'))
        with open('train_states\\' + game_file, 'rb') as input_file:
            game_memory = pickle.load(input_file)
        remove('train_states\\' + game_file)
            
        hist = net.fit(game_memory['batch_states'], game_memory['batch_targets'], config.EPOCHS, 2, 0.0, 32, (validation['batch_states'], validation['batch_targets']))
        
        if train_phase[1] == 'value':
            metric = hist.history['val_value_head_loss'][config.EPOCHS - 1]
        else:
            metric = hist.history['val_policy_head_loss'][config.EPOCHS - 1]
            
        if metric < min_val_error:
            min_val_error = metric
            net.write(agent, net_str)
            
        print ("Min Loss: " + str(min_val_error))