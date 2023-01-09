# mpge

matt's python game engine

This is mostly an exercise to learn Python inheritance, modules, packages, and whatnot.  If I wanted to do this for serious, I'd be writing it in a faster langauge.  However, it does work

mpge.py contains virtual, inheritable classes for boards, moves, searches.

Three games are implemented
* Tic Tac Toe
* Mancala
* Gobblet Gobblers

the search sub-package contains the various search algorithms

* Negamax -- full width, brute force search
* Alpha Beta -- backwards pruning so it should get the same results as a full width search
* PVS -- An alpha beta refinement that searches less nodes given reasonably good move ordering
* PVS with hashing -- The above but with a transposition table, literally a python dictionary

The searches are side-aware -- in Mancala, the same player may take multiple turns in a row.
The searches will also pass heuristic information back to the board (e.g. a certain move at a 
certain depth failed high in alpha beta, so maybe give that move a higher move-ordering score next time)


Known issues:

* max search time is more of a suggestion currently.  It won't iterate to a deeper search when it's out of time, but it doesn't interrupt the current search.  In some cases, it may take several times as long as the max time.  Multithreading is probably the right answer there.
* PV reconstruction via hash table would be good

The game module has a simple CLI with reasonable defaults.  It can be called something like this:

```
#!/usr/bin/python3

import mpge
import mpge.search

mpge.Game()
```

Output looks something like this

