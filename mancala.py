#!/usr/bin/python3

import time
import mpge
import random

class Move(mpge.Move):
    def __init__(self, move, score=0):
        self.move = int(move)
        self.score = score
    def __str__(self) -> str:
        if(self.move < 6):
            return chr(ord('a')+self.move)
        return chr(ord('A') + self.move - 7)
    def __repr__(self) -> str:
        return self.__str__()
    def __eq__(self, other):
        return self.move == other.move

class Board(mpge.Board):

    killer_bonus = 1000000

    def __init__(self):
        self.generate_hash_keys()
        self.new_game()

    def generate_hash_keys(self):
        self.hash_board = [[] for i in range(14)]
        for square in range(14):
            for count in range(49):
                self.hash_board[square].append(random.getrandbits(64))
        self.hash_side = random.getrandbits(64)

    def calculate_hash(self):
        self.hash_key = 0
        for i in range(14):
            self.hash_key ^= self.hash_board[i][self.board[i]]
        if self.side == 2:
            self.hash_key ^= self.side

    def new_game(self):
        self.board = [4, 4, 4, 4, 4, 4, 0, 4, 4, 4, 4, 4, 4, 0]
        self.side = 1
        self.history = []
        self.winning_side = 0
        self.killers = []
        self.calculate_hash()

    def __str__(self):
        s = '    '
        for i in range(12, 6, -1):
            s += f"{self.board[i]:2n} "
        s += f"\n {self.board[13]:2n} ------------------ {self.board[6]:2n}\n    "
        for i in range(6):
            s += f"{self.board[i]:2n} "
        if self.winning_side:
            s += f"\nPlayer {self.winning_side} Won ({sum(self.board[:7])} - {sum(self.board[7:])})\n"
        else:
            s += f"\nPlayer {self.side} to move\n"
        s += f"Hash: {self.hash_key}\n"
        return s

    def __repr__(self):
        return self.__str__()

    def make_move(self, m):

        # bail on obviously invalid moves
        if self.winning_side:
            return False
        if self.side == 2 and (m.move < 7 or m.move > 12):
            return False
        if self.side == 1 and (m.move < 0 or m.move > 5):
            return False
        if self.board[m.move] == 0:
            return False

        # backup state
        self.history.append( (self.side, self.board[:], m, self.hash_key))
       
        #do move
        in_hand = self.board[m.move]
        self.board[m.move] = 0
        spot = m.move
        while in_hand > 0:
            spot = spot + 1
            if spot == 6 and self.side == 2:
                spot += 1
            if spot == 13 and self.side == 1:
                spot += 1
            spot = spot % 14
            #if spot == m.move:
            #    spot += 1

            self.board[spot] += 1
            in_hand -= 1

       
        # do capture
        if self.board[spot] == 1:
            if self.side == 1 and spot < 6 and self.board[12-spot] > 0:
                self.board[6] += self.board[12-spot] + self.board[spot]
                self.board[12 - spot] = 0
                self.board[spot] = 0
            if self.side == 2 and spot > 6 and spot < 13 and self.board[-spot + 12] > 0:
                self.board[13] += self.board[-spot+12] + self.board[spot]
                self.board[spot] = 0
                self.board[-spot + 12] = 0
       
        # flip sides unless bonus move
        if (self.side == 1 and spot != 6) or (self.side == 2 and spot != 13):
            self.side ^= 3

        # end game check
        if (self.side == 1 and sum(self.board[:6]) == 0) or \
           (self.side == 2 and sum(self.board[7:13]) == 0):
            result = sum(self.board[:7]) - sum(self.board[7:])
            if result > 0:
                self.winning_side = 1
            elif result < 0:
                self.winning_side = 2
            else:
                self.winning_side = 3
        self.calculate_hash()
        return True
        
    def undo_move(self):
        if len(self.history) == 0:
            return
        h = self.history.pop()
        self.side = h[0]
        self.board = h[1]
        self.winning_side = 0
        self.hash_key = h[3]

    def gen_moves(self, ply=0, depth=0):
        while len(self.killers) < ply + 1:
            self.killers.append(Move(-1))
        move_list = []
        if self.side == 1:
            for i in range(6):
                if self.board[i] > 0:
                    move_list.append(Move(i))
        else:
            for i in range(7, 13):
                if self.board[i] > 0:
                    move_list.append(Move(i))
        for move in move_list:
            if move == self.killers[ply]:
                move.score += self.killer_bonus
        return move_list

    def gen_quiescence_moves(self, ply=0):
        return []

    def winner(self):
        return self.winning_side

    def __perft(self, depth):
        return 0

    def perft(self, depth):
        pass

    def side_to_move(self):
        return self.side

    def evaluate(self, ply=0):
        if self.winning_side:
            if self.side == self.winning_side:
                return 1000000 - ply
            elif self.side ^ 3 == self.winning_side:
                return -1000000 + ply
            else:
                return 0

        score = [0,0]

        score[0] += 2 * sum(self.board[:6]) + 5 * self.board[6]
        score[1] += 2 * sum(self.board[7:13]) + 5 * self.board[13]

        for i in range(6):
            if self.board[i] == 0:
                score[0] += self.board[12 - i]
            elif self.board[i] == 6 - i:
                score[0] += 5
        for i in range(7,13):
            if self.board[i] == 0:
                score[1] += self.board[12 - i]
            elif self.board[i] == 6 - i:
                score[1] += 5

        s = score[0] - score[1]
        if self.side == 2:
            return -s
        return s

    def parse_move(self, move_string):
        move_list = self.gen_moves()
        for move in move_list:
            if str(move) == move_string:
                return move
        return None
    
    def heuristic_fail_high(self, move, ply, depth):
        while len(self.killers) < ply + 1:
            self.killers.append(Move(-1))
        self.killers[ply] = move

    def heuristic_last_pv(self, move_list):
        self.killers = move_list[:]
        pass

    def heuristic_reset(self):
        self.killers = []

    def history_string(self):
        movenum = 0
        last_side = 2
        for h in self.history:
            if h[0] == 1 and last_side == 2:
                movenum += 1
                print(f"\n{movenum:2}.", end='')
            elif h[0] == 1 and last_side == 1:
                print("\n   ", end='')
            elif h[0] == 2 and last_side == 2:
                print(f"\n   \t", end='')
            print(f"\t{h[2]}", end='')
            last_side = h[0]
        print("\n")
