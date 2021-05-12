import pygame
from typing import Tuple, List, Dict, cast
from dataclasses import dataclass


from .pieces import (
    Piece, Pawn, Rook, Bishop, King, Knight, Queen, 
    WHITE_PIECE, BLACK_PIECE
)


WINDOW_WIDTH, WINDOW_HEIGHT = (480, 480)

BOARD_OFFSET = (-17, -17)
BOARD_IMAGE = pygame.image.load('./images/board.jpg')

POSSIBLE_MOVES_BORDER = pygame.Surface((60,60))
POSSIBLE_MOVES_BORDER.set_alpha(128)

EVENT_MOVE = 0
EVENT_CAPTURE = 1
EVENT_ENPASSANT = 2
EVENT_CASTLE = 3
EVENT_PROMOTION = 4

@dataclass
class MoveLog:
    from_pos    : Tuple[int, int]
    to_pos      : Tuple[int, int]
    from_tile   : Tuple[int, int]
    to_tile     : Tuple[int, int]
    piece       : Piece or None
    capture     : Piece or None
    castle      : Piece or None
    event       : int

class Board:

    def __init__(self) -> None:
        self.board = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), 0, 32)
        self.board.fill((220,220,220))

        self.logger: List[MoveLog] = list()
        self.tiles: Dict[str, Piece] = dict()
        self.tiles_position: Dict[str, Tuple[int,int]] = dict()
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

        self.starting_positions = {
            Pawn    : tiles[1] + tiles[6],
            Rook    : ['a1', 'a8', 'h1', 'h8'],
            Bishop  : ['c1', 'c8', 'f1', 'f8'],
            Knight  : ['b1', 'b8', 'g1', 'g8'],
            King    : ['e1', 'e8'],
            Queen   : ['d1', 'd8']
        }

        for x, tile_group in enumerate(tiles):
            for y, tile in enumerate(tile_group):
                position = (60*y,60*x)
                self.tiles.update({tile: None})
                self.tiles_position.update({position: tile})

                for piece, placement in self.starting_positions.items():
                    if tile in placement:
                        color = BLACK_PIECE if int(tile[1:]) >= 7 else WHITE_PIECE
                        piece = piece(tile=tile, color=color, position=position)
                        self.board.blit(piece.load_image, position)
                        self.tiles[tile] = piece

    
    def select(self) -> None:
        tile, _ = self._get_event()
        self.piece = self.tiles[tile]

        if self.piece:
            self.piece_is_moving = True
            self.move_validation()
            self.refresh()
            self.tiles[tile] = None

            
    def release(self) -> None:
        event = EVENT_MOVE
        capture = None
        castle = None

        if self.piece:
            tile, position = self._get_event()
            validated = self.release_validation(tile, position)
            
            if not validated:
                self.reset_piece_location()

            elif validated:

                if isinstance(self.piece, Pawn) and self.has_en_passant:
                    self.tiles[self.logger[-1].piece.tile] = None
                    event = EVENT_ENPASSANT
                    capture = self.logger[-1].piece


                if isinstance(self.piece, King):
                    if self.piece.can_castle():
                        event = EVENT_CASTLE
                        capture, castle = self.castle(tile[:1])

                self.log(position, tile, capture, event, castle)

                self.tiles[self.piece.tile] = None

                if not self.piece.has_moved:
                    self.piece.has_moved = True

                self.piece.position = position
                self.piece.tile = tile
                self.tiles[tile] = self.piece

        self.reset_board_movement()
        self.refresh()


    def release_validation(self, tile, position) -> bool:
        '''
        Validates the following:
        1. That a piece can only take of the opposite color.
        2. Possible piece positions.
        3. No node position to move to.
        4. That its the corret color to move.
        '''
    
        if any([
            self.whos_turn() != self.piece.color,
            self.piece == self.tiles[tile],
            position not in self.valid_moves
        ]):
            return False

        return True


    def move(self) -> None:
        x, y = self.event_pos
        if self.piece and pygame.mouse.get_focused():
            self.refresh()
            self.board.blit(self.piece.load_image, (x-35, y-35))

    
    def move_validation(self) -> None:
   
        for motion, positions in enumerate(self.piece.get_moves().values()):
            for pos in positions:
                tile = self.tiles_position.get(pos)
                if tile:
                    self.valid_moves.append(pos)

                    if other := self.tiles[tile]:
                        
                        if self.piece.color == other.color:
                            self.valid_moves.remove(pos)

                            if not isinstance(self.piece, Knight): #allow knight to jump over same color
                                break

                        elif self.piece.color != other.color:

                            if isinstance(self.piece, Pawn) and motion == 2: #pawn cant take piece in front of it
                                self.valid_moves.remove(pos)
                                break
                            
                            if not isinstance(self.piece, Knight): #allow knight to jump over diff color
                                break
                    
                    elif isinstance(self.piece, Pawn) and motion < 2: #dont allow pawn to move diagonal on empty node
                        if pos != self.en_passant(): #check for en_passant
                            self.valid_moves.remove(pos)


    def undo_move(self) -> None:
        if self.logger:
            move = self.logger[-1]

            if move.from_tile in sum(list(self.starting_positions.values()), []):
                move.piece.has_moved = False

            move.piece.position = move.from_pos
            move.piece.tile = move.from_tile
            self.tiles[move.from_tile] = move.piece

            if move.capture:
                self.tiles[move.capture.tile] = move.capture
                if move.event == EVENT_CASTLE:
                    self.tiles[move.castle.tile] = None

            self.tiles[move.to_tile] = None

            del self.logger[-1]

        self.refresh()


    def reset_piece_location(self) -> None:
        self.tiles[self.piece.tile] = self.piece

        
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
        for node in self.tiles.values():
            if isinstance(node, Piece):
                self.board.blit(node.load_image, node.position)

        if self.valid_moves:
            for area in self.valid_moves:
                POSSIBLE_MOVES_BORDER.fill((152,251,152)) #green
                self.board.blit(POSSIBLE_MOVES_BORDER, area)
            

    def en_passant(self) -> bool:
        if self.logger and self.whos_turn() == self.piece.color:
            previous_move = self.logger[-1]

            if isinstance(previous_move.piece, Pawn):
                if previous_move.from_pos[1] == previous_move.piece.starting_position:
                    passant = getattr(previous_move.piece, previous_move.piece._reverse_orient)(1)
                    
                    if any([
                        self.piece.left(1) == previous_move.to_pos, 
                        self.piece.right(1) == previous_move.to_pos
                    ]):
                        self.has_en_passant = True
                        return passant
        return False


    def castle(self, file) -> Tuple[Rook, Rook] or Tuple[None, None]:
        direction = 'right' if file == 'g' else 'left'
        distance = 3 if direction == 'right' else 4
        movefunc = getattr(self.piece, direction)

        rook = self.tiles[self.tiles_position[movefunc(distance)]]
        prev_rook = Rook(rook.tile, rook.color, rook.position)

        if rook and rook.can_castle():
            self.tiles[rook.tile] = None
            rook.position = movefunc(1)
            rook.tile = self.tiles_position[rook.position]
            self.tiles[rook.tile] = rook
            return prev_rook, rook
        return None, None


    def log(self, to_position: Tuple[int, int], to_tile: Tuple[int, int], 
        capture: Piece = None, event: int = 0, castle: Piece = None):

        self.logger.append(
            MoveLog(
                from_pos    =self.piece.position, 
                to_pos      =to_position, 
                from_tile   =self.piece.tile, 
                to_tile     =to_tile, 
                piece       =self.piece,
                capture     =capture,
                castle      =castle,
                event       =event
            )
        )
        print(self.logger[-1])



    def __draw_board(self) -> None:
        self.board.blit(BOARD_IMAGE, BOARD_OFFSET)


    def _get_event(self) -> Tuple[str, Tuple[int, int]] or None:
        x, y = self.event_pos
        for pos, tile in self.tiles_position.items():
            if x in range(pos[0] + 60) and y in range(pos[1] + 60):
                return tile, pos
        return None, None
            

    


    