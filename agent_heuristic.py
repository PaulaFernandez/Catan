import config
import numpy as np

class Agent_Heuristic():
    def __init__(self):
        self.state = None
        self.perspective = None
        self.mcts = None
        self.determined = None
        self.points = None
        
    def predict(self, state, perspective, mcts, determined = 0):
        self.state = state
        self.perspective = perspective
        self.mcts = mcts
        self.determined = determined        
        
        self.points = self.players_points()
        base_values = self.base_value()
        extra_value = self.extra_value()
        
        sum_value = np.max([np.sum(extra_value), 0.01])
        max_points = np.max(self.points)
        extra_value = extra_value * (2.0 - 0.15 * max_points) / sum_value
        
        if self.state.game_phase == config.PHASE_INITIAL_SETTLEMENT or self.state.game_phase == config.PHASE_INITIAL_ROAD:
            move_probabilities = [0.1] * config.OUTPUT_START_DIM
        else:
            move_probabilities = [0.1] * config.OUTPUT_DIM
        
        return [[[base_values[self.perspective] + extra_value[self.perspective]]], [move_probabilities]]
    
    def long_road_probs(self):
        max_points = np.max(self.points)
        
        longest_road = np.array([p.longest_road + p.longest_road_badge + 2 for p in self.state.players])
        lr_power = np.power(longest_road, max_points - 2.5)
        
        return lr_power / np.sum(lr_power)
    
    def army_probs(self):
        max_points = np.max(self.points)
        
        army_played = np.array([p.used_knights + p.largest_army_badge + 1 for p in self.state.players])
        la_power = np.power(army_played, max_points - 2.5)
        
        return la_power / np.sum(la_power)
        
    def base_value(self):
        base_value = []
        
        for p in range(4):
            b = -1.4
            
            # Settlements / Cities
            b += 0.2 * len(self.state.players[p].settlements)
            b += 0.4 * len(self.state.players[p].cities)
            
            # Points Cards
            if self.determined == 1 or p == self.mcts.player_id:
                b += 0.2 * self.state.players[p].special_cards.count(config.VICTORY_POINT)
                
            if self.state.players[p].longest_road_badge == 1:
                b += 0.3
                
            #if self.state.players[p].largest_army_badge == 1:
            #    b += 0.3
            
            base_value.append(b)
            
        base_value = np.array(base_value) + 0.4 * self.army_probs()
            
        return base_value
    
    def players_points(self):
        points = []
        
        for p in range(4):
            if self.determined == 1 or p == self.mcts.player_id:
                points.append(self.state.players[p].points(hidden = 1))
            else:
                points.append(self.state.players[p].points(hidden = 0))
                
        return np.array(points)
        
    def get_tile_output(self, tile):
        numbers_output = {2: 1, 3: 2, 4: 3, 5: 4, 6: 5, 8: 5, 9: 4, 10: 3, 11: 2, 12: 1}
        robber_correction = 0.7
        
        for number, tile_n in self.state.numbers:
            if tile == tile_n:
                if self.state.robber_tile == tile:
                    return robber_correction * numbers_output[number]
                else:
                    return numbers_output[number]
            
    def extra_value(self):
        extra_value = []
        
        for p in range(4):
            resources = np.array([0, 0, 0, 0, 0])
            
            # Resources
            for s in self.state.players[p].settlements:
                for tile, vertices in config.tiles_vertex.items():
                    if s in vertices:
                        if self.state.tiles[tile] != config.DESERT:
                            resources[self.state.tiles[tile] - 2] += self.get_tile_output(tile)
                        
            for c in self.state.players[p].cities:
                for tile, vertices in config.tiles_vertex.items():
                    if c in vertices:
                        if self.state.tiles[tile] != config.DESERT:
                            resources[self.state.tiles[tile] - 2] += 2 * self.get_tile_output(tile)
                            
            estimated_value = np.sum(np.array([0.025, 0.035, 0.03, 0.03, 0.03]) * resources)
                
            has_road_in_pot_sett = 0
            # Has road in potential settlement
            for r in self.state.players[p].roads:
                for v in r:
                    if self.state.available_settlement_spot(v):
                        has_road_in_pot_sett = 1
                        break
                        
            # Has road 1 step from potential settlement
            has_road_at_1_step = 0
            if has_road_in_pot_sett == 0:
                for r in self.state.players[p].roads:
                    for v in r:
                        for x in config.roads_from_settlement[v]:
                            if v == x[0]:
                                if self.state.available_settlement_spot(x[1]):
                                    has_road_at_1_step = 1
                                    break
                            elif v == x[1]:
                                if self.state.available_settlement_spot(x[0]):
                                    has_road_at_1_step = 1
                                    break
                    if has_road_at_1_step == 1:
                        break
                                    
            
            # Cards In Hand
            if self.state.players[p].available_resources('city'):
                estimated_value += 0.175
            if self.state.players[p].available_resources('settlement') and has_road_in_pot_sett == 1:
                estimated_value += 0.175
            elif self.state.players[p].available_resources('settlement'):
                estimated_value += 0.1
            elif has_road_in_pot_sett == 1:
                estimated_value += 0.05
            elif has_road_at_1_step == 1:
                estimated_value += 0.02
            if self.state.players[p].available_resources('road'):
                estimated_value += 0.025
            if self.state.players[p].available_resources('special_card'):
                estimated_value += 0.05
                
            # Special Cards In Hand
            if config.KNIGHT in self.state.players[p].special_cards:
                estimated_value += 0.025
            if config.MONOPOLY in self.state.players[p].special_cards:
                estimated_value += 0.05
            if config.ROAD_BUILDING in self.state.players[p].special_cards:
                estimated_value += 0.025
            if config.YEAR_OF_PLENTY in self.state.players[p].special_cards:
                estimated_value += 0.05
                
            # More 7 cards penalty
            if self.state.players[p].total_cards() > 7:
                estimated_value -= 0.02
                            
            extra_value.append(estimated_value)
            
        return np.array(extra_value)