#!/usr/bin/python3

import time
import mpge
import random

class Move(mpge.Move):
    def __init__(self, move, score=0):
        self.move = int(move)
        self.score = score
    def __str__(self) -> str:
        return str(self.move)
    def __repr__(self) -> str:
        return self.__str__()
    def __eq__(self, other):
        return self.move == other.move

class Board(mpge.Board):
    
    # for printing the board and describing the end game state
    letter = {0: ' ', 1: 'X', 2: 'O', 3: 'Draw'}

    # defines the endgame conditions (three in a row)
    win_conditions = [[0, 1, 2], [3, 4, 5], [6, 7, 8], \
                      [0, 3, 6], [1, 4, 7], [2, 5, 8], \
                      [0, 4, 8], [2, 4, 6]]

    # for rudimentary move ordering, ie. try moving to center first
    move_ordering_score = [3, 2, 3, 2, 4, 2, 3, 2, 3]

    # for staic evaluation of unfinished games
    square_value = [3, 2, 3, 2, 4, 2, 3, 2, 3]

    # for killer move heuristic
    killers = []
    killer_bonus = 1000000

    # 
    use_heuristics=True

    hash_board = [[0, 0] for i in range(9)]
    hash_side = 0
    hash_key = 0

    def __init__(self):
        self.generate_hash_keys()
        self.new_game()

    def generate_hash_keys(self):
        for square in range(9):
            for piece in range(2):
                self.hash_board[square][piece] = random.getrandbits(64)
        self.hash_side = random.getrandbits(64)
 

    def new_game(self):
        self.board = [0,0,0,0,0,0,0,0,0]
        self.side = 1
        self.history = []
        self.winning_side = 0
        self.killers = []

    def __str__(self):
        s = (f"{self.letter[self.board[0]]}|{self.letter[self.board[1]]}|{self.letter[self.board[2]]}\n"
              "-+-+-\n"
             f"{self.letter[self.board[3]]}|{self.letter[self.board[4]]}|{self.letter[self.board[5]]}\n"
              "-+-+-\n"
             f"{self.letter[self.board[6]]}|{self.letter[self.board[7]]}|{self.letter[self.board[8]]}\n")
        if self.winning_side:
            s += f"Winner: {self.letter[self.winning_side]}\n"
        else:
            s += f"{self.letter[self.side]} to move\n"
        s += f"Hash: {self.hash_key}\n"
        return s

    def __repr__(self):
        return self.__str__()

    def make_move(self, m):
        if m.move > 8 or self.board[m.move] != 0 or self.winning_side: 
            return False
        self.board[m.move] = self.side
        self.hash_key ^= self.hash_board[m.move][self.side-1]
        for w in self.win_conditions:
            if m.move in w and self.board[w[0]] == self.side and \
                               self.board[w[1]] == self.side and \
                               self.board[w[2]] == self.side:
                self.winning_side = self.side
                break
        self.side ^= 3
        self.hash_key ^= self.hash_side
        self.history.append(m)
        if len(self.history) == 9 and self.winning_side == 0: # drawn
            self.winning_side = 3
        return True
        
    def undo_move(self):
        if len(self.history) > 0:
            self.side ^= 3
            self.hash_key ^= self.hash_side
            m = self.history.pop()
            self.board[m.move] = 0
            self.hash_key ^= self.hash_board[m.move][self.side - 1]
            self.winning_side = 0

    def gen_moves(self, ply=0, depth=0):
        while ply >= len(self.killers):
            self.killers.append(Move(-1))
        move_list = []
        for i in range(9):
            if self.board[i] == 0:
                move_list.append(Move(i, score=self.move_ordering_score[i]))
        for move in move_list:
            if move == self.killers[ply]:
                move.score += self.killer_bonus
                break
        return  move_list

    def gen_quiescence_moves(self, ply=0):
        #while ply >= len(self.killers):
        #    self.killers.append(Move(-1))
        #for move in move_list:
        #    if move == self.killers[ply]:
        #        move.score += self.killer_bonus
        #        break
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

    def evaluate(self, ply=0):
        if self.winning_side:
            if self.side == self.winning_side:
                return 1000000 - ply
            elif self.side == self.winning_side ^ 3:
                return -1000000 + ply
            else:
                return 0
        score = [0,0,0]
        for i in range(9):
            score[self.board[i]] += self.square_value[i]
        score[self.side] += 3
        return score[self.side] - score[self.side ^ 3]

    def parse_move(self, move_string):
        move_list = self.gen_moves()
        for move in move_list:
            if str(move) == move_string:
                return move
        return None
    
    def heuristic_fail_high(self, move, ply, depth):
        if self.use_heuristics:
            self.killers[ply] = move

    def heuristic_last_pv(self, move_list):
        if self.use_heuristics:
            self.killers = move_list

    def heuristic_reset(self):
        if self.use_heuristics:
            self.killers = []

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

if __name__ == "__main__":
    b = Board()
    for i in range(1, 10):
        b.perft(i)