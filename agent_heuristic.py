import config
import numpy as np

class Agent_Heuristic():
    def __init__(self):
        pass
        
    def predict(self, state, perspective, mcts, determined = 0):
        base_values = self.base_value(state, mcts, determined)
        points = self.players_points(state, mcts, determined)
        extra_value = self.extra_value(state, mcts)
        
        sum_value = np.max([np.sum(extra_value), 0.01])
        max_points = np.max(points)
        extra_value = extra_value * (2.0 - 0.1 * max_points) / sum_value
        
        if state.game_phase == config.PHASE_INITIAL_SETTLEMENT or state.game_phase == config.PHASE_INITIAL_ROAD:
            move_probabilities = [0.1] * config.OUTPUT_START_DIM
        else:
            move_probabilities = [0.1] * config.OUTPUT_DIM
        
        return [[[base_values[perspective] + extra_value[perspective]]], [move_probabilities]]
        
    def base_value(self, state, mcts, determined):
        base_value = []
        
        for p in range(4):
            b = -1.0
            
            # Settlements / Cities
            b += 0.2 * len(state.players[p].settlements)
            b += 0.4 * len(state.players[p].cities)
            
            # Points Cards
            if determined == 1 or p == mcts.player_id:
                b += 0.2 * state.players[p].special_cards.count(config.VICTORY_POINT)
                
            if state.players[p].longest_road_badge == 1:
                b += 0.3
                
            if state.players[p].largest_army_badge == 1:
                b += 0.3
            
            base_value.append(b - 0.4)
            
        return np.array(base_value)
    
    def players_points(self, state, mcts, determined):
        points = []
        
        for p in range(4):
            if determined == 1 or p == mcts.player_id:
                points.append(state.players[p].points(hidden = 1))
            else:
                points.append(state.players[p].points(hidden = 0))
                
        return np.array(points)
    
    def extra_value(self, state, mcts):
        extra_value = []
        
        for p in range(4):
            resources = np.array([0, 0, 0, 0, 0])
            
            # Resources
            for s in state.players[p].settlements:
                for tile, vertices in config.tiles_vertex.items():
                    if s in vertices:
                        if state.tiles[tile] != config.DESERT:
                            resources[state.tiles[tile] - 2] += 1
                        
            for c in state.players[p].cities:
                for tile, vertices in config.tiles_vertex.items():
                    if c in vertices:
                        if state.tiles[tile] != config.DESERT:
                            resources[state.tiles[tile] - 2] += 2
                            
            estimated_value = np.sum(np.array([0.15, 0.2, 0.15, 0.15, 0.15]) * resources)
                
            has_road_in_pot_sett = 0
            # Has road in potential settlement
            for r in state.players[p].roads:
                for v in r:
                    if state.available_settlement_spot(v):
                        has_road_in_pot_sett = 1
                        break
            
            # Cards In Hand
            if state.players[p].available_resources('city'):
                estimated_value += 0.2
            if state.players[p].available_resources('settlement') and has_road_in_pot_sett == 1:
                estimated_value += 0.2
            elif state.players[p].available_resources('settlement'):
                estimated_value += 0.1
            elif has_road_in_pot_sett == 1:
                estimated_value += 0.05
            if state.players[p].available_resources('road'):
                estimated_value += 0.025
            if state.players[p].available_resources('special_card'):
                estimated_value += 0.05
                            
            extra_value.append(estimated_value)
            
        return np.array(extra_value)