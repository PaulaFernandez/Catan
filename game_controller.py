import pickle
import config
from draw_screen import DrawScreen
from game_state import GameState
from model import Residual_CNN

class GameController:
    def __init__(self):
        self.controller_state = 0
        self.config_game = {'MCTS_EXPLORATION': config.MCTS_EXPLORATION}

        self.draw_tool = DrawScreen()
        self.redraw()

    def start_game(self):
        agents = config.CURRENT_AGENT
        agents_obj = []

        for a in agents:
            net = Residual_CNN(config.REG_CONST, config.LEARNING_RATE, config.INPUT_DIM, config.OUTPUT_DIM, config.HIDDEN_CNN_LAYERS)
            net.read(a)
            agents_obj.append((str(a), net))

        self.game = GameState(agents_obj = agents_obj, game_config = self.config_game)
        self.redraw()
        self.controller_state = 1

    @staticmethod
    def pos_in_rectangle(pos, x, y, width, height):
        return pos[0] >= x and pos[0] <= (x + width) and pos[1] >= (y) and pos[1] <= (y + height)

    def redraw(self):
        if self.controller_state == 1:
            self.draw_tool.draw_board(self.game.tiles,
                                    self.game.numbers,
                                    self.game.ports,
                                    self.game.robber_tile,
                                    self.game.players,
                                    self.game.player_turn,
                                    self.game.log,
                                    self.game.dices,
                                    self.game.get_player_moving(),
                                    self.game.game_phase)
        elif self.controller_state == 0:
            self.draw_tool.draw_start()
        elif self.controller_state == 2:
            self.draw_tool.draw_options(self.config_game)

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

            for j, special_card_type in enumerate(self.game.players[self.game.player_turn].special_cards):
                if self.pos_in_rectangle(pos, config.card_positions[j + len(config.screen_objects)][0], config.card_positions[j + len(config.screen_objects)][1], config.card_size[0], config.card_size[1]):
                    if self.game.special_card_played_in_turn == 0:
                        return ('special_card', special_card_type)

            for p in range(4):
                if self.pos_in_rectangle(pos, 
                                         config.player_stats_x + config.start_trade_x_offset, 
                                         config.player_stats_y + p * (config.player_stats_y + config.player_stats_height) + config.start_trade_y_offset, 
                                         config.start_trade_size[0], 
                                         config.start_trade_size[1]):
                    return ('action', config.TRADE_OFFER, p)

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

            if self.pos_in_rectangle(pos, config.buy_special_card_position[0], config.buy_special_card_position[1], config.buy_special_card_size[0], config.buy_special_card_size[1]):
                return ('action', config.BUY_SPECIAL_CARD)

            if self.pos_in_rectangle(pos, config.accept_trade_position[0], config.accept_trade_position[1], config.accept_trade_size[0], config.accept_trade_size[1]):
                return ('action', config.ACCEPT_TRADE)

            if self.pos_in_rectangle(pos, config.reject_trade_position[0], config.reject_trade_position[1], config.reject_trade_size[0], config.reject_trade_size[1]):
                return ('action', config.REJECT_TRADE)

            for i, tile_pos in enumerate(config.tile_position):
                if self.pos_in_rectangle(pos, tile_pos[0] + config.number_x_offset, tile_pos[1] + config.number_y_offset, config.numbers_size[0], config.numbers_size[1]):
                    return ('tile', i)

        return ('', -1)

    def check_click_menu(self, pos):
        if self.pos_in_rectangle(pos, config.menu_x_offset, config.menu_y_offset, config.menu_image_size[0], config.menu_image_size[1]):
            return 'start_game'
        elif self.pos_in_rectangle(pos, config.menu_x_offset, config.menu_y_offset + config.menu_y_step, config.menu_image_size[0], config.menu_image_size[1]):
            return 'load_game'
        elif self.pos_in_rectangle(pos, config.menu_x_offset, config.menu_y_offset + 2 * config.menu_y_step, config.menu_image_size[0], config.menu_image_size[1]):
            return 'options'

    def check_click_options(self, pos):
        if self.pos_in_rectangle(pos, config.menu_x_offset + config.menu_image_size[0] + 200, config.menu_y_offset, config.circle_image_size[0], config.circle_image_size[1]):
            return 'increase_mcts'
        if self.pos_in_rectangle(pos, config.menu_x_offset + config.menu_image_size[0] + 20, config.menu_y_offset, config.circle_image_size[0], config.circle_image_size[1]):
            return 'decrease_mcts'
        if self.pos_in_rectangle(pos, config.menu_x_offset, config.menu_y_offset + 500, config.menu_image_size[0], config.menu_image_size[1]):
            return 'back'

    def handle_mouse_button_down(self, pos, button):
        if self.controller_state == 0:
            if self.check_click_menu(pos) == 'start_game':
                self.start_game()
            elif self.check_click_menu(pos) == 'options':
                self.controller_state = 2
        if self.controller_state == 2:
            if self.check_click_options(pos) == 'increase_mcts':
                self.config_game['MCTS_EXPLORATION'] += 50
            elif self.check_click_options(pos) == 'decrease_mcts':
                self.config_game['MCTS_EXPLORATION'] -= 50
            elif self.check_click_options(pos) == 'back':
                self.controller_state = 0
        if self.controller_state == 1:
            if self.game.current_action == config.THROW_DICE:
                self.game.current_action = -1
                self.game.dices = (0, 0)
                self.redraw()
                return

            if self.game.players[self.game.get_player_moving()].is_human == 0:
                if self.check_click(pos) == ('action', config.CONTINUE_GAME):
                    self.game.dices = (0, 0)
                    move, _, _, _ = self.game.players[self.game.get_player_moving()].ai.move(self.game)
                    self.game.ai_do_move(move)
                    self.redraw()
                return

            if self.game.game_phase == config.PHASE_INITIAL_SETTLEMENT:
                if self.check_click(pos) == ('action', config.BUILD_SETTLEMENT):
                    self.game.current_action = config.BUILD_SETTLEMENT
            elif self.game.game_phase == config.PHASE_INITIAL_ROAD:
                if self.check_click(pos) == ('action', config.BUILD_ROAD):
                    self.game.current_action = config.BUILD_ROAD
            elif self.game.game_phase == config.PHASE_THROW_DICE:
                if self.check_click(pos) == ('action', config.THROW_DICE):
                    self.game.current_action = config.THROW_DICE
                    self.game.calculate_throw_dice()
                elif self.check_click(pos) == ('special_card', config.KNIGHT):
                    self.game.handle_play_knight()
            elif self.game.game_phase == config.PHASE_WAIT:
                click_port = self.click_in_port(pos)
                if self.check_click(pos) == ('action', config.CONTINUE_GAME):
                    #with open('train_set\\' + str(self.game.uuid) + '_' + str(self.game.counter), 'wb') as #output:
                    #    self.game.counter += 1
                    #    pickle.dump(self.game, output, -1)
                    result = self.game.continue_game()
                    #if result:
                    #    with open("train_set/winners.txt", "a") as results:
                    #        print(result, file=results)
                elif self.check_click(pos) == ('action', config.BUILD_ROAD):
                    self.game.current_action = config.BUILD_ROAD
                elif self.check_click(pos) == ('action', config.BUILD_CITY):
                    self.game.current_action = config.BUILD_CITY
                elif self.check_click(pos) == ('action', config.BUILD_SETTLEMENT):
                    self.game.current_action = config.BUILD_SETTLEMENT
                elif self.check_click(pos) == ('action', config.BUY_SPECIAL_CARD):
                    self.game.handle_buy_special_card()
                elif self.check_click(pos) == ('action', config.TRADE_41):
                    self.game.game_phase = config.PHASE_PORTS_TRADE
                    self.game.start_4_1_trade()
                elif self.check_click(pos) == ('special_card', config.KNIGHT):
                    self.game.handle_play_knight()
                elif self.check_click(pos) == ('special_card', config.MONOPOLY):
                    self.game.game_phase = config.PHASE_MONOPOLY
                    self.game.log = "Choose resource"
                elif self.check_click(pos) == ('special_card', config.ROAD_BUILDING):
                    self.game.game_phase = config.PHASE_ROAD_BUILDING
                    self.game.log = "Build roads"
                    self.game.roads_in_road_building = 2
                elif self.check_click(pos) == ('special_card', config.YEAR_OF_PLENTY):
                    self.game.game_phase = config.PHASE_YEAR_OF_PLENTY
                    self.game.log = "Choose resources"
                    self.game.resources_in_year_of_plenty = 2
                elif self.check_click(pos)[1] == config.TRADE_OFFER:
                    self.game.start_players_trade(self.check_click(pos)[2])
                elif click_port[0] == 'port':
                    self.game.game_phase = config.PHASE_PORTS_TRADE
                    self.game.start_port_trade(click_port[1])
            elif self.game.game_phase == config.PHASE_DISCARD:
                click = self.check_click(pos)
                if click[0] == 'card':
                    self.game.handle_discard(click[1])
            elif self.game.game_phase == config.PHASE_MOVE_ROBBER:
                click = self.check_click(pos)
                if click[0] == 'tile':
                    self.game.handle_move_robber(click[1])
            elif self.game.game_phase == config.PHASE_STEAL_CARD:
                click = self.click_in_vertex(pos)
                if click[0] == 'vertex':
                    self.game.handle_steal_from(click[1])
            elif self.game.game_phase == config.PHASE_PORTS_TRADE:
                click = self.check_click(pos)
                if click == ('action', config.TRADE_41):
                    self.game.game_phase = config.PHASE_WAIT
                    self.game.players[self.game.player_turn].initialize_trade()
                    self.game.log = "Choose your action"
                elif click[0] == 'card':
                    self.game.handle_trade(click[1])
            elif self.game.game_phase == config.PHASE_MONOPOLY:
                click = self.check_click(pos)
                if click[0] == 'card':
                    self.game.handle_play_monopoly(click[1])
            elif self.game.game_phase == config.PHASE_ROAD_BUILDING:
                if self.check_click(pos) == ('action', config.BUILD_ROAD):
                    self.game.current_action = config.BUILD_ROAD
            elif self.game.game_phase == config.PHASE_YEAR_OF_PLENTY:
                click = self.check_click(pos)
                if click[0] == 'card':
                    self.game.handle_play_year_of_plenty(click[1])
            elif self.game.game_phase == config.PHASE_TRADE_OFFER:
                click = self.check_click(pos)
                if click[0] == 'card':
                    self.game.handle_resource_added_trade(click[1])
                elif click == ('action', config.ACCEPT_TRADE):
                    self.game.handle_move_trade_forward()
                elif click == ('action', config.REJECT_TRADE):
                    self.game.handle_cancel_trade()
            elif self.game.game_phase == config.PHASE_TRADE_RECEIVE:
                click = self.check_click(pos)
                if click[0] == 'card':
                    self.game.handle_resource_added_trade(click[1])
                elif click == ('action', config.ACCEPT_TRADE):
                    self.game.handle_move_trade_forward()
                elif click == ('action', config.REJECT_TRADE):
                    self.game.handle_cancel_trade()
            elif self.game.game_phase == config.PHASE_TRADE_RESPOND:
                click = self.check_click(pos)
                if click == ('action', config.ACCEPT_TRADE):
                    self.game.execute_players_trade()
                elif click == ('action', config.REJECT_TRADE):
                    self.game.handle_cancel_trade()

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
        if self.controller_state == 1:
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
        