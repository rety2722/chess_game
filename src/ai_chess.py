import random

from board import Board
from move import Move
from const import *


class AI_engine:

    def __init__(self):
        self.valid_moves = []

    # gets random moves of possible moves
    def get_random_move(self) -> Move:
        rand_num = random.randint(0, len(self.valid_moves) - 1)
        return self.valid_moves[rand_num]

    # for now does nothing useful, it will be implemented later
    def get_best_move(self) -> Move:
        return self.get_random_move()

    # gets all valid moves and puts them into AI_engine.valid_moves
    def get_valid_moves(self, board: Board, color: str):
        # loops into all squares
        for row in range(ROWS):
            for col in range(COLS):
                # when finds team piece adds its valid moves
                if board.squares[row][col].has_piece():
                    piece = board.squares[row][col].piece
                    if piece.color == color:
                        # calculates possible moves
                        board.calc_moves(piece, row, col, check=True)
                        for move in piece.moves:
                            # appends possible moves
                            self.valid_moves.append(move)

    def clear(self):
        self.valid_moves = []
