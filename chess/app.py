import pygame

from .board import Board

pygame.init()
pygame.display.set_caption('Chess')

board = Board()
board.new_game(white=True)

fps = pygame.time.Clock()

is_running = True
while is_running:

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            is_running = False

        elif event.type == pygame.ACTIVEEVENT:
            if event.gain == 0 and board.selected_piece_is_moving:
                board.reset_piece_state()
                board.reset_board_state()
                board.refresh()

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                board.select(event_position=event.pos)

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                board.release(event_position=event.pos)

        elif event.type == pygame.MOUSEMOTION:
            if board.selected_piece_is_moving:
                board.move(event_position=event.pos)

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                board.move_reset()
                
                
    fps.tick(60)
    pygame.display.update()

pygame.quit()