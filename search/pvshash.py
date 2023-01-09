#!/usr/bin/python3

import mpge, time

# Principle Variation search
# Search all moves after the first with a zero window search
# assuming it will fail low.  If it fails high with this zero window search
# re-search with normal alpha-beta search


class PVSHash(mpge.Search):

    class ht_entry:
        def __init__(self, hash_key, score, score_type, depth, best_move):
            self.hash_key = hash_key
            self.score = score
            self.score_type = score_type
            self.depth = depth
            self.best_move = best_move

    ht_size = 1000000

    def __init__(self, board: mpge.Board):
        self.board = board
        self.pv = [[] for i in range(self.max_depth * 2)]
        self.nodes = 0
        self.leaves = 0
        self.ht = {}

    def pvs(self, alpha, beta, depth, ply):
        if depth == 0:
            self.leaves += 1
            return self.quiescence(alpha, beta, ply)
        
        self.nodes += 1
        move_found = False 
        principle_variation = True
        current_side = self.board.side_to_move()
        initial_alpha = alpha    
        move_list = self.board.gen_moves(ply, depth)
        hash_index = self.board.hash_key % self.ht_size
        if (hash_index) in self.ht:
            entry = self.ht[hash_index]
            if entry.hash_key == self.board.hash_key:
                if entry.depth >= depth:
                    if entry.score_type == 0:
                        self.pv[ply] = [entry.best_move]
                        return entry.score
                    elif entry.score_type == 1 and entry.score >= beta:
                        return entry.score
                    elif entry.score_type == -1 and entry.score <= alpha:
                        return entry.score
                for move in move_list:
                    if move == entry.best_move:
                        move.score += 2000000
                        break
        move_list.sort(key = lambda x: x.score, reverse = True) 
        for move in move_list:
            if self.board.make_move(move):
                move_found = True
                same_side_to_move = current_side == self.board.side_to_move()
                if(principle_variation or depth <= 1):
                    if same_side_to_move:
                        score = self.pvs(alpha, beta, depth, ply + 1)
                    else:
                        score = -self.pvs(-beta, -alpha, depth - 1,  ply + 1)
                else:
                    if same_side_to_move:
                        score = self.pvs(alpha, alpha + 1, depth, ply + 1)
                    else:
                        score = -self.pvs(-(alpha + 1), -alpha, depth -1, ply + 1)
                    if score > alpha and score < beta:
                        if current_side == self.board.side_to_move:
                            score = self.pvs(alpha, beta, depth, ply + 1)
                        else:
                            score = -self.pvs(-beta, -alpha, depth - 1, ply + 1)
                self.board.undo_move()
                if score > alpha:
                    if score >= beta: # cutoff!
                        self.board.heuristic_fail_high(move, ply, depth)
                        self.ht[self.board.hash_key % self.ht_size] = \
                            self.ht_entry(self.board.hash_key, score, 1, depth, move)
                        return score
                    alpha = score
                    self.pv[ply] = [move] + self.pv[ply + 1]
                    self.ht[self.board.hash_key % self.ht_size] = \
                        self.ht_entry(self.board.hash_key, score, 0, depth, move)
            principle_variation = False
        
        # if no valid moves found, check for game end
        if not move_found:
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

        if alpha == initial_alpha:
            self.ht[self.board.hash_key % self.ht_size] = \
                self.ht_entry(self.board.hash_key, alpha, -1, depth, move_list[0])
        # return best value found
        return alpha

    def quiescence(self, alpha, beta, ply):
        self.nodes+= 1
        current_score = self.board.evaluate(ply=ply)
        current_side = self.board.side_to_move()
        if current_score > alpha:
            if current_score > beta:
                return current_score
            alpha = current_score
        move_list = self.board.gen_quiescence_moves(ply)
        move_list.sort(key = lambda x: x.score, reverse = True)
        for move in move_list:
            if self.board.make_move(move):
                same_side_to_move = current_side == self.board.side_to_move()
                if same_side_to_move:
                    score = self.quiescence(alpha, beta, ply + 1)
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
        self.pv = [[] for i in range(self.max_depth * 2)]
        self.board.heuristic_reset()
        for depth in range(1, self.max_depth + 1):
            self.leaves = 0
            value = self.pvs(-self.infinity, self.infinity, depth, 0)
            end = time.time()
            print(f"Depth {depth}, Score {value}, "
                  f"time {round(end - start, 2)}, "
                  f"nodes {self.nodes} ({int(round(self.nodes/(end - start))):,} nps), "
                  f"BF {round(self.leaves**(1/depth), 1)}")
            print(f"\tPV: {self.pv[0]}")
            self.board.heuristic_last_pv(self.pv[0][:])
            if self.max_time and end - start > self.max_time:
                break
            if value > 999000 or value < -999000:
                break
        print(f"Move: {self.pv[0][0]}")
        self.board.make_move(self.pv[0][0])

