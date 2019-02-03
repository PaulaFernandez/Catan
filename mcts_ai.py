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

    def move_index(self, move):
        if move[0] != config.STEAL_FROM_HOUSE:
            return config.available_moves.index(move)
        else:
            p_order = (4 + move[1][1] - self.current_player) % 4
            return config.available_moves.index((move[0], (move[1][0], p_order)))
        
    def add_probabilities(self, probs):
        self.move_probabilities = probs
        
    def UCTSelectChild(self):
        potential_moves = []
        
        for m in self.possible_moves:
            n = self.childNodes[self.child_moves.index(m)]
            potential_moves.append(n)
        
        s = sorted(potential_moves, key = lambda c: c.Q + 0.2 * c.prior_probabilities * sqrt(self.N / (1 + c.N)))[-1]
        return s
    
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
        index_probs = self.move_index(move)
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
        return "[M:" + str(self.move) + " Q/N:" + str(self.Q) + "/" + str(self.N) + "]"

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
    def __init__(self, player_id, itermax):
        self.itermax = itermax
        self.player_id = player_id
        self.rivals_info = {}

        self.nn = Residual_CNN(config.REG_CONST, config.LEARNING_RATE, config.INPUT_DIM, config.OUTPUT_DIM, config.HIDDEN_CNN_LAYERS)
        self.nn.read(1)

        for p in range(4):
            if p != self.player_id:
                self.rivals_info[p] = {'cards': set(),
                                       'special_cards': 0}
        
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
        for cards in self.rivals_info[player_id]['cards']:
            for c in range(2, 7):
                if cards[c - 2] >= 1:
                    cards_x = list(cards)
                    cards_x[c - 2] -= 1
                    cards_x = tuple(cards_x)
                    new_set.add(cards_x)
        self.rivals_info[player_id]['cards'] = new_set

    def add_unknown_resource_rival(self, player_id):
        new_set = set()
        for cards in self.rivals_info[player_id]['cards']:
            for c in range(2, 7):
                cards_x = list(cards)
                cards_x[c - 2] += 1
                cards_x = tuple(cards_x)
                new_set.add(cards_x)
        self.rivals_info[player_id]['cards'] = new_set
            
    def add_special_card_rival(self, player_id):
        self.rivals_info[player_id]['special_cards'] += 1
            
    def remove_special_card_rival(self, player_id):
        self.rivals_info[player_id]['special_cards'] -= 1
    
    def select(self, state, node):
        while 1:
            if node.is_random:
                node, evaluate = node.roll(state)
                state.ai_do_move(node.move)

                if evaluate == True:
                    network = self.build_nn_input(state, determined = 1)
                    prediction = self.nn.predict(network)
                    
                    node.add_probabilities(prediction[1][0])
            else:
                expansion_nodes = node.check_untried(state)
                if expansion_nodes != [] or (expansion_nodes == [] and node.childNodes == []):
                    return node, expansion_nodes
                else:
                    node = node.UCTSelectChild()
                    if node.move[0] != config.THROW_DICE and node.move[0] != config.BUY_SPECIAL_CARD and node.move[0] != config.STEAL_FROM_HOUSE:
                        state.ai_do_move(node.move)
                    
    def expand(self, state, node, possible_expansions):
        m = choice(possible_expansions) 
        current_player = state.get_player_moving()
        if m[0] != config.THROW_DICE and m[0] != config.BUY_SPECIAL_CARD and m[0] != config.STEAL_FROM_HOUSE:
            state.ai_do_move(m)
        node = node.add_child(current_player, m) # add child and descend tree

        network = self.build_nn_input(state, determined = 1)
        prediction = self.nn.predict(network)
        
        node.add_probabilities(prediction[1][0])

        if node.is_random:
            node, evaluate = node.roll(state)
            state.ai_do_move(node.move)

            if evaluate == True:
                network = self.build_nn_input(state, determined = 1)
                prediction = self.nn.predict(network)
                
                node.add_probabilities(prediction[1][0])

        return node, prediction

    def build_nn_input(self, state, determined = 0):
        nn_input = np.zeros((1, 70, 6, 11), dtype=np.float32)

        # Resources
        for key, r in enumerate([config.SHEEP, config.ORE, config.BRICK, config.WHEAT, config.WOOD]):
            indices = [i for i, x in enumerate(state.tiles) if x == r]
            for i in indices:
                for vertex in config.tiles_vertex[i]:
                    nn_input[0, key, config.vertex_to_nn_input[vertex][0], config.vertex_to_nn_input[vertex][1]] += 1
        
        # Numbers
        for number, tile in state.numbers:
            for vertex in config.tiles_vertex[tile]:
                nn_input[0, number + 3, config.vertex_to_nn_input[vertex][0], config.vertex_to_nn_input[vertex][1]] += 1

        # Ports
        for key, r in enumerate([config.SHEEP, config.ORE, config.BRICK, config.WHEAT, config.WOOD, config.GENERIC]):
            indices = [i for i, x in enumerate(state.ports) if x == r]
            for i in indices:
                for vertex in config.ports_vertex[i]['vert']:
                    nn_input[0, key + 16, config.vertex_to_nn_input[vertex][0], config.vertex_to_nn_input[vertex][1]] = 1
        
        # Settlements, cities, roads
        for p in range(4):
            p_order = (4 + p - state.get_player_moving()) % 4
            for s in state.players[p].settlements:
                nn_input[0, 22 + 3 * p_order, config.vertex_to_nn_input[s][0], config.vertex_to_nn_input[s][1]] = 1
            for c in state.players[p].cities:
                nn_input[0, 23 + 3 * p_order, config.vertex_to_nn_input[c][0], config.vertex_to_nn_input[c][1]] = 1
            for r in state.players[p].roads:
                nn_input[0, 24 + 3 * p_order, config.vertex_to_nn_input[r[0]][0], config.vertex_to_nn_input[r[0]][1]] = 1
                nn_input[0, 24 + 3 * p_order, config.vertex_to_nn_input[r[1]][0], config.vertex_to_nn_input[r[1]][1]] = 1

        # Own Cards
        for key, r in enumerate([config.SHEEP, config.ORE, config.BRICK, config.WHEAT, config.WOOD]):
            nn_input[0, 34 + key, :, :] = state.players[state.get_player_moving()].cards[r]

        # Rival Cards
        for p in range(4):
            p_order = (4 + p - state.get_player_moving()) % 4

            if p_order > 0:
                if determined == 0:
                    if p == self.player_id:
                        nn_input[0, 38 + p_order, :, :] = state.players[p].total_cards()
                    elif len(self.rivals_info[p]['cards']) > 0:
                        sample_set = sample(self.rivals_info[p]['cards'], 1)
                        nn_input[0, 38 + p_order, :, :] = sum(sample_set[0])
                else:
                    nn_input[0, 38 + p_order, :, :] = state.players[p].total_cards()

        # Robber
        for vertex in config.tiles_vertex[state.robber_tile]:
            nn_input[0, 42, config.vertex_to_nn_input[vertex][0], config.vertex_to_nn_input[vertex][1]] = 1

        # Army Cards Played
        for p in range(4):
            p_order = (4 + p - state.get_player_moving()) % 4
            nn_input[0, 43 + p_order, :, :] = state.players[p].used_knights

        # Army Holder
        for p in range(4):
            p_order = (4 + p - state.get_player_moving()) % 4
            nn_input[0, 47 + p_order, :, :] = state.players[p].largest_army_badge

        # Longest Road Holder
        for p in range(4):
            p_order = (4 + p - state.get_player_moving()) % 4
            nn_input[0, 51 + p_order, :, :] = state.players[p].longest_road_badge

        # Own Special Cards
        for key, r in enumerate([config.VICTORY_POINT, config.KNIGHT, config.MONOPOLY, config.ROAD_BUILDING, config.YEAR_OF_PLENTY]):
            nn_input[0, 55 + key, :, :] = state.players[state.get_player_moving()].special_cards.count(r)

        # Rival Special Cards
        for p in range(4):
            p_order = (4 + p - state.get_player_moving()) % 4

            if p_order > 0:
                if determined == 0:
                    if p == self.player_id:
                        nn_input[0, 59 + p_order, :, :] = state.players[p].total_special_cards()
                    else:
                        nn_input[0, 59 + p_order, :, :] = self.rivals_info[p]['special_cards']
                else:
                    nn_input[0, 59 + p_order, :, :] = state.players[state.get_player_moving()].total_special_cards()

        # Points
        for p in range(4):
            p_order = (4 + p - state.get_player_moving()) % 4
            nn_input[0, 63 + p_order, :, :] = state.players[p].points()

        # Discarding, initial game phase
        if state.game_phase == config.PHASE_DISCARD:
            nn_input[0, 67, :, :] = 1
        if (state.game_phase == config.PHASE_INITIAL_SETTLEMENT or state.game_phase == config.PHASE_INITIAL_ROAD) and state.initial_phase_decrease == 0:
            nn_input[0, 68, :, :] = 1
        if (state.game_phase == config.PHASE_INITIAL_SETTLEMENT or state.game_phase == config.PHASE_INITIAL_ROAD) and state.initial_phase_decrease == 1:
            nn_input[0, 69, :, :] = 1

        return nn_input
    
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
        state.special_cards = config.special_cards_vector
        for c in state.special_cards_played:
            try:
                state.special_cards.pop(c)
            except:
                raise Exception("c: " + str(c) + ", special_cards: " + str(state.special_cards))
        for c in state.players[self.player_id].special_cards:
            try:
                state.special_cards.pop(c)
            except:
                raise Exception("c: " + str(c) + ", special_cards: " + str(state.special_cards))

        shuffle(state.special_cards)

        for p in range(4):
            if p != self.player_id:
                for card in range(self.rivals_info[p]['special_cards']):
                    self.players[p].special_cards.append(self.special_cards.pop())

    def calc_posteriors(self, rootnode):
        posteriors = np.zeros(config.OUTPUT_DIM)

        for n in rootnode.childNodes:
            index_probs = n.move_index(n.move)
            posteriors[index_probs] = n.N / self.itermax

        return posteriors
    
    def move(self, rootstate):
        rootnode = Node(rootstate.get_player_moving())
        
        if len(rootnode.get_possible_moves(rootstate)) == 1:
            print (rootstate.get_player_moving())
            print (rootnode.possible_moves[0])
            return rootnode.possible_moves[0], 0, 0, -1
        
        start_network = self.build_nn_input(rootstate, determined = 0)
        start_prediction = self.nn.predict(start_network)
        rootnode.add_probabilities(start_prediction[1][0])
        print(rootstate.get_player_moving())
        print(start_prediction[0])
        
        for i in range(self.itermax):            
            node = rootnode
            state = deepcopy(rootstate)
            state.ai_rollout = 1

            # Determinization
            self.determinization(state)
            
            # Select
            node, expansion_nodes = self.select(state, node)
            
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
                expansion_result = prediction[0][0]
            while node != None: # backpropagate from the expanded node and work back to the root node
                p_order = (4 + node.current_player - last_node_player) % 4
                node.update(expansion_result[p_order]) # state is terminal. Update node with result from POV of node.playerJustMoved
                node = node.parentNode
                
        print (rootnode.ChildrenToString())

        posterior_probs = self.calc_posteriors(rootnode)
        
        return sorted(rootnode.childNodes, key = lambda c: c.N)[-1].move, posterior_probs, start_network, rootstate.get_player_moving()