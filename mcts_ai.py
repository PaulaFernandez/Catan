from math import sqrt, log
from copy import deepcopy
from random import shuffle, choice, sample
import config
import pickle
import numpy as np

from model import Residual_CNN

class Node:
    """ A node in the game tree. Note wins is always from the viewpoint of player_turn.
        Crashes if state not specified.
    """
    def __init__(self, player, parent = None, move = None, prior_probs = 0.0):
        self.current_player = player
        self.parentNode = parent # "None" for the root node
        self.move = move
        self.childNodes = []
        self.child_moves = []
        self.possible_moves = []
        self.is_random = False
        self.W = 0 # Total value of node
        self.N = 0 # Total visits
        self.Q = 0
        self.move_probabilities = []
        self.prior_probabilities = prior_probs

    def move_index(self, move, player):
        if len(self.move_probabilities) == config.OUTPUT_START_DIM:
            return config.start_available_moves.index(move)
        else:
            if move[0] == config.STEAL_FROM_HOUSE:
                p_order = (4 + move[1][1] - self.current_player) % 4
                return config.available_moves.index((move[0], (move[1][0], p_order)))
            elif move[0] == config.TRADE_OFFER:
                p_order = (4 + move[1] - player) % 4
                return config.available_moves.index((move[0], p_order, move[2], move[3]))
            else:
                return config.available_moves.index(move)
        
    def add_probabilities(self, probs):
        self.move_probabilities = probs
        
    def UCTSelectChild(self, weight):
        def evaluation(x):
            return weight * x.Q + (1 - weight) * 0.2 * (x.prior_probabilities / 2.0 + 0.5) * sqrt(self.N / (0.01 + x.N))

        potential_moves = []
        
        for m in self.possible_moves:
            n = self.childNodes[self.child_moves.index(m)]
            potential_moves.append(n)
        
        s = sorted(potential_moves, key = evaluation )
        try:
            return s[-1]
        except:
            raise Exception("No moves found. Move: " + str(self.move) + "; Possible_moves: " + str(self.possible_moves))
    
    def get_child_probs(self):
        probs = []
        for c in self.childNodes:
            probs.append(c.N)
        
        probs = np.array(probs)
        probs = np.power(probs, 1 / config.ETA)
        probs = probs / np.sum(probs)
        
        return probs
    
    def update(self, result):
        self.N += 1
        self.W += result
        self.Q = self.W / self.N
        
    def get_possible_moves(self, state):
        self.possible_moves = state.ai_get_moves()
        return self.possible_moves
    
    def check_untried(self, state):
        self.get_possible_moves(state)
        
        possible_expansion = []
        for m in self.possible_moves:
            if m not in self.child_moves:
                possible_expansion.append(m)
                
        return possible_expansion
    
    def add_child(self, player, move):
        index_probs = self.move_index(move, player)
        if move[0] == config.THROW_DICE:
            n = Dice_Node(player, self, prior_probs = self.move_probabilities[index_probs])
        elif move[0] == config.BUY_SPECIAL_CARD:
            n = Buy_Card_Node(player, self, prior_probs = self.move_probabilities[index_probs])
        elif move[0] == config.STEAL_FROM_HOUSE:
            n = Steal_Card_Node(player, move, self, prior_probs = self.move_probabilities[index_probs])
        else:
            try:
                n = Node(player, self, move, prior_probs = self.move_probabilities[index_probs])
            except:
                raise Exception("index: " + str(index_probs) + "move_probs: " + str(self.move_probabilities))
        self.childNodes.append(n)
        self.child_moves.append(move)
        return n
        
    def ChildrenToString(self):
        s = ""
        for c in self.childNodes:
             s += str(c) + "\n"
        return s

    def __repr__(self):
        return "[M:" + str(self.move) + " Q/N:" + str(self.Q) + "/" + str(self.N) + "] P: " + str(self.prior_probabilities)

