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
            piece = temp_board.squares[initial.row][initial.col].piece
            # make a move
            temp_board.move(piece, move)
            color = 'white' if player_coefficient < 0 else 'black'

            temp_ai_engine = copy.deepcopy(self)
            temp_ai_engine.clear()
            temp_ai_engine.get_valid_moves(temp_board, color)

            current_score = CHECKMATE_VALUE

            for m in temp_ai_engine.valid_moves:
                # copy a board
                opponent_temp_board = copy.deepcopy(temp_board)

                # initialize a move of an opponent
                opponent_initial = m.initial
                opponent_piece = opponent_temp_board.squares[opponent_initial.row][opponent_initial.col].piece

                # opponent make a move
                opponent_temp_board.move(opponent_piece, m)

                color = 'black' if color == 'white' else 'white'

                current_score = min(opponent_temp_board.count_score() * player_coefficient, current_score)

            if current_score > score:
                score = current_score
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
