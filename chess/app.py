import pygame

from .board import Board

pygame.init()
pygame.display.set_caption('Chess')

board = Board()
board.new_game()

fps = pygame.time.Clock()

is_running = True
while is_running:
    
    for event in pygame.event.get():


        if event.type == pygame.QUIT:
            is_running = False

        elif event.type == pygame.ACTIVEEVENT:
            if event.gain == 0 and board.piece_is_moving:
                board.reset_piece_location()
                board.reset_board_movement()
                board.refresh()


        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                board.update(event_pos=event.pos)
                board.select()


        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                board.update(event_pos=event.pos)
                board.release()


        elif event.type == pygame.MOUSEMOTION:
            if board.piece_is_moving:
                 board.update(event_pos=event.pos)
                 board.move()


        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                board.undo_move()


    fps.tick(60)
    pygame.display.update()

pygame.quit()