```
tictactoe> help
Commands:
        game {'mancala', 'gobbletgobblers', 'tictactoe'}: set game, start new game
        go: sets computer side to the side to move
        exit: quits
        new: makes new game
        perft [depth] : run perft
        undo: turn off computer, undoes move
        eval: evaluate position
        history: print history
        most anything else: do the move


 | |
-+-+-
 | |
-+-+-
 | |
X to move
Hash: 0

tictactoe> perft 9
perft(0): 1 leaves
        1 ongoing, 0 wins, 0 losses, 0 draws
        1 nodes in 0.0 seconds, 466,034 nodes/sec
perft(1): 9 leaves
        9 ongoing, 0 wins, 0 losses, 0 draws
        10 nodes in 0.0 seconds, 67,433 nodes/sec
perft(2): 72 leaves
        72 ongoing, 0 wins, 0 losses, 0 draws
        82 nodes in 0.0 seconds, 93,766 nodes/sec
perft(3): 504 leaves
        504 ongoing, 0 wins, 0 losses, 0 draws
        586 nodes in 0.01 seconds, 98,840 nodes/sec
perft(4): 3,024 leaves
        3,024 ongoing, 0 wins, 0 losses, 0 draws
        3,610 nodes in 0.04 seconds, 99,025 nodes/sec
perft(5): 15,120 leaves
        13,680 ongoing, 1,440 wins, 0 losses, 0 draws
        17,290 nodes in 0.19 seconds, 92,469 nodes/sec
perft(6): 56,160 leaves
        49,392 ongoing, 1,440 wins, 5,328 losses, 0 draws
        66,682 nodes in 0.73 seconds, 91,244 nodes/sec
perft(7): 154,944 leaves
        100,224 ongoing, 49,392 wins, 5,328 losses, 0 draws
        166,906 nodes in 2.15 seconds, 77,592 nodes/sec
perft(8): 255,168 leaves
        127,872 ongoing, 49,392 wins, 77,904 losses, 0 draws
        294,778 nodes in 4.13 seconds, 71,367 nodes/sec
perft(9): 255,168 leaves
        0 ongoing, 131,184 wins, 77,904 losses, 46,080 draws
        294,778 nodes in 5.36 seconds, 54,999 nodes/sec
 | |
-+-+-
 | |
-+-+-
 | |
X to move
Hash: 0

tictactoe> go
 | |
-+-+-
 | |
-+-+-
 | |
X to move
Hash: 0

Depth 1, Score 1, time 0.0, nodes 10 (40,960 nps), BF 9.0
        PV: [4]
Depth 2, Score 4, time 0.0, nodes 36 (43,290 nps), BF 4.0
        PV: [4, 0]
Depth 3, Score 1, time 0.0, nodes 132 (55,649 nps), BF 4.1
        PV: [4, 0, 2]
Depth 4, Score 4, time 0.01, nodes 310 (54,503 nps), BF 3.0
        PV: [4, 0, 2, 6]
Depth 5, Score 1, time 0.01, nodes 795 (58,111 nps), BF 3.1
        PV: [4, 0, 2, 6, 8]
Depth 6, Score 4, time 0.03, nodes 1507 (56,209 nps), BF 2.6
        PV: [4, 0, 1, 7, 2, 6]
Depth 7, Score 1, time 0.05, nodes 2594 (56,205 nps), BF 2.4
        PV: [4, 0, 1, 7, 2, 6, 8]
Depth 8, Score 5, time 0.07, nodes 3591 (53,994 nps), BF 2.0
        PV: [4, 0, 1, 7, 6, 2, 8, 3]
Depth 9, Score 0, time 0.09, nodes 4589 (53,602 nps), BF 1.8
        PV: [4, 0, 1, 7, 6, 2, 8, 3, 5]
Move: 4
 | |
-+-+-
 |X|
-+-+-
 | |
O to move
Hash: 10772131572909586189

tictactoe> game mancala
     4  4  4  4  4  4
  0 ------------------  0
     4  4  4  4  4  4
Player 1 to move
Hash: 5709755043105241381

mancala> go
     4  4  4  4  4  4
  0 ------------------  0
     4  4  4  4  4  4
Player 1 to move
Hash: 5709755043105241381

Depth 1, Score 12, time 0.0, nodes 12 (29,572 nps), BF 10.0
        PV: [c, a]
Depth 2, Score -2, time 0.0, nodes 81 (36,531 nps), BF 6.8
        PV: [c, b, C, D]
Depth 3, Score 7, time 0.01, nodes 335 (39,708 nps), BF 5.4
        PV: [f, B, A, a, a]
Depth 4, Score 0, time 0.02, nodes 728 (39,365 nps), BF 3.8
        PV: [f, B, A, d, B, C]
Depth 5, Score 12, time 0.04, nodes 1671 (40,150 nps), BF 3.5
        PV: [f, B, A, e, B, f, c, f, d]
Depth 6, Score 12, time 0.09, nodes 3440 (39,197 nps), BF 3.0
        PV: [f, B, A, e, D, f, b, f, c, A]
Depth 7, Score 20, time 0.31, nodes 12637 (41,078 nps), BF 3.4
        PV: [f, B, A, e, D, f, c, A, f, b, f, e, c, a]
Depth 8, Score 19, time 0.75, nodes 30079 (39,888 nps), BF 3.1
        PV: [f, B, A, e, D, f, c, A, f, b, f, e, c, B]
Depth 9, Score 35, time 2.81, nodes 117599 (41,839 nps), BF 3.4
        PV: [f, B, A, d, C, f, b, f, e, A, f, d, C, c, f, d, b, a]
Depth 10, Score 22, time 5.19, nodes 207252 (39,963 nps), BF 2.9
        PV: [f, B, A, d, C, f, b, f, e, B, f, a, C, c, E, d, b, a]
Move: f
     4  4  4  5  5  5
  0 ------------------  1
     4  4  4  4  4  0
Player 2 to move
Hash: 11976162411049706689

mancala> game gobbletgobblers
   SO SO    MO MO    LO LO

  |  |
--+--+--
  |  |
--+--+--
  |  |

   SX SX    MX MX    LX LX

X to move
Hash: 0

gobbletgobblers> go
   SO SO    MO MO    LO LO

  |  |
--+--+--
  |  |
--+--+--
  |  |

   SX SX    MX MX    LX LX

X to move
Hash: 0

Depth 1, Score 11, time 0.0, nodes 28 (43,352 nps), BF 27.0
        PV: [LX4]
Depth 2, Score 4, time 0.0, nodes 106 (28,010 nps), BF 7.1
        PV: [LX4, LO0]
Depth 3, Score 11, time 0.02, nodes 891 (40,894 nps), BF 8.9
        PV: [LX4, LO0, LX2]
Depth 4, Score 4, time 0.11, nodes 2811 (26,743 nps), BF 5.8
        PV: [LX4, LO0, LX2, LO6]
Depth 5, Score 1, time 0.38, nodes 12242 (32,269 nps), BF 6.0
        PV: [LX4, LO0, LX2, LO6, MX8]
Depth 6, Score 3, time 1.31, nodes 35162 (26,869 nps), BF 4.9
        PV: [LX4, LO0, LX2, LO6, MX3, MO8]
Depth 7, Score 1, time 4.69, nodes 155702 (33,207 nps), BF 5.2
        PV: [LX4, LO0, LX2, MO6, 26, LO2, MX8]
Depth 8, Score 3, time 18.4, nodes 451953 (24,567 nps), BF 4.5
        PV: [LX4, LO0, MX5, LO5, MX1, 01, LX0, MO2]
Move: LX4
   SO SO    MO MO    LO LO

  |  |
--+--+--
  |LX|
--+--+--
  |  |

   SX SX    MX MX    LX

O to move
Hash: 12566584186028127575
```



