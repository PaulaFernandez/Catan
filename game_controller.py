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

        # Robber initial position
        self.robber_tile = self.tiles.index(config.DESERT)

        self.players = []
        for i in range(4): # 4 players
            self.players.append(player.Player(i))

        # Starter player
        self.player_turn = choice([0, 1, 2, 3])

        # Game Phase # (0, 0): Initial placement biuild settlement, (0, 1): Build road, 1: Normal game
        self.game_phase = (0, 0)

        self.log = "Player: " + str(self.player_turn + 1) + " place settlement"

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

    def check_click(self, pos):
        if self.current_action == -1:
            for i, action in enumerate(config.screen_objects):
                if self.pos_in_rectangle(pos, config.card_positions[i][0] - config.card_size[0], config.card_positions[i][1], config.card_size[0], config.card_size[1]):
                    return action

    def handle_mouse_button_down(self, pos, button):
        self.log = "Mouse clicked in x = " + str(pos[0]) + ", y = " + str(pos[1]) + ", button: " + str(button)

        if self.game_phase == (0, 0):
            if self.check_click(pos) == ('action', config.BUILD_SETTLEMENT):
                self.current_action = config.BUILD_SETTLEMENT

        self.log = "Action: " + str(self.current_action)

        self.redraw()

    def check_release(self, pos):
        if self.current_action == 0:
            for _, vertices in config.tiles_vertex.items():
                for _, vertex in enumerate(vertices):
                    if self.pos_in_rectangle(pos, config.vertex_position[vertex][0] - config.vertex_size[0], config.vertex_position[vertex][1] - config.vertex_size[1], config.vertex_size[0], config.vertex_size[1]):
                        return vertex
            return -1

    def handle_mouse_button_up(self, pos, button):
        if self.current_action == config.BUILD_SETTLEMENT:
            vertex_released = self.check_release(pos)

            if vertex_released >= 0:
                self.players[self.player_turn].settlements.append(vertex_released)

            self.current_action = -1
            self.log = "Action: " + str(self.current_action)

        self.redraw()
        