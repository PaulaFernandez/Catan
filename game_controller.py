import pickle
import config
import draw_screen
from game_state import GameState

class GameController:
    def __init__(self, screen):
        self.game = GameState()

        self.screen = screen
        self.draw_tool = draw_screen.DrawScreen(self.screen)
        self.redraw()

    @staticmethod
    def pos_in_rectangle(pos, x, y, width, height):
        return pos[0] >= x and pos[0] <= (x + width) and pos[1] >= (y) and pos[1] <= (y + height)

    def redraw(self):
        self.screen.fill((0, 0, 0))

        if len(self.game.players_to_discard) > 0:
            player_to_discard = self.game.players_to_discard[0][0]
        else:
            player_to_discard = None

        self.draw_tool.draw_board(self.game.tiles,
                                  self.game.numbers,
                                  self.game.ports,
                                  self.game.robber_tile,
                                  self.game.players,
                                  self.game.player_turn,
                                  self.game.log,
                                  self.game.dices,
                                  player_to_discard)

    def click_in_vertex(self, pos):
        for _, vertices in config.tiles_vertex.items():
            for _, vertex in enumerate(vertices):
                if self.pos_in_rectangle(pos, config.vertex_position[vertex][0], config.vertex_position[vertex][1], config.vertex_size[0], config.vertex_size[1]):
                    return ('vertex', vertex)
        return ('', -1)

    def click_in_port(self, pos):
        for port_id, ports in config.ports_vertex.items():
            x = config.tile_position[ports['tile']][0] + ports['offset'][0]
            y = config.tile_position[ports['tile']][1] + ports['offset'][1]
            if self.pos_in_rectangle(pos, x, y, config.ports_size[0], config.ports_size[1]):
                return ('port', port_id)
        return ('', -1)

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

            if self.pos_in_rectangle(pos, config.continue_game_position[0], config.continue_game_position[1], config.continue_game_size[0], config.continue_game_size[1]):
                return ('action', config.CONTINUE_GAME)

            if self.pos_in_rectangle(pos, config.trade41_position[0], config.trade41_position[1], config.trade41_size[0], config.trade41_size[1]):
                return ('action', config.TRADE_41)

            for i, tile_pos in enumerate(config.tile_position):
                if self.pos_in_rectangle(pos, tile_pos[0], tile_pos[1], config.numbers_size[0], config.numbers_size[1]):
                    return ('tile', i)

        return ('', -1)

    def handle_mouse_button_down(self, pos, button):
        if self.game.current_action == config.THROW_DICE:
            self.game.current_action = -1
            self.game.dices = (0, 0)
            self.redraw()
            return

        if self.game.game_phase == (0, 0):
            if self.check_click(pos) == ('action', config.BUILD_SETTLEMENT):
                self.game.current_action = config.BUILD_SETTLEMENT
        elif self.game.game_phase == (0, 1):
            if self.check_click(pos) == ('action', config.BUILD_ROAD):
                self.game.current_action = config.BUILD_ROAD
        elif self.game.game_phase == (1, 0):
            if self.check_click(pos) == ('action', config.THROW_DICE):
                self.game.current_action = config.THROW_DICE
                self.game.calculate_throw_dice()
        elif self.game.game_phase == (1, 1):
            click_port = self.click_in_port(pos)
            if self.check_click(pos) == ('action', config.CONTINUE_GAME):
                self.game.game_phase = (1, 0)
                self.game.next_player()
            elif self.check_click(pos) == ('action', config.BUILD_ROAD):
                self.game.current_action = config.BUILD_ROAD
            elif self.check_click(pos) == ('action', config.BUILD_CITY):
                self.game.current_action = config.BUILD_CITY
            elif self.check_click(pos) == ('action', config.BUILD_SETTLEMENT):
                self.game.current_action = config.BUILD_SETTLEMENT
            elif self.check_click(pos) == ('action', config.TRADE_41):
                self.game.game_phase = (1, 5)
                self.game.start_4_1_trade()
            elif click_port[0] == 'port':
                self.game.game_phase = (1, 5)
                self.game.start_port_trade(click_port[1])
        elif self.game.game_phase == (1, 2):
            click = self.check_click(pos)
            if click[0] == 'card':
                self.game.handle_discard(click[1])
        elif self.game.game_phase == (1, 3):
            click = self.check_click(pos)
            if click[0] == 'tile':
                self.game.handle_move_robber(click[1])
        elif self.game.game_phase == (1, 4):
            click = self.click_in_vertex(pos)
            if click[0] == 'vertex':
                self.game.handle_steal_from(click[1])
        elif self.game.game_phase == (1, 5):
            click = self.check_click(pos)
            if click == ('action', config.TRADE_41):
                self.game.game_phase = (1, 1)
                self.game.players[self.game.player_turn].initialize_trade()
                self.game.log = "Choose your action"
            elif click[0] == 'card':
                self.game.handle_trade(click[1])

        if self.check_click(pos) == ('action', config.SAVE_GAME):
            with open('game.pkl', 'wb') as output:
                pickle.dump(self.game, output, -1)
                self.game.log = "Game saved"

        if self.check_click(pos) == ('action', config.LOAD_GAME):
            with open('game.pkl', 'rb') as input_file:
                self.game = pickle.load(input_file)
                self.game.log = "Game loaded"

        self.redraw()

    def check_release(self, pos):
        if self.game.current_action == config.BUILD_SETTLEMENT or self.game.current_action == config.BUILD_CITY:
            return self.click_in_vertex(pos)

        elif self.game.current_action == config.BUILD_ROAD:
            for _, vertices in config.tiles_vertex.items():
                for i, vertex in enumerate(vertices):
                    # Road vertex
                    x = (config.vertex_position[vertex][0] + config.vertex_position[vertices[i-1]][0]) / 2
                    y = (config.vertex_position[vertex][1] + config.vertex_position[vertices[i-1]][1]) / 2
                    if self.pos_in_rectangle(pos, x, y, config.vertex_size[0], config.vertex_size[1]):
                        if vertex < vertices[i-1]:
                            return ('road', (vertex, vertices[i-1]))
                        else:
                            return ('road', (vertices[i-1], vertex))

            return ('', -1)

    def handle_mouse_button_up(self, pos, button):
        if self.game.current_action == config.BUILD_SETTLEMENT:
            _, vertex_released = self.check_release(pos)
            self.game.handle_build_settlement(vertex_released)

        elif self.game.current_action == config.BUILD_ROAD:
            _, road_released = self.check_release(pos)
            self.game.handle_build_road(road_released)

        elif self.game.current_action == config.BUILD_CITY:
            _, vertex_released = self.check_release(pos)
            self.game.handle_build_city(vertex_released)

        self.redraw()
        