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

    def available_resources(self, resource_type):
        for resource, value in config.resources[resource_type].items():
            if self.cards[resource] < value:
                return False

        if resource_type == 'road':
            if len(self.roads) >= config.max_roads:
                return False
        elif resource_type == 'city':
            if len(self.cities) >= config.max_cities:
                return False
        elif resource_type == 'settlement':
            if len(self.settlements) >= config.max_settlements:
                return False

        return True

    def add_resources(self, resources):
        for resource, value in resources.items():
            self.cards[resource] += value

    def remove_resources(self, resources):
        for resource, value in resources.items():
            self.cards[resource] -= value

    def remove_resources_by_improvement(self, improvement):
        self.remove_resources(config.resources[improvement])

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

    def cards_as_list(self):
        cards_list = []

        for resource, number in self.cards.items():
            cards_list = cards_list + [resource] * number

        return cards_list
