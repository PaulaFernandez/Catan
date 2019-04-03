import math
import config
import pygame

class DrawScreen:
    def __init__(self):
        self.screen = pygame.display.set_mode((1400, 900))
        self.screen.fill((0, 0, 0))
        self.font = pygame.font.SysFont("sans-serif", 25)

    def draw(self, x, y, image_path, scale, angle=0):
        def rot_center(image, angle):
            # rotate an image while keeping its center and size
            orig_rect = image.get_rect()
            rot_image = pygame.transform.rotate(image, angle)
            rot_rect = orig_rect.copy()
            rot_rect.center = rot_image.get_rect().center
            rot_image = rot_image.subsurface(rot_rect).copy()
            return rot_image

        image = pygame.image.load(image_path)
        image = pygame.transform.scale(image, scale)

        if angle != 0:
            image = rot_center(image, angle)

        self.screen.blit(image, (x, y))

    def draw_tiles(self, tiles):
        for i in range(37):
            self.draw(config.tile_position[i][0], config.tile_position[i][1], config.tile_types[tiles[i]]['img'], config.tiles_size)

    def draw_numbers(self, tiles, numbers):
        for number, tile in numbers:
            self.draw(config.tile_position[tile][0] + config.number_x_offset, config.tile_position[tile][1] + config.number_y_offset, 'img/number_' + str(number) + '.png', config.numbers_size)

    def draw_ports(self, ports):
        for i, port in enumerate(ports):
            self.draw(config.tile_position[config.ports_vertex[i]['tile']][0] + config.ports_vertex[i]['offset'][0], config.tile_position[config.ports_vertex[i]['tile']][1] + config.ports_vertex[i]['offset'][1], config.port_types[port]['img'], config.ports_size)

    def draw_robber(self, tile_num):
        self.draw(config.tile_position[tile_num][0] + config.number_x_offset, config.tile_position[tile_num][1] + config.number_y_offset, config.robber['img'], config.numbers_size)

    def draw_summary(self, players, player_turn, log, stage):
        for key, player_x in enumerate(players):
            x, y = config.player_stats_x, config.player_stats_y + key * (config.player_stats_y + config.player_stats_height)

            pygame.draw.rect(self.screen, config.players[key]['color'], (x, y, config.player_stats_width, config.player_stats_height), config.thickness)
            x += config.player_stats_x_offset
            y += config.player_stats_y_offset

            self.draw(x + config.start_trade_x_offset, y + config.start_trade_y_offset, config.start_trade['img'], config.start_trade_size)

            if player_turn == key:
                pygame.draw.circle(self.screen, config.players[key]['color'], (x + config.turn_x_offset, y + config.turn_y_offset), config.turn_radius, config.turn_radius)
            if player_x.largest_army_badge == 1:
                self.draw(x + config.largest_army_x_offset, y + config.largest_army_y_offset, config.largest_army['img'], config.largest_army_size)
            if player_x.longest_road_badge == 1:
                self.draw(x + config.longest_road_x_offset, y + config.longest_road_y_offset, config.longest_road['img'], config.longest_road_size)

            label = self.font.render(config.players[key]['name'], 1, config.players[key]['color'])
            self.screen.blit(label, (x, y))

            y += config.line_space
            message = 'Points: ' + str(player_x.points())
            if key == player_turn:
                message = message + ' (' + str(player_x.points(hidden=0)) + ')'
            label_points = self.font.render(message, 1, config.players[key]['color'])
            self.screen.blit(label_points, (x, y))

            y += config.line_space
            label_cards = self.font.render('Cards in hand: ' + str(player_x.total_cards()), 1, config.players[key]['color'])
            self.screen.blit(label_cards, (x, y))

            y += config.line_space
            label_special_cards = self.font.render('Development cards in hand: ' + str(player_x.total_special_cards()), 1, config.players[key]['color'])
            self.screen.blit(label_special_cards, (x, y))

            y += config.line_space
            label_knigts = self.font.render('Knights played: ' + str(player_x.used_knights), 1, config.players[key]['color'])
            self.screen.blit(label_knigts, (x, y))

            y += config.line_space
            label_road = self.font.render('Longest road: ' + str(player_x.longest_road), 1, config.players[key]['color'])
            self.screen.blit(label_road, (x, y))

        x, y = config.player_stats_x, config.player_stats_y + 4 * config.player_stats_height + 4 * config.player_stats_y_offset
        pygame.draw.rect(self.screen, config.main_color, (x, y, config.player_stats_width, config.player_stats_height / 2), config.thickness)
        label_msg = self.font.render(log, 1, config.main_color)
        self.screen.blit(label_msg, (x + config.player_stats_x_offset, y + config.player_stats_y_offset))

        # Draw throw dice button
        self.draw(config.throw_dice_position[0], config.throw_dice_position[1], config.throw_dice['img'], config.throw_dice_size)

        # Draw save and load
        self.draw(config.save_game_position[0], config.save_game_position[1], config.save_game['img'], config.save_game_size)
        self.draw(config.load_game_position[0], config.load_game_position[1], config.load_game['img'], config.load_game_size)

        # Draw continue button
        self.draw(config.continue_game_position[0], config.continue_game_position[1], config.continue_game['img'], config.continue_game_size)

        # Draw trade 4-1 button
        self.draw(config.trade41_position[0], config.trade41_position[1], config.trade41['img'], config.trade41_size)

        # Draw buy special card button
        self.draw(config.buy_special_card_position[0], config.buy_special_card_position[1], config.buy_special_card['img'], config.buy_special_card_size)

        # Draw trade buttons
        if stage in [config.PHASE_TRADE_OFFER, config.PHASE_TRADE_RECEIVE, config.PHASE_TRADE_RESPOND]:
            self.draw(config.accept_trade_position[0], config.accept_trade_position[1], config.accept_trade['img'], config.accept_trade_size)
            self.draw(config.reject_trade_position[0], config.reject_trade_position[1], config.reject_trade['img'], config.reject_trade_size)

    def draw_current_player(self, player):
        def draw_card(i, img, label):
            self.draw(config.card_positions[i][0], config.card_positions[i][1], img, config.card_size)
            label_num = self.font.render(label, 1, config.main_color)
            self.screen.blit(label_num, (config.card_positions[i][0], config.card_positions[i][1] + config.label_y_offset))
            return i + 1

        x, y, width, height = config.player_screen_x, config.player_screen_y, config.player_screen_width, config.player_screen_height

        pygame.draw.rect(self.screen, config.players[player.player_id]['color'], (x, y, width, height), config.thickness)

        i = 0

        for card_type, img in config.card_types.items():
            i = draw_card(i, img['img'], str(player.cards[card_type]))

        # Settlements
        i = draw_card(i, config.players[player.player_id]['img_settlement'], str(config.max_settlements - len(player.settlements)))

        # Cities
        i = draw_card(i, config.players[player.player_id]['img_city'], str(config.max_cities - len(player.cities)))

        # Roads
        i = draw_card(i, config.players[player.player_id]['img_road'], str(config.max_roads - len(player.roads)))

        # Special Cards
        for special_card_type in player.special_cards:
            i = draw_card(i, config.special_cards[special_card_type]['img'], '')

    def draw_improvements(self, players):
        for player in players:
            # Roads
            for road in player.roads:
                vertex_1_x = config.vertex_position[road[0]][0]
                vertex_1_y = config.vertex_position[road[0]][1]
                vertex_2_x = config.vertex_position[road[1]][0]
                vertex_2_y = config.vertex_position[road[1]][1]

                if int(vertex_1_x) == int(vertex_2_x):
                    angle = 90
                else:
                    angle = math.degrees(math.atan((vertex_1_y - vertex_2_y) / (vertex_2_x - vertex_1_x)))

                x = (vertex_2_x + vertex_1_x) / 2
                y = (vertex_2_y + vertex_1_y) / 2
                self.draw(x, y, config.players[player.player_id]['img_road'], config.road_size, angle=angle)

            # Settlements
            for vertex in player.settlements:
                self.draw(config.vertex_position[vertex][0], config.vertex_position[vertex][1], config.players[player.player_id]['img_settlement'], config.settlement_size)

            # Cities
            for vertex in player.cities:
                self.draw(config.vertex_position[vertex][0], config.vertex_position[vertex][1], config.players[player.player_id]['img_city'], config.city_size)

    def draw_position_squares(self):
        for _, vertices in config.tiles_vertex.items():
            for i in range(len(vertices)):
                x = (config.vertex_position[vertices[i]][0] + config.vertex_position[vertices[i-1]][0]) / 2
                y = (config.vertex_position[vertices[i]][1] + config.vertex_position[vertices[i-1]][1]) / 2
                pygame.draw.rect(self.screen, config.main_color, (x, y, config.road_size[0], config.road_size[1]), config.thickness)

    def draw_vertices(self):
        for vertex in config.vertex_position:
            pygame.draw.rect(self.screen, config.main_color, (vertex[0], vertex[1], config.vertex_size[0], config.vertex_size[1]), config.thickness)

    def draw_big_dices(self, dices):
        self.draw(config.big_dice_x1, config.big_dice_y, 'img/dice' + str(dices[0]) + '.png', config.big_dice_size)
        self.draw(config.big_dice_x2, config.big_dice_y, 'img/dice' + str(dices[1]) + '.png', config.big_dice_size)

    def draw_board(self, tiles, numbers, ports, robber_tile, players, player_turn, log, dices, perspective, stage):
        self.screen.fill((0, 0, 0))

        self.draw_tiles(tiles)
        self.draw_numbers(tiles, numbers)
        self.draw_ports(ports)
        self.draw_robber(robber_tile)
        self.draw_improvements(players)
        self.draw_summary(players, player_turn, log, stage)
        if perspective is not None:
            self.draw_current_player(players[perspective])
        else:
            self.draw_current_player(players[player_turn])
        # self.draw_position_squares()
        # self.draw_vertices()

        if dices != (0, 0):
            self.draw_big_dices(dices)

    def draw_dice_options(self):
        self.draw(0, 0, 'img/background.jpg', (1400,900))
        for i, dice in enumerate([(1, 1), (1, 2), (1, 3), (1, 4), (1, 5), (1, 6), (2, 6), (3, 6), (4, 6), (5, 6), (6, 6)]):
            self.draw(config.menu_x_offset, config.menu_y_offset + i * config.dice_step, 'img/dice' + str(dice[0]) + '.png', config.ports_size, angle=0)
            self.draw(config.menu_x_offset + 50, config.menu_y_offset + i * config.dice_step, 'img/dice' + str(dice[1]) + '.png', config.ports_size, angle=0)

    def draw_start(self):
        self.draw(0, 0, 'img/background.jpg', (1400,900))
        self.draw(config.menu_x_offset, config.menu_y_offset, config.start_image, config.menu_image_size, angle=0)
        self.draw(config.menu_x_offset, config.menu_y_offset + config.menu_y_step, config.load_game_image, config.menu_image_size, angle=0)
        self.draw(config.menu_x_offset, config.menu_y_offset + 2 * config.menu_y_step, config.options_image, config.menu_image_size, angle=0)
        
    def draw_options(self, config_game):
        self.draw(0, 0, 'img/background.jpg', (1400,900))

        # MCTS Explore
        self.draw(config.menu_x_offset, config.menu_y_offset, config.mcts_image, config.menu_image_size, angle=0)
        self.draw(config.menu_x_offset + config.menu_image_size[0] + 20, config.menu_y_offset, config.minus_image, config.circle_image_size, angle=0)
        self.draw(config.menu_x_offset + config.menu_image_size[0] + 200, config.menu_y_offset, config.plus_image, config.circle_image_size, angle=0)
        self.screen.fill((255, 255, 255), rect = pygame.Rect(config.menu_x_offset + config.menu_image_size[0] + 110, config.menu_y_offset + 20, 70, 30))
        mcts_explore_text = self.font.render(str(config_game['MCTS_EXPLORATION']), 1, (0, 0, 0))
        self.screen.blit(mcts_explore_text, (config.menu_x_offset + config.menu_image_size[0] + 120, config.menu_y_offset + 25))

        # Type of Game
        self.draw(config.menu_x_offset, config.menu_y_offset + config.menu_y_step, config.game_type_image, config.menu_image_size, angle=0)
        self.draw(config.menu_x_offset + config.menu_image_size[0] + 20, config.menu_y_offset + config.menu_y_step, config.minus_image, config.circle_image_size, angle=0)
        self.draw(config.menu_x_offset + config.menu_image_size[0] + 270, config.menu_y_offset + config.menu_y_step, config.plus_image, config.circle_image_size, angle=0)
        self.screen.fill((255, 255, 255), rect = pygame.Rect(config.menu_x_offset + config.menu_image_size[0] + 110, config.menu_y_offset + config.menu_y_step + 20, 140, 30))
        game_type = "COMPUTER" if config_game['TYPE_OF_GAME'] == 0 else "BOARD"
        game_type_text = self.font.render(game_type, 1, (0, 0, 0))
        self.screen.blit(game_type_text, (config.menu_x_offset + config.menu_image_size[0] + 120, config.menu_y_offset + config.menu_y_step + 25))

        # Players
        for p in range(4):
            self.draw(config.menu_x_offset_col2, config.menu_y_offset + p * config.menu_y_step, config.player_image[p], config.menu_image_size, angle=0)
            self.draw(config.menu_x_offset_col2 + config.menu_image_size[0] + 20, config.menu_y_offset + p * config.menu_y_step, config.minus_image, config.circle_image_size, angle=0)
            self.draw(config.menu_x_offset_col2 + config.menu_image_size[0] + 200, config.menu_y_offset + p * config.menu_y_step, config.plus_image, config.circle_image_size, angle=0)
            self.screen.fill((255, 255, 255), rect = pygame.Rect(config.menu_x_offset_col2 + config.menu_image_size[0] + 110, config.menu_y_offset + p * config.menu_y_step + 20, 90, 30))
            human_cpu = "CPU" if config_game['PLAYER_IS_HUMAN'][p] == 0 else "HUMAN"
            player_text = self.font.render(human_cpu, 1, (0, 0, 0))
            self.screen.blit(player_text, (config.menu_x_offset_col2 + config.menu_image_size[0] + 120, config.menu_y_offset + p * config.menu_y_step + 25))

        # Back
        self.draw(config.menu_x_offset, config.menu_y_offset + 500, config.back_image, config.menu_image_size, angle=0)
        
    def draw_configure(self, config_game, state):
        self.screen.fill((0, 0, 0))

        self.draw_tiles(config_game['tiles'])
        self.draw_numbers(config_game['tiles'], config_game['numbers'])
        self.draw_ports(config_game['ports'])

        # Paint tiles available
        if state == 3:
            for tile in [config.SHEEP, config.ORE, config.BRICK, config.WHEAT, config.WOOD]:
                if tile in config_game['available_tiles']:
                    self.draw(config.available_tiles_x_offset + (tile - 2) * config.available_tiles_gap, config.available_tiles_y_offset, config.tile_types[tile]['img'], config.tiles_size)

        # Paint numbers available
        if state == 4:
            for i, number in enumerate([2, 3, 4, 5, 6, 8, 9, 10, 11, 12]):
                if number in config_game['available_numbers']:
                    self.draw(config.available_tiles_x_offset + i * config.available_numbers_gap, config.available_tiles_y_offset, 'img/number_' + str(number) + '.png', config.numbers_size)

        # Paint ports available
        if state == 5:
            for i, port in enumerate(config.card_types.keys()):
                if port in config_game['available_ports']:
                    self.draw(config.available_tiles_x_offset + i * config.available_numbers_gap, config.available_tiles_y_offset, config.port_types[port]['img'], config.ports_size)