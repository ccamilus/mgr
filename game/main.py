from ai import AI
from cnf import Cnf
from cli import Game

board_size = 15
ai_ = AI(Cnf(board_size), board_size)
game = Game(ai_, board_size)
game.main_loop()
