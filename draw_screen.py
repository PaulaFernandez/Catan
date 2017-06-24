import config
import pygame

class DrawScreen:
    def __init__(self, tiles, numbers, ports, screen):
        self.tiles = tiles
        self.numbers = numbers
        self.ports = ports

        self.screen = screen
        self.font = pygame.font.SysFont("sans-serif", 25)

    def draw(self, x, y, image_path, scale):
        image = pygame.image.load(image_path)
        image = pygame.transform.scale(image, scale)
        self.screen.blit(image, (x, y))

    def draw_tiles(self, tiles):
        for i in range(37):
            self.draw(config.tile_position[i][0], config.tile_position[i][1], config.tile_types[tiles[i]]['img'], config.tiles_size)

    def draw_numbers(self, tiles, numbers):
        j = 0
        for i in range(len(tiles)):
            if tiles[i] != config.WATER and tiles[i] != config.DESERT:
                self.draw(config.tile_position[i][0] + config.number_x_offset, config.tile_position[i][1] + config.number_y_offset, 'img/number_' + str(numbers[j]) + '.png', config.numbers_size)
                j += 1

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
        i = draw_card(i, config.players[player.player_id]['img_settlement'], str(5 - len(player.settlements)))

        # Cities
        i = draw_card(i, config.players[player.player_id]['img_city'], str(4 - len(player.cities)))

        # Roads
        i = draw_card(i, config.players[player.player_id]['img_road'], str(15 - len(player.roads)))

    def draw_improvements(self, players):
        for player in players:
            # Settlements
            for vertex in player.settlements:
                self.draw(config.vertex_position[vertex][0], config.vertex_position[vertex][1], config.players[player.player_id]['img_settlement'], config.settlement_size)

    def draw_board(self, robber_tile, players, player_turn, log):
        self.draw_tiles(self.tiles)
        self.draw_numbers(self.tiles, self.numbers)
        self.draw_ports(self.ports)
        self.draw_robber(robber_tile)
        self.draw_improvements(players)
        self.draw_summary(players, player_turn, log)
        self.draw_current_player(players[player_turn])
        