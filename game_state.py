from random import shuffle, choice
import player
import config

class GameState:
    def __init__(self):
        self.tiles = self.generate_tiles()
        self.numbers = self.generate_numbers()
        self.ports = self.generate_ports()
        self.current_action = -1
        self.initial_phase_settlement = 0
        self.initial_phase_decrease = 0
        self.dices = (0, 0)
        self.players_to_discard = []

        # Robber initial position
        self.robber_tile = self.tiles.index(config.DESERT)

        self.players = []
        for i in range(4): # 4 players
            self.players.append(player.Player(i))

        # Starting player
        self.player_turn = choice([0, 1, 2, 3])
        self.initial_phase_start_player = self.player_turn

        # Log
        self.log = "Player " + str(self.player_turn + 1) + ": place settlement"

        # Game Phase
        # (0, 0): Initial placement build settlement, (0, 1): Build road
        # (1, 0): Throw dice, (1, 1): Wait for end of turn, (1, 2): Discard, (1, 3): Move robber
        self.game_phase = (0, 0)

    @staticmethod
    def generate_ports():
        ports = []

        for key, value in config.port_types.items():
            ports.extend([key] * value['number'])
        shuffle(ports)

        return ports

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
        roads = []
        for _, vertices in config.tiles_vertex.items():
            for i, vertex in enumerate(vertices):
                if vertex == sett_num:
                    if vertex < vertices[i-1]:
                        roads.append((vertex, vertices[i-1]))
                    else:
                        roads.append((vertices[i-1], vertex))
                    if vertex < vertices[i-5 % 6]:
                        roads.append((vertex, vertices[i-5 % 6]))
                    else:
                        roads.append((vertices[i-5 % 6], vertex))

        return set(roads)

    def next_player(self):
        if self.game_phase[0] == 1:
            self.player_turn = (self.player_turn + 1) % 4
            self.log = "Player " + str(self.player_turn + 1) + ": throw dice"
            return

        if self.initial_phase_decrease == 1:
            if self.player_turn == self.initial_phase_start_player:
                self.game_phase = (1, 0)
                self.log = "Player " + str(self.player_turn + 1) + ": throw dice"
                return

            self.player_turn = (self.player_turn - 1) % 4

            return

        if (self.initial_phase_start_player + 3) % 4 == self.player_turn:
            self.initial_phase_decrease = 1
            return

        self.player_turn = (self.player_turn + 1) % 4

        return

    def dice_resources(self, result):
        for number, tile in self.numbers:
            if number == result:
                resource = self.tiles[tile]

                for player_x in self.players:
                    for settlement in player_x.settlements:
                        if settlement in config.tiles_vertex[tile]:
                            player_x.cards[resource] += 1

                    for city in player_x.cities:
                        if city in config.tiles_vertex[tile]:
                            player_x.cards[resource] += 2

    def calculate_throw_dice(self):
        dice_1 = choice([1, 2, 3, 4, 5, 6])
        dice_2 = choice([1, 2, 3, 4, 5, 6])
        self.dices = (dice_1, dice_2)

        result = dice_1 + dice_2
        self.log = "Dice result = " + str(result)
        self.dice_resources(result)

        if result == 7:
            '''self.game_phase = (1, 2)
            self.log = "Discard"

            for player_x in self.players:
                if len(player_x.cards) > 7:
                    self.players_to_discard.append((player_x.player_id, int(len(player_x.cards) / 2)))

            if len(self.players_to_discard) == 0:
                self.game_phase = (1, 3)
                self.log = "Move the robber"'''

            self.game_phase = (1, 1)
        else:
            self.game_phase = (1, 1)
            self.log = "Choose your action"

    def initial_settlement_resources(self, vertex):
        for tile, vertices in config.tiles_vertex.items():
            if vertex in vertices:
                if self.tiles[tile] in self.players[self.player_turn].cards:
                    self.players[self.player_turn].cards[self.tiles[tile]] += 1

    def valid_settlement(self, vertex):
        def settlement_clash(vertex_1, vertex_2):
            if vertex_1 == vertex_2:
                return True

            for _, vertices in config.tiles_vertex.items():
                if vertex_1 in vertices and vertex_2 in vertices:
                    distance = abs(vertices.index(vertex_1) - vertices.index(vertex_2))
                    if distance == 1 or distance == 5:
                        return True

            return False

        if vertex < 0:
            return False

        for player_x in self.players:
            for settlement in player_x.settlements + player_x.cities:
                if settlement_clash(vertex, settlement):
                    return False

        return True

    def valid_roads(self):
        potential_roads = set()
        for road in self.players[self.player_turn].roads:
            for out_roads in map(self.roads_from_settlement, list(road)):
                potential_roads = potential_roads | out_roads

        for player_x in self.players:
            for road in player_x.roads:
                if road in potential_roads:
                    potential_roads.remove(road)

        return potential_roads

    def valid_city(self):
        return self.players[self.player_turn].settlements

    def handle_build_settlement(self, vertex_released):
        if self.valid_settlement(vertex_released):
            self.players[self.player_turn].settlements.append(vertex_released)

            if self.game_phase == (0, 0):
                self.game_phase = (0, 1)
                self.initial_phase_settlement = vertex_released
                self.initial_settlement_resources(vertex_released)
                self.log = "Player " + str(self.player_turn + 1) + ": place road"

        self.current_action = -1

    def handle_build_city(self, vertex_released):
        if vertex_released in self.valid_city() and self.players[self.player_turn].available_resources('city'):
            self.players[self.player_turn].settlements.remove(vertex_released)
            self.players[self.player_turn].cities.append(vertex_released)
            self.players[self.player_turn].remove_resources('city')

        self.current_action = -1

    def handle_build_road(self, road_released):
        if self.game_phase == (0, 1):
            if road_released in self.roads_from_settlement(self.initial_phase_settlement):
                self.players[self.player_turn].roads.append(road_released)
                self.game_phase = (0, 0)
                self.next_player()

                if self.game_phase == (0, 0):
                    self.log = "Player " + str(self.player_turn + 1) + ": place settlement"

        elif self.game_phase == (1, 1):
            if road_released in self.valid_roads() and self.players[self.player_turn].available_resources('road'):
                self.players[self.player_turn].roads.append(road_released)
                self.players[self.player_turn].remove_resources('road')

        self.current_action = -1