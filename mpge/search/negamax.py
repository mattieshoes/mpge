#!/usr/bin/python3

import mpge
import time

# Brute force, full width search

class Negamax(mpge.Search):

    def __init__(self, board: mpge.Board):
        self.board = board
        self.pv = [[] for i in range(self.max_depth * 2)]
        self.nodes = 0
        self.leaves = 0

    def negamax(self, depth, ply):
        self.nodes += 1
        # run quiescence search at leaves
        if depth == 0:
            self.leaves += 1
            return self.quiescence(ply)

        current_side = self.board.side_to_move()
        # iterative recursive search
        value = -self.infinity
        move_list = self.board.gen_moves()
        for move in move_list:
            if self.board.make_move(move):
                if self.board.side_to_move() == current_side:
                    result = self.negamax(depth, ply+1)
                else:
                    result = -self.negamax(depth - 1,  ply + 1)
                # if we found a new best, update the value of the node
                # and update the principle variation that got us there
                if result > value:
                    value = result
                    self.pv[ply] = [move] + self.pv[ply+1]
                self.board.undo_move()
        
        # if no valid moves found, check for game end
        if value == -self.infinity:
            w = self.board.winner()
            if w: # game is ended
                self.pv[ply] = []
                self.leaves += 1
                if w == 3: # game ended in draw
                    return 0
                elif w == self.board.side: # we won
                    return self.infinity - ply
                else: # we lost
                    return -self.infinity + ply

        # return best value found
        return value

    def quiescence(self, ply):
        # default value is if we do nothing
        value = self.board.evaluate(ply=ply)
        current_side = self.board.side_to_move()
        # recursive quiescence search
        move_list = self.board.gen_quiescence_moves()
        for move in move_list:
            if self.board.make_move(move):
                if self.board.side_to_move() == current_side:
                    result = self.quiescence(ply+1)
                else:
                    result = -self.quiescence(ply + 1)
                if result > value:
                    value = result
                    pv[ply] = [move] + pv[ply+1]
                self.board.undo_move()
        return value

    def search(self):
        if self.board.winner():
            return
        start = time.time()
        self.nodes = 0
        self.pv = [[] for i in range(self.max_depth * 2)]
        for depth in range(1, self.max_depth + 1):
            self.leaves = 0
            value = self.negamax(depth, 0)
            end = time.time()
            print(f"Depth {depth}, Score {value}, "
                  f"time {round(end-start, 2)}, "
                  f"nodes {self.nodes} ({int(round(self.nodes/(end-start))):,} nps), "
                  f"BF {round(self.leaves**(1/depth), 1)}")
            print(f"\tPV: {self.pv[0]}")
            if self.max_time and (end - start) > self.max_time:
                break
            if value > 999000 or value < -999000:
                break
        print(f"Move: {self.pv[0][0]}")
        self.board.make_move(self.pv[0][0])
