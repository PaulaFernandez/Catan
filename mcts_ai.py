from math import sqrt, log
from copy import deepcopy
import random
import config
import pickle

class Node:
    """ A node in the game tree. Note wins is always from the viewpoint of player_turn.
        Crashes if state not specified.
    """
    def __init__(self, move = None, parent = None, state = None):
        self.move = move # the move that got us to this node - "None" for the root node
        self.parentNode = parent # "None" for the root node
        self.childNodes = []
        self.wins = 0
        self.visits = 0
        self.untriedMoves = state.ai_get_moves() # future child nodes
        self.player_turn = state.player_turn # the only part of the state that the Node needs later
        
    def UCTSelectChild(self):
        """ Use the UCB1 formula to select a child node. Often a constant UCTK is applied so we have
            lambda c: c.wins/c.visits + UCTK * sqrt(2*log(self.visits)/c.visits to vary the amount of
            exploration versus exploitation.
        """
        s = sorted(self.childNodes, key = lambda c: c.wins/c.visits + sqrt(2*log(self.visits)/c.visits))[-1]
        return s
    
    def AddChild(self, m, s):
        """ Remove m from untriedMoves and add a new child node for this move.
            Return the added child node
        """
        if m[0] == config.THROW_DICE:
            n = DiceNode(move = m, parent = self, state = s)
        else:
            n = Node(move = m, parent = self, state = s)
        self.untriedMoves.remove(m)
        self.childNodes.append(n)
        return n
    
    def Update(self, result):
        """ Update this node - one additional visit and result additional wins. result must be from the viewpoint of playerJustmoved.
        """
        self.visits += 1
        self.wins += result

    def __repr__(self):
        return "[M:" + str(self.move) + " W/V:" + str(self.wins) + "/" + str(self.visits) + " U:" + str(self.untriedMoves) + "]"

    def TreeToString(self, indent):
        s = self.IndentString(indent) + str(self)
        for c in self.childNodes:
             s += c.TreeToString(indent+1)
        return s

    def IndentString(self,indent):
        s = "\n"
        for i in range (1,indent+1):
            s += "| "
        return s

    def ChildrenToString(self):
        s = ""
        for c in self.childNodes:
             s += str(c) + "\n"
        return s

class DiceNode(Node):
    def __init__(self, move = None, parent = None, state = None):
        self.move = move # the move that got us to this node - "None" for the root node
        self.parentNode = parent # "None" for the root node
        self.childNodes = []
        self.wins = 0
        self.visits = 0
        self.untriedMoves = [] # future child nodes
        self.player_turn = state.player_turn # the only part of the state that the Node needs later

        if self.move == (3,):
            for i in range(2, 13):
                self.AddChild((config.THROW_DICE, i), state)

    def calculate_throw_dice(self):
        dice_1 = random.choice([1, 2, 3, 4, 5, 6])
        dice_2 = random.choice([1, 2, 3, 4, 5, 6])

        result = dice_1 + dice_2
        self.execute_dice_result(result)
        
    def UCTSelectChild(self):
        """ Use the UCB1 formula to select a child node. Often a constant UCTK is applied so we have
            lambda c: c.wins/c.visits + UCTK * sqrt(2*log(self.visits)/c.visits to vary the amount of
            exploration versus exploitation.
        """
        dice_result = self.calculate_throw_dice()
        for s in self.childNodes:
            if s.move == (config.THROW_DICE, dice_result):
                return s

        raise Exception("Node not found")


class MCTS_AI:
    def __init__(self, itermax):
        self.itermax = itermax

    def move(self, rootstate, verbose = False):
        rootnode = Node(state = rootstate)

        for i in range(self.itermax):
            node = rootnode
            state = deepcopy(rootstate)

            # Select
            while node.untriedMoves == [] and node.childNodes != []: # node is fully expanded and non-terminal
                node = node.UCTSelectChild()
                state.ai_do_move(node.move)

            # Expand
            if node.untriedMoves != []: # if we can expand (i.e. state/node is non-terminal)
                m = random.choice(node.untriedMoves) 
                state.ai_do_move(m)
                node = node.AddChild(m,state) # add child and descend tree

            # Rollout - this can often be made orders of magnitude quicker using a state.GetRandomMove() function
            moves = state.ai_get_moves()
            m = 0
            while moves != []: # while state is non-terminal
                state.ai_do_move(random.choice(moves))
                moves = state.ai_get_moves()
                m += 1

            #with open('train_set\\' + str(state.uuid) + '_' + str(i), 'wb') as output:
            #    pickle.dump(state, output, -1)

            # Backpropagate
            while node != None: # backpropagate from the expanded node and work back to the root node
                node.Update(state.ai_get_result(node.player_turn)) # state is terminal. Update node with result from POV of node.playerJustMoved
                node = node.parentNode

        # Output some information about the tree - can be omitted
        if (verbose): 
            print (rootnode.TreeToString(0))
        else: 
            print (rootnode.ChildrenToString())

        return sorted(rootnode.childNodes, key = lambda c: c.visits)[-1].move # return the move that was most visited