from math import sqrt, log
from copy import deepcopy
import random
import config
import pickle

class Node:
    """ A node in the game tree. Note wins is always from the viewpoint of player_turn.
        Crashes if state not specified.
    """
    def __init__(self, player, parent = None, move = None):
        self.current_player = player
        self.parentNode = parent # "None" for the root node
        self.move = move
        self.childNodes = []
        self.child_moves = []
        self.possible_moves = []
        self.is_random = False
        self.wins = 0
        self.visits = 0
        self.available = 0
        
    def UCTSelectChild(self):
        potential_moves = []
        
        for m in self.possible_moves:
            n = self.childNodes[self.child_moves.index(m)]
            n.available += 1
            potential_moves.append(n)
        
        s = sorted(potential_moves, key = lambda c: c.wins/c.visits + sqrt(2*log(c.available)/c.visits))[-1]
        return s
    
    def update(self, result):
        self.visits += 1
        self.wins += result
        
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
        if move[0] == config.THROW_DICE:
            n = Dice_Node(player, self)
        else:
            n = Node(player, self, move)
        self.childNodes.append(n)
        self.child_moves.append(move)
        return n

    def ChildrenToString(self):
        s = ""
        for c in self.childNodes:
             s += str(c) + "\n"
        return s

    def __repr__(self):
        return "[M:" + str(self.move) + " W/V:" + str(self.wins) + "/" + str(self.visits) + "]"

class Dice_Node(Node):
    def __init__(self, player, parent = None):
        Node.__init__(self, player, parent, (config.THROW_DICE,))
        self.possible_moves = [(config.THROW_DICE, x) for x in range(2, 13)]
        self.is_random = True
        
    def get_possible_moves(self, state):
        return self.possible_moves

    def calculate_throw_dice(self):
        dice_1 = random.choice([1, 2, 3, 4, 5, 6])
        dice_2 = random.choice([1, 2, 3, 4, 5, 6])

        return (dice_1 + dice_2)
    
    def roll(self):
        dice_result = self.calculate_throw_dice()
        
        if ((config.THROW_DICE, dice_result) in self.child_moves):
            idx = self.child_moves.index((config.THROW_DICE, dice_result))
            return self.childNodes[idx]
        else:
            node = self.add_child((config.THROW_DICE, dice_result))
            return node
            
    def add_child(self, move):
        node = Node(self.current_player, self, move)
        self.childNodes.append(node)
        self.child_moves.append(move)
        return node

class MCTS_AI:
    def __init__(self, itermax):
        self.itermax = itermax
        
    def select(self, state, node):
        while 1:
            if node.is_random:
                node = node.roll()
                state.ai_do_move(node.move)
            else:
                expansion_nodes = node.check_untried(state)
                if expansion_nodes != [] or (expansion_nodes == [] and node.childNodes == []):
                    return node, expansion_nodes
                else:
                    node = node.UCTSelectChild()
                    if node.move[0] != config.THROW_DICE:
                        state.ai_do_move(node.move)
                    
    def expand(self, state, node, possible_expansions):    
        m = random.choice(possible_expansions) 
        current_player = state.player_turn
        if m[0] != config.THROW_DICE:
            state.ai_do_move(m)
        node = node.add_child(current_player, m) # add child and descend tree
        
        return node
    
    def move(self, rootstate):
        rootnode = Node(rootstate.player_turn)
        
        if len(rootnode.get_possible_moves(rootstate)) == 1:
            return rootnode.possible_moves[0]
        
        for i in range(self.itermax):
            # TODO: Determinization in the future
            
            node = rootnode
            state = deepcopy(rootstate)
            
            # Select
            node, expansion_nodes = self.select(state, node)
            
            # Expand
            if expansion_nodes != []: # Otherwise this is a terminal Node
                node = self.expand(state, node, expansion_nodes)
                
            # Rollout
            moves = state.ai_get_moves()
            m = 0
            while moves != [] and m < 3000: # while state is non-terminal
                state.ai_do_move(random.choice(moves))
                moves = state.ai_get_moves()
                m += 1

            # Backpropagate
            while node != None: # backpropagate from the expanded node and work back to the root node
                node.update(state.ai_get_result(node.current_player)) # state is terminal. Update node with result from POV of node.playerJustMoved
                node = node.parentNode
                
        print (rootstate.player_turn)
        print (rootnode.ChildrenToString())
        
        return sorted(rootnode.childNodes, key = lambda c: c.visits)[-1].move