from random import shuffle, choice
import config
import draw_screen
import player

class GameController:
    def __init__(self, screen):
        self.tiles = self.generate_tiles()
        self.numbers = self.generate_numbers()
        self.ports = self.generate_ports()
        self.current_action = -1

        self.screen = screen
        self.draw_tool = draw_screen.DrawScreen(self.tiles, self.numbers, self.ports, self.screen)

        # Initialize variables
        self.initial_phase_settlement = 0
        self.initial_phase_start_player = 0
        self.initial_phase_decrease = 0

        # Robber initial position
        self.robber_tile = self.tiles.index(config.DESERT)

        self.players = []
        for i in range(4): # 4 players
            self.players.append(player.Player(i))

        # Starter player
        self.player_turn = choice([0, 1, 2, 3])
        self.initial_phase_start_player = self.player_turn

        # Game Phase # (0, 0): Initial placement build settlement, (0, 1): Build road, 1: Normal game
        self.game_phase = (0, 0)

        self.log = "Player " + str(self.player_turn + 1) + ": place settlement"

        self.draw_tool.draw_board(self.robber_tile, self.players, self.player_turn, self.log)

    def generate_ports(self):
        ports = []

        for key, value in config.port_types.items():
            ports.extend([key] * value['number'])
        shuffle(ports)

        return ports

    def generate_numbers(self):
        numbers = config.roll_numbers
        shuffle(numbers)
        return numbers

    def generate_tiles(self):
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

    def redraw(self):
        self.screen.fill((0, 0, 0))
        self.draw_tool.draw_board(self.robber_tile, self.players, self.player_turn, self.log)

    def pos_in_rectangle(self, pos, x, y, height, width):
        return pos[0] >= x and pos[0] <= (x + width) and pos[1] >= (y) and pos[1] <= (y + height)

    def roads_from_settlement(self, sett_num):
        roads = []
        for _, vertices in config.tiles_vertex.items():
            for i, vertex in enumerate(vertices):
                if vertex == sett_num:
                    if vertex < vertices[i-1]:
                        roads.append((vertex, vertices[i-1]))
                    else:
                        roads.append((vertices[i-1], vertex))

        return frozenset(roads)

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

    def initial_settlement_resources(self, vertex):
        for tile, vertices in config.tiles_vertex.items():
            if vertex in vertices:
                if self.tiles[tile] in self.players[self.player_turn].cards:
                    self.players[self.player_turn].cards[self.tiles[tile]] += 1

    def next_player(self):
        if self.game_phase == 1:
            self.player_turn = (self.player_turn + 1) % 4
            return

        if self.initial_phase_decrease == 1:
            if self.player_turn == self.initial_phase_start_player:
                self.game_phase = 1
                return

            self.player_turn = (self.player_turn - 1) % 4

            return

        if (self.initial_phase_start_player + 3) % 4 == self.player_turn:
            self.initial_phase_decrease = 1
            return

        self.player_turn = (self.player_turn + 1) % 4

        return

    def check_click(self, pos):
        if self.current_action == -1:
            for i, action in enumerate(config.screen_objects):
                if self.pos_in_rectangle(pos, config.card_positions[i][0], config.card_positions[i][1], config.card_size[0], config.card_size[1]):
                    return action

    def handle_mouse_button_down(self, pos, button):
        self.log = "Mouse clicked in x = " + str(pos[0]) + ", y = " + str(pos[1]) + ", button: " + str(button)

        if self.game_phase == (0, 0):
            if self.check_click(pos) == ('action', config.BUILD_SETTLEMENT):
                self.current_action = config.BUILD_SETTLEMENT
        elif self.game_phase == (0, 1):
            if self.check_click(pos) == ('action', config.BUILD_ROAD):
                self.current_action = config.BUILD_ROAD

        self.log = "Action: " + str(self.current_action)

        self.redraw()

    def check_release(self, pos):
        if self.current_action == config.BUILD_SETTLEMENT:
            for _, vertices in config.tiles_vertex.items():
                for _, vertex in enumerate(vertices):
                    if self.pos_in_rectangle(pos, config.vertex_position[vertex][0], config.vertex_position[vertex][1], config.vertex_size[0], config.vertex_size[1]):
                        return vertex
            return -1

        elif self.current_action == config.BUILD_ROAD:
            for _, vertices in config.tiles_vertex.items():
                for i, vertex in enumerate(vertices):
                    # Road vertex
                    x = (config.vertex_position[vertex][0] + config.vertex_position[vertices[i-1]][0]) / 2
                    y = (config.vertex_position[vertex][1] + config.vertex_position[vertices[i-1]][1]) / 2
                    if self.pos_in_rectangle(pos, x, y, config.vertex_size[0], config.vertex_size[1]):
                        if vertex < vertices[i-1]:
                            return (vertex, vertices[i-1])
                        else:
                            return (vertices[i-1], vertex)

            return -1

    def handle_mouse_button_up(self, pos, button):
        if self.current_action == config.BUILD_SETTLEMENT:
            vertex_released = self.check_release(pos)

            if self.valid_settlement(vertex_released):
                self.players[self.player_turn].settlements.append(vertex_released)

                if self.game_phase == (0, 0):
                    self.game_phase = (0, 1)
                    self.initial_phase_settlement = vertex_released
                    self.initial_settlement_resources(vertex_released)
                    self.log = "Player " + str(self.player_turn + 1) + ": place road"

            self.current_action = -1

        elif self.current_action == config.BUILD_ROAD:
            road_released = self.check_release(pos)

            if self.game_phase == (0, 1):
                if road_released in self.roads_from_settlement(self.initial_phase_settlement):
                    self.players[self.player_turn].roads.append(road_released)
                    self.game_phase = (0, 0)
                    self.next_player()

                    self.log = "Player " + str(self.player_turn + 1) + ": place settlement"


            self.current_action = -1

        self.redraw()
        