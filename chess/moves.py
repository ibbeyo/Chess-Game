
class Moves:
    def __init__(self) -> None:
        self.sq: int = 60
        self.diagonal_pattern: list = [
            ('left', 'up'), ('left', 'down'), 
            ('right', 'up'), ('right', 'down')
        ]
        self.max_move: int = 7


    def up(self,i) -> tuple:
        return (self.x, self.y - (self.sq*i))
        

    def down(self,i) -> tuple:
        return (self.x, self.y + (self.sq*i))

    
    def left(self,i) -> tuple:
        return (self.x - (self.sq*i), self.y)
    

    def right(self,i) -> tuple:
        return (self.x + (self.sq*i), self.y)


    def diagonals(self) -> dict:
        moves = {}
        for n, (fX, fY) in enumerate(self.diagonal_pattern):
            moves.update({
                n: [(getattr(self, fX)(i)[0], getattr(self, fY)(i)[1])
                        for i in range(1, self.max_move + 1)
                ]
            })
        return moves


    def cross(self) -> dict:
        moves = {}
        axis = ['up', 'down', 'left', 'right']
        for n, func in enumerate(axis):
            moves.update({
                n: [getattr(self, func)(i) for i in range(1, self.max_move + 1)]
            })
        return  moves


    def lshape(self) -> dict:
        moves = {}
        for i in range(1, 3):
            moves.update({
                i: [(getattr(self, fX)(3-i)[0], getattr(self, fY)(i)[1])
                        for fX, fY in self.diagonal_pattern
                ]
            })
        return moves


    def all(self) -> dict:
        _all = list(self.diagonals().values()) + list(self.cross().values())
        return {n: m for n, m in enumerate(_all)}