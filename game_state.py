from random import shuffle, choice
import player
import config

class GameState:
    def __init__(self):
        self.tiles = self.generate_tiles()
        self.numbers = self.generate_numbers()
        self.ports = self.generate_ports()
        self.current_action = -1
        self.initial_phase_settlement = 0
        self.initial_phase_decrease = 0
        self.dices = (0, 0)

        # Robber initial position
        self.robber_tile = self.tiles.index(config.DESERT)

        self.players = []
        for i in range(4): # 4 players
            self.players.append(player.Player(i))

        # Starting player
        self.player_turn = choice([0, 1, 2, 3])
        self.initial_phase_start_player = self.player_turn

        # Game Phase # (0, 0): Initial placement build settlement, (0, 1): Build road, (1, 0): Throw dice
        self.game_phase = (0, 0)

    @staticmethod
    def generate_ports():
        ports = []

        for key, value in config.port_types.items():
            ports.extend([key] * value['number'])
        shuffle(ports)

        return ports

    def generate_numbers(self):
        numbers = config.roll_numbers
        shuffle(numbers)

        numbers_tiles = []
        j = 0
        for i in range(len(self.tiles)):
            if self.tiles[i] != config.WATER and self.tiles[i] != config.DESERT:
                numbers_tiles.append((numbers[j], i))
                j += 1

        return numbers_tiles

    @staticmethod
    def generate_tiles():
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
        