import config
import numpy as np

class Agent_Heuristic():
    def __init__(self):
        self.state = None
        self.perspective = None
        self.mcts = None
        self.points = None
        
        self.cache_tile_output = {}
        self.robber_correction = 0.7
        self.numbers_output = {2: 1, 3: 2, 4: 3, 5: 4, 6: 5, 8: 5, 9: 4, 10: 3, 11: 2, 12: 1}
        self.resources_value = np.array([0.025, 0.035, 0.03, 0.03, 0.03])
        
    def predict(self, state, perspective, mcts):
        self.state = state
        self.perspective = perspective
        self.mcts = mcts    
        
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
            b += 0.2 * self.state.players[p].special_cards.count(config.VICTORY_POINT)
            
            base_value.append(b)
            
        base_value = np.array(base_value) + 0.4 * self.army_probs()
        base_value = np.array(base_value) + 0.4 * self.long_road_probs()
            
        return base_value
    
    def players_points(self):
        points = []
        
        for p in range(4):
            points.append(self.state.players[p].points(hidden = 0))
                
        return np.array(points)
        
    def get_tile_output(self, tile):
        if tile in self.cache_tile_output:
            if tile == self.state.robber_tile:
                return self.robber_correction * self.cache_tile_output[tile]
            else:
                return self.cache_tile_output[tile]
        
        for number, tile_n in self.state.numbers:
            if tile == tile_n:
                self.cache_tile_output[tile] = self.numbers_output[number]
                if tile == self.state.robber_tile:
                    return self.robber_correction * self.numbers_output[number]
                else:
                    return self.numbers_output[number]
                
    def get_vertex_output(self, vertex):        
        resources = np.array([0, 0, 0, 0, 0])
        for tile in config.vertex_tiles[vertex]:
            if self.state.tiles[tile] != config.DESERT:
                resources[self.state.tiles[tile] - 2] += self.get_tile_output(tile)
                    
        return resources
    
    def get_port_output(self, vertex, player):
        for p, value in config.ports_vertex.items():
            if vertex in value['vert']:
                if self.state.ports[p] == config.GENERIC and config.GENERIC not in self.state.players[player].ports:
                    return 0.05
                else:
                    return 0.025
                return 0.0
            
        return 0.0
            
    def extra_value(self):
        extra_value = []
        
        for p in range(4):
            resources = np.array([0, 0, 0, 0, 0])
            
            # Resources
            for s in self.state.players[p].settlements:
                resources += resources + self.get_vertex_output(s)
                        
            for c in self.state.players[p].cities:
                resources += resources + 2 * self.get_vertex_output(c)
                            
            estimated_value = np.sum(self.resources_value * resources)
                
            has_road_in_pot_sett = 0
            max_value_potential_settl = 0.0
            # Has road in potential settlement
            for r in self.state.players[p].roads:
                for v in r:
                    if self.state.available_settlement_spot(v):
                        has_road_in_pot_sett = 1
                        v_value = np.sum(self.resources_value * self.get_vertex_output(v)) + self.get_port_output(v, p)
                        if v_value > max_value_potential_settl:
                            max_value_potential_settl = v_value
                        
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
            elif self.state.players[p].available_resources('settlement'):
                estimated_value += 0.1 + 0.15 * max_value_potential_settl
            elif has_road_in_pot_sett == 1:
                estimated_value += 0.05 + 0.15 * max_value_potential_settl
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
                
            # Ports
            for p in self.state.players[p].ports:
                if p == config.GENERIC:
                    estimated_value += 0.05
                else:
                    estimated_value += 0.025                    
                            
            extra_value.append(estimated_value)
            
        return np.array(extra_value)