import pickle
import config
from draw_screen import DrawScreen
from game_state import GameState

from agent_nn import Agent_NN
from agent_heuristic import Agent_Heuristic

class GameController:
    def __init__(self):
        self.controller_state = 0
        self.config_game = {'MCTS_EXPLORATION': config.MCTS_EXPLORATION,
                            'TYPE_OF_GAME': config.TYPE_OF_GAME,
                            'PLAYER_IS_HUMAN': config.player_is_human}

        self.draw_tool = DrawScreen()
        self.redraw()

    def start_game(self):
        agents = config.CURRENT_AGENT
        agents_obj = []

        for a in agents:
            print ("Loading Agent: " + str(a))
            if a == "h":
                net = Agent_Heuristic()
            else:
                net = Agent_NN()
                net.nn_read(a)
            
            agents_obj.append((str(a), net))

        self.game = GameState(agents_obj = agents_obj, game_config = self.config_game)
        self.redraw()
        self.controller_state = 1

    def check_state(self):
        try:
            if self.game.boardgame_state == 0:
                if self.game.players[self.game.get_player_moving()].is_human == 0:
                    self.game.dices = (0, 0)
                    move, _, _ = self.game.players[self.game.get_player_moving()].ai.move(self.game)
                    self.game.ai_do_move(move)
                    self.redraw()
                    return

            if self.game.boardgame_state == 1:
                if self.game.game_phase == config.PHASE_THROW_DICE:
                    self.controller_state = 10
                    self.game.boardgame_state = 0
            elif self.game.boardgame_state == 2:
                self.controller_state = 11
                self.game.boardgame_state = 0
            elif self.game.boardgame_state == 3:
                self.controller_state = 12
                self.game.boardgame_state = 0
        except:
            pass

    def configure_game(self):
        self.controller_state = 3
        self.av_tile_selected = None
        self.av_num_selected = None
        self.av_port_selected = None

        self.config_game['tiles'] = []
        self.config_game['numbers'] = []
        self.config_game['ports'] = [config.GENERIC for i in config.ports_vertex.keys()]
        
        for i in range(37):
            if i in config.water_tiles:
                self.config_game['tiles'].append(config.WATER)
                continue
            self.config_game['tiles'].append(config.DESERT)

        self.config_game['available_tiles'] = []
        for key, value in config.tile_types.items():
            if key != config.WATER:
                self.config_game['available_tiles'].extend([key] * value['number'])

        self.config_game['available_numbers'] = config.roll_numbers
        self.config_game['available_ports'] = [*config.card_types]

    @staticmethod
    def pos_in_rectangle(pos, x, y, width, height):
        return pos[0] >= x and pos[0] <= (x + width) and pos[1] >= (y) and pos[1] <= (y + height)

    def redraw(self):
        if self.controller_state == 1:
            draw_player_info = False
            if self.game.players[self.game.get_player_moving()].ai is None or self.game.all_ai() is True:
                draw_player_info = True

            self.draw_tool.draw_board(self.game.tiles,
                                    self.game.numbers,
                                    self.game.ports,
                                    self.game.robber_tile,
                                    self.game.players,
                                    self.game.player_turn,
                                    self.game.log,
                                    self.game.dices,
                                    self.game.get_player_moving(),
                                    self.game.game_phase,
                                    self.game.players_trade,
                                    draw_player_info)
        elif self.controller_state == 0:
            self.draw_tool.draw_start()
        elif self.controller_state == 2:
            self.draw_tool.draw_options(self.config_game)
        elif self.controller_state in [3, 4, 5]:
            self.draw_tool.draw_configure(self.config_game, self.controller_state)
        elif self.controller_state == 10:
            self.draw_tool.draw_dice_options()
        elif self.controller_state == 11:
            self.draw_tool.draw_special_cards_options()
        elif self.controller_state == 12:
            self.draw_tool.draw_steal_cards_options()

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
        if self.pos_in_rectangle(pos, config.menu_x_offset + config.menu_image_size[0] + 270, config.menu_y_offset + config.menu_y_step, config.circle_image_size[0], config.circle_image_size[1]):
            return 'increase_game_type'
        if self.pos_in_rectangle(pos, config.menu_x_offset + config.menu_image_size[0] + 20, config.menu_y_offset + config.menu_y_step, config.circle_image_size[0], config.circle_image_size[1]):
            return 'decrease_game_type'
        if self.pos_in_rectangle(pos, config.menu_x_offset, config.menu_y_offset + 500, config.menu_image_size[0], config.menu_image_size[1]):
            return 'back'

        for p in range(4):
            if self.pos_in_rectangle(pos, config.menu_x_offset_col2 + config.menu_image_size[0] + 20, config.menu_y_offset + p * config.menu_y_step, config.circle_image_size[0], config.circle_image_size[1]):
                return ('player', p)
            if self.pos_in_rectangle(pos, config.menu_x_offset_col2 + config.menu_image_size[0] + 200, config.menu_y_offset + p * config.menu_y_step, config.circle_image_size[0], config.circle_image_size[1]):
                return ('player', p)

    def check_click_configure(self, pos):
        if self.controller_state == 3:
            for av_tile in config.card_types.keys():
                if self.pos_in_rectangle(pos, config.available_tiles_x_offset + (av_tile - 2) * config.available_tiles_gap, config.available_tiles_y_offset, config.tiles_size[0], config.tiles_size[1]):
                    return('av_tile', av_tile)
        elif self.controller_state == 4:
            for i, number in enumerate([2, 3, 4, 5, 6, 8, 9, 10, 11, 12]):
                if self.pos_in_rectangle(pos, config.available_tiles_x_offset + i * config.available_numbers_gap, config.available_tiles_y_offset, config.numbers_size[0], config.numbers_size[1]):
                    return('av_num', number)
        elif self.controller_state == 5:
            for av_port in config.card_types.keys():
                if self.pos_in_rectangle(pos, config.available_tiles_x_offset + (av_port - 2) * config.available_numbers_gap, config.available_tiles_y_offset, config.ports_size[0], config.ports_size[1]):
                    return('av_port', av_port)
            click_port = self.click_in_port(pos)
            if click_port[0] == 'port':
                return click_port

        for i, tile_pos in enumerate(config.tile_position):
            if self.pos_in_rectangle(pos, tile_pos[0] + config.number_x_offset, tile_pos[1] + config.number_y_offset, config.numbers_size[0], config.numbers_size[1]):
                return ('tile', i)

        return None

    def check_click_dice(self, pos):
        for i in range(2, 13):
            if self.pos_in_rectangle(pos, config.menu_x_offset, config.menu_y_offset + (i - 2) * config.dice_step, 2 * config.ports_size[0], config.ports_size[1]):
                return i

        return None

    def check_click_special_card(self, pos):
        for i in range(config.YEAR_OF_PLENTY + 1):
            if self.pos_in_rectangle(pos, config.menu_x_offset, config.menu_y_offset + i * config.dice_step, config.ports_size[0], config.ports_size[1]):
                return i

        return None

    def check_click_stolen_card(self, pos):
        for i, card in enumerate(config.card_types):
            if self.pos_in_rectangle(pos, config.menu_x_offset, config.menu_y_offset + i * config.dice_step, config.ports_size[0], config.ports_size[1]):
                return card

        if self.pos_in_rectangle(pos, config.menu_x_offset, config.menu_y_offset + len(config.card_types) * config.dice_step, config.ports_size[0], config.ports_size[1]):
            return 0

        return None

    def handle_mouse_button_down(self, pos, button):
        if self.controller_state == 0:
            if self.check_click_menu(pos) == 'start_game':
                if self.config_game['TYPE_OF_GAME'] == 0:
                    self.start_game()
                elif self.config_game['TYPE_OF_GAME'] == 1:
                    self.configure_game()
                    #self.start_game()
            elif self.check_click_menu(pos) == 'load_game':
                with open('game.pkl', 'rb') as input_file:
                    self.game = pickle.load(input_file)
                    self.game.log = "Game loaded"
                self.controller_state = 1
            elif self.check_click_menu(pos) == 'options':
                self.controller_state = 2

        elif self.controller_state == 2:
            pos_clicked = self.check_click_options(pos)
            if pos_clicked == 'increase_mcts':
                self.config_game['MCTS_EXPLORATION'] += 50
            elif pos_clicked == 'decrease_mcts':
                self.config_game['MCTS_EXPLORATION'] -= 50
            elif pos_clicked in ['increase_game_type', 'decrease_game_type']:
                self.config_game['TYPE_OF_GAME'] = (self.config_game['TYPE_OF_GAME'] + 1) % 2
            elif pos_clicked == 'back':
                self.controller_state = 0
            elif isinstance(pos_clicked, tuple):
                if pos_clicked[0] == 'player':
                    self.config_game['PLAYER_IS_HUMAN'][pos_clicked[1]] = (self.config_game['PLAYER_IS_HUMAN'][pos_clicked[1]] + 1) % 2

        elif self.controller_state == 3:
            click_action = self.check_click_configure(pos)
            if click_action is not None:
                if click_action[0] == 'av_tile':
                    self.av_tile_selected = click_action[1]
                if click_action[0] == 'tile' and self.av_tile_selected is not None:
                    self.config_game['tiles'][click_action[1]] = self.av_tile_selected
                    self.config_game['available_tiles'].remove(self.av_tile_selected)
                    self.av_tile_selected = None
                    if self.config_game['available_tiles'] == [1]:
                        self.controller_state = 4

        elif self.controller_state == 4:
            click_action = self.check_click_configure(pos)
            if click_action is not None:
                if click_action[0] == 'av_num':
                    self.av_num_selected = click_action[1]
                if click_action[0] == 'tile' and self.av_num_selected is not None:
                    self.config_game['numbers'].append( (self.av_num_selected, click_action[1]) )
                    self.config_game['available_numbers'].remove(self.av_num_selected)
                    self.av_num_selected = None
                    if self.config_game['available_numbers'] == []:
                        self.controller_state = 5

        elif self.controller_state == 5:
            click_action = self.check_click_configure(pos)
            if click_action is not None:
                if click_action[0] == 'av_port':
                    self.av_port_selected = click_action[1]
                if click_action[0] == 'port' and self.av_port_selected is not None:
                    self.config_game['ports'][click_action[1]] = self.av_port_selected
                    self.config_game['available_ports'].remove(self.av_port_selected)
                    self.av_port_selected = None
                    if self.config_game['available_ports'] == []:
                        self.start_game()

        elif self.controller_state == 10:
            click_action = self.check_click_dice(pos)
            if click_action is not None:
                self.game.execute_dice_result(click_action)
                self.game.last_dice_rolled = click_action
                self.controller_state = 1

        elif self.controller_state == 11:
            click_action = self.check_click_special_card(pos)
            if click_action is not None:
                self.game.handle_buy_given_special_card(click_action)
                self.controller_state = 1

        elif self.controller_state == 12:
            click_action = self.check_click_stolen_card(pos)
            if click_action is not None:
                self.game.handle_steal_given_card_from(self.game.vertex_to_steal, click_action)
                self.controller_state = 1

        elif self.controller_state == 1:
            if self.game.current_action == config.THROW_DICE:
                self.game.current_action = -1
                self.game.dices = (0, 0)
                self.redraw()
                return

            if self.game.players[self.game.get_player_moving()].is_human == 0:
                if self.check_click(pos) == ('action', config.CONTINUE_GAME):
                    self.game.dices = (0, 0)
                    move, _, _ = self.game.players[self.game.get_player_moving()].ai.move(self.game)
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
                    self.game.start_port_trade(self.game.ports[click_port[1]])
            elif self.game.game_phase == config.PHASE_DISCARD:
                click = self.check_click(pos)
                if click[0] == 'card':
                    self.game.handle_discard(click[1])
                    self.game.descend_trees((config.DISCARD, click[1]))
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
                    self.game.descend_trees((config.TRADE_RESPONSE, 1))
                elif click == ('action', config.REJECT_TRADE):
                    self.game.handle_cancel_trade()
                    self.game.descend_trees((config.TRADE_RESPONSE, 0))

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
                self.game.descend_trees((config.BUILD_SETTLEMENT, vertex_released))

            elif self.game.current_action == config.BUILD_ROAD:
                _, road_released = self.check_release(pos)
                self.game.handle_build_road(road_released)
                self.game.descend_trees((config.BUILD_ROAD, road_released))

            elif self.game.current_action == config.BUILD_CITY:
                _, vertex_released = self.check_release(pos)
                self.game.handle_build_city(vertex_released)

        self.redraw()
        