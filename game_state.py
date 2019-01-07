from random import shuffle, choice
from copy import deepcopy
import uuid
import player
import config
from mcts_ai import MCTS_AI

class GameState:
    def __init__(self):
        self.uuid = uuid.uuid1()
        self.counter = 0

        self.tiles = self.generate_tiles()
        self.numbers = self.generate_numbers()
        self.ports = self.generate_ports()
        self.special_cards = self.generate_special_cards()
        self.current_action = -1
        self.initial_phase_settlement = 0
        self.initial_phase_decrease = 0
        self.dices = (0, 0)
        self.players_to_discard = []
        self.houses_to_steal_from = []
        self.roads_in_road_building = 0
        self.resources_in_year_of_plenty = 0
        self.special_card_played_in_turn = 0
        self.winner = None

        # Robber initial position
        self.robber_tile = self.tiles.index(config.DESERT)

        self.players = []
        for i in range(4): # 4 players
            self.players.append(player.Player(i, config.player_is_human[i]))

            if config.player_is_human[i] == 0:
                self.players[i].ai = MCTS_AI(1)

        self.max_road = {0: 1, 1: 1, 2: 1, 3: 1}
        
        # Starting player
        self.player_turn = choice([0, 1, 2, 3])
        self.initial_phase_start_player = self.player_turn

        # Log
        self.log = "Player " + str(self.player_turn + 1) + ": place settlement"

        # Game Phase
        self.game_phase = config.PHASE_INITIAL_SETTLEMENT

    @staticmethod
    def generate_ports():
        ports = []

        for key, value in config.port_types.items():
            ports.extend([key] * value['number'])
        shuffle(ports)

        return ports

    @staticmethod
    def generate_tiles():
        shuffled_tiles = []
        for key, value in config.tile_types.items():
            if key != config.WATER:
                shuffled_tiles.extend([key] * value['number'])
        shuffle(shuffled_tiles)

        tiles = []

        for i in range(37):
            if i in config.water_tiles:
                tiles.append(config.WATER)
                continue
            tiles.append(shuffled_tiles.pop())

        return tiles

    @staticmethod
    def roads_from_settlement(sett_num):
        return config.roads_from_settlement[sett_num]

    @staticmethod
    def generate_special_cards():
        special_cards = []

        for key, value in config.special_cards.items():
            special_cards.extend([key] * value['count'])
        shuffle(special_cards)
        return special_cards

    def generate_numbers(self):
        numbers = config.roll_numbers
        shuffle(numbers)

        numbers_tiles = []
        j = 0
        for i in range(len(self.tiles)):
            if self.tiles[i] != config.WATER and self.tiles[i] != config.DESERT:
                numbers_tiles.append((numbers[j], i))
                j += 1

        return numbers_tiles

    def next_player(self):
        if self.game_phase[0] == 1:
            self.player_turn = (self.player_turn + 1) % 4
            self.log = "Player " + str(self.player_turn + 1) + ": throw dice"
            return

        if self.initial_phase_decrease == 1:
            if self.player_turn == self.initial_phase_start_player:
                self.game_phase = config.PHASE_THROW_DICE
                self.log = "Player " + str(self.player_turn + 1) + ": throw dice"
                return

            self.player_turn = (self.player_turn - 1) % 4

            return

        if (self.initial_phase_start_player + 3) % 4 == self.player_turn:
            self.initial_phase_decrease = 1
            return

        self.player_turn = (self.player_turn + 1) % 4

        return

    def total_resources_in_play(self):
        resources_in_play = {config.BRICK: 0, config.ORE: 0, config.WHEAT: 0, config.WOOD: 0, config.SHEEP: 0}
        for player_x in self.players:
            for resource in resources_in_play:
                resources_in_play[resource] += player_x.cards[resource]

        return resources_in_play

    def dice_resources(self, result):
        resources_to_distribute = []
        for number, tile in self.numbers:
            if number == result and self.robber_tile != tile:
                resource = self.tiles[tile]

                for player_x in self.players:
                    for settlement in player_x.settlements:
                        if settlement in config.tiles_vertex[tile]:
                            resources_to_distribute.append((player_x.player_id, {resource: 1}))

                    for city in player_x.cities:
                        if city in config.tiles_vertex[tile]:
                            resources_to_distribute.append((player_x.player_id, {resource: 2}))

        distribute_resource = {config.BRICK: True, config.ORE: True, config.WHEAT: True, config.WOOD: True, config.SHEEP: True}
        resources_in_play = self.total_resources_in_play()
        for resource, in_play in resources_in_play.items():
            total_resources = in_play + sum([y[resource] for x, y in resources_to_distribute if resource in y])
            if total_resources > config.max_resources:
                distribute_resource[resource] = False

        for player_id, resources in resources_to_distribute:
            if distribute_resource[list(resources)[0]]:
                self.players[player_id].add_resources(resources)

    def calculate_throw_dice(self):
        dice_1 = choice([1, 2, 3, 4, 5, 6])
        dice_2 = choice([1, 2, 3, 4, 5, 6])
        self.dices = (dice_1, dice_2)

        result = dice_1 + dice_2
        self.execute_dice_result(result)

    def execute_dice_result(self, result):
        self.log = "Dice result = " + str(result)
        self.dice_resources(result)

        if result == 7:
            self.game_phase = config.PHASE_DISCARD

            for player_x in self.players:
                if player_x.total_cards() > 7:
                    self.players_to_discard.append((player_x.player_id, int(player_x.total_cards() / 2)))

            if len(self.players_to_discard) == 0:
                self.game_phase = config.PHASE_MOVE_ROBBER
                self.log = "Move the robber"
            else:
                self.log = "Player " + str(self.players_to_discard[0][0] + 1) + ": Discard " + str(self.players_to_discard[0][1]) + " cards"
        else:
            self.game_phase = config.PHASE_WAIT
            self.log = "Choose your action"

    def initial_settlement_resources(self, vertex):
        for tile, vertices in config.tiles_vertex.items():
            if vertex in vertices:
                if self.tiles[tile] in self.players[self.player_turn].cards:
                    self.players[self.player_turn].cards[self.tiles[tile]] += 1

    def valid_settlement(self, vertex):
        def settlement_clash(vertex_1, vertex_2):
            return config.settlement_clash[(vertex_1, vertex_2)]

        def road_reaches_vertex(vertex, player_roads):
            for road in player_roads:
                if road[0] == vertex or road[1] == vertex:
                    return True

            return False

        if vertex < 0:
            return False

        for player_x in self.players:
            for settlement in player_x.settlements + player_x.cities:
                if settlement_clash(vertex, settlement):
                    return False

        if self.game_phase == config.PHASE_WAIT:
            if road_reaches_vertex(vertex, self.players[self.player_turn].roads) is False:
                return False

        return True

    def valid_roads(self):
        def vertex_is_rival(self, vertex):
            for player_x in (x for x in self.players if x.player_id != self.player_turn):
                if vertex in player_x.settlements + player_x.cities:
                    return True
            return False

        potential_roads = set()
        for road in self.players[self.player_turn].roads:
            for vertex in road:
                if vertex_is_rival(self, vertex) is False:
                    potential_roads = potential_roads | self.roads_from_settlement(vertex)

        for player_x in self.players:
            for road in player_x.roads:
                if road in potential_roads:
                    potential_roads.remove(road)

        return potential_roads

    def valid_city(self):
        return self.players[self.player_turn].settlements

    def calculate_all_roads(self, available_roads_cycle, player_id):
        def ends_to_explore(potential_roads):
            for road_id, road in enumerate(potential_roads):
                if road['start_vertex'][1] == 1:
                    return (road_id, 'start_vertex')
                elif road['end_vertex'][1] == 1:
                    return (road_id, 'end_vertex')

            return False

        all_roads = []
        if len(available_roads_cycle) == 0:
            return []

        for start_road in available_roads_cycle:
            available_roads = deepcopy(available_roads_cycle)

            # Starting road
            available_roads.remove(start_road)
            start_road = {'sections': [start_road], 'start_vertex': (start_road[0], 1), 'end_vertex': (start_road[1], 1)}
            potential_roads = [start_road]
            road_end = ends_to_explore(potential_roads)

            while road_end:
                vertex = potential_roads[road_end[0]][road_end[1]][0]
                end_while = False

                # End is rival settlement
                for player_x in (x for x in self.players if x.player_id != player_id):
                    if vertex in player_x.settlements + player_x.cities:
                        potential_roads[road_end[0]][road_end[1]] = (vertex, 0) # Can't jump over rival settlement
                        end_while = True

                if end_while:
                    road_end = ends_to_explore(potential_roads)
                    continue

                neighbours = self.roads_from_settlement(vertex)

                valid_neighbours_found = False
                for next_road in neighbours:
                    if next_road in self.players[player_id].roads and next_road not in potential_roads[road_end[0]]['sections']:
                        if next_road[0] == vertex:
                            new_end = next_road[1]
                        else:
                            new_end = next_road[0]

                        if road_end[1] == 'start_vertex':
                            start_v = (new_end, 1)
                            end_v = potential_roads[road_end[0]]['end_vertex']
                        else:
                            start_v = potential_roads[road_end[0]]['start_vertex']
                            end_v = (new_end, 1)

                        new_road = {'sections': potential_roads[road_end[0]]['sections'] + [next_road],
                                    'start_vertex': start_v,
                                    'end_vertex': end_v}

                        potential_roads.append(new_road)
                        valid_neighbours_found = True

                        if next_road in available_roads:
                            available_roads.remove(next_road)

                if valid_neighbours_found:
                    potential_roads.pop(road_end[0])
                else:
                    potential_roads[road_end[0]][road_end[1]] = (vertex, 0)

                road_end = ends_to_explore(potential_roads)

            all_roads = all_roads + potential_roads

        return all_roads

    def calculate_longest_road(self, player_id):
        current_holder = -1

        all_roads = self.calculate_all_roads(self.players[player_id].roads, player_id)
        road_lengths = [len(x['sections']) for x in all_roads]
        self.max_road[player_id] = max(road_lengths)

        for player_x in self.players:
            if player_x.longest_road_badge == 1:
                current_holder = player_x.player_id

        if self.max_road[player_id] < 5:
            if current_holder == player_id:
                self.players[player_id].longest_road_badge = 0

                long_road = [(-1, 0)]
                for player_x in self.players:
                    if self.max_road[player_x.player_id] > long_road[0][1]:
                        long_road = [(player_x.player_id, self.max_road[player_x.player_id])]
                    elif self.max_road[player_x.player_id] == long_road[0][1]:
                        long_road.append((player_x.player_id, self.max_road[player_x.player_id]))

                if len(long_road) == 1 and long_road[0][0] != -1:
                    self.players[long_road[0][0]].longest_road_badge = 1
            else:
                return
        else:
            if current_holder == -1:
                self.players[player_id].longest_road_badge = 1
            elif self.max_road[current_holder] >= self.max_road[player_id]:
                return
            else:
                self.players[current_holder].longest_road_badge = 0
                self.players[player_id].longest_road_badge = 1

    def check_largest_army_badge(self):
        for player_x in self.players:
            if player_x.used_knights >= self.players[self.player_turn].used_knights and player_x.player_id != self.player_turn:
                return
            else:
                player_x.largest_army_badge = 0

        self.players[self.player_turn].largest_army_badge = 1

    def handle_build_settlement(self, vertex_released):
        if self.valid_settlement(vertex_released):

            if self.game_phase == config.PHASE_INITIAL_SETTLEMENT:
                self.game_phase = config.PHASE_INITIAL_ROAD
                self.players[self.player_turn].settlements.append(vertex_released)
                self.initial_phase_settlement = vertex_released
                self.initial_settlement_resources(vertex_released)
                self.log = "Player " + str(self.player_turn + 1) + ": place road"

            elif self.game_phase == config.PHASE_WAIT and self.players[self.player_turn].available_resources('settlement'):
                self.players[self.player_turn].remove_resources_by_improvement('settlement')
                self.players[self.player_turn].settlements.append(vertex_released)
                #self.calculate_longest_road()

        self.current_action = -1

    def handle_build_city(self, vertex_released):
        if vertex_released in self.valid_city() and self.players[self.player_turn].available_resources('city'):
            self.players[self.player_turn].settlements.remove(vertex_released)
            self.players[self.player_turn].cities.append(vertex_released)
            self.players[self.player_turn].remove_resources_by_improvement('city')

        self.current_action = -1

    def handle_build_road(self, road_released):
        if self.game_phase == config.PHASE_INITIAL_ROAD:
            if road_released in self.roads_from_settlement(self.initial_phase_settlement):
                self.players[self.player_turn].roads.append(road_released)
                self.game_phase = config.PHASE_INITIAL_SETTLEMENT
                self.next_player()

                if self.game_phase == config.PHASE_INITIAL_SETTLEMENT:
                    self.log = "Player " + str(self.player_turn + 1) + ": place settlement"

        elif self.game_phase == config.PHASE_WAIT:
            if road_released in self.valid_roads() and self.players[self.player_turn].available_resources('road'):
                self.players[self.player_turn].roads.append(road_released)
                self.players[self.player_turn].remove_resources_by_improvement('road')
                self.calculate_longest_road(self.player_turn)

        elif self.game_phase == config.PHASE_ROAD_BUILDING:
            if road_released in self.valid_roads():
                self.players[self.player_turn].roads.append(road_released)
                self.calculate_longest_road(self.player_turn)
                self.roads_in_road_building -= 1
                if self.roads_in_road_building == 0:
                    self.players[self.player_turn].use_special_card(config.ROAD_BUILDING)
                    self.special_card_played_in_turn = 1
                    self.game_phase = config.PHASE_WAIT
                    self.log = "Choose action"

        self.current_action = -1

    def handle_discard(self, card):
        player_discarding_id = self.players_to_discard[0][0]

        if self.players[player_discarding_id].cards[card] > 0:
            self.players[player_discarding_id].cards[card] -= 1

            if self.players_to_discard[0][1] <= 1:
                self.players_to_discard.pop(0)
            else:
                self.players_to_discard[0] = (player_discarding_id, self.players_to_discard[0][1] - 1)

        if len(self.players_to_discard) > 0:
            self.log = "Player " + str(self.players_to_discard[0][0] + 1) + ": discard " + str(self.players_to_discard[0][1]) + " cards"
        else:
            self.game_phase = config.PHASE_MOVE_ROBBER
            self.log = "Player " + str(self.player_turn + 1) + ": move robber"

    def compute_houses_to_steal_from(self, tile):
        all_settlements = []
        for player_x in self.players:
            if player_x.player_id != self.player_turn:
                for settlement in player_x.settlements + player_x.cities:
                    all_settlements.append((settlement, player_x.player_id))

        self.houses_to_steal_from = []

        for settlement in all_settlements:
            if settlement[0] in config.tiles_vertex[tile]:
                self.houses_to_steal_from.append(settlement)

    def port_belongs_to_player(self, port_id):
        for vertex in config.ports_vertex[port_id]['vert']:
            if vertex in self.players[self.player_turn].settlements + self.players[self.player_turn].cities:
                return True
        return False

    def start_4_1_trade(self):
        self.players[self.player_turn].current_trade['type'] = config.PORT_4_1
        self.log = "Pick resource to offer"

    def start_port_trade(self, port_id):
        if self.port_belongs_to_player(port_id):
            self.players[self.player_turn].current_trade['type'] = self.ports[port_id]

            if self.ports[port_id] == config.GENERIC:
                self.log = "Pick resource to offer"
            else:
                if self.players[self.player_turn].available_cards({self.ports[port_id]: 2}):
                    self.players[self.player_turn].current_trade['resource_offered'] = {self.ports[port_id]: 2}
                    self.log = "Pick resource to receive"
                else:
                    self.game_phase = config.PHASE_WAIT
                    self.log = "Choose action, no resources available"

        else:
            self.game_phase = config.PHASE_WAIT
            self.log = "Choose action"

    def check_end_game(self):
        max_points = []
        for player_x in self.players:
            pl_points = player_x.points(hidden=0)
            if len(max_points) == 0 or max_points[0][1] < pl_points:
                max_points = [(player_x.player_id, pl_points)]
            elif max_points[0][1] == pl_points:
                max_points.append((player_x.player_id, pl_points))

        # Is game finished?
        if max_points[0][1] >= 10:
            if len(max_points) == 1:
                self.winner = max_points[0][0]
            else:
                tied_players = [player_id for player_id, points in max_points]
                if self.player_turn in tied_players:
                    self.winner = self.player_turn
                else:
                    self.winner = max_points[0][0]

            self.game_phase = config.PHASE_END_GAME
            self.log = "Player " + str(self.winner + 1) + " is the winner!"
            points = [str(player_x.points(hidden=0)) for player_x in self.players]
            return ";".join([str(self.uuid), str(self.winner), ",".join(points)])

        return None

    def handle_move_robber(self, tile):
        if tile not in config.water_tiles and tile != self.robber_tile:
            self.robber_tile = tile
            self.compute_houses_to_steal_from(tile)

            if len(self.houses_to_steal_from) > 0:
                self.game_phase = config.PHASE_STEAL_CARD
                self.log = "Player " + str(self.player_turn + 1) + ": choose house to steal from"

            else:
                self.game_phase = config.PHASE_WAIT

    def handle_steal_from(self, vertex):
        for vertex_from, player_id in self.houses_to_steal_from:
            if vertex_from == vertex:
                cards_list = self.players[player_id].cards_as_list()
                if len(cards_list) > 0:
                    card_stolen = choice(cards_list)
                    self.players[self.player_turn].add_resources({card_stolen: 1})
                    self.players[player_id].remove_resources({card_stolen: 1})

                self.game_phase = config.PHASE_WAIT
                self.log = "Choose action"
                return

    def handle_trade_x_1(self, resource_clicked, x):
        if self.players[self.player_turn].current_trade['resource_offered']:
            self.players[self.player_turn].current_trade['resource_received'] = {resource_clicked: 1}

            resources_in_play = self.total_resources_in_play()
            if resources_in_play[resource_clicked] < config.max_resources:
                self.players[self.player_turn].execute_trade()
            self.players[self.player_turn].initialize_trade()

            self.game_phase = config.PHASE_WAIT
            self.log = "Choose action"
        else:
            if self.players[self.player_turn].available_cards({resource_clicked: x}):
                self.players[self.player_turn].current_trade['resource_offered'] = {resource_clicked: x}
                self.log = "Pick resource to receive"

    def handle_trade(self, resource_clicked):
        if self.players[self.player_turn].current_trade['type'] == config.PORT_4_1:
            self.handle_trade_x_1(resource_clicked, 4)
        elif self.players[self.player_turn].current_trade['type'] == config.GENERIC:
            self.handle_trade_x_1(resource_clicked, 3)
        else:
            self.players[self.player_turn].current_trade['resource_received'] = {resource_clicked: 1}

            resources_in_play = self.total_resources_in_play()
            if resources_in_play[resource_clicked] < config.max_resources:
                self.players[self.player_turn].execute_trade()
            self.players[self.player_turn].initialize_trade()

            self.game_phase = config.PHASE_WAIT
            self.log = "Choose action"

    def handle_buy_special_card(self):
        if self.players[self.player_turn].available_resources('special_card'):
            if len(self.special_cards) > 0:
                self.players[self.player_turn].remove_resources_by_improvement('special_card')
                self.players[self.player_turn].special_cards.append(self.special_cards.pop())

    def handle_play_knight(self):
        self.players[self.player_turn].use_special_card(config.KNIGHT)
        if self.players[self.player_turn].used_knights >= 3:
            self.check_largest_army_badge()

        self.special_card_played_in_turn = 1
        self.game_phase = config.PHASE_MOVE_ROBBER
        self.log = "Player " + str(self.player_turn + 1) + ": move robber"

    def handle_play_monopoly(self, resource):
        self.players[self.player_turn].use_special_card(config.MONOPOLY)
        number = 0
        for player_x in self.players:
            number += player_x.remove_all_resources(resource)

        self.players[self.player_turn].add_resources({resource: number})
        self.special_card_played_in_turn = 1
        self.game_phase = config.PHASE_WAIT
        self.log = "Choose action"

    def handle_play_year_of_plenty(self, resource):
        resources_in_play = self.total_resources_in_play()
        if resources_in_play[resource] < config.max_resources:
            self.players[self.player_turn].add_resources({resource: 1})
            self.resources_in_year_of_plenty -= 1
            if self.resources_in_year_of_plenty == 0:
                self.players[self.player_turn].use_special_card(config.YEAR_OF_PLENTY)
                self.special_card_played_in_turn = 1
                self.game_phase = config.PHASE_WAIT
                self.log = "Choose action"

    def continue_game(self):
        self.game_phase = config.PHASE_THROW_DICE
        self.special_card_played_in_turn = 0
        self.next_player()
        return self.check_end_game()
    
    def ai_get_moves(self):
        moves = []

        if self.game_phase == config.PHASE_INITIAL_SETTLEMENT:
            for i in range(len(config.vertex_position)):
                if self.valid_settlement(i):
                    moves.append((config.BUILD_SETTLEMENT, i))
        elif self.game_phase == config.PHASE_INITIAL_ROAD:
            for r in self.roads_from_settlement(self.initial_phase_settlement):
                moves.append((config.BUILD_ROAD, r))
        elif self.game_phase == config.PHASE_THROW_DICE:
            moves.append((config.THROW_DICE,))
        elif self.game_phase == config.PHASE_WAIT:
            # Settlements
            if self.players[self.player_turn].available_resources('settlement'):
                for i in range(len(config.vertex_position)):
                    if self.valid_settlement(i):
                        moves.append((config.BUILD_SETTLEMENT, i))
            # Cities
            if self.players[self.player_turn].available_resources('city'):
                for s in self.valid_city():
                    moves.append((config.BUILD_CITY, s))
            # Roads
            if self.players[self.player_turn].available_resources('road'):
                for r in self.valid_roads():
                    moves.append((config.BUILD_ROAD, r))
            # Trade 4 - 1
            for key in config.card_types:
                if self.players[self.player_turn].available_cards({key: 4}):
                    for key2 in config.card_types:
                        if key != key2:
                            moves.append((config.TRADE_41, (key, key2)))
            # End Turn
            moves.append((config.CONTINUE_GAME,))
        elif self.game_phase == config.PHASE_MOVE_ROBBER:
            for key in config.tiles_vertex:
                moves.append((config.MOVE_ROBBER, key))
        elif self.game_phase == config.PHASE_STEAL_CARD:
            self.compute_houses_to_steal_from(self.robber_tile)
            for h in self.houses_to_steal_from:
                moves.append((config.STEAL_FROM_HOUSE, h))
        elif self.game_phase == config.PHASE_DISCARD:
            for key in config.card_types:
                if self.players[self.players_to_discard[0][0]].available_cards({key: 1}):
                    moves.append((config.DISCARD, key))

        return moves

    def ai_do_move(self, move):
        if move[0] == config.BUILD_SETTLEMENT:
            self.handle_build_settlement(move[1])
        elif move[0] == config.BUILD_ROAD:
            self.handle_build_road(move[1])
        elif move[0] == config.BUILD_CITY:
            self.handle_build_city(move[1])
        elif move[0] == config.THROW_DICE:
            if len(move) == 1:
                self.calculate_throw_dice()
        elif move[0] == config.CONTINUE_GAME:
            self.continue_game()
        elif move[0] == config.TRADE_41:
            self.start_4_1_trade()
            self.handle_trade(move[1][0])
            self.handle_trade(move[1][1])
        elif move[0] == config.MOVE_ROBBER:
            self.handle_move_robber(move[1])
        elif move[0] == config.STEAL_FROM_HOUSE:
            self.handle_steal_from(move[1][0])
        elif move[0] == config.DISCARD:
            self.handle_discard(move[1])

    def ai_get_result(self, player):
        if self.game_phase == config.PHASE_END_GAME:
            if self.winner == player:
                return 1
            else:
                return 0
        else:
            raise Exception("AI checking result when game has not finished")