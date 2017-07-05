import config

class Player():
    def __init__(self, player_id):
        self.player_id = player_id

        self.cards = {config.SHEEP: 0, config.ORE: 0, config.WHEAT: 0, config.BRICK: 0, config.WOOD: 0}
        self.special_cards = []
        self.used_knights = 0

        self.settlements = []
        self.cities = []
        self.roads = []

        self.valid_roads = []

    def total_cards(self):
        total = 0

        for _, value in self.cards.items():
            total += value

        return total

    def points(self, hidden=1):
        points = 0

        # Cities and settlements
        points = points + len(self.settlements) + 2 * len(self.cities)

        return points

    def total_special_cards(self):
        return len(self.special_cards)

    def longest_road_length(self):
        return 0
