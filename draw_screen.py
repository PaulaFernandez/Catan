import math
import config
import pygame

class DrawScreen:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.SysFont("sans-serif", 25)

    def draw(self, x, y, image_path, scale, angle=0):
        image = pygame.image.load(image_path)
        image = pygame.transform.scale(image, scale)

        if angle != 0:
            image = pygame.transform.rotate(image, angle)

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

    def draw_summary(self, players, player_turn, log):
        for key, i in enumerate(players):
            x, y = config.player_stats_x, config.player_stats_y + key * (config.player_stats_y + config.player_stats_height)

            pygame.draw.rect(self.screen, config.players[key]['color'], (x, y, config.player_stats_width, config.player_stats_height), config.thickness)
            x += config.player_stats_x_offset
            y += config.player_stats_y_offset

            if player_turn == key:
                pygame.draw.circle(self.screen, config.players[key]['color'], (x + config.turn_x_offset, y + config.turn_y_offset), config.turn_radius, config.turn_radius)

            label = self.font.render(config.players[key]['name'], 1, config.players[key]['color'])
            self.screen.blit(label, (x, y))

            y += config.line_space
            label_points = self.font.render('Points: ' + str(i.points()), 1, config.players[key]['color'])
            self.screen.blit(label_points, (x, y))

            y += config.line_space
            label_cards = self.font.render('Cards in hand: ' + str(i.total_cards()), 1, config.players[key]['color'])
            self.screen.blit(label_cards, (x, y))

            y += config.line_space
            label_special_cards = self.font.render('Development cards in hand: ' + str(i.total_special_cards()), 1, config.players[key]['color'])
            self.screen.blit(label_special_cards, (x, y))

            y += config.line_space
            label_knigts = self.font.render('Knights played: ' + str(i.used_knights), 1, config.players[key]['color'])
            self.screen.blit(label_knigts, (x, y))

            y += config.line_space
            label_road = self.font.render('Longest road: ' + str(i.longest_road_length()), 1, config.players[key]['color'])
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

    def draw_improvements(self, players):
        for player in players:
            # Settlements
            for vertex in player.settlements:
                self.draw(config.vertex_position[vertex][0], config.vertex_position[vertex][1], config.players[player.player_id]['img_settlement'], config.settlement_size)

            # Cities
            for vertex in player.cities:
                self.draw(config.vertex_position[vertex][0], config.vertex_position[vertex][1], config.players[player.player_id]['img_city'], config.city_size)

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

                self.draw((vertex_2_x + vertex_1_x) / 2, (vertex_2_y + vertex_1_y) / 2, config.players[player.player_id]['img_road'], config.road_size, angle=angle)

    def draw_position_squares(self):
        for _, vertices in config.tiles_vertex.items():
            for i in range(len(vertices)):
                x = (config.vertex_position[vertices[i]][0] + config.vertex_position[vertices[i-1]][0]) / 2
                y = (config.vertex_position[vertices[i]][1] + config.vertex_position[vertices[i-1]][1]) / 2
                pygame.draw.rect(self.screen, config.players[0]['color'], (x, y, config.road_size[0], config.road_size[1]), config.thickness)

    def draw_big_dices(self, dices):
        self.draw(config.big_dice_x1, config.big_dice_y, 'img/dice' + str(dices[0]) + '.png', config.big_dice_size)
        self.draw(config.big_dice_x2, config.big_dice_y, 'img/dice' + str(dices[1]) + '.png', config.big_dice_size)

    def draw_board(self, tiles, numbers, ports, robber_tile, players, player_turn, log, dices):
        self.draw_tiles(tiles)
        self.draw_numbers(tiles, numbers)
        self.draw_ports(ports)
        self.draw_robber(robber_tile)
        self.draw_improvements(players)
        self.draw_summary(players, player_turn, log)
        self.draw_current_player(players[player_turn])
        #self.draw_position_squares()

        if dices != (0, 0):
            self.draw_big_dices(dices)
        