import pygame
import string

from const import *
from board import Board
from dragger import Dragger
from config import Config
from square import Square
from piece import *
from ai_chess import AI_engine


class Game:

    def __init__(self):
        self.next_player = 'white'
        self.hovered_sqr = None
        self.board = Board()
        self.ai_engine = AI_engine()
        self.dragger = Dragger()
        self.config = Config()
        self.promoting = False
        # for keeping move log and for undoing moves
        self.moves = []
        self.changed_squares = []
        # necessary for not recalculating moves
        self.clicked_square = Square(0, 0)
        self.released_square = Square(7, 7)
        # end of game
        self.checkmate = False
        self.stalemate = False
        # game over variable for clarity
        self.game_over = False
        # game mode (PvP/PvE/CompVsComp)
        self.player = {'white': True, 'black': False}

    # blit methods
    def show_all(self, surface, show_hover=True, show_moves=True, show_promotion=True):
        self.show_background(surface)
        self.show_last_move(surface)
        if show_moves:
            self.show_moves(surface)
        self.show_pieces(surface)
        if show_hover:
            self.show_hover(surface)
        if show_promotion:
            self.show_promotion(surface)

    def show_background(self, surface):
        theme = self.config.theme

        for row in range(ROWS):
            for col in range(COLS):
                # color
                color = theme.background.light if (row + col) % 2 == 0 else theme.background.dark
                # rect
                rect = (col * SQSIZE, row * SQSIZE, SQSIZE, SQSIZE)
                # blit
                pygame.draw.rect(surface, color, rect)

                # row coordinates
                if col == 0:
                    # color
                    color = theme.background.dark if row % 2 == 0 else theme.background.light
                    # label
                    lbl = self.config.font.render(str(ROWS - row), 1, color)
                    lbl_pos = (5, 5 + row * SQSIZE)
                    # blit
                    surface.blit(lbl, lbl_pos)

                # col coordinates
                if row == 7:
                    # color
                    color = theme.background.dark if (row + col) % 2 == 0 else theme.background.light
                    # label
                    lbl = self.config.font.render(Square.get_alphacol(col), 1, color)
                    lbl_pos = (col * SQSIZE + SQSIZE - 20, HEIGHT - 20)
                    # blit
                    surface.blit(lbl, lbl_pos)

    def show_pieces(self, surface):
        for row in range(ROWS):
            for col in range(COLS):
                # piece ?
                if self.board.squares[row][col].has_piece():
                    piece = self.board.squares[row][col].piece

                    # all pieces except dragger piece
                    if piece is not self.dragger.piece:
                        piece.set_texture(size=80)
                        img = pygame.image.load(piece.texture)
                        img_center = col * SQSIZE + SQSIZE // 2, row * SQSIZE + SQSIZE // 2
                        piece.texture_rect = img.get_rect(center=img_center)
                        surface.blit(img, piece.texture_rect)

    def show_moves(self, surface):
        theme = self.config.theme

        if self.dragger.dragging:
            piece = self.dragger.piece

            # loop all valid moves
            for move in piece.moves:
                # color
                color = theme.moves.light if (move.final.row + move.final.col) % 2 == 0 else theme.moves.dark
                # rect
                rect = (move.final.col * SQSIZE, move.final.row * SQSIZE, SQSIZE, SQSIZE)
                # blit
                pygame.draw.rect(surface, color, rect)

    # shows some text in the center of a screen
    def show_text(self, surface, text):
        # creates font
        font = pygame.font.SysFont('Times New Roman', 40, True, False)
        # creates text object and its location
        text_object = font.render(text, 0, pygame.Color('Purple'))
        text_location = text_object.get_rect()
        text_location.center = (WIDTH // 2, HEIGHT // 2)
        # draws text
        surface.blit(text_object, text_location)

    def show_last_move(self, surface):
        theme = self.config.theme

        if self.board.last_move:
            initial = self.board.last_move.initial
            final = self.board.last_move.final

            for pos in [initial, final]:
                # color
                color = theme.trace.light if (pos.row + pos.col) % 2 == 0 else theme.trace.dark
                # rect
                rect = (pos.col * SQSIZE, pos.row * SQSIZE, SQSIZE, SQSIZE)
                # blit
                pygame.draw.rect(surface, color, rect)

    def show_hover(self, surface):
        if self.hovered_sqr:
            # color
            color = (180, 180, 180)
            # rect
            rect = (self.hovered_sqr.col * SQSIZE, self.hovered_sqr.row * SQSIZE, SQSIZE, SQSIZE)
            # blit
            pygame.draw.rect(surface, color, rect, width=3)

    def show_promotion(self, surface):
        if self.promoting:
            theme = self.config.theme
            final = self.board.last_move.final
            squares = [(i, final.col) for i in range(4)] if final.row == 0 else [(i, final.col) for i in
                                                                                 range(7, 3, -1)]
            pieces = [
                Queen(self.board.squares[final.row][final.col].piece.color),
                Knight(self.board.squares[final.row][final.col].piece.color),
                Rook(self.board.squares[final.row][final.col].piece.color),
                Bishop(self.board.squares[final.row][final.col].piece.color)
            ]
            for square in squares:
                color = theme.moves.light if (final.row + final.col) % 2 == 0 else theme.moves.dark
                rect = (square[1] * SQSIZE, square[0] * SQSIZE, SQSIZE, SQSIZE)
                pygame.draw.rect(surface, color, rect)
            for i in range(4):
                piece = pieces[i]
                piece.set_texture()
                img = pygame.image.load(piece.texture)
                piece_center = squares[i][1] * SQSIZE + SQSIZE // 2, squares[i][0] * SQSIZE + SQSIZE // 2
                piece.texture_square = img.get_rect(center=piece_center)
                surface.blit(img, piece.texture_square)

    # other methods

    def next_turn(self):
        self.next_player = 'white' if self.next_player == 'black' else 'black'

    def set_hover(self, row, col):
        self.hovered_sqr = self.board.squares[row][col]

    def change_theme(self):
        self.config.change_theme()

    def play_sound(self, captured=False):
        if captured:
            self.config.capture_sound.play()
        else:
            self.config.move_sound.play()

    def reset(self):
        self.__init__()
