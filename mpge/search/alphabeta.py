#!/usr/bin/python3

import mpge, time

# alpha beta search.  alpha is the floor, beta the ceiling
# opponent's ceiling is our floor, and their floor our ceiling
# signs are reversed because this gives a score relative to the side to move
#
# scores > beta cause a cutoff -- essentially, the move in question is so 
# good that the opponent won't play the preceding move, refuting whole sections
# of the search tree.  This allows one to arrive at the same answer as a full
# search with less searching.
#
# fail soft means we can return scores outside of the range of alpha to beta 
#
# Move ordering (searching the best move first) makes alpha beta algorithms
# more efficient -- it raises our alpha, which lowers the opponent's beta.
# this allows for more moves to trigger beta cutoffs and shed more of the 
# search tree.  We don't know the best move before doing the search, but
# we can make some heuristic guesses 
# (e.g. capturing unprotected pieces in chess)


class AlphaBeta(mpge.Search):

    def __init__(self, board: mpge.Board):
        self.board = board
        self.pv = [[] for i in range(self.max_depth * 2)]
        self.nodes = 0
        self.leaves = 0

    def AlphaBeta(self, alpha, beta, depth, ply):
        if depth == 0:
            self.leaves += 1
            return self.quiescence(alpha, beta, ply)
        current_side = self.board.side_to_move() 
        self.nodes += 1
        move_found = False 
        move_list = self.board.gen_moves(ply, depth)
        move_list.sort(key = lambda x: x.score, reverse = True) 
        for move in move_list:
            if self.board.make_move(move):
                move_found = True
                if current_side == self.board.side_to_move():
                    score = self.AlphaBeta(alpha, beta, depth, ply + 1)
                else:
                    score = -self.AlphaBeta(-beta, -alpha, depth - 1,  ply + 1)
                self.board.undo_move()
                if score > alpha:
                    if score >= beta: # cutoff!
                        self.board.heuristic_fail_high(move, ply, depth)
                        return score
                    alpha = score
                    self.pv[ply] = [move] + self.pv[ply + 1]
        
        # if no valid moves found, check for game end
        if not move_found:
            w = self.board.winner()
            if w: # game is ended
                #self.pv[ply] = []
                self.leaves += 1
                if w == 3: # game ended in draw
                    return 0
                elif w == self.board.side: # we won
                    return self.infinity - ply
                else: # we lost
                    return -self.infinity + ply

        # return best value found
        return alpha

    def quiescence(self, alpha, beta, ply):
        self.nodes += 1
        current_score = self.board.evaluate(ply=ply)
        if current_score > alpha:
            if current_score > beta:
                return current_score
            alpha = current_score
            self.pv[ply] = []

        current_side = self.board.side_to_move()

        move_list = self.board.gen_quiescence_moves(ply)
        move_list.sort(key = lambda x: x.score, reverse = True)
        for move in move_list:
            if self.board.make_move(move):
                if current_side == self.board.side_to_move():
                    score = self.quiescence(alpha, beta, ply+1)
                else:
                    score = -self.quiescence(-beta, -alpha, ply + 1)
                self.board.undo_move()
                if score > alpha:
                    if score >= beta: # cutoff!
                        self.board.heuristic_fail_high(move, ply, 0)
                        return score
                    alpha = score
                    pv[ply] = [move] + pv[ply+1]
        return alpha

    def search(self):
        if self.board.winner():
            return
        start = time.time()
        self.nodes = 0
        self.board.heuristic_reset()
        for depth in range(1, self.max_depth + 1):
            self.leaves = 0
            value = self.AlphaBeta(-self.infinity, self.infinity, depth, 0)
            end = time.time()
            print(f"Depth {depth}, Score {value}, "
                  f"time {round(end-start, 2)}, "
                  f"nodes {self.nodes} ({int(round(self.nodes/(end-start))):,} nps), "
                  f"BF {round(self.leaves**(1/depth), 1)}")
            print(f"\tPV: {self.pv[0]}")
            self.board.heuristic_last_pv(self.pv[0][:])
            if self.max_time and end - start > self.max_time:
                break
            if value > 999000 or value < -999000:
                break
        print(f"Move: {self.pv[0][0]}")
        self.board.make_move(self.pv[0][0])

