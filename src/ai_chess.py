import copy
import random
import time

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

    # shows the best move using a greedy algorithm for one move for now
    def get_best_move(self, board: Board, player_coefficient: int) -> Move:

        # score equals -inf
        score = -CHECKMATE_VALUE

        # initialize
        best_move = None

        # loop through possible moves
        for move in self.valid_moves:

            # copy a board to make a move there
            temp_board = copy.deepcopy(board)

            # initialize move
            initial = move.initial
            final = move.final
            piece = temp_board.squares[initial.row][initial.col].piece

            # make a move
            temp_board.move(piece, move)
            temp_score = 0

            if temp_board.checkmate:
                temp_score = CHECKMATE_VALUE

            elif temp_board.stalemate:
                temp_score = STALEMATE_VALUE

            else:
                temp_score = temp_board.count_score() * player_coefficient

            # if temp_score is bigger than current score, we found better move
            if temp_score > score:
                score = temp_score
                best_move = move

        return best_move

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
