#!/usr/bin/python3

# Contains the mpge interfaces
# games should inherit from these classes so that searches behave properly

# a description of a move.  should be able to stringify and test for equality
class Move:
    score = 0
    def __str__(self):
        pass
    def __repr__(self):
        pass
    def __eq__(self, other):
        pass

# Board representation class
#
# legality checking of moves lives in make_move()
# this is to delay potentially costly legality checking 
# during move generation (e.g. moving into check)
# This is because not all generated moves may be checked
class Board:

    # you need to generate hashes for positions if you use a 
    # search algorithm with hashing
    hash_key = 0

    # should reset to a new game
    def new_game(self):
        pass
    # Should do legality checking of the move and return True/False
    def make_move(self, m: Move) -> bool:
        pass

    # reset board state to before the most recent move
    # no-op at game start
    def undo_move(self):
        pass

    # should generate all pseudo-legal moves (make_move checks legality)
    # should score moves based on their likelihood of being the best move
    # This is because alpha beta search algorithms perform better if 
    # more likely moves are considered first.  
    def gen_moves(self, ply=0, depth=0) -> list:
        pass

    # should generate all "significant" moves for quiescence search
    # candidates in chess would be captures, promotions, giving check
    # this is to minimize horizon effects, where for instance
    # a capture happens at a leaf node ignoring the immediate recapture
    def gen_quiescence_moves(self, ply=0) -> list:
        pass

    # should return 0 when the game is not over
    # should return 1 for player 1 winning
    # should return 2 for player 2 winning
    def winner(self) -> int:
        pass

    # should return 1 (player 1) or 2 (player 2)
    def side_to_move(self) -> int:
        pass

    # should return a static evaluation score relative to the side to move
    # ie. positive numbers mean the side to move is winning
    def evaluate(self) -> int:
        pass

    # Should attempt to turn the move_string into a valid move
    def parse_move(self, move_string):
        pass

    # Search will call this to let the board know a refutation move has 
    # been found at a given depth.  
    def heuristic_fail_high(self, move, depth):
        pass

    # Search will call this to let the board know the last principle variation
    # so that the board may order 
    def heuristic_last_pv(self, move_list):
        pass
    
    # Lets the board know to reset heuristics used in move ordering.  It's called
    # after the search engine makes a real move in the game
    def heuristic_reset(self):
        pass
    def history_string(self):
        return '\n'

class Search:

    max_depth = 64
    max_time = 5
    infinity = 1000000

    def __init__(self, board: Board):
        self.board = Board

    def search(self):
        pass
