#!/usr/bin/python3

import time
import random
import mpge

class Move(mpge.Move):
    move = -1
    score = 0
    def __init__(self, fr, to, score=0):
        self.move = (fr << 4) | to
        self.score = score
    def __str__(self):
        fr = self.move >> 4
        if fr < 9:
            fr = str(fr)
        elif fr == 9:
            fr = 'SX'
        elif fr == 10:
            fr = 'MX'
        elif fr == 11:
            fr = 'LX'
        elif fr == 12:
            fr = 'SO'
        elif fr == 13:
            fr = 'MO'
        elif fr == 14:
            fr = 'LO'
        return fr + str(self.move & 15)
    def __repr__(self) :
        return self.__str__()
    def __eq__(self, other):
        return self.move == other.move

class Board(mpge.Board):
   
    letters = ['  ', 'SX', 'MX', 'LX', 'SO', 'MO', 'LO']
    piece_side = [0, 1, 1, 1, 2, 2, 2]
    side_letter = ['', 'X', 'O']

    # defines the endgame conditions (three in a row)
    win_conditions = [[0, 1, 2], [3, 4, 5], [6, 7, 8], \
                      [0, 3, 6], [1, 4, 7], [2, 5, 8], \
                      [0, 4, 8], [2, 4, 6]]

    # for rudimentary move ordering, ie. try moving to center first
    move_ordering_score = [3, 2, 3, 2, 4, 2, 3, 2, 3]
    piece_value = [0, 1, 3, 5, 1, 3, 5]

    # for static evaluation of unfinished games
    square_value = [3, 2, 3, 2, 4, 2, 3, 2, 3]

    def __init__(self):
        self.make_hash_keys()
        self.new_game()

    def new_game(self):
        self.board = [[0],[0],[0],[0],[0],[0],[0],[0],[0], \
            [0, 1, 1], [0, 2, 2], [0, 3, 3], [0, 4, 4], [0, 5, 5], [0, 6, 6]]
        self.side = 1
        self.history = []
        self.winning_side = 0

    def make_hash_keys(self):
        self.hash_board = [[0, 0, 0, 0, 0, 0] for i in range(9)]
        for square in range(9):
            for piece in range(6):
                self.hash_board[square][piece] = random.getrandbits(64)
        self.hash_side = random.getrandbits(64)
        self.hash_key = 0

    def __str__(self):
        b = self.board
        l = self.letters
        s = ''

        for i in range(12, 15):
            for j in range(len(b[i])):
                s += l[b[i][j]] + " "

        s += (f"\n\n{l[b[0][-1]]}|{l[b[1][-1]]}|{l[b[2][-1]]} \n"
              "--+--+--\n"
             f"{l[b[3][-1]]}|{l[b[4][-1]]}|{l[b[5][-1]]}\n"
              "--+--+--\n"
             f"{l[b[6][-1]]}|{l[b[7][-1]]}|{l[b[8][-1]]}\n\n")
        
        for i in range(9, 12):
            for j in range(len(b[i])):
                s += l[b[i][j]] + " "

        if self.winning_side:
            s += f"\n\nWinner: {self.side_letter[self.winning_side]}\n"
        else:
            s += f"\n\n{self.side_letter[self.side]} to move\n"
        s += f"Hash: {self.hash_key}\n"
        return s

    def __repr__(self):
        return self.__str__()

    def make_move(self, m):
        fr = m.move >> 4
        to = m.move & 15

        # check for illegal moves
        if self.winning_side or to > 8 or to < 0 or fr < 0 or fr > 14:
            return False
        if len(self.board[fr]) < 2:
            return False
        if self.board[to][-1] != 0 and (self.board[fr][-1] - 1) % 3 <= (self.board[to][-1] - 1) % 3:
            return False

        # do move
        p = self.board[fr].pop()
        if fr < 9:
            self.hash_key ^= self.hash_board[fr][p - 1]
        self.board[to].append(p)
        self.hash_key ^= self.hash_board[to][p - 1]

        # check for win via discovery
        if self.winning_side == 0:
            for w in self.win_conditions:
                if fr in w and self.piece_side[self.board[w[0]][-1]] == self.side ^ 3 and \
                                   self.piece_side[self.board[w[1]][-1]] == self.side ^ 3 and \
                                   self.piece_side[self.board[w[2]][-1]] == self.side ^ 3:
                    self.winning_side = self.side ^ 3
                    break
        
        # if no discovery win, check for normal win
        if self.winning_side == 0:
            for w in self.win_conditions:
                if to in w and self.piece_side[self.board[w[0]][-1]] == self.side and \
                                   self.piece_side[self.board[w[1]][-1]] == self.side and \
                                   self.piece_side[self.board[w[2]][-1]] == self.side:
                    self.winning_side = self.side
                    break

        self.side ^= 3
        self.hash_key ^= self.hash_side
        self.history.append(m)
        return True
        
    def undo_move(self):
        if len(self.history) > 0:
            self.side ^= 3
            self.hash_key ^= self.hash_side
            m = self.history.pop()
            fr = m.move >> 4
            to = m.move & 15
            p = self.board[to].pop()
            self.hash_key ^= self.hash_board[to][p - 1]
            self.board[fr].append(p)
            if fr < 9:
                self.hash_key ^= self.hash_board[fr][p - 1]
            self.winning_side = 0

    def gen_moves(self, ply=0, depth=0):
        move_list = []

        # place from in-hand
        for fr in range(self.side * 3 + 6, self.side * 3 + 9):
            if len(self.board[fr]) < 2:
                continue
            p = self.board[fr][-1]
            for to in range(9):
                if self.board[to][-1] == 0 or (self.board[to][-1] - 1) % 3 < (p - 1) % 3:
                    move_list.append(Move(fr, to, score=self.move_ordering_score[to] + self.piece_value[p] + 10))
                    if self.piece_side[self.board[to][-1]] == self.side ^ 3:
                        move_list[-1].score += 100

        # move pieces on board
        for fr in range(9):
            if self.piece_side[self.board[fr][-1]] == self.side:
                p = self.board[fr][-1]
                for to in range(9):
                    if fr == to:
                        continue
                    if self.board[to][-1] == 0 or (self.board[to][-1] - 1) % 3 < ( p - 1) % 3:
                        move_list.append(Move(fr, to, score = self.piece_value[p]))
                        if self.piece_side[self.board[to][-1]] == self.side ^ 3:
                            move_list[-1].score += 100
                        if self.piece_side[self.board[fr][-2]] == self.side ^ 3:
                            move_list[-1].score -= 100
                        
        return move_list

    def gen_quiescence_moves(self, ply=0):
        return []

    def winner(self):
        return self.winning_side

    def __perft(self, depth):
        s = [0, 0, 0, 0, 1]
        if depth==0:
            s[self.winning_side] += 1
            return s
            
        move_list = self.gen_moves()
        for move in move_list:
            if self.make_move(move):
                if self.winning_side:
                    s[self.winning_side] += 1
                else:
                    s = [sum(i) for i in zip(s, self.__perft(depth-1))]
                self.undo_move()
        return s

    def perft(self, depth):
        start = time.time()
        r = self.__perft(depth)
        end = time.time()
        print(f"perft({depth}): {sum(r[:4]):,} leaves")
        print(f"\t{r[0]:,} ongoing, ", end='')
        print(f"{r[1]:,} wins, ", end='')
        print(f"{r[2]:,} losses, ", end='')
        print(f"{r[3]:,} draws")
        print(f"\t{r[4]:,} nodes in ", end='')
        print(f"{round(end-start, 2)} seconds, ", end='')
        print(f"{int(round(r[4] / (end-start), 0)):,} nodes/sec")
    def side_to_move(self):
        return self.side

    def evaluate(self, ply = 0):
        if self.winning_side:
            if self.winning_side == self.side:
                return 1000000 - ply
            elif self.winning_side == self.side ^ 3:
                return -1000000 + ply
                
        score = [0,0,0]
        for i in range(9):
            score[self.piece_side[self.board[i][-1]]] += self.square_value[i]
        score[self.side] += 3
        score[1] += 3 * len(self.board[9])
        score[2] += 3 * len(self.board[12])
        score[1] -= 10 * len(self.board[11])
        score[2] -= 10 * len(self.board[14])
        return score[self.side] - score[self.side ^ 3]

    def parse_move(self, move_string):
        move_list = self.gen_moves()
        for move in move_list:
            if str(move) == move_string:
                return move
        return None
    
    def heuristic_fail_high(self, move, ply, depth):
        #if self.use_heuristics:
        #    self.killers[ply] = move
        pass

    def heuristic_last_pv(self, move_list):
        #if self.use_heuristics:
        #    self.killers = move_list
        pass

    def heuristic_reset(self):
        #if self.use_heuristics:
        #    self.killers = []
        pass

    def history_string(self):
        movenum = 0
        s = 1
        for h in self.history:
            if s == 1:
                movenum += 1
                print(f"\n{movenum:2}.", end='')
            print(f"\t{h}", end='')
            s ^= 3
        print("\n")
