import math

player_is_human = {0: 0,
                   1: 0,
                   2: 0,
                   3: 0}

main_color = (255, 255, 255)

WIN_POINTS = 10
MAX_MOVES = 125

# Neural Network
ETA = 0.65
DETERMINISTIC_PLAY = False
CURRENT_AGENT = 15
SELF_PLAY_BATCH_SIZE = 100
TRAIN_BATCH_SIZE = 256
TRAINING_LOOPS = 35
EPOCHS = 2
MCTS_EXPLORATION = 35
MOMENTUM = 0.9
REG_CONST = 0.0001
LEARNING_RATE = 0.1
INPUT_DIM = (80, 6, 11)
OUTPUT_DIM = 941
HIDDEN_CNN_LAYERS = [
	{'filters':128, 'kernel_size': (3,3)}
	 , {'filters':128, 'kernel_size': (3,3)}
	 , {'filters':128, 'kernel_size': (3,3)}
	 , {'filters':128, 'kernel_size': (3,3)}
	 , {'filters':128, 'kernel_size': (3,3)}
	 , {'filters':128, 'kernel_size': (3,3)}
	]

folder_self_play = 'games'
folder_agents = 'agents'

# Resources
WATER = 0
DESERT = 1
SHEEP = 2
ORE = 3
BRICK = 4
WHEAT = 5
WOOD = 6
GENERIC = 7
PORT_4_1 = 8

# Special cards
VICTORY_POINT = 0
KNIGHT = 1
MONOPOLY = 2
ROAD_BUILDING = 3
YEAR_OF_PLENTY = 4

# Game Phases
PHASE_INITIAL_SETTLEMENT = (0, 0) # Initial placement: build settlement
PHASE_INITIAL_ROAD = (0, 1)       # Initial placement: build road
PHASE_THROW_DICE = (1, 0)         # Throw dice
PHASE_WAIT = (1, 1)               # Choose action: wait for end of turn
PHASE_DISCARD = (1, 2)            # Discard before moving robber
PHASE_MOVE_ROBBER = (1, 3)        # Move robber to another tile
PHASE_STEAL_CARD = (1, 4)         # Chosse settlement to steal from
PHASE_PORTS_TRADE = (1, 5)        # Trade in ports (including 4:1)
PHASE_MONOPOLY = (1, 6)           # Choose resource to monopolise
PHASE_ROAD_BUILDING = (1, 7)      # Build 2 roads for free
PHASE_YEAR_OF_PLENTY = (1, 8)     # Choose 2 resources from the bank
PHASE_TRADE_OFFER = (1, 9)        # Choose resources to offer
PHASE_TRADE_RECEIVE = (1, 10)     # Choose resources to receive
PHASE_TRADE_RESPOND = (1, 11)     # Choose whether to accept or reject
PHASE_END_GAME = (2, 0)           # End of game, player has reached 10 points

# Needed resources for actions
resources = {'road': {BRICK: 1, WOOD: 1},
             'settlement': {BRICK: 1, WOOD: 1, SHEEP: 1, WHEAT: 1},
             'city': {ORE: 3, WHEAT: 2},
             'special_card': {ORE: 1, WHEAT: 1, SHEEP: 1}}

# Max number of elements
max_settlements = 5
max_cities = 4
max_roads = 15
max_resources = 19

special_cards = {VICTORY_POINT: {'img': 'img/victory_point.png', 'count': 5},
                 KNIGHT: {'img': 'img/knight.png', 'count': 14},
                 MONOPOLY: {'img': 'img/monopoly.png', 'count': 2},
                 ROAD_BUILDING: {'img': 'img/road_building.png', 'count': 2},
                 YEAR_OF_PLENTY: {'img': 'img/year_of_plenty.png', 'count': 2}}

special_cards_vector = []

for key, value in special_cards.items():
    special_cards_vector.extend([key] * value['count'])

# Actions
BUILD_SETTLEMENT = 0
BUILD_CITY = 1
BUILD_ROAD = 2
THROW_DICE = 3
TRADE_41 = 4
BUY_SPECIAL_CARD = 5
MOVE_ROBBER = 6
STEAL_FROM_HOUSE = 7
DISCARD = 8
PLAY_SPECIAL_CARD = 9
PORT_TRADE = 10
RESOURCE_YEAR_PLENTY = 11
TRADE_OFFER = 12
TRADE_RESPONSE = 13
ACCEPT_TRADE = 14
REJECT_TRADE = 15
SAVE_GAME = 100
LOAD_GAME = 101
CONTINUE_GAME = 102

