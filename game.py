#!/usr/bin/python3

import time
import re 
import mpge

class Game():
    
    games = {'tictactoe', 'mancala', 'gobbletgobblers'}
    game_type = 'tictactoe'
    computer_side = 2


    def __init__(self):
        self.new_game()
        self.game_loop()

    def new_game(self):
        self.computer_side = 0
        if self.game_type == 'tictactoe':
            self.b = mpge.tictactoe.Board()
            #self.s = mpge.search.Negamax(self.b)
            #self.s = mpge.search.AlphaBeta(self.b)
            #self.s = mpge.search.PVS(self.b)
            self.s = mpge.search.PVSHash(self.b)
            self.s.max_depth=9
            self.s.max_time = 5
        elif self.game_type == 'mancala':
            self.b = mpge.mancala.Board()
            #self.s = mpge.search.Negamax(self.b)
            #self.s = mpge.search.AlphaBeta(self.b)
            #self.s = mpge.search.PVS(self.b)
            self.s = mpge.search.PVSHash(self.b)
            self.s.max_depth = 64
            self.s.max_time = 5
        elif self.game_type == 'gobbletgobblers':
            self.b = mpge.gobbletgobblers.Board()
            #self.s = mpge.search.Negamax(self.b)
            #self.s = mpge.search.AlphaBeta(self.b)
            #self.s = mpge.search.PVS(self.b)
            self.s = mpge.search.PVSHash(self.b)
            self.s.max_depth = 64
            self.s.max_time = 5

    def game_loop(self):
        while(True):
            print(self.b)
            line = input(f"{self.game_type}> ")
            line.rstrip('\n')
            if re.match("help", line):
                print("Commands:")
                print(f"\tgame {self.games}: set game, start new game")
                print("\tgo: sets computer side to the side to move")
                print("\texit: quits")
                print("\tnew: makes new game")
                print("\tperft [depth] : run perft")
                print("\tundo: turn off computer, undoes move")
                print("\teval: evaluate position")
                print("\thistory: print history")
                print("\tmost anything else: do the move")
            elif re.match("game ", line):
                g = line[5:]
                if g in self.games:
                    self.game_type = g
                    self.new_game()
            elif re.match("go", line):
                self.computer_side = self.b.side_to_move()
            elif re.match("new", line):
                self.new_game()
            elif re.match("undo", line):
                self.computer_side = 0
                self.b.undo_move()
            elif re.match("exit", line) or re.match("quit", line):
                break
            elif re.match("perft", line):
                m = re.match("perft (\d+)", line)
                if m:
                    end = int(m.group(1))
                else:
                    end = 4
                for i in range(end + 1):
                    self.b.perft(i)
            elif re.match("eval", line):
                print(f"Score: {self.b.evaluate()}")
            elif re.match("history", line):
                self.b.history_string()
            else:
                m = self.b.parse_move(line)
                if m:
                    success = self.b.make_move(m)
                    if not success:
                        print(f"Illegal move! ({line})")
                else:
                    print(f"Not a valid move ({line})")

            while self.b.side_to_move() == self.computer_side:
                print(self.b)
                self.s.search()
                if self.b.winner():
                    break
