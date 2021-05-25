import pygame
from string import ascii_lowercase
from typing import Tuple, List, Dict, Optional
from dataclasses import dataclass

from .movement import Node
from .pieces import Colors, Piece, Rook, King, Pawn, Queen, Bishop, Knight


WINDOW_HEIGHT, WINDOW_WIDTH = (480, 480)

BOARD_OFFSET = (-17, -17)
BOARD_IMAGE = pygame.image.load('./images/board.jpg')

POSSIBLE_MOVES_BORDER = pygame.Surface((60,60))
POSSIBLE_MOVES_BORDER.set_alpha(128)


@dataclass
class History:
    from_position   : Node
    to_position     : Node
    from_tile       : str
    to_tile         : str
    main_piece      : Piece
    caputered_piece : Optional[Piece] = None
    castled_piece   : Optional[Piece] = None


class Board:
    def __init__(self) -> None:
        self.board = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), 0, 32)
        self.board.fill((200,200,200))

        self.selected_piece: Piece = None
        self.selected_piece_tile: str = None
        self.selected_piece_position: Node = None
        self.selected_piece_is_moving: bool = False

        self.valid_moves: List[Node] = list()

        self.nodes: Dict[str, Piece] = dict()
        self.position_to_tile: Dict[Node, str] = dict()

        self.history: List[History] = list()
        self.castling_event: Dict[str, Rook] = dict()
        self.enpassant_event: Node = None
        

    def new_game(self, white: bool = True) -> None:
        '''Start a New Game. Defaults as White, set False to play as Black.'''
        self._playing_as_white = white

        ranks = range(8,0,-1)
        files = ascii_lowercase[:8]

        if not self._playing_as_white:
            ranks = range(1,9)
            files = list(reversed(files))

        tiles = [[file + str(rank) for file in files] for rank in ranks]

        starting_positions = {
            Pawn    : tiles[1]+tiles[6],
            Rook    : ['a1', 'a8', 'h1', 'h8'],
            King    : ['e1', 'e8'],
            Bishop  : ['c1', 'c8', 'f1', 'f8'],
            Queen   : ['d1', 'd8'],
            Knight  : ['b1', 'b8', 'g1', 'g8']
        }

        for y, tile_group in enumerate(tiles):
            for x, tile in enumerate(tile_group):
                position = (60*x, 60*y)
                self.nodes.update({tile: None})
                self.position_to_tile.update({position:tile})

                for piece, placement in starting_positions.items():
                    if tile in placement:
                        self.nodes[tile] = piece(tile=tile, position=position)
        self.refresh()

    
    def refresh(self) -> None:
        '''Update board and all piece images with new locations/data.'''

        self.board.blit(BOARD_IMAGE, BOARD_OFFSET)

        for node in self.nodes.values():
            if isinstance(node, Piece):
                self.board.blit(node.load_image, node.position)

        if self.valid_moves:
            for position in self.valid_moves:
                POSSIBLE_MOVES_BORDER.fill((152,251,152))
                self.board.blit(POSSIBLE_MOVES_BORDER, position)
        return

        
    def select(self, event_position) -> None:
        position, tile = self.__get_event__(event_position=event_position)
        node = self.nodes[tile]

        if isinstance(node, Piece):
            self.selected_piece = node
            self.selected_piece_is_moving = True
            self.selected_piece_position = position
            self.selected_piece_tile = tile
            self.move_validation()
            self.refresh()
            self.nodes[node.tile] = None
        return


    def move(self, event_position) -> None:
        x, y = event_position
        if self.selected_piece and pygame.mouse.get_focused():
            self.refresh()
            self.board.blit(self.selected_piece.load_image, (x-35, y-35))

    
    def move_validation(self) -> None:
    
        for orient, positions in self.selected_piece.get_moves().items():
            
            if isinstance(self.selected_piece, King):
                if orient == 'castle':
                    self.eval_castling(positions)
                    continue

            for pos in positions:
                try:
                    node = self.nodes[self.position_to_tile[pos]]
                except KeyError:
                    continue
                
                self.valid_moves.append(pos)

                if isinstance(node, Piece):
                    if self.selected_piece == node:
                        self.valid_moves.remove(pos)
                        if not isinstance(self.selected_piece, Knight):
                            break
                        
                    elif self.selected_piece != node:
                        if isinstance(self.selected_piece, Pawn):
                            if orient == 'capture':
                                continue
                            self.valid_moves.remove(pos)
                            break
                        if not isinstance(self.selected_piece, Knight):
                            break

                elif isinstance(self.selected_piece, Pawn):
                    if orient != 'capture' or self.eval_en_passant(pos):
                        continue
                    self.valid_moves.remove(pos)


    def move_reset(self):
        if self.history:
            move = self.history[-1]

            if move.from_position == move.main_piece.starting_position:
                move.main_piece.has_moved = False

            move.main_piece.position = move.from_position
            move.main_piece.tile = move.from_tile
            self.nodes[move.from_tile] = move.main_piece

            self.nodes[move.to_tile] = None

            if isinstance(move.caputered_piece, Piece):
                self.nodes[move.caputered_piece.tile] = move.caputered_piece

                if isinstance(move.castled_piece, Rook):
                    self.nodes[move.castled_piece.tile] = None

            del self.history[-1]

        self.refresh()


    def eval_en_passant(self, position) -> bool:
        if self.history and self.whos_turn() == self.selected_piece.color:
            prev_move = self.history[-1]

            if isinstance(prev_move.main_piece, Pawn):
                if prev_move.from_position[1] == prev_move.main_piece.starting_position[1]:
                    if any([
                        self.selected_piece.left(1) == prev_move.to_position,
                        self.selected_piece.right(1) == prev_move.to_position
                    ]):
                        if position == prev_move.main_piece.en_passant_sq():
                            self.enpassant_event = position
                            return True
        return False


    def eval_castling(self, positions: dict) -> bool:
        for direction, position in positions.items():

            func = getattr(self.selected_piece, direction)

            if self._playing_as_white:
                dist = 3 if direction == 'right' else 4
            else:
                dist = 4 if direction == 'right' else 3

            try:
                for i in range(1, dist):
                    tile = self.position_to_tile[func(i)]
                    node = self.nodes[tile]
                    if isinstance(node, Piece) and node == self.selected_piece:
                        raise Exception
            except Exception:
                continue

            rook = self.nodes[self.position_to_tile[func(dist)]]

            if isinstance(rook, Rook) and not rook.has_moved:
                self.castling_event.update({
                    self.position_to_tile[position] : {
                        'after': {
                            'tile': self.position_to_tile[func(1)],
                            'pos': func(1)
                        }, 
                        'before': {
                            'tile': rook.tile,
                            'pos': rook.position
                        }
                    }
                })
                self.valid_moves.append(position)
        

    def release(self, event_position) -> None:
        position, tile = self.__get_event__(event_position=event_position)
        node = self.nodes[tile]

        if self.selected_piece:
            if any([
                self.whos_turn() != self.selected_piece.color,
                self.selected_piece.tile == tile,
                position not in self.valid_moves
                ]):

                self.reset_piece_state()

            else:
                self.history.append(
                    History(
                        from_position=self.selected_piece_position,
                        to_position=position,
                        from_tile=self.selected_piece_tile,
                        to_tile=tile,
                        main_piece=self.selected_piece,
                        caputered_piece=node
                    )
                )

                if isinstance(self.selected_piece, King) and tile in self.castling_event:
                    castle = self.castling_event[tile]
                    rook = self.nodes[castle['before']['tile']]

                    self.history[-1].caputered_piece = Rook(rook.tile, rook.position)

                    rook.tile = castle['after']['tile']
                    rook.position = castle['after']['pos']

                    self.nodes[rook.tile] = rook
                    self.nodes[castle['before']['tile']] = None
                    self.history[-1].castled_piece = rook

                elif isinstance(self.selected_piece, Pawn):
                    if self.enpassant_event == position:
                        self.nodes[self.history[-2].main_piece.tile] = None
                        self.history[-1].caputered_piece = self.history[-2].main_piece

                self.selected_piece.position = position
                self.selected_piece.tile = tile
                self.selected_piece.has_moved = True

                self.nodes[tile] = self.selected_piece

        self.reset_board_state()
        self.refresh()


    def reset_piece_state(self):
        self.nodes[self.selected_piece.tile] = self.selected_piece


    def reset_board_state(self):
        self.selected_piece = None
        self.selected_piece_is_moving = False
        self.enpassant_event = None
        self.valid_moves.clear()
        self.castling_event.clear()


    def whos_turn(self) -> str:
        if len(self.history) % 2 == 0:
            return Colors.WHITE
        return Colors.BLACK


    def __get_event__(self, event_position) -> Tuple[Node, str]:
        '''Gets the closest position and tile based on the event position'''

        x, y = event_position
        for position, tile in self.position_to_tile.items():
            if x in range(position[0] + 60) and y in range(position[1] + 60):
                return (position, tile)
        return (None, None)