class Dice_Node(Node):
    def __init__(self, player, parent = None, prior_probs = 0.0):
        Node.__init__(self, player, parent, (config.THROW_DICE,), prior_probs)
        self.possible_moves = [(config.THROW_DICE, x) for x in range(2, 13)]
        self.is_random = True
        
    def get_possible_moves(self, state):
        return self.possible_moves

    def calculate_throw_dice(self):
        dice_1 = choice([1, 2, 3, 4, 5, 6])
        dice_2 = choice([1, 2, 3, 4, 5, 6])

        return (dice_1 + dice_2)
    
    def roll(self, state):
        dice_result = self.calculate_throw_dice()
        
        if ((config.THROW_DICE, dice_result) in self.child_moves):
            idx = self.child_moves.index((config.THROW_DICE, dice_result))
            return self.childNodes[idx], False
        else:
            node = self.add_child((config.THROW_DICE, dice_result))
            return node, True
            
    def add_child(self, move):
        node = Node(self.current_player, self, move)
        self.childNodes.append(node)
        self.child_moves.append(move)
        return node

class Steal_Card_Node(Node):
    def __init__(self, player, move, parent = None, prior_probs = 0.0):
        Node.__init__(self, player, parent, move, prior_probs)
        self.possible_moves = [(config.STEAL_FROM_HOUSE, move[1], key) for key in config.card_types]
        self.is_random = True
        
    def get_possible_moves(self, state):
        return self.possible_moves
    
    def roll(self, state):
        player_cards = state.players[self.move[1][1]].cards_as_list()
        if len(player_cards) > 0:
            card = choice(player_cards)
        else:
            card = 0
        
        if ((config.STEAL_FROM_HOUSE, self.move[1], card) in self.child_moves):
            idx = self.child_moves.index((config.STEAL_FROM_HOUSE, self.move[1], card))
            return self.childNodes[idx], False
        else:
            node = self.add_child((config.STEAL_FROM_HOUSE, self.move[1], card))
            return node, True
            
    def add_child(self, move):
        node = Node(self.current_player, self, move)
        self.childNodes.append(node)
        self.child_moves.append(move)
        return node

class Buy_Card_Node(Node):
    def __init__(self, player, parent = None, prior_probs = 0.0):
        Node.__init__(self, player, parent, (config.BUY_SPECIAL_CARD,), prior_probs)
        self.possible_moves = [(config.BUY_SPECIAL_CARD, config.VICTORY_POINT),
                               (config.BUY_SPECIAL_CARD, config.KNIGHT),
                               (config.BUY_SPECIAL_CARD, config.MONOPOLY),
                               (config.BUY_SPECIAL_CARD, config.ROAD_BUILDING),
                               (config.BUY_SPECIAL_CARD, config.YEAR_OF_PLENTY)]
        self.is_random = True
        
    def get_possible_moves(self, state):
        return self.possible_moves
    
    def roll(self, state):
        card = choice(state.special_cards)
        
        if ((config.BUY_SPECIAL_CARD, card) in self.child_moves):
            idx = self.child_moves.index((config.BUY_SPECIAL_CARD, card))
            return self.childNodes[idx], False
        else:
            node = self.add_child((config.BUY_SPECIAL_CARD, card))
            return node, True
            
    def add_child(self, move):
        node = Node(self.current_player, self, move)
        self.childNodes.append(node)
        self.child_moves.append(move)
        return node

