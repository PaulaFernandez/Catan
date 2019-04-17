from create_train_states import create_sets
from train_network import train_network
import config

training_passes = [('start', 'value'), ('start', 'policy'), ('general', 'value'), ('general', 'policy')]
agents_to_train = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]

# Create states
val_states_per_loop = 1
val_number_of_sets = 1
states_per_loop = 50#30
number_of_sets = 100#50

for net, head in training_passes:
    # Validation
    for i in range(val_number_of_sets):
        print ("Validation Iteration #" + str(i))
        create_sets('validation', config.VALIDATION_BATCH_SIZE, i, val_states_per_loop, net, head)

    # Training
    for i in range(number_of_sets):
        print ("Iteration #" + str(i))
        create_sets('training', config.TRAIN_BATCH_SIZE, i, states_per_loop, net, head)
        
    for a in agents_to_train:
        print ("Training Agent: " + str(a))
        train_network(a, (net, head))