import math

main_color = (255, 255, 255)

# Resources
WATER = 0
DESERT = 1
SHEEP = 2
ORE = 3
BRICK = 4
WHEAT = 5
WOOD = 6
GENERIC = 7

# Needed resources for actions
resources = {'road': {BRICK: 1, WOOD: 1},
             'settlement': {BRICK: 1, WOOD: 1, SHEEP: 1, WHEAT: 1},
             'city': {ORE: 3, WHEAT: 2},
             'special_card': {ORE: 1, WHEAT: 1, SHEEP: 1}}

# Max number of elements
max_settlements = 5
max_cities = 4
max_roads = 15

# Actions
BUILD_SETTLEMENT = 0
BUILD_CITY = 1
BUILD_ROAD = 2
THROW_DICE = 3
TRADE_41 = 4
SAVE_GAME = 100
LOAD_GAME = 101
CONTINUE_GAME = 102

# Board dimensions
x_dist = 120
y_dist = 105
x_offset = x_dist / 2
total_x_offset = 5
total_y_offset = 5
number_x_offset = 25
number_y_offset = 30

# Sizes
tiles_size = (112, 124)
numbers_size = (60, 60)
ports_size = (50, 50)
settlement_size = (30, 30)
city_size = (40, 30)
road_size = (30, 30)

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

# Position of the tiles
done = 0
tile_position = []

for i in range(7):
    tiles_per_row = ((4 + i) * (1 - math.floor(i / 4)) + math.floor(i / 4) * (10 - i))

    for j in range(tiles_per_row):
        tile_position.append((total_x_offset + (7 - tiles_per_row) * x_offset + j * x_dist, i * y_dist + total_y_offset))

    done = done + tiles_per_row

# Vertex position upper left corner = tile_position + tile_vertex_offset - vertex_size
vertex_size = (40, 40)
tile_vertex_offset = [(-20, 10), (42, -20), (104, 10), (104, 84), (42, 114), (-20, 84)]

# Store positions for all vertices
vertex_position = [(0, 0) for i in range(54)]
for tile, vertices in tiles_vertex.items():
    for i, vertex in enumerate(vertices):
        vertex_position[vertex] = (tile_position[tile][0] + tile_vertex_offset[i][0], tile_position[tile][1] + tile_vertex_offset[i][1])

ports_vertex = {0: {'vert': [16, 27], 'tile': 16, 'offset': (-60, 35)},
                1: {'vert': [7, 8], 'tile': 10, 'offset': (-15, -45)},
                2: {'vert': [2, 3], 'tile': 6, 'offset': (-15, -45)},
                3: {'vert': [5, 6], 'tile': 7, 'offset': (77, -45)},
                4: {'vert': [15, 25], 'tile': 13, 'offset': (123, 35)},
                5: {'vert': [36, 46], 'tile': 26, 'offset': (123, 35)},
                6: {'vert': [52, 53], 'tile': 31, 'offset': (80, 118)},
                7: {'vert': [49, 50], 'tile': 30, 'offset': (-15, 120)},
                8: {'vert': [38, 39], 'tile': 23, 'offset': (-15, 120)}}

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

players = {0: {'name': 'Player 1', 'color': (255, 0, 0), 'img_settlement': 'img/settlement_red.png', 'img_city': 'img/city_red.png', 'img_road': 'img/road_red.png'},
           1: {'name': 'Player 2', 'color': (80, 80, 255), 'img_settlement': 'img/settlement_blue.png', 'img_city': 'img/city_blue.png', 'img_road': 'img/road_blue.png'},
           2: {'name': 'Player 3', 'color': (0, 255, 0), 'img_settlement': 'img/settlement_green.png', 'img_city': 'img/city_green.png', 'img_road': 'img/road_green.png'},
           3: {'name': 'Player 4', 'color': (255, 153, 0), 'img_settlement': 'img/settlement_orange.png', 'img_city': 'img/city_orange.png', 'img_road': 'img/road_orange.png'}
          }

throw_dice = {'img': 'img/dices.png'}
throw_dice_position = (1000, 675)
throw_dice_size = (80, 51)
big_dice_x1 = 350
big_dice_x2 = 650
big_dice_y = 400
big_dice_size = (299, 294)

save_game = {'img': 'img/save.png'}
save_game_position = (1000, 15)
save_game_size = (64, 64)

load_game = {'img': 'img/load.png'}
load_game_position = (925, 15)
load_game_size = (64, 64)

continue_game = {'img': 'img/next.png'}
continue_game_position = (1000, 575)
continue_game_size = (64, 64)

trade41 = {'img': 'img/trade4-1.png'}
trade41_position = (1000, 115)
trade41_size = (64, 64)