class MCTS_AI:
    def __init__(self, player_id, agent, itermax, agent_name):
        self.itermax = itermax
        self.player_id = player_id
        self.agent_name = agent_name
        self.rivals_info = {}
        self.rootnode = None
        
        self.nn_start = agent[0]
        self.nn = agent[1]

        for p in range(4):
            if p != self.player_id:
                self.rivals_info[p] = {'cards': set([(0, 0, 0, 0, 0)]),
                                       'special_cards': 0}

    def __deepcopy__(self, memo):
        cls = self.__class__
        result = cls.__new__(cls)
        memo[id(self)] = result
        for k, v in self.__dict__.items():
            if k not in ["nn", "nn_start"]:
                setattr(result, k, deepcopy(v, memo))
        return result
        
    def add_resources_rival(self, cards_taken, player_id):
        for key, value in cards_taken.items():
            if len(self.rivals_info[player_id]['cards']) == 0:
                cards_set = tuple([value if key == (x + 2) else 0 for x in range(5)])
                self.rivals_info[player_id]['cards'].add(cards_set)
            else:
                new_set = set()
                for cards in self.rivals_info[player_id]['cards']:
                    cards = list(cards)
                    cards[key - 2] += value
                    cards = tuple(cards)
                    new_set.add(cards)
                self.rivals_info[player_id]['cards'] = new_set

    def remove_resources_rival(self, cards_taken, player_id):
        for key, value in cards_taken.items():
            new_set = set()
            for cards in self.rivals_info[player_id]['cards']:
                if cards[key - 2] < value:
                    continue
                else:
                    cards = list(cards)
                    cards[key - 2] -= value
                    cards = tuple(cards)
                    new_set.add(cards)
            self.rivals_info[player_id]['cards'] = new_set

    def remove_unknown_resource_rival(self, player_id):
        new_set = set()
        cards_available = set()
        for cards in self.rivals_info[player_id]['cards']:
            for c in range(2, 7):
                if cards[c - 2] >= 1:
                    cards_x = list(cards)
                    cards_x[c - 2] -= 1
                    cards_x = tuple(cards_x)
                    new_set.add(cards_x)
                    cards_available.add(c)
        self.rivals_info[player_id]['cards'] = new_set
        
        return cards_available

    def add_unknown_resource_rival(self, player_id, cards_available = set([2,3,4,5,6])):
        new_set = set()
        for cards in self.rivals_info[player_id]['cards']:
            for c in cards_available:
                cards_x = list(cards)
                cards_x[c - 2] += 1
                cards_x = tuple(cards_x)
                new_set.add(cards_x)
        self.rivals_info[player_id]['cards'] = new_set
            
    def add_special_card_rival(self, player_id):
        self.rivals_info[player_id]['special_cards'] += 1
            
    def remove_special_card_rival(self, player_id):
        self.rivals_info[player_id]['special_cards'] -= 1
        
    def get_undetermined_resources_rivals(self, player):
        min_cards = [100, 100, 100, 100, 100]
        for cards in self.rivals_info[player]['cards']:
            for c in range(len(cards)):
                if cards[c] < min_cards[c]:
                    min_cards[c] = cards[c]
                    
        return min_cards
    
    def select(self, state, node, weight):
        while 1:
            if node.is_random:
                node, evaluate = node.roll(state)
                state.ai_do_move(node.move)

                if evaluate == True:
                    network = self.build_nn_input(state, node.current_player, determined = 1)
                    prediction = self.predict(network)
                    
                    node.add_probabilities(prediction[1][0])
            else:
                expansion_nodes = node.check_untried(state)
                if expansion_nodes != [] or state.game_phase == config.PHASE_END_GAME:
                    return node, expansion_nodes
                else:
                    node = node.UCTSelectChild(weight)
                    if node.move[0] != config.THROW_DICE and node.move[0] != config.BUY_SPECIAL_CARD and node.move[0] != config.STEAL_FROM_HOUSE:
                        state.ai_do_move(node.move)
                    
    def expand(self, state, node, possible_expansions):
        m = choice(possible_expansions) 
        current_player = state.get_player_moving()
        if m[0] != config.THROW_DICE and m[0] != config.BUY_SPECIAL_CARD and m[0] != config.STEAL_FROM_HOUSE:
            state.ai_do_move(m)
        node = node.add_child(current_player, m) # add child and descend tree

        network = self.build_nn_input(state, node.current_player, determined = 1)
        prediction = self.predict(network)
        
        node.add_probabilities(prediction[1][0])

        if node.is_random:
            node, evaluate = node.roll(state)
            state.ai_do_move(node.move)

            if evaluate == True:
                network = self.build_nn_input(state, node.current_player, determined = 1)
                prediction = self.predict(network)
                
                node.add_probabilities(prediction[1][0])

        return node, prediction
    
    def build_start_nn_input(self, state, perspective):
        nn_input = np.zeros((1, config.INPUT_START_DIM[0], config.INPUT_START_DIM[1], config.INPUT_START_DIM[2]), dtype=np.float32)

        numbers_output = {2: 1, 3: 2, 4: 3, 5: 4, 6: 5, 8: 5, 9: 4, 10: 3, 11: 2, 12: 1}

        # Resources outputs
        for number, tile in state.numbers:
            resource = state.tiles[tile]
            for vertex in config.tiles_vertex[tile]:
                nn_input[0, resource - 2, config.vertex_to_nn_input[vertex][0], config.vertex_to_nn_input[vertex][1]] += numbers_output[number] / 15.0

        # Ports
        for key, r in enumerate([config.SHEEP, config.ORE, config.BRICK, config.WHEAT, config.WOOD, config.GENERIC]):
            indices = [i for i, x in enumerate(state.ports) if x == r]
            for i in indices:
                for vertex in config.ports_vertex[i]['vert']:
                    nn_input[0, key + 5, config.vertex_to_nn_input[vertex][0], config.vertex_to_nn_input[vertex][1]] = 1
        
        # Settlements, cities, roads
        for p in range(4):
            p_order = (4 + p - perspective) % 4
            for s in state.players[p].settlements:
                nn_input[0, 11 + 2 * p_order, config.vertex_to_nn_input[s][0], config.vertex_to_nn_input[s][1]] = 1
            for r in state.players[p].roads:
                nn_input[0, 12 + 2 * p_order, config.vertex_to_nn_input[r[0]][0], config.vertex_to_nn_input[r[0]][1]] += 1 / 3.0
                nn_input[0, 12 + 2 * p_order, config.vertex_to_nn_input[r[1]][0], config.vertex_to_nn_input[r[1]][1]] += 1 / 3.0

        # Cards
        for p in range(4):
            p_order = (4 + p - perspective) % 4
            
            if p != self.player_id:
                min_cards = self.get_undetermined_resources_rivals(p)
                
                for key, r in enumerate([config.SHEEP, config.ORE, config.BRICK, config.WHEAT, config.WOOD]):
                    nn_input[0, 19 + key + 6 * p_order, :, :] = min_cards[key] / 10.0         
                    
            else:
                for key, r in enumerate([config.SHEEP, config.ORE, config.BRICK, config.WHEAT, config.WOOD]):
                    nn_input[0, 19 + key + 6 * p_order, :, :] = state.players[p].cards[r] / 10.0
                    
            nn_input[0, 24 + 6 * p_order, :, :] = state.players[p].total_cards() / 20.0
                
        # State
        if (state.game_phase == config.PHASE_INITIAL_SETTLEMENT or state.game_phase == config.PHASE_INITIAL_ROAD) and state.initial_phase_decrease == 0:
            nn_input[0, 43, :, :] = 1
        if (state.game_phase == config.PHASE_INITIAL_SETTLEMENT or state.game_phase == config.PHASE_INITIAL_ROAD) and state.initial_phase_decrease == 1:
            nn_input[0, 44, :, :] = 1

        # Player turn
        for p in range(4):
            p_order = (4 + p - perspective) % 4
            if p == state.player_turn:
                nn_input[0, 45 + p_order, :, :] = 1

        return nn_input

    def build_nn_input(self, state, perspective, determined = 0):
        if state.game_phase == config.PHASE_INITIAL_SETTLEMENT or state.game_phase == config.PHASE_INITIAL_ROAD:
            return self.build_start_nn_input(state, perspective)
        
        nn_input = np.zeros((1, config.INPUT_DIM[0], config.INPUT_DIM[1], config.INPUT_DIM[2]), dtype=np.float32)

        numbers_output = {2: 1, 3: 2, 4: 3, 5: 4, 6: 5, 8: 5, 9: 4, 10: 3, 11: 2, 12: 1}

        # Resources outputs
        for number, tile in state.numbers:
            resource = state.tiles[tile]
            for vertex in config.tiles_vertex[tile]:
                nn_input[0, resource - 2, config.vertex_to_nn_input[vertex][0], config.vertex_to_nn_input[vertex][1]] += numbers_output[number] / 15.0

        # Ports
        for key, r in enumerate([config.SHEEP, config.ORE, config.BRICK, config.WHEAT, config.WOOD, config.GENERIC]):
            indices = [i for i, x in enumerate(state.ports) if x == r]
            for i in indices:
                for vertex in config.ports_vertex[i]['vert']:
                    nn_input[0, key + 5, config.vertex_to_nn_input[vertex][0], config.vertex_to_nn_input[vertex][1]] = 1
        
        # Settlements, cities, roads
        for p in range(4):
            p_order = (4 + p - perspective) % 4
            for s in state.players[p].settlements:
                nn_input[0, 11 + 3 * p_order, config.vertex_to_nn_input[s][0], config.vertex_to_nn_input[s][1]] = 1
            for c in state.players[p].cities:
                nn_input[0, 12 + 3 * p_order, config.vertex_to_nn_input[c][0], config.vertex_to_nn_input[c][1]] = 1
            for r in state.players[p].roads:
                nn_input[0, 13 + 3 * p_order, config.vertex_to_nn_input[r[0]][0], config.vertex_to_nn_input[r[0]][1]] += 1 / 3.0
                nn_input[0, 13 + 3 * p_order, config.vertex_to_nn_input[r[1]][0], config.vertex_to_nn_input[r[1]][1]] += 1 / 3.0

        # Cards
        for p in range(4):
            p_order = (4 + p - perspective) % 4
            
            if determined == 0 and p != self.player_id:
                min_cards = self.get_undetermined_resources_rivals(p)
                
                for key, r in enumerate([config.SHEEP, config.ORE, config.BRICK, config.WHEAT, config.WOOD]):
                    nn_input[0, 23 + key + 6 * p_order, :, :] = min_cards[key] / 10.0         
                    
            else:
                for key, r in enumerate([config.SHEEP, config.ORE, config.BRICK, config.WHEAT, config.WOOD]):
                    nn_input[0, 23 + key + 6 * p_order, :, :] = state.players[p].cards[r] / 10.0
                    
            nn_input[0, 28 + 6 * p_order, :, :] = state.players[p].total_cards() / 20.0

        # Robber
        for vertex in config.tiles_vertex[state.robber_tile]:
            nn_input[0, 47, config.vertex_to_nn_input[vertex][0], config.vertex_to_nn_input[vertex][1]] = 1

        # Army Cards Played
        for p in range(4):
            p_order = (4 + p - perspective) % 4
            nn_input[0, 48 + p_order, :, :] = state.players[p].used_knights / 5.0

        # Army Holder
        for p in range(4):
            p_order = (4 + p - perspective) % 4
            nn_input[0, 52 + p_order, :, :] = state.players[p].largest_army_badge

        # Longest Road Holder
        for p in range(4):
            p_order = (4 + p - perspective) % 4
            nn_input[0, 56 + p_order, :, :] = state.players[p].longest_road_badge
            
        # Special Cards
        for p in range(4):
            p_order = (4 + p - perspective) % 4
            
            if determined == 1 or p == self.player_id:
                for key, r in enumerate([config.VICTORY_POINT, config.KNIGHT, config.MONOPOLY, config.ROAD_BUILDING, config.YEAR_OF_PLENTY]):
                    nn_input[0, 60 + key + 6 * p_order, :, :] = state.players[p].special_cards.count(r) / 3.0
                
            nn_input[0, 65 + 6 * p_order, :, :] = state.players[p].total_special_cards() / 3.0

        # Points
        for p in range(4):
            p_order = (4 + p - perspective) % 4
            nn_input[0, 84 + p_order, :, :] = state.players[p].points() / 10.0

        # Discarding, initial game phase
        if state.game_phase == config.PHASE_DISCARD:
            nn_input[0, 88, :, :] = 1

        # Player turn
        for p in range(4):
            p_order = (4 + p - perspective) % 4
            if p == state.player_turn:
                nn_input[0, 89 + p_order, :, :] = 1

        # Other game phases
        if state.game_phase == config.PHASE_THROW_DICE:
            nn_input[0, 93, :, :] = 1
        if state.game_phase == config.PHASE_MOVE_ROBBER:
            nn_input[0, 94, :, :] = 1
        if state.game_phase == config.PHASE_STEAL_CARD:
            nn_input[0, 95, :, :] = 1
        if state.game_phase == config.PHASE_ROAD_BUILDING:
            nn_input[0, 96, :, :] = 1
        if state.game_phase == config.PHASE_YEAR_OF_PLENTY:
            nn_input[0, 97, :, :] = 1
        if state.game_phase == config.PHASE_TRADE_RESPOND:
            nn_input[0, 98, :, :] = 1
            
        for s in range(54):
            if state.available_settlement_spot(s):
                nn_input[0, 99, config.vertex_to_nn_input[s][0], config.vertex_to_nn_input[s][1]] = 1

        return nn_input
    
    def predict(self, network):
        if network.shape[1] == config.INPUT_DIM[0]:
            return self.nn.predict(network)
        else:
            return self.nn_start.predict(network)
    
    def determinization(self, state):
        # Rivals cards
        for p in range(4):
            if p != self.player_id:
                if len(self.rivals_info[p]['cards']) > 0:
                    cards_set = choice(list(self.rivals_info[p]['cards']))
                else:
                    cards_set = (0,0,0,0,0)
                state.players[p].cards = {config.SHEEP: cards_set[0], 
                                          config.ORE: cards_set[1], 
                                          config.WHEAT: cards_set[2], 
                                          config.BRICK: cards_set[3], 
                                          config.WOOD: cards_set[4]}

        # Special Cards
        state.special_cards = deepcopy(config.special_cards_vector)
        for c in state.special_cards_played:
            try:
                state.special_cards.remove(c)
            except:
                raise Exception("c: " + str(c) + ", special_cards: " + str(state.special_cards))
        for c in state.players[self.player_id].special_cards:
            try:
                state.special_cards.remove(c)
            except:
                raise Exception("c: " + str(c) + ", special_cards: " + str(state.special_cards))

        shuffle(state.special_cards)

        for p in range(4):
            if p != self.player_id:
                for card in range(self.rivals_info[p]['special_cards']):
                    state.players[p].special_cards.append(state.special_cards.pop())

    def calc_posteriors(self, rootnode, rootstate):
        if rootstate.game_phase == config.PHASE_INITIAL_SETTLEMENT or rootstate.game_phase == config.PHASE_INITIAL_ROAD:
            posteriors = np.zeros(config.OUTPUT_START_DIM)
        else:
            posteriors = np.zeros(config.OUTPUT_DIM)

        for n in rootnode.childNodes:
            index_probs = rootnode.move_index(n.move, self.player_id)
            try:
                posteriors[index_probs] = n.N / self.itermax
            except:
                raise Exception(rootnode.ChildrenToString())

        return posteriors
    
    def move(self, rootstate):
        rootnode = Node(rootstate.get_player_moving())
        
        if len(rootnode.get_possible_moves(rootstate)) == 1:
            print (rootstate.get_player_moving())
            print (rootnode.possible_moves[0])
            return rootnode.possible_moves[0], 0, rootstate.get_player_moving()
        
        start_network = self.build_nn_input(rootstate, rootnode.current_player, determined = 0)
        start_prediction = self.predict(start_network)
        rootnode.add_probabilities(start_prediction[1][0])
        print(rootstate.get_player_moving())
        print(start_prediction[0])
        
        for i in range(self.itermax):
            valid_determinization = False
            
            while valid_determinization is False:
                node = rootnode
                state = deepcopy(rootstate)
                state.ai_rollout = 1

                # Determinization
                self.determinization(state)
                
                if state.game_phase != config.PHASE_END_GAME:
                    valid_determinization = True
            
            # Select
            node, expansion_nodes = self.select(state, node, (i / self.itermax) * (i / self.itermax))
            
            # Expand
            if expansion_nodes != []: # Otherwise this is a terminal Node
                node, prediction = self.expand(state, node, expansion_nodes)

            # Backpropagate
            last_node_player = node.current_player
            if state.game_phase == config.PHASE_END_GAME:
                expansion_result = np.zeros(4)
                for p in range(4):
                    p_order = (4 + p - last_node_player) % 4
                    expansion_result[p_order] = state.ai_get_result(p)
            else:
                expansion_result = [None, None, None, None]
                expansion_result[0] = prediction[0][0][0]
            while node != None: # backpropagate from the expanded node and work back to the root node
                p_order = (4 + node.current_player - last_node_player) % 4
                
                if expansion_result[p_order] is None:
                    network = self.build_nn_input(state, node.current_player, determined = 1)
                    prediction = self.predict(network)
                    expansion_result[p_order] = prediction[0][0][0]
                    
                node.update(expansion_result[p_order]) # state is terminal. Update node with result from POV of node.playerJustMoved
                node = node.parentNode
                
            if config.DETERMINISTIC_PLAY is True and i > self.itermax / 2.0:
                s_children = sorted(rootnode.childNodes, key = lambda c: c.N)
                
                if s_children[-1].N > s_children[-2].N + self.itermax - i:
                    move = s_children[-1].move
                    
                    print (rootnode.ChildrenToString())
                    posterior_probs = self.calc_posteriors(rootnode, rootstate)
                    
                    print ("Move selected: " + str(move))
                    return move, posterior_probs, rootstate.get_player_moving()
                
        print (rootnode.ChildrenToString())

        posterior_probs = self.calc_posteriors(rootnode, rootstate)
        
        if config.DETERMINISTIC_PLAY is True:
            move = sorted(rootnode.childNodes, key = lambda c: c.N)[-1].move
        else:
            move = np.random.choice(rootnode.childNodes, p = rootnode.get_child_probs()).move
        print ("Move selected: " + str(move))
        return move, posterior_probs, rootstate.get_player_moving()