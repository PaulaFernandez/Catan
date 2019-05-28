from math import sqrt
from copy import copy, deepcopy
from random import shuffle, choice
import config
import numpy as np
import pickle

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
        self.deteministic_play = config.DETERMINISTIC_PLAY
        self.agent = agent

        for p in range(4):
            if p != self.player_id:
                self.rivals_info[p] = {'cards': set([(0, 0, 0, 0, 0)]),
                                       'special_cards': [[], []]}

    def __deepcopy__(self, memo):
        cls = self.__class__
        result = cls.__new__(cls)
        memo[id(self)] = result
        for k, v in self.__dict__.items():
            if k not in ["agent", "rootnode"]:
                setattr(result, k, deepcopy(v, memo))
        return result
    
    def descend_tree(self, move):
        if self.rootnode is not None:
            for n in self.rootnode.childNodes:
                if n.move == move:
                    self.rootnode = n
                    self.rootnode.parentNode = None
                    return
                
        self.rootnode = None
        
    def remove_tree(self):
        self.rootnode = None
        
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
        
    def special_cards_probability(self, state):
        all_special_cards = config.special_cards_vector[:]
        for c in state.special_cards_played:
            all_special_cards.remove(c)
        
        remaining_count = np.array([0, 0, 0, 0, 0])
        for c in config.special_cards.keys():
            remaining_count[c] = all_special_cards.count(c)
            
        return remaining_count / np.sum(remaining_count)
        
    def normalize_probs(self, vector):
        vector = np.array(vector)
        return vector / np.sum(vector)
            
    def add_special_card_rival(self, player_id, state):
        probabilities = self.special_cards_probability(state)
        
        if len(self.rivals_info[player_id]['special_cards'][0]) == 0:
            self.rivals_info[player_id]['special_cards'] = [[[x] for x in range(5)], probabilities]
            return
        
        new_sp_cards = [[], []]
        for i in range(len(self.rivals_info[player_id]['special_cards'][0])):
            for c, p in enumerate(probabilities):
                if p > 0.0:
                    cards_sample = self.rivals_info[player_id]['special_cards'][0][i] + [c]
                    cards_sample.sort()
                    try:
                        idx_sample = new_sp_cards[0].index(cards_sample)
                        new_sp_cards[1][idx_sample] = new_sp_cards[1][idx_sample] + p * self.rivals_info[player_id]['special_cards'][1][i]
                    except:
                        new_sp_cards[0].append(cards_sample)
                        new_sp_cards[1].append(p * self.rivals_info[player_id]['special_cards'][1][i])
                    
        self.rivals_info[player_id]['special_cards'] = new_sp_cards
            
    def remove_special_card_rival(self, player_id, card):
        if len(self.rivals_info[player_id]['special_cards'][0]) > 0 and len(self.rivals_info[player_id]['special_cards'][0][0]) == 1:
            self.rivals_info[player_id]['special_cards'] = [[], []]
            return
        
        new_sp_cards = [[], []]
        for i in range(len(self.rivals_info[player_id]['special_cards'][0])):
            if card in self.rivals_info[player_id]['special_cards'][0][i]:
                cards_sample = self.rivals_info[player_id]['special_cards'][0][i]
                cards_sample.remove(card)
                try:
                    idx_sample = new_sp_cards[0].index(cards_sample)
                    new_sp_cards[1][idx_sample] = new_sp_cards[1][idx_sample] + self.rivals_info[player_id]['special_cards'][1][i]
                except:
                    new_sp_cards[0].append(cards_sample) 
                    new_sp_cards[1].append(self.rivals_info[player_id]['special_cards'][1][i])
                
        probs = self.normalize_probs(new_sp_cards[1])
        new_sp_cards[1] = probs
        
        self.rivals_info[player_id]['special_cards'] = new_sp_cards     
    
    def select(self, state, node, weight):
        while 1:
            if node.is_random:
                node, evaluate = node.roll(state)
                state.ai_do_move(node.move)

                if evaluate == True:
                    prediction = self.agent.predict(state, node.current_player, self)
                    
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

        prediction = self.agent.predict(state, node.current_player, self)
        node.add_probabilities(prediction[1][0])

        if node.is_random:
            node, evaluate = node.roll(state)
            state.ai_do_move(node.move)

            if evaluate == True:
                prediction = self.agent.predict(state, node.current_player, self)
                node.add_probabilities(prediction[1][0])

        return node, prediction
        
    def expansion_possibilities(self, state, node):
        expansion_nodes = node.check_untried(state)
        return expansion_nodes    
    
    def decrease_probs_special_card(self, card):
        for p in range(4):
            if p != self.player_id:
                for i, card_set in enumerate(self.rivals_info[p]['special_cards'][0]):
                    if card in card_set:
                        self.rivals_info[p]['special_cards'][1][i] = (1 - 0.1 * card_set.count(card)) * self.rivals_info[p]['special_cards'][1][i]
                        
                probs = self.normalize_probs(self.rivals_info[p]['special_cards'][1])
                
                self.rivals_info[p]['special_cards'][1] = probs  
    
    def determinization(self, state, relax = 0):
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
        state.special_cards = config.special_cards_vector[:]
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

        if relax == 0:
            for p in range(4):
                if p != self.player_id:
                    if len(self.rivals_info[p]['special_cards'][0]) > 0:
                        cards_idx = np.random.choice(range(len(self.rivals_info[p]['special_cards'][0])), p = self.rivals_info[p]['special_cards'][1])
                        cards_realization = self.rivals_info[p]['special_cards'][0][cards_idx]
                        state.players[p].special_cards = []
                        for c in cards_realization:
                            state.players[p].special_cards.append(c)
                            try:
                                state.special_cards.remove(c)
                            except:
                                self.decrease_probs_special_card(c)
                                return False
    
            shuffle(state.special_cards)
            
        else:
            shuffle(state.special_cards)
            
            for p in range(4):
                if p != self.player_id:
                    state.players[p].special_cards = []
                    if len(self.rivals_info[p]['special_cards'][0]) > 0:
                        for _ in range(len(self.rivals_info[p]['special_cards'][0][0])):
                            state.players[p].special_cards.append(state.special_cards.pop())
            
        return True

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
        iterations_done = 0
        
        if rootstate.moves >= config.DETEMINISTIC_MOVES_THRESHOLD:
            self.deteministic_play = True
        
        if self.rootnode is None:
            self.rootnode = Node(rootstate.get_player_moving())
        else:
            iterations_done = int(self.rootnode.N / config.EXPANSION_STEPS) 
            self.rootnode.current_player = rootstate.get_player_moving()
        
        if len(self.rootnode.get_possible_moves(rootstate)) == 1:
            print (rootstate.get_player_moving())
            print (self.rootnode.possible_moves[0])
            return self.rootnode.possible_moves[0], 0, rootstate.get_player_moving()
        
        start_prediction = self.agent.predict(rootstate, self.rootnode.current_player, self)
        self.rootnode.add_probabilities(start_prediction[1][0])
        print(rootstate.get_player_moving())
        print(start_prediction[0])
        
        for i in range(iterations_done - 1, self.itermax):
            valid_determinization = False
            
            num_determ = 0
            relax_det = 0
            while valid_determinization is False:
                node = self.rootnode
                state = copy(rootstate)
                state.ai_rollout = 1

                # Determinization
                success = self.determinization(state, relax = relax_det)
                state.check_end_game()
                
                if success:
                    valid_determinization = True                    
                    if state.game_phase == config.PHASE_END_GAME:
                        valid_determinization = False
                        self.decrease_probs_special_card(0)
                        
                num_determ += 1
                if num_determ > 10:
                    relax_det = 1
            
            # Select
            node, expansion_nodes = self.select(state, node, (i / self.itermax) * (i / self.itermax))
            
            for j in range(config.EXPANSION_STEPS):
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
                    
                backprop_node = node
                while backprop_node != None: # backpropagate from the expanded node and work back to the root node
                    p_order = (4 + backprop_node.current_player - last_node_player) % 4
                    
                    if expansion_result[p_order] is None:
                        prediction = self.agent.predict(state, backprop_node.current_player, self)
                        expansion_result[p_order] = prediction[0][0][0]
                        
                    backprop_node.update(expansion_result[p_order]) # state is terminal. Update node with result from POV of node.playerJustMoved
                    backprop_node = backprop_node.parentNode
                    
                expansion_nodes = self.expansion_possibilities(state, node)
                
                if expansion_nodes == []: # It was a terminal node
                    break
                
            if self.deteministic_play is True and i > self.itermax / 2.0:
                s_children = sorted(self.rootnode.childNodes, key = lambda c: c.N)
                
                if len(s_children) < 2 or s_children[-1].N > s_children[-2].N + config.EXPANSION_STEPS * (self.itermax - i):
                    move = s_children[-1].move
                    
                    print (self.rootnode.ChildrenToString())
                    posterior_probs = self.calc_posteriors(self.rootnode, rootstate)
                    
                    print ("Move selected: " + str(move))
                    return move, posterior_probs, rootstate.get_player_moving()
                
        print (self.rootnode.ChildrenToString())

        posterior_probs = self.calc_posteriors(self.rootnode, rootstate)
        
        if self.deteministic_play is True:
            move = sorted(self.rootnode.childNodes, key = lambda c: c.N)[-1].move
        else:
            move = np.random.choice(self.rootnode.childNodes, p = self.rootnode.get_child_probs()).move
        print ("Move selected: " + str(move))
        return move, posterior_probs, rootstate.get_player_moving()