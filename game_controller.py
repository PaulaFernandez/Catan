from random import choice
import pickle
import config
import draw_screen
from game_state import GameState

class GameController:
    def __init__(self, screen):
        self.game = GameState()

        self.screen = screen
        self.draw_tool = draw_screen.DrawScreen(self.screen)
        self.log = "Player " + str(self.game.player_turn + 1) + ": place settlement"
        self.redraw()

    def redraw(self):
        self.screen.fill((0, 0, 0))
        self.draw_tool.draw_board(self.game.tiles, self.game.numbers, self.game.ports, self.game.robber_tile, self.game.players, self.game.player_turn, self.log, self.game.dices)

    @staticmethod
    def pos_in_rectangle(pos, x, y, width, height):
        return pos[0] >= x and pos[0] <= (x + width) and pos[1] >= (y) and pos[1] <= (y + height)

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

        for player_x in self.game.players:
            for settlement in player_x.settlements + player_x.cities:
                if settlement_clash(vertex, settlement):
                    return False

        return True

    def initial_settlement_resources(self, vertex):
        for tile, vertices in config.tiles_vertex.items():
            if vertex in vertices:
                if self.game.tiles[tile] in self.game.players[self.game.player_turn].cards:
                    self.game.players[self.game.player_turn].cards[self.game.tiles[tile]] += 1

    def dice_resources(self, result):
        for number, tile in self.game.numbers:
            if number == result:
                resource = self.game.tiles[tile]

                for player_x in self.game.players:
                    for settlement in player_x.settlements:
                        if settlement in config.tiles_vertex[tile]:
                            player_x.cards[resource] += 1

                    for city in player_x.cities:
                        if city in config.tiles_vertex[tile]:
                            player_x.cards[resource] += 2

    def next_player(self):
        if self.game.game_phase[0] == 1:
            self.game.player_turn = (self.game.player_turn + 1) % 4
            return

        if self.game.initial_phase_decrease == 1:
            if self.game.player_turn == self.game.initial_phase_start_player:
                self.game.game_phase = (1, 0)
                return

            self.game.player_turn = (self.game.player_turn - 1) % 4

            return

        if (self.game.initial_phase_start_player + 3) % 4 == self.game.player_turn:
            self.game.initial_phase_decrease = 1
            return

        self.game.player_turn = (self.game.player_turn + 1) % 4

        return

    def calculate_throw_dice(self):
        dice_1 = choice([1, 2, 3, 4, 5, 6])
        dice_2 = choice([1, 2, 3, 4, 5, 6])
        self.game.dices = (dice_1, dice_2)

        result = dice_1 + dice_2
        self.log = "Dice result = " + str(result)
        self.dice_resources(result)

        # Paint, discard, move robber, next action

    def check_click(self, pos):
        if self.game.current_action == -1:
            for i, action in enumerate(config.screen_objects):
                if self.pos_in_rectangle(pos, config.card_positions[i][0], config.card_positions[i][1], config.card_size[0], config.card_size[1]):
                    return action

            if self.pos_in_rectangle(pos, config.throw_dice_position[0], config.throw_dice_position[1], config.throw_dice_size[0], config.throw_dice_size[1]):
                return ('action', config.THROW_DICE)

            if self.pos_in_rectangle(pos, config.save_game_position[0], config.save_game_position[1], config.save_game_size[0], config.save_game_size[1]):
                return ('action', config.SAVE_GAME)

            if self.pos_in_rectangle(pos, config.load_game_position[0], config.load_game_position[1], config.load_game_size[0], config.load_game_size[1]):
                return ('action', config.LOAD_GAME)

    def handle_mouse_button_down(self, pos, button):
        self.log = "Mouse clicked in x = " + str(pos[0]) + ", y = " + str(pos[1]) + ", button: " + str(button)

        if self.game.game_phase == (0, 0):
            if self.check_click(pos) == ('action', config.BUILD_SETTLEMENT):
                self.game.current_action = config.BUILD_SETTLEMENT
        elif self.game.game_phase == (0, 1):
            if self.check_click(pos) == ('action', config.BUILD_ROAD):
                self.game.current_action = config.BUILD_ROAD
        elif self.game.game_phase == (1, 0):
            if self.check_click(pos) == ('action', config.THROW_DICE):
                self.game.current_action = config.THROW_DICE
                self.calculate_throw_dice()

        if self.check_click(pos) == ('action', config.SAVE_GAME):
            with open('game.pkl', 'wb') as output:
                pickle.dump(self.game, output, -1)

        if self.check_click(pos) == ('action', config.LOAD_GAME):
            with open('game.pkl', 'rb') as input_file:
                self.game = pickle.load(input_file)

        self.log = "Action: " + str(self.game.current_action)

        self.redraw()

    def check_release(self, pos):
        if self.game.current_action == config.BUILD_SETTLEMENT:
            for _, vertices in config.tiles_vertex.items():
                for _, vertex in enumerate(vertices):
                    if self.pos_in_rectangle(pos, config.vertex_position[vertex][0], config.vertex_position[vertex][1], config.vertex_size[0], config.vertex_size[1]):
                        return vertex
            return -1

        elif self.game.current_action == config.BUILD_ROAD:
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
        if self.game.current_action == config.BUILD_SETTLEMENT:
            vertex_released = self.check_release(pos)

            if self.valid_settlement(vertex_released):
                self.game.players[self.game.player_turn].settlements.append(vertex_released)

                if self.game.game_phase == (0, 0):
                    self.game.game_phase = (0, 1)
                    self.game.initial_phase_settlement = vertex_released
                    self.initial_settlement_resources(vertex_released)
                    self.log = "Player " + str(self.game.player_turn + 1) + ": place road"

            self.game.current_action = -1

        elif self.game.current_action == config.BUILD_ROAD:
            road_released = self.check_release(pos)

            if self.game.game_phase == (0, 1):
                if road_released in self.roads_from_settlement(self.game.initial_phase_settlement):
                    self.game.players[self.game.player_turn].roads.append(road_released)
                    self.game.game_phase = (0, 0)
                    self.next_player()

                    self.log = "Player " + str(self.game.player_turn + 1) + ": place settlement"


            self.game.current_action = -1

        self.redraw()
        