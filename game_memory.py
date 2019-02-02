import numpy as np

class GameMemory():
    def __init__(self, game_uuid):
        self.game_id = game_uuid
        self.states = []
        self.game_results = []
    
    def add_to_memory_states(self, player, nn_state, posterior_probs):
        self.states.append((player, nn_state, posterior_probs))
    
    def add_game_result(self, result):
        for k, s in enumerate(self.states):
            self.game_results.append(np.zeros(4))
            for p in range(4):
                p_order = (4 + p - s[0]) % 4
                self.game_results[k] = result[p]
