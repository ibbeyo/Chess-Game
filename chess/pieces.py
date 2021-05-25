import pygame

from .movement import Movement, Node

class Colors:
    BLACK: str = 'black'
    WHITE: str = 'white'


class Piece(Movement):
    def __init__(self, tile: str, position: Node) -> None:
        super().__init__()

        self.tile = tile
        self.position = position
        self.starting_tile = tile
        self.starting_position = position
        self.has_moved: bool = False
        self.name: str = self.__class__.__name__
        self.symbol: str = self.name[:1]
        self.max_move: int = 7
        self.color = Colors.BLACK if self.rank >= 7 else Colors.WHITE
        self._load_image: pygame.Surface = None
        self._color: str = None


    @property
    def rank(self) -> int:
        return int(self.tile[1:])


    @property
    def file(self) -> str:
        return self.tile[:1]


    @property
    def load_image(self) -> pygame.Surface:
        if isinstance(self._load_image, pygame.Surface):
            return self._load_image

        img_path = f'./images/{self.color}/{self.name}.png'
        self._load_image = pygame.image.load(img_path)
        return self._load_image


    def get_moves(self) -> dict:
        return
    

    def __eq__(self, o: object) -> bool:
        if isinstance(o, Piece):
            if self.color == o.color:
                return True
        return False


    def __ne__(self, o: object) -> bool:
        if isinstance(o, Piece):
            if self.color != o.color:
                return True
        return False


class Pawn(Piece):
    def __init__(self, tile: str, position: Node) -> None:
        super().__init__(tile, position)

        self.symbol = ''
        self.max_move = 1
        self.orient = 'up' if self.starting_position[1] == 360 else 'down'


    def en_passant_sq(self) -> Node:
        reversed_orient = 'down' if self.orient == 'up' else 'up'
        backone = getattr(self, reversed_orient)(1)
        if backone == self.starting_position:
            return None
        return backone

    
    def get_moves(self) -> dict:
        amt = 1 if self.has_moved else 2
        captures = self.diagonals()
        moves = {
            self.orient :[getattr(self, self.orient)(i) for i in range(1, amt + 1)],
            'capture': captures['left' + self.orient] + captures['right' + self.orient]
        }
        return moves



class Knight(Piece):
    def __init__(self, tile: str, position: Node) -> None:
        super().__init__(tile, position)
        
        self.symbol = 'N'


    def get_moves(self) -> dict:
        return self.lshape()


class King(Piece):
    def __init__(self, tile: str, position: Node) -> None:
        super().__init__(tile, position)

        self.max_move = 1

    
    def get_moves(self) -> dict:
        moves = {**self.cross(), **self.diagonals()}
        if not self.has_moved:
            moves.update({
                'castle': {
                    'left': self.left(2), 
                    'right': self.right(2)
                }
            })
        return moves
        

class Rook(Piece):
    def __init__(self, tile: str, position: Node) -> None:
        super().__init__(tile, position)


    def get_moves(self) -> dict:
        return self.cross()


class Queen(Piece):
    def __init__(self, tile: str, position: Node) -> None:
        super().__init__(tile, position)


    def get_moves(self) -> dict:
        return {**self.cross(), **self.diagonals()}


class Bishop(Piece):
    def __init__(self, tile: str, position: Node) -> None:
        super().__init__(tile, position)
    

    def get_moves(self) -> dict:
        return self.diagonals()
