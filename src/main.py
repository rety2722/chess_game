import pygame
import sys

from const import *
from game import Game
from square import Square
from move import Move
from piece import *


class Main:

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption('Chess')
        self.game = Game()

    def promote(self):

        screen = self.screen
        game = self.game
        board = self.game.board
        dragger = self.game.dragger

        run = True
        while run:
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if e.type == pygame.MOUSEBUTTONDOWN:
                    dragger.update_mouse(e.pos)

                    clicked_row = max(min(HEIGHT - 1, dragger.mouseY), 0) // SQSIZE
                    clicked_col = max(min(WIDTH - 1, dragger.mouseX), 0) // SQSIZE

                    final = board.last_move.final
                    squares = [(i, final.col) for i in range(4)] if final.row == 0 else [(i, final.col) for i in
                                                                                         range(7, 3, -1)]
                    pieces = [
                        Queen(board.squares[final.row][final.col].piece.color),
                        Knight(board.squares[final.row][final.col].piece.color),
                        Rook(board.squares[final.row][final.col].piece.color),
                        Bishop(board.squares[final.row][final.col].piece.color)
                    ]
                    for i in range(4):
                        if squares[i] == (clicked_row, clicked_col):
                            # assign a piece
                            board.squares[final.row][final.col].piece = pieces[i]
                            # exit promoting
                            run = False
                            game.promoting = False
                            # show
                            game.show_all(screen)

    def mainloop(self):

        screen = self.screen
        game = self.game
        board = self.game.board
        dragger = self.game.dragger

        while True:
            # show methods
            game.show_all(screen, show_promotion=False)
            if game.promoting:
                game.show_promotion(screen)
                self.promote()

            if dragger.dragging:
                dragger.update_blit(screen)

            for event in pygame.event.get():

                # click
                if event.type == pygame.MOUSEBUTTONDOWN:
                    dragger.update_mouse(event.pos)

                    clicked_row = min(HEIGHT - 1, max(0, dragger.mouseY)) // SQSIZE
                    clicked_col = min(WIDTH - 1, max(0, dragger.mouseX)) // SQSIZE

                    # if clicked square has a piece ?
                    if board.squares[clicked_row][clicked_col].has_piece():
                        piece = board.squares[clicked_row][clicked_col].piece
                        # valid piece (color) ?
                        if piece.color == game.next_player:
                            board.calc_moves(piece, clicked_row, clicked_col, check=True)
                            dragger.save_initial(event.pos)
                            dragger.drag_piece(piece)
                            # show methods 
                            game.show_all(screen, show_hover=False)

                # mouse motion
                elif event.type == pygame.MOUSEMOTION:
                    motion_row = max(0, min(HEIGHT - 1, event.pos[1])) // SQSIZE
                    motion_col = max(0, min(WIDTH - 1, event.pos[0])) // SQSIZE

                    game.set_hover(motion_row, motion_col)

                    if dragger.dragging:
                        dragger.update_mouse(event.pos)
                        # show methods
                        game.show_all(screen)
                        dragger.update_blit(screen)

                # click release
                elif event.type == pygame.MOUSEBUTTONUP:

                    if dragger.dragging:
                        dragger.update_mouse(event.pos)

                        released_row = min(WIDTH - 1, max(0, dragger.mouseY)) // SQSIZE
                        released_col = min(WIDTH - 1, max(0, dragger.mouseX)) // SQSIZE

                        # create possible move
                        initial = Square(dragger.initial_row, dragger.initial_col)
                        final = Square(released_row, released_col)
                        if initial == final:
                            # show
                            game.show_all(screen)
                            dragger.undrag_piece()
                            continue
                        move = Move(initial, final)

                        # valid move ?
                        if board.valid_move(dragger.piece, move):
                            # normal capture
                            captured = board.squares[released_row][released_col].has_piece()
                            changed_squares = board.move(dragger.piece, move)
                            game.changed_squares.append(changed_squares)
                            game.moves.append(move)

                            board.set_true_en_passant(dragger.piece)

                            if board.check_promotion(dragger.piece, final):
                                game.promoting = True

                            # sounds
                            game.play_sound(captured)
                            # show methods
                            game.show_all(screen, show_moves=False, show_hover=False)
                            # next turn
                            game.next_turn()

                    dragger.undrag_piece()

                # key press
                elif event.type == pygame.KEYDOWN:

                    # unmoving
                    if event.key == pygame.K_z:
                        if len(game.moves) > 0:
                            board.undo_move(game.changed_squares.pop(-1))
                            game.moves.pop(-1)
                            game.show_all(screen, show_hover=False, show_moves=False)
                            game.next_turn()

                    # changing themes
                    if event.key == pygame.K_t:
                        game.change_theme()

                    # changing themes
                    if event.key == pygame.K_r:
                        game.reset()
                        game = self.game
                        board = self.game.board
                        dragger = self.game.dragger

                # quit application
                elif event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            pygame.display.update()


main = Main()
main.mainloop()
