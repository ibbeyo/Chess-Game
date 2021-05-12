import pygame
from typing import Tuple

from .moves import Moves

BLACK_PIECE = 'black'
WHITE_PIECE = 'white'


class Piece(Moves):
    def __init__(self, tile: str, color: str, position: Tuple[int, int]) -> None:
        super().__init__()
        self.tile = tile
        self.color = color
        self.position = position
        self.has_moved: bool = False
        self._load_image: pygame.Surface = None

    @property
    def x(self):
        return self.position[0]

    
    @property
    def y(self):
        return self.position[1]


    @property
    def load_image(self) -> pygame.Surface:
        if isinstance(self._load_image, pygame.Surface):
            return self._load_image
        
        img_path = f'./images/{self.color}/{self.name}.png'
        self._load_image = pygame.image.load(img_path)
        return self._load_image
    

    def notation(self):
        return self.name[:1]


class Pawn(Piece):
    def __init__(self, tile: str, color: str, position: Tuple[int, int]) -> None:
        super().__init__(tile, color, position)
        self.name: str = 'Pawn'
        self.max_move = 1
        self.starting_position = self.position[1]
        self._orient = 'up' if self.starting_position == 360 else 'down'
        self._reverse_orient = 'down' if self.starting_position == 360 else 'up'
        self.diagonal_pattern = [('left', self._orient), ('right', self._orient)]


    def get_moves(self) -> dict:
        max_move = 1 if self.has_moved else 2
        moves = self.diagonals()
        moves.update({
            len(moves): [
                getattr(self, self._orient)(i) 
                for i in range(1, max_move + 1)
            ]
        })
        return moves


    def notation(self):
        return ''


class Rook(Piece):
    def __init__(self, tile: str, color: str, position: Tuple[int, int]) -> None:
        super().__init__(tile, color, position)
        self.name: str = 'Rook'


    def can_castle(self):
        return False if self.has_moved else True


    def get_moves(self) -> dict:
        return self.cross()


class Bishop(Piece):
    def __init__(self, tile: str, color: str, position: Tuple[int, int]) -> None:
        super().__init__(tile, color, position)
        self.name: str = 'Bishop'

    
    def get_moves(self) -> dict:
        return self.diagonals()


class Knight(Piece):
    def __init__(self, tile: str, color: str, position: Tuple[int, int]) -> None:
        super().__init__(tile, color, position)
        self.name: str = 'Knight'
    

    def get_moves(self) -> dict:
        return self.lshape()


    def notation(self):
        return 'N'


class King(Piece):
    def __init__(self, tile: str, color: str, position: Tuple[int, int]) -> None:
        super().__init__(tile, color, position)
        self.name: str = 'King'
        self.max_move = 1

    
    def can_castle(self):
        return False if self.has_moved else True


    def get_moves(self) -> dict:
        _diagonals = list(self.diagonals().values())
        _cross = self.cross()
        if not self.has_moved:
            _cross[2].append(self.left(2))
            _cross[3].append(self.right(2))

        return {n: m for n, m in enumerate(_diagonals + list(_cross.values()))}


class Queen(Piece):
    def __init__(self, tile: str, color: str, position: Tuple[int, int]) -> None:
        super().__init__(tile, color, position)
        self.name: str = 'Queen'


    def get_moves(self) -> dict:
        _diagonals = list(self.diagonals().values())
        _cross = list(self.cross().values())
        return {n: m for n, m in enumerate(_diagonals + _cross)}