# Numbers dimensions
numbers_size = (60, 60)
number_x_offset = 25
number_y_offset = 30

# Sizes
ports_size = (50, 50)
settlement_size = (40, 40)
city_size = (40, 40)
road_size = (40, 40)

# Player stats offsets
player_stats_x = 1100
player_stats_y = 10
player_stats_height = 150
player_stats_width = 280
player_stats_x_offset = 10
player_stats_y_offset = 10

turn_x_offset = 230
turn_y_offset = 20
turn_radius = 20

largest_army = {'img': 'img/largest_army.png'}
largest_army_x_offset = 220
largest_army_y_offset = 80
largest_army_size = (40, 40)

longest_road = {'img': 'img/longest_road.png'}
longest_road_x_offset = 170
longest_road_y_offset = 80
longest_road_size = (40, 40)

thickness = 3
line_space = 20

# Current player screen
player_screen_x = 5
player_screen_y = 775
player_screen_height = 100
player_screen_width = player_stats_x + player_stats_width - player_screen_x

card_1_x = 15 + player_screen_x
card_1_y = 15 + player_screen_y
card_size = (40, 40)
card_space_x = 90

label_y_offset = 55

screen_objects = [('card', SHEEP),
                  ('card', ORE),
                  ('card', BRICK),
                  ('card', WHEAT),
                  ('card', WOOD),
                  ('action', BUILD_SETTLEMENT),
                  ('action', BUILD_CITY),
                  ('action', BUILD_ROAD)
                 ]

card_positions = []
for i in range(15):
    card_positions.append((card_1_x + card_space_x * i, card_1_y))

# Vertex belonging to tiles
tiles_vertex = {5: [0, 1, 2, 10, 9, 8],
                6: [2, 3, 4, 12, 11, 10],
                7: [4, 5, 6, 14, 13, 12],
                10: [7, 8, 9, 19, 18, 17],
                11: [9, 10, 11, 21, 20, 19],
                12: [11, 12, 13, 23, 22, 21],
                13: [13, 14, 15, 25, 24, 23],
                16: [16, 17, 18, 29, 28, 27],
                17: [18, 19, 20, 31, 30, 29],
                18: [20, 21, 22, 33, 32, 31],
                19: [22, 23, 24, 35, 34, 33],
                20: [24, 25, 26, 37, 36, 35],
                23: [28, 29, 30, 40, 39, 38],
                24: [30, 31, 32, 42, 41, 40],
                25: [32, 33, 34, 44, 43, 42],
                26: [34, 35, 36, 46, 45, 44],
                29: [39, 40, 41, 49, 48, 47],
                30: [41, 42, 43, 51, 50, 49],
                31: [43, 44, 45, 53, 52, 51]}

# Vertex to nn input
vertex_to_nn_input = [(0, 2), (0, 3), (0, 4), (0, 5), (0, 6), (0, 7), (0, 8),
                      (1, 1), (1, 2), (1, 3), (1, 4), (1, 5), (1, 6), (1, 7), (1, 8), (1, 9),
                      (2, 0), (2, 1), (2, 2), (2, 3), (2, 4), (2, 5), (2, 6), (2, 7), (2, 8), (2, 9), (2, 10),
                      (3, 0), (3, 1), (3, 2), (3, 3), (3, 4), (3, 5), (3, 6), (3, 7), (3, 8), (3, 9), (3, 10),
                      (4, 1), (4, 2), (4, 3), (4, 4), (4, 5), (4, 6), (4, 7), (4, 8), (4, 9),
                      (5, 2), (5, 3), (5, 4), (5, 5), (5, 6), (5, 7), (5, 8)]

# Tiles dimensions
total_offset = 5
tiles_size = (112, 129)
tiles_x_offset = 112
tiles_y_offset = 96

# Position of the tiles
done = 0
tile_position = []

for i in range(7):
    tiles_per_row = ((4 + i) * (1 - math.floor(i / 4)) + math.floor(i / 4) * (10 - i))

    for j in range(tiles_per_row):
        x = total_offset + (7 - tiles_per_row) * tiles_x_offset / 2 + j * tiles_x_offset
        y = i * tiles_y_offset + total_offset
        tile_position.append((x, y))

    done = done + tiles_per_row

# Vertex position upper left corner = tile_position + tile_vertex_offset - vertex_size / 2
vertex_size = (40, 40)
tile_vertex_offset = [(0, 33), (56, 0), (112, 33), (112, 96), (56, 129), (0, 96)]

# Store positions for all vertices
vertex_position = [(0, 0) for i in range(54)]
for tile, vertices in tiles_vertex.items():
    for i, vertex in enumerate(vertices):
        x = tile_position[tile][0] + tile_vertex_offset[i][0] - vertex_size[0] / 2
        y = tile_position[tile][1] + tile_vertex_offset[i][1] - vertex_size[1] / 2
        vertex_position[vertex] = (x, y)

roads_from_settlement = []
for s in range(54):
    roads = []
    for _, vertices in tiles_vertex.items():
        for i, vertex in enumerate(vertices):
            if vertex == s:
                if vertex < vertices[i-1]:
                    roads.append((vertex, vertices[i-1]))
                else:
                    roads.append((vertices[i-1], vertex))
                if vertex < vertices[i-5 % 6]:
                    roads.append((vertex, vertices[i-5 % 6]))
                else:
                    roads.append((vertices[i-5 % 6], vertex))

    roads_from_settlement.append(set(roads))

settlement_clash = {}
for vertex_1 in range(54):
    for vertex_2 in range(54):
        if vertex_1 == vertex_2:
            settlement_clash[(vertex_1, vertex_2)] = True
        else:
            for _, vertices in tiles_vertex.items():
                if vertex_1 in vertices and vertex_2 in vertices:
                    distance = abs(vertices.index(vertex_1) - vertices.index(vertex_2))
                    if distance == 1 or distance == 5:
                        settlement_clash[(vertex_1, vertex_2)] = True
                    else:
                        settlement_clash[(vertex_1, vertex_2)] = False
            if (vertex_1, vertex_2) not in settlement_clash:
                settlement_clash[(vertex_1, vertex_2)] = False
            

ports_vertex = {0: {'vert': [16, 27], 'tile': 16, 'offset': (-55, 39.5)},
                1: {'vert': [7, 8], 'tile': 10, 'offset': (-13, -35)},
                2: {'vert': [2, 3], 'tile': 6, 'offset': (-13, -35)},
                3: {'vert': [5, 6], 'tile': 7, 'offset': (75, -35)},
                4: {'vert': [15, 25], 'tile': 13, 'offset': (117, 39.5)},
                5: {'vert': [36, 46], 'tile': 26, 'offset': (117, 39.5)},
                6: {'vert': [52, 53], 'tile': 31, 'offset': (78, 112)},
                7: {'vert': [49, 50], 'tile': 30, 'offset': (-13, 112)},
                8: {'vert': [38, 39], 'tile': 23, 'offset': (-13, 112)}}

tile_types = {WATER: {'img': 'img/water.png'},
              DESERT: {'img': 'img/desert.png', 'number': 1},
              SHEEP: {'img': 'img/sheep.png', 'number': 4},
              ORE: {'img': 'img/ore.png', 'number': 3},
              BRICK: {'img': 'img/brick.png', 'number': 3},
              WHEAT: {'img': 'img/wheat.png', 'number': 4},
              WOOD: {'img': 'img/wood.png', 'number': 4}
             }

card_types = {SHEEP: {'img': 'img/sheep_icon.png'},
              ORE: {'img': 'img/ore_icon.png'},
              BRICK: {'img': 'img/brick_icon.png'},
              WHEAT: {'img': 'img/wheat_icon.png'},
              WOOD: {'img': 'img/wood_icon.png'}
             }

port_types = {SHEEP:{'img': 'img/sheep_port.png', 'number': 1},
              ORE:{'img': 'img/ore_port.png', 'number': 1},
              BRICK:{'img': 'img/brick_port.png', 'number': 1},
              WHEAT:{'img': 'img/wheat_port.png', 'number': 1},
              WOOD:{'img': 'img/wood_port.png', 'number': 1},
              GENERIC:{'img': 'img/port.png', 'number': 4}
             }

robber = {'img': 'img/robber.png'}

roll_numbers = [2, 3, 3, 4, 4, 5, 5, 6, 6, 8, 8, 9, 9, 10, 10, 11, 11, 12]
water_tiles = [0, 1, 2, 3, 4, 8, 9, 14, 15, 21, 22, 27, 28, 32, 33, 34, 35, 36]

players = {0: {'name': 'Player 1', 'color': (182, 43, 63), 'img_settlement': 'img/settlement_red.png', 'img_city': 'img/city_red.png', 'img_road': 'img/road_red.png'},
           1: {'name': 'Player 2', 'color': (32, 84, 200), 'img_settlement': 'img/settlement_blue.png', 'img_city': 'img/city_blue.png', 'img_road': 'img/road_blue.png'},
           2: {'name': 'Player 3', 'color': (53, 149, 35), 'img_settlement': 'img/settlement_green.png', 'img_city': 'img/city_green.png', 'img_road': 'img/road_green.png'},
           3: {'name': 'Player 4', 'color': (197, 116, 22), 'img_settlement': 'img/settlement_orange.png', 'img_city': 'img/city_orange.png', 'img_road': 'img/road_orange.png'}
          }

throw_dice = {'img': 'img/dices.png'}
throw_dice_position = (1000, 650)
throw_dice_size = (64, 64)

continue_game = {'img': 'img/next.png'}
continue_game_position = (925, 650)
continue_game_size = (64, 64)

accept_trade = {'img': 'img/thumb-up.png'}
accept_trade_position = (925, 550)
accept_trade_size = (64, 64)

reject_trade = {'img': 'img/cancel.png'}
reject_trade_position = (1000, 550)
reject_trade_size = (64, 64)

save_game = {'img': 'img/save.png'}
save_game_position = (1000, 15)
save_game_size = (64, 64)

load_game = {'img': 'img/load.png'}
load_game_position = (925, 15)
load_game_size = (64, 64)

trade41 = {'img': 'img/trade4-1.png'}
trade41_position = (1000, 115)
trade41_size = (64, 64)

buy_special_card = {'img': 'img/card-draw.png'}
buy_special_card_position = (925, 115)
buy_special_card_size = (64, 64)

start_trade = {'img': 'img/card-exchange.png'}
start_trade_x_offset = 160
start_trade_y_offset = 5
start_trade_size = (35, 35)

big_dice_x1 = 350
big_dice_x2 = 650
big_dice_y = 400
big_dice_size = (299, 294)

# Moves mapping
available_moves = []
for s in range(54):
    available_moves.append((BUILD_SETTLEMENT, s))
    available_moves.append((BUILD_CITY, s))
for s in range(54):
    for r in roads_from_settlement[s]:
        if r[0] < r[1]:
            available_moves.append((BUILD_ROAD, r))
available_moves.append((THROW_DICE, ))
available_moves.append((CONTINUE_GAME, ))
for i in [SHEEP, ORE, WHEAT, BRICK, WOOD]:
    for j in [SHEEP, ORE, WHEAT, BRICK, WOOD]:
        if i != j:
            available_moves.append((TRADE_41, (i, j)))
for i in range(9):
    for j in [SHEEP, ORE, WHEAT, BRICK, WOOD]:
        for k in [SHEEP, ORE, WHEAT, BRICK, WOOD]:
            available_moves.append((PORT_TRADE, (i, j, k)))
for key in tiles_vertex:
    available_moves.append((MOVE_ROBBER, key))
for s in range(54):
    for p in range(1, 4):
        available_moves.append((STEAL_FROM_HOUSE, (s, p)))
for i in [SHEEP, ORE, WHEAT, BRICK, WOOD]:
    available_moves.append((DISCARD, i))
available_moves.append((BUY_SPECIAL_CARD, ))
for i in [KNIGHT, MONOPOLY, ROAD_BUILDING, YEAR_OF_PLENTY]:
    if i == MONOPOLY:
        for j in [SHEEP, ORE, WHEAT, BRICK, WOOD]:
            available_moves.append((PLAY_SPECIAL_CARD, i, j))
    else:
        available_moves.append((PLAY_SPECIAL_CARD, i))
for i in [SHEEP, ORE, WHEAT, BRICK, WOOD]:
    available_moves.append((RESOURCE_YEAR_PLENTY, i))
for p in range(1, 4):
    for i in [SHEEP, ORE, WHEAT, BRICK, WOOD]:
        for q in range(1, 3):
            for j in [SHEEP, ORE, WHEAT, BRICK, WOOD]:
                if i != j:
                    for l in range(1, 3):
                        available_moves.append((TRADE_OFFER, p, (i, q), (j, l)))
available_moves.append((TRADE_RESPONSE, 1))
available_moves.append((TRADE_RESPONSE, 0))