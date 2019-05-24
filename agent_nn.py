import numpy as np

import config
from model import Residual_CNN

class Agent_NN:
    def __init__(self, enable_cache = False):
        self.nn_start = Residual_CNN(config.REG_CONST, config.LEARNING_RATE, config.INPUT_START_DIM, config.OUTPUT_START_DIM, config.HIDDEN_CNN_LAYERS)
        self.nn = Residual_CNN(config.REG_CONST, config.LEARNING_RATE, config.INPUT_DIM, config.OUTPUT_DIM, config.HIDDEN_CNN_LAYERS)
        
        self.enable_cache = enable_cache
        self.cache = {}
        
    def nn_read(self, name):
        self.nn_start.read(name, 's')
        self.nn.read(name, 'g')
        
    def nn_write(self, name):
        self.nn_start.write(name, 's')
        self.nn.write(name, 'g')
    
    def predict(self, state, perspective, mcts, determined = 0):
        network = self.build_nn_input(state, perspective, mcts = mcts, determined = 0)
    
        if network.shape[1] == config.INPUT_DIM[0]:
            return self.nn.predict(network)
        else:
            return self.nn_start.predict(network)
    
    def build_start_nn_input(self, state, perspective):
        nn_input = np.zeros((1, config.INPUT_START_DIM[0], config.INPUT_START_DIM[1], config.INPUT_START_DIM[2]), dtype=np.float32)

        numbers_output = {2: 1, 3: 2, 4: 3, 5: 4, 6: 5, 8: 5, 9: 4, 10: 3, 11: 2, 12: 1}
        rotation = np.random.randint(12)
        
        if self.enable_cache is True and rotation in self.cache:
            nn_input[:, :11, :, :] = self.cache[rotation]
            
        else:
            # Resources outputs
            for number, tile in state.numbers:
                resource = state.tiles[tile]
                for vertex in config.tiles_vertex[tile]:
                    nn_input[0, resource - 2, config.vertex_to_nn_input[rotation][vertex][0], config.vertex_to_nn_input[rotation][vertex][1]] += numbers_output[number] / 15.0
    
            # Ports
            for key, r in enumerate([config.SHEEP, config.ORE, config.BRICK, config.WHEAT, config.WOOD, config.GENERIC]):
                indices = [i for i, x in enumerate(state.ports) if x == r]
                for i in indices:
                    for vertex in config.ports_vertex[i]['vert']:
                        nn_input[0, key + 5, config.vertex_to_nn_input[rotation][vertex][0], config.vertex_to_nn_input[rotation][vertex][1]] = 1
                        
            if self.enable_cache is True:
                self.cache[rotation] = nn_input[:, :11, :, :]
        
        # Settlements, cities, roads
        for p in range(4):
            p_order = (4 + p - perspective) % 4
            for s in state.players[p].settlements:
                nn_input[0, 11 + 2 * p_order, config.vertex_to_nn_input[rotation][s][0], config.vertex_to_nn_input[rotation][s][1]] = 1
            for r in state.players[p].roads:
                nn_input[0, 12 + 2 * p_order, config.vertex_to_nn_input[rotation][r[0]][0], config.vertex_to_nn_input[rotation][r[0]][1]] += 1 / 3.0
                nn_input[0, 12 + 2 * p_order, config.vertex_to_nn_input[rotation][r[1]][0], config.vertex_to_nn_input[rotation][r[1]][1]] += 1 / 3.0

        # Cards
        for p in range(4):
            p_order = (4 + p - perspective) % 4

            for key, r in enumerate([config.SHEEP, config.ORE, config.BRICK, config.WHEAT, config.WOOD]):
                nn_input[0, 19 + key + 5 * p_order, :, :] = state.players[p].cards[r] / 10.0
                
        # State
        if (state.game_phase == config.PHASE_INITIAL_SETTLEMENT or state.game_phase == config.PHASE_INITIAL_ROAD) and state.initial_phase_decrease == 0:
            nn_input[0, 39, :, :] = 1
        if (state.game_phase == config.PHASE_INITIAL_SETTLEMENT or state.game_phase == config.PHASE_INITIAL_ROAD) and state.initial_phase_decrease == 1:
            nn_input[0, 40, :, :] = 1

        # Player turn
        for p in range(4):
            p_order = (4 + p - perspective) % 4
            if p == state.player_turn:
                nn_input[0, 41 + p_order, :, :] = 1

        return nn_input

    def build_nn_input(self, state, perspective, mcts = None, determined = 0):
        if state.game_phase == config.PHASE_INITIAL_SETTLEMENT or state.game_phase == config.PHASE_INITIAL_ROAD:
            return self.build_start_nn_input(state, perspective)
        
        nn_input = np.zeros((1, config.INPUT_DIM[0], config.INPUT_DIM[1], config.INPUT_DIM[2]), dtype=np.float32)

        numbers_output = {2: 1, 3: 2, 4: 3, 5: 4, 6: 5, 8: 5, 9: 4, 10: 3, 11: 2, 12: 1}
        rotation = np.random.randint(12)
        
        if self.enable_cache is True and rotation in self.cache:
            nn_input[:, :11, :, :] = self.cache[rotation]
            
        else:
            # Resources outputs
            for number, tile in state.numbers:
                resource = state.tiles[tile]
                for vertex in config.tiles_vertex[tile]:
                    nn_input[0, resource - 2, config.vertex_to_nn_input[rotation][vertex][0], config.vertex_to_nn_input[rotation][vertex][1]] += numbers_output[number] / 15.0
    
            # Ports
            for key, r in enumerate([config.SHEEP, config.ORE, config.BRICK, config.WHEAT, config.WOOD, config.GENERIC]):
                indices = [i for i, x in enumerate(state.ports) if x == r]
                for i in indices:
                    for vertex in config.ports_vertex[i]['vert']:
                        nn_input[0, key + 5, config.vertex_to_nn_input[rotation][vertex][0], config.vertex_to_nn_input[rotation][vertex][1]] = 1
                        
            if self.enable_cache is True:
                self.cache[rotation] = nn_input[:, :11, :, :]
        
        # Settlements, cities, roads
        for p in range(4):
            p_order = (4 + p - perspective) % 4
            for s in state.players[p].settlements:
                nn_input[0, 11 + 3 * p_order, config.vertex_to_nn_input[rotation][s][0], config.vertex_to_nn_input[rotation][s][1]] = 1
            for c in state.players[p].cities:
                nn_input[0, 12 + 3 * p_order, config.vertex_to_nn_input[rotation][c][0], config.vertex_to_nn_input[rotation][c][1]] = 1
            for r in state.players[p].roads:
                nn_input[0, 13 + 3 * p_order, config.vertex_to_nn_input[rotation][r[0]][0], config.vertex_to_nn_input[rotation][r[0]][1]] += 1 / 3.0
                nn_input[0, 13 + 3 * p_order, config.vertex_to_nn_input[rotation][r[1]][0], config.vertex_to_nn_input[rotation][r[1]][1]] += 1 / 3.0

        # Cards
        for p in range(4):
            p_order = (4 + p - perspective) % 4
            
            if determined == 0 and p != mcts.player_id:
                min_cards = mcts.get_undetermined_resources_rivals(p)
                
                for key, r in enumerate([config.SHEEP, config.ORE, config.BRICK, config.WHEAT, config.WOOD]):
                    nn_input[0, 23 + key + 5 * p_order, :, :] = min_cards[key] / 10.0         
                    
            else:
                for key, r in enumerate([config.SHEEP, config.ORE, config.BRICK, config.WHEAT, config.WOOD]):
                    nn_input[0, 23 + key + 5 * p_order, :, :] = state.players[p].cards[r] / 10.0

        # Robber
        for vertex in config.tiles_vertex[state.robber_tile]:
            nn_input[0, 43, config.vertex_to_nn_input[rotation][vertex][0], config.vertex_to_nn_input[rotation][vertex][1]] = 1

        # Army Cards Played
        for p in range(4):
            p_order = (4 + p - perspective) % 4
            nn_input[0, 44 + p_order, :, :] = state.players[p].used_knights / 5.0

        # Army Holder
        for p in range(4):
            p_order = (4 + p - perspective) % 4
            nn_input[0, 48 + p_order, :, :] = state.players[p].largest_army_badge

        # Longest Road Holder
        for p in range(4):
            p_order = (4 + p - perspective) % 4
            nn_input[0, 52 + p_order, :, :] = state.players[p].longest_road_badge
            
        # Special Cards
        for p in range(4):
            p_order = (4 + p - perspective) % 4
            
            if determined == 1 or p == mcts.player_id:
                for key, r in enumerate([config.VICTORY_POINT, config.KNIGHT, config.MONOPOLY, config.ROAD_BUILDING, config.YEAR_OF_PLENTY]):
                    nn_input[0, 56 + key + 5 * p_order, :, :] = state.players[p].special_cards.count(r) / 3.0

        # Discarding, initial game phase
        if state.game_phase == config.PHASE_DISCARD:
            nn_input[0, 76, :, :] = 1

        # Player turn
        for p in range(4):
            p_order = (4 + p - perspective) % 4
            if p == state.player_turn:
                nn_input[0, 77 + p_order, :, :] = 1

        # Other game phases
        if state.game_phase == config.PHASE_THROW_DICE:
            nn_input[0, 81, :, :] = 1
        if state.game_phase == config.PHASE_MOVE_ROBBER:
            nn_input[0, 82, :, :] = 1
        if state.game_phase == config.PHASE_STEAL_CARD:
            nn_input[0, 83, :, :] = 1
        if state.game_phase == config.PHASE_ROAD_BUILDING:
            nn_input[0, 84, :, :] = 1
        if state.game_phase == config.PHASE_YEAR_OF_PLENTY:
            nn_input[0, 85, :, :] = 1
        if state.game_phase == config.PHASE_TRADE_RESPOND:
            nn_input[0, 86, :, :] = 1
            
        for s in range(54):
            if state.available_settlement_spot(s):
                nn_input[0, 87, config.vertex_to_nn_input[rotation][s][0], config.vertex_to_nn_input[rotation][s][1]] = 1

        return nn_input