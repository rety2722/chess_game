from const import *
from square import Square
from piece import *
from move import Move
from sound import Sound
import copy
import os


class Board:

    def __init__(self):
        # checkmate and stalemate
        self.checkmate = False
        self.stalemate = False

        self.squares = [[Square(row, col) for col in range(COLS)] for row in range(ROWS)]
        self.last_move = None
        self._create()
        self._add_pieces('white')
        self._add_pieces('black')

    # makes a move and remembers last move made
    def move(self, piece: Piece, move: Move, testing=False):
        '''
        Makes a move
        :param piece: piece being moved
        :param move: Move that is being done
        :param testing:
        :return: return all changed squares
        '''

        changed_squares = []

        initial = move.initial
        final = move.final

        en_passant_empty = self.squares[final.row][final.col].is_empty()

        # write changed squares
        changed_squares.append(copy.deepcopy(self.squares[initial.row][initial.col]))
        changed_squares.append(copy.deepcopy(self.squares[final.row][final.col]))

        # console board move update
        self.squares[initial.row][initial.col].piece = None
        self.squares[final.row][final.col].piece = piece

        # making en-passant move if possible
        if isinstance(piece, Pawn):
            # en passant capture
            diff = final.col - initial.col
            if diff != 0 and en_passant_empty:
                # write changed squares
                if not testing:
                    changed_squares.append(copy.deepcopy(self.squares[initial.row][initial.col + diff]))
                # console board move update
                self.squares[initial.row][initial.col + diff].piece = None
                self.squares[final.row][final.col].piece = piece
                if not testing:
                    sound = Sound(
                        os.path.join('../assets/sounds/capture.wav'))
                    sound.play()

        # castling if possible
        if isinstance(piece, King):
            if self.castling(initial, final) and not testing:
                diff = final.col - initial.col
                rook = piece.left_rook if (diff < 0) else piece.right_rook
                # write changed squares
                c = 0 if diff < 0 else 7
                changed_squares.append(copy.deepcopy(self.squares[initial.row][c]))
                changed_squares.append(copy.deepcopy(self.squares[initial.row][final.col - abs(diff) // diff]))

                self.move(rook, rook.moves[-1])

        # move
        piece.moved = True

        # clear valid moves
        self.clear_moves()

        # set last move
        self.last_move = move

        return changed_squares

    # makes last move backwards
    def undo_move(self, fields):
        '''
        undoes last move
        :param fields: get all changed fields and return their pieces back
        :return: None
        '''
        for field in fields:
            self.squares[field.row][field.col].piece = field.piece

    # checks if the move is valid or not
    def valid_move(self, piece: Piece, move: Move):
        '''
        :param piece: any piece
        :param move: any move
        :return: True if piece can do the move, else False
        '''
        return move in piece.moves

    # checks if promotion is happening
    def check_promotion(self, piece: Piece, final: Square):
        '''
        :param piece: is a pawn
        :param final: final square
        :return: True if a pawn reaches promotion field else False
        '''
        if isinstance(piece, Pawn):
            if final.row == 0 or final.row == 7:
                return True
        return False

    def moves_left(self, color):
        '''
        checks if moves of pieces of a color left
        :param color: black or white
        :return: True if this color's pieces can move
        '''
        for row in range(ROWS):
            for col in range(COLS):
                if self.squares[row][col].has_enemy_piece(color):
                    p = self.squares[row][col].piece
                    self.calc_moves(p, row, col, check=True)
                    if len(p.moves) > 0:
                        return True
                    p.clear_moves()
        return False

    # checks if castling is valid in self.move()
    def valid_castling(self, king_move: Move, piece: Piece):
        '''
        :param king_move: pieces, that king traveles
        :param piece: king
        :return: checks if a castling is valid
        '''
        row = king_move.initial.row
        start = min(king_move.initial.col, king_move.final.col)
        end = max(king_move.initial.col, king_move.final.col)
        for col in range(start, end + 1):
            if self.square_under_attack(self.squares[row][col], piece):
                return False
        return True

    # checks if castling is happening during king move. Needed in self.move()
    def castling(self, initial: Square, final: Square):
        return abs(initial.col - final.col) == 2

    def set_true_en_passant(self, piece: Piece):

        if not isinstance(piece, Pawn):
            return

        for row in range(ROWS):
            for col in range(COLS):
                if isinstance(self.squares[row][col].piece, Pawn):
                    self.squares[row][col].piece.en_passant = False

        piece.en_passant = True

    # checks whether piece.color king is checked after a move, needed in calc_moves with checks
    def in_check(self, piece: Piece, move: Move):
        '''

        :param piece: any piece
        :param move: any valid move
        :return: if a king is in check after a move
        '''
        temp_piece = copy.deepcopy(piece)
        temp_board = copy.deepcopy(self)
        temp_board.move(temp_piece, move, testing=True)

        for row in range(ROWS):
            for col in range(COLS):
                if temp_board.squares[row][col].has_enemy_piece(piece.color):
                    p = temp_board.squares[row][col].piece
                    temp_board.calc_moves(p, row, col, check=False)
                    for m in p.moves:
                        if isinstance(m.final.piece, King):
                            return True

        return False

    # checks if king is checked for mate or stalemate
    def king_checked(self, color):
        '''
        Used to check stalemate or checkmate
        :param color: white or black
        :return: True if king of given color is checked else False
        '''
        for row in range(ROWS):
            for col in range(COLS):
                if self.squares[row][col].has_enemy_piece(color):
                    p = self.squares[row][col].piece
                    self.calc_moves(p, row, col, check=False)
                    for m in p.moves:
                        if isinstance(m.final.piece, King):
                            p.clear_moves()
                            return True
                    p.clear_moves()
        return False

    # checks whether the square is attacked, needed for checking castling validity
    def square_under_attack(self, square: Square, piece: Piece):
        temp_board = copy.deepcopy(self)
        for row in range(ROWS):
            for col in range(COLS):
                if temp_board.squares[row][col].has_enemy_piece(piece.color):
                    p = temp_board.squares[row][col].piece
                    temp_board.calc_moves(p, row, col, check=False)
                    for m in p.moves:
                        if m.final == square:
                            return True

        return False

    # clears possible moves for all pieces
    def clear_moves(self):
        for row in range(ROWS):
            for col in range(COLS):
                if self.squares[row][col].has_piece():
                    self.squares[row][col].piece.clear_moves()

    # calculates all possible/valid moves (depends on check kwarg) for a given piece
    def calc_moves(self, piece: Piece, row, col, check=True):
        '''
            Calculate all the possible (valid) moves of an specific piece on a specific position
        '''

        # identifies pawn's possible/valid moves
        def pawn_moves():
            # steps
            steps = 1 if piece.moved else 2

            # vertical moves
            start = row + piece.dir
            end = row + (piece.dir * (1 + steps))
            for possible_move_row in range(start, end, piece.dir):
                if Square.in_range(possible_move_row):
                    if self.squares[possible_move_row][col].is_empty():
                        # create initial and final move squares
                        initial = Square(row, col)
                        final = Square(possible_move_row, col)
                        # create a new move
                        move = Move(initial, final)

                        # check potential checks
                        if check:
                            if not self.in_check(piece, move):
                                # append new move
                                piece.add_move(move)
                        else:
                            # append new move
                            piece.add_move(move)
                    # blocked
                    else:
                        break
                # not in range
                else:
                    break

            # diagonal moves
            possible_move_row = row + piece.dir
            possible_move_cols = [col - 1, col + 1]
            for possible_move_col in possible_move_cols:
                if Square.in_range(possible_move_row, possible_move_col):
                    if self.squares[possible_move_row][possible_move_col].has_enemy_piece(piece.color):
                        # create initial and final move squares
                        initial = Square(row, col)
                        final_piece = self.squares[possible_move_row][possible_move_col].piece
                        final = Square(possible_move_row, possible_move_col, final_piece)
                        # create a new move
                        move = Move(initial, final)

                        # check potential checks
                        if check:
                            if not self.in_check(piece, move):
                                # append new move
                                piece.add_move(move)
                        else:
                            # append new move
                            piece.add_move(move)

            # en passant moves
            r = 3 if piece.color == 'white' else 4
            fr = 2 if piece.color == 'white' else 5
            # left en passant
            if Square.in_range(col - 1) and row == r:
                if self.squares[row][col - 1].has_enemy_piece(piece.color):
                    p = self.squares[row][col - 1].piece
                    if isinstance(p, Pawn):
                        if p.en_passant:
                            # create initial and final move squares
                            initial = Square(row, col)
                            final = Square(fr, col - 1, p)
                            # create a new move
                            move = Move(initial, final)

                            # check potential checks
                            if check:
                                if not self.in_check(piece, move):
                                    # append new move
                                    piece.add_move(move)
                            else:
                                # append new move
                                piece.add_move(move)

            # right en passant
            if Square.in_range(col + 1) and row == r:
                if self.squares[row][col + 1].has_enemy_piece(piece.color):
                    p = self.squares[row][col + 1].piece
                    if isinstance(p, Pawn):
                        if p.en_passant:
                            # create initial and final move squares
                            initial = Square(row, col)
                            final = Square(fr, col + 1, p)
                            # create a new move
                            move = Move(initial, final)

                            # check potential checks
                            if check:
                                if not self.in_check(piece, move):
                                    # append new move
                                    piece.add_move(move)
                            else:
                                # append new move
                                piece.add_move(move)

        # identifies knight's possible/valid moves
        def knight_moves():
            # 8 possible moves
            possible_moves = [
                (row - 2, col + 1),
                (row - 1, col + 2),
                (row + 1, col + 2),
                (row + 2, col + 1),
                (row + 2, col - 1),
                (row + 1, col - 2),
                (row - 1, col - 2),
                (row - 2, col - 1),
            ]

            for possible_move in possible_moves:
                possible_move_row, possible_move_col = possible_move

                if Square.in_range(possible_move_row, possible_move_col):
                    if self.squares[possible_move_row][possible_move_col].is_empty_or_enemy(piece.color):
                        # create squares of the new move
                        initial = Square(row, col)
                        final_piece = self.squares[possible_move_row][possible_move_col].piece
                        final = Square(possible_move_row, possible_move_col, final_piece)
                        # create new move
                        move = Move(initial, final)

                        # check potential checks
                        if check:
                            if not self.in_check(piece, move):
                                # append new move
                                piece.add_move(move)
                        else:
                            # append new move
                            piece.add_move(move)

        # identifies linear possible/valid moves, used for queens, bishops and rooks
        def straight_line_moves(incrs):
            for incr in incrs:
                row_incr, col_incr = incr
                possible_move_row = row + row_incr
                possible_move_col = col + col_incr

                while True:
                    if Square.in_range(possible_move_row, possible_move_col):
                        # create squares of the possible new move
                        initial = Square(row, col)
                        final_piece = self.squares[possible_move_row][possible_move_col].piece
                        final = Square(possible_move_row, possible_move_col, final_piece)
                        # create a possible new move
                        move = Move(initial, final)

                        # empty = continue looping
                        if self.squares[possible_move_row][possible_move_col].is_empty():
                            # check potential checks
                            if check:
                                if not self.in_check(piece, move):
                                    # append new move
                                    piece.add_move(move)
                            else:
                                # append new move
                                piece.add_move(move)

                        # has enemy piece = add move + break
                        elif self.squares[possible_move_row][possible_move_col].has_enemy_piece(piece.color):
                            # check potential checks
                            if check:
                                if not self.in_check(piece, move):
                                    # append new move
                                    piece.add_move(move)
                            else:
                                # append new move
                                piece.add_move(move)
                            break

                        # has team piece = break
                        elif self.squares[possible_move_row][possible_move_col].has_team_piece(piece.color):
                            break

                    # not in range
                    else:
                        break

                    # incrementing incrs
                    possible_move_row = possible_move_row + row_incr
                    possible_move_col = possible_move_col + col_incr

        # identifies king's possible/valid moves
        def king_moves():
            adjs = [
                (row - 1, col + 0),  # up
                (row - 1, col + 1),  # up-right
                (row + 0, col + 1),  # right
                (row + 1, col + 1),  # down-right
                (row + 1, col + 0),  # down
                (row + 1, col - 1),  # down-left
                (row + 0, col - 1),  # left
                (row - 1, col - 1),  # up-left
            ]

            # normal moves
            for possible_move in adjs:
                possible_move_row, possible_move_col = possible_move

                if Square.in_range(possible_move_row, possible_move_col):
                    if self.squares[possible_move_row][possible_move_col].is_empty_or_enemy(piece.color):
                        # create squares of the new move
                        initial = Square(row, col)
                        final = Square(possible_move_row, possible_move_col)  # piece=piece
                        # create new move
                        move = Move(initial, final)
                        # check potential checks
                        if check:
                            if not self.in_check(piece, move):
                                # append new move
                                piece.add_move(move)
                        else:
                            # append new move
                            piece.add_move(move)

            # castling moves
            if not piece.moved:
                cols = [0, 7]
                for r_col in cols:
                    rook = self.squares[row][r_col].piece
                    if isinstance(rook, Rook):
                        if not rook.moved:
                            step = abs(r_col - col) // (r_col - col)
                            for c in range(col + step, r_col, step):
                                if self.squares[row][c].has_piece():
                                    break
                            else:

                                if step < 0:
                                    piece.left_rook = rook
                                else:
                                    piece.right_rook = rook

                                initial = Square(row, r_col)
                                final = Square(row, col + step)
                                move_rook = Move(initial, final)

                                initial = Square(row, col)
                                final = Square(row, col + 2 * step)
                                move_king = Move(initial, final)

                                if check:
                                    if self.valid_castling(move_king, piece):
                                        # add rook move
                                        rook.add_move(move_rook)
                                        # add king move
                                        piece.add_move(move_king)
                                else:
                                    # add rook move
                                    rook.add_move(move_rook)
                                    # add king move
                                    piece.add_move(move_king)

        if isinstance(piece, Pawn):
            pawn_moves()

        elif isinstance(piece, Knight):
            knight_moves()

        elif isinstance(piece, Bishop):
            straight_line_moves([
                (-1, 1),  # up-right
                (-1, -1),  # up-left
                (1, 1),  # down-right
                (1, -1),  # down-left
            ])

        elif isinstance(piece, Rook):
            straight_line_moves([
                (-1, 0),  # up
                (0, 1),  # right
                (1, 0),  # down
                (0, -1),  # left
            ])

        elif isinstance(piece, Queen):
            straight_line_moves([
                (-1, 1),  # up-right
                (-1, -1),  # up-left
                (1, 1),  # down-right
                (1, -1),  # down-left
                (-1, 0),  # up
                (0, 1),  # right
                (1, 0),  # down
                (0, -1)  # left
            ])

        elif isinstance(piece, King):
            king_moves()

    def count_score(self) -> int:
        score = 0
        for row in range(ROWS):
            for col in range(COLS):
                if self.squares[row][col].has_piece():
                    piece = self.squares[row][col].piece
                    score += piece.value
        return score

    # creates a board
    def _create(self):
        for row in range(ROWS):
            for col in range(COLS):
                self.squares[row][col] = Square(row, col)

    # adds pieces to the board
    def _add_pieces(self, color):
        row_pawn, row_other = (6, 7) if color == 'white' else (1, 0)

        # pawns
        for col in range(COLS):
            self.squares[row_pawn][col] = Square(row_pawn, col, Pawn(color))

        # knights
        self.squares[row_other][1] = Square(row_other, 1, Knight(color))
        self.squares[row_other][6] = Square(row_other, 6, Knight(color))

        # bishops
        self.squares[row_other][2] = Square(row_other, 2, Bishop(color))
        self.squares[row_other][5] = Square(row_other, 5, Bishop(color))

        # rooks
        self.squares[row_other][0] = Square(row_other, 0, Rook(color))
        self.squares[row_other][7] = Square(row_other, 7, Rook(color))

        # queen
        self.squares[row_other][3] = Square(row_other, 3, Queen(color))

        # king
        self.squares[row_other][4] = Square(row_other, 4, King(color))
