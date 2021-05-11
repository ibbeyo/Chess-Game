import pygame
from typing import Tuple
from collections import namedtuple

from .pieces import Pawn, Rook, Bishop, King, Knight, Queen, WHITE_PIECE, BLACK_PIECE


WINDOW_WIDTH, WINDOW_HEIGHT = (480, 480)
BOARD_OFFSET = (-17, -17)
BOARD_IMAGE = pygame.image.load('./images/board.jpg')
POSSIBLE_MOVES_BORDER = pygame.Surface((60,60))
POSSIBLE_MOVES_BORDER.set_alpha(128)


MoveLog = namedtuple('MoveLog', field_names=[
        'from_node', 'to_node', 'from_tile', 'to_tile', 'piece', 'event'
    ])


class Board:

    def __init__(self) -> None:
        self.board = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), 0, 32)
        self.board.fill((220,220,220))

        self.logger: list = list()
        self.nodes: dict = dict()
        self.valid_moves: list = list()

        self.piece = None
        self.piece_is_moving: bool = False

        self.has_en_passant: bool = False
        
        self.__draw_board()


    def new_game(self, is_white: bool = True) -> None:
        rows = range(8, 0, -1)
        cols = ['a','b','c','d','e','f','g','h']

        if not is_white:
            rows = range(1, 9)
            cols = list(reversed(cols))

        tiles = [[c+str(r) for c in cols] for r in rows]

        starting_positions = {
            Pawn    : tiles[1] + tiles[6],
            Rook    : ['a1', 'a8', 'h1', 'h8'],
            Bishop  : ['c1', 'c8', 'f1', 'f8'],
            Knight  : ['b1', 'b8', 'g1', 'g8'],
            King    : ['e1', 'e8'],
            Queen   : ['d1', 'd8']
        }

        for x, tile_group in enumerate(tiles):
            for y, tile in enumerate(tile_group):
                node_position = (60*y,60*x)
                self.nodes.update({node_position: {'piece': None, 'tile': tile}})

                for piece, placement in starting_positions.items():
                    if tile in placement:
                        color = BLACK_PIECE if int(tile[1:]) >= 7 else WHITE_PIECE
                        piece = piece(tile=tile, color=color, position=node_position)
                        self.board.blit(piece.load_image, node_position)
                        self.nodes[node_position]['piece'] = piece

        self.node_positions = list(self.nodes.keys())

    
    def select(self) -> None:
        node_position = self._get_nearest_node_pos()
        self.piece = self.nodes[node_position]['piece']

        if self.piece:
            self.piece_is_moving = True
            self.move_validation()
            self.refresh()
            self.nodes[node_position]['piece'] = None

            
    def release(self) -> None:
        if self.piece:
            node_position = self.release_validation()

            if not node_position:
                self.reset_piece_location()

            elif node_position:
                to_tile = self.nodes[node_position]['tile']

                if self.has_en_passant:
                    self.nodes[self.logger[-1].piece.position]['piece'] = None

                self.logger.append(
                    MoveLog(
                        from_node=self.piece.position, 
                        to_node=node_position, 
                        from_tile=self.piece.tile, 
                        to_tile=to_tile, 
                        piece=self.piece,
                        event='move'
                    )
                )

                self.nodes[self.piece.position]['piece'] = None

                if not self.piece.has_moved:
                    self.piece.has_moved = True

                self.piece.position = node_position
                self.piece.tile = to_tile
                self.nodes[node_position]['piece'] = self.piece

        self.reset_board_movement()
        self.refresh()


    def release_validation(self) -> Tuple[int, int] or bool:
        '''
        Validates the following:
        1. That a piece can only take of the opposite color.
        2. Possible piece positions.
        3. No node position to move to.
        4. That its the corret color to move.
        '''
    
        node_position = self._get_nearest_node_pos()
        if any([
            self.whos_turn() != self.piece.color,
            self.piece == self.nodes[node_position]['piece'],
            node_position not in self.valid_moves
        ]):
            return False

        return node_position


    def move(self) -> None:
        x, y = self.event_pos
        if self.piece and pygame.mouse.get_focused():
            self.refresh()
            self.board.blit(self.piece.load_image, (x-35, y-35))

    
    def move_validation(self) -> None:
   
        for motion, positions in enumerate(self.piece.get_moves().values()):
            for pos in positions:
                if pos in self.node_positions:
                    self.valid_moves.append(pos)

                    if other := self.nodes[pos]['piece']:
                        
                        if self.piece.color == other.color:
                            self.valid_moves.remove(pos)

                            #allow knight to jump
                            if not isinstance(self.piece, Knight):
                                break

                        elif self.piece.color != other.color:

                            #pawn cant take piece in front of it
                            if isinstance(self.piece, Pawn) and motion == 2:
                                self.valid_moves.remove(pos)
                                break
                            
                            #allow knight to jump
                            if not isinstance(self.piece, Knight):
                                break
                    
                    #dont allow pawn to move diagonal on empty node
                    elif isinstance(self.piece, Pawn) and motion < 2:
                        self.valid_moves.remove(pos)
                        if passant := self.en_passant():
                            self.valid_moves.append(passant)

                    

    def undo_move(self) -> None:
        if self.logger:
            move = self.logger[-1]
            self.nodes[move.to_node]['piece'] = None

            piece = move.piece
            piece.position = move.from_node
            piece.tile = move.from_tile

            self.nodes[move.from_node]['piece'] = piece

            del self.logger[-1]

        self.refresh()


    def reset_piece_location(self) -> None:
        self.nodes[self.piece.position]['piece'] = self.piece

        
    def reset_board_movement(self) -> None:
        self.piece = None
        self.piece_is_moving = False
        self.has_en_passant = False
        self.valid_moves.clear()


    def whos_turn(self) -> str:
        if len(self.logger) % 2 == 0:
            return WHITE_PIECE
        return BLACK_PIECE


    def update(self, event_pos) -> None:
        self.event_pos = event_pos


    def refresh(self) -> None:
        self.__draw_board()
        for node in self.nodes.values():
            if node['piece']:
                self.board.blit(node['piece'].load_image, node['piece'].position)

        if self.valid_moves:
            for area in self.valid_moves:
                POSSIBLE_MOVES_BORDER.fill((152,251,152)) #green
                self.board.blit(POSSIBLE_MOVES_BORDER, area)
            

    def en_passant(self) -> bool:
        if self.logger and self.whos_turn() == self.piece.color:
            previous_move = self.logger[-1]
            if isinstance(previous_move.piece, Pawn) and previous_move.piece != self.piece:

                if previous_move.from_node[1] == previous_move.piece.starting_position:
                    passant = getattr(previous_move.piece, previous_move.piece._reverse_orient)(1)
                    if any([
                        self.piece.left(1) == previous_move.to_node, 
                        self.piece.right(1) == previous_move.to_node
                    ]):
                        self.has_en_passant = True
                        return passant
        return False



    def __draw_board(self) -> None:
        self.board.blit(BOARD_IMAGE, BOARD_OFFSET)


    def _get_nearest_node_pos(self) -> Tuple[int, int] or None:
        x, y = self.event_pos
        for pos in self.node_positions:
            if x in range(pos[0] + 60) and y in range(pos[1] + 60):
                return pos
        return None
            

    


    