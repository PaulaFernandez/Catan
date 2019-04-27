import numpy as np

from create_train_states import create_sets
from train_network import train_network
import config

from agent_nn import Agent_NN

training_passes = [('start', 'value'), ('start', 'policy'), ('general', 'value'), ('general', 'policy')]
agents_to_train = [7, 8]
new_agents = [10, 11]

# New combinations
agents = []
for a in agents_to_train:
    agent_object = Agent_NN()
    agent_object.nn_read(a)
    agents.append(agent_object)
    
new_agent_breed = Agent_NN()
for nets in ['nn', 'nn_start']:
    nn0 = getattr(agents[0], nets)
    nn1 = getattr(agents[1], nets)
    
    nn_new = getattr(new_agent_breed, nets)
    
    break_point = np.random.randint(len(nn0.model.layers))
    
    for i in range(len(nn0.model.layers)):
        if i < break_point:
            nn_new.model.set_weights(nn0.model.get_weights())
        else:
            nn_new.model.set_weights(nn1.model.get_weights())
            
for i, new_networks in enumerate([new_agent_breed, agents[0]]):
    choice = np.random.randint(2)
    if choice == 0:
        try:
            random_layer = np.random.randint(len(new_networks.nn_start.model.layers))
            required_shape = new_networks.nn_start.model.layers[random_layer].shape
            new_networks.nn_start.model.layers[random_layer].set_weights(np.random.randn(required_shape))
        except:
            pass
    elif choice == 1:
        try:
            random_layer = np.random.randint(len(new_networks.nn.model.layers))
            required_shape = new_networks.nn.model.layers[random_layer].shape
            new_networks.nn.model.layers[random_layer].set_weights(np.random.randn(required_shape))
        except:
            pass
        
    new_networks.nn_write(new_agents[i])

# Create states
val_states_per_loop = 1
val_number_of_sets = 1
states_per_loop = 10
number_of_sets = 4

for net, head in training_passes:
    # Validation
    for i in range(val_number_of_sets):
        print ("Validation Iteration #" + str(i))
        create_sets('validation', config.VALIDATION_BATCH_SIZE, i, val_states_per_loop, net, head)

    # Training
    for i in range(number_of_sets):
        print ("Iteration #" + str(i))
        create_sets('training', config.TRAIN_BATCH_SIZE, i, states_per_loop, net, head)
        
    for a in new_agents:
        print ("Training Agent: " + str(a))
        train_network(a, (net, head))