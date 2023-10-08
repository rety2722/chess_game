import pygame
import sys

from const import *
from game import Game
from square import Square
from move import Move
from piece import *
from ai_chess import AI_engine


class Main:

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption('Chess')
        self.game = Game()

    # shows promotion options, collects a choice and promotes
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

    # human play methods

    # registers player's click
    def player_click(self, event: pygame.event.Event):
        # variables' initialisation
        screen = self.screen
        game = self.game
        board = self.game.board
        dragger = self.game.dragger

        # click main code
        dragger.update_mouse(event.pos)

        # saves position of a click
        clicked_row = min(HEIGHT - 1, max(0, dragger.mouseY)) // SQSIZE
        clicked_col = min(WIDTH - 1, max(0, dragger.mouseX)) // SQSIZE

        # saves clicked square
        game.clicked_square = Square(clicked_row, clicked_col)

        # if clicked square has a piece ?
        if board.squares[clicked_row][clicked_col].has_piece():
            piece = board.squares[clicked_row][clicked_col].piece
            # valid piece (color) ?
            if piece.color == game.next_player:
                if game.released_square != game.clicked_square:
                    board.calc_moves(piece, clicked_row, clicked_col, check=True)
                dragger.save_initial(event.pos)
                dragger.drag_piece(piece)
                # show methods
                game.show_all(screen, show_hover=False)

    # registers player's dragging piece
    def player_drag(self, event: pygame.event.Event):
        # variables' initialisation
        screen = self.screen
        game = self.game
        board = self.game.board
        dragger = self.game.dragger

        # dragging main code
        # tracks current position
        motion_row = max(0, min(HEIGHT - 1, event.pos[1])) // SQSIZE
        motion_col = max(0, min(WIDTH - 1, event.pos[0])) // SQSIZE

        # puts hover onto it
        game.set_hover(motion_row, motion_col)

        # updates everything
        if dragger.dragging:
            dragger.update_mouse(event.pos)
            # show methods
            game.show_all(screen)
            dragger.update_blit(screen)

    # registers if dragged piece is released
    def player_release(self, event: pygame.event.Event):
        screen = self.screen
        game = self.game
        board = self.game.board
        dragger = self.game.dragger

        if dragger.dragging:
            dragger.update_mouse(event.pos)

            released_row = min(WIDTH - 1, max(0, dragger.mouseY)) // SQSIZE
            released_col = min(HEIGHT - 1, max(0, dragger.mouseX)) // SQSIZE

            # saves released square
            game.released_square = Square(released_row, released_col)

            # create possible move
            initial = Square(dragger.initial_row, dragger.initial_col)
            final = Square(released_row, released_col)
            # if move wasn't done to avoid clicking to much
            if initial == final:
                # show
                game.show_all(screen)
                dragger.undrag_piece()
                # if click is in the same position no need to re-calculate moves
                return
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

                # checkmate and stalemate
                if not board.moves_left(game.next_player):
                    game.game_over = True
                    game.next_turn()
                    if board.king_checked(game.next_player):
                        game.checkmate = True
                        print('checkmate')
                    else:
                        game.stalemate = True
                        print('stalemate')
                    game.next_turn()
                else:
                    game.checkmate = False
                    game.stalemate = False

                # sounds
                game.play_sound(captured)
                # show methods
                game.show_all(screen, show_moves=False, show_hover=False)
                # next turn
                game.next_turn()

        dragger.undrag_piece()

    def mainloop(self):

        screen = self.screen
        game = self.game
        board = self.game.board
        dragger = self.game.dragger
        ai_engine = self.game.ai_engine

        while True:
            # show methods
            game.show_all(screen, show_promotion=False)

            # shows a message if checkmate on the board
            if game.checkmate:

                last_square = board.last_move.final
                color = board.squares[last_square.row][last_square.col].piece.color
                text = color + ' wins by checkmate. Press r to restart'
                game.show_text(screen, text)

            # shows a message if stalemate on the board
            elif game.stalemate:

                text = 'game ended with stalemate. Press r to restart'
                game.show_text(screen, text)

            # starts promoting if pawn is promoting
            if game.promoting:
                game.show_promotion(screen)
                self.promote()

            if dragger.dragging:
                dragger.update_blit(screen)

            for event in pygame.event.get():

                # click
                if event.type == pygame.MOUSEBUTTONDOWN:
                    # no need to collect moves data if the game is ended
                    if not game.game_over:
                        # if player has to make a move
                        if game.player[game.next_player]:
                            self.player_click(event)
                        else:

                            # calculates valid moves for engine
                            ai_engine.get_valid_moves(board, game.next_player)

                            # gets best move, which is now just a random move
                            move = ai_engine.get_best_move()
                            initial = move.initial
                            final = move.final
                            piece = board.squares[initial.row][initial.col].piece
                            # normal capture
                            captured = board.squares[final.row][final.col].has_piece()
                            # move piece
                            changed_squares = board.move(piece, move, testing=False)
                            # clear engine moves
                            ai_engine.clear()
                            # change move log
                            game.changed_squares.append(changed_squares)
                            game.moves.append(move)

                            board.set_true_en_passant(piece)

                            if board.check_promotion(piece, final):
                                board.squares[final.row][final.col] = Queen(piece.color)

                            # checkmate and stalemate
                            if not board.moves_left(game.next_player):
                                game.game_over = True
                                game.next_turn()
                                if board.king_checked(game.next_player):
                                    game.checkmate = True
                                else:
                                    game.stalemate = True
                                game.next_turn()
                            else:
                                game.checkmate = False
                                game.stalemate = False

                            # sounds
                            game.play_sound(captured)
                            # show methods
                            game.show_all(screen, show_moves=False, show_hover=False)
                            # next turn
                            game.next_turn()

                # mouse motion
                elif event.type == pygame.MOUSEMOTION:
                    # no need to collect moves data if the game is ended
                    if not game.game_over:
                        # if player has to make a move
                        if game.player[game.next_player]:
                            self.player_drag(event)

                # click release
                elif event.type == pygame.MOUSEBUTTONUP:
                    # no need to collect moves data if the game is ended
                    if not game.game_over:
                        # if player has to make a move
                        if game.player[game.next_player]:
                            self.player_release(event)

                # key press
                elif event.type == pygame.KEYDOWN:

                    # unmoving
                    if event.key == pygame.K_z:
                        if len(game.moves) > 0 and not dragger.dragging:
                            # if move undone, no checkmate or stalemate
                            game.checkmate = False
                            game.stalemate = False
                            # undoes move and removes last move from move log
                            board.undo_move(game.changed_squares.pop(-1))
                            game.moves.pop(-1)
                            # show methods
                            game.show_all(screen, show_hover=False, show_moves=False)
                            # switch turns back
                            game.next_turn()

                    # changing themes
                    elif event.key == pygame.K_t:
                        game.change_theme()

                    # resets the game
                    elif event.key == pygame.K_r:
                        if not dragger.dragging:
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
