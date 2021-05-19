from typing import Dict, Tuple, List


class Movement:
    def __init__(self) -> None:

        self.max_move = 7
        self.sq = 60

    @property
    def x(self) -> int:
        return self.position[0]


    @property
    def y(self) -> int:
        return self.position[1]


    def up(self, y) -> Tuple[int,int]:
        return (self.x, self.y - (self.sq * y))

    
    def down(self, y) -> Tuple[int,int]:
        return (self.x, self.y + (self.sq * y))


    def left(self, x) -> Tuple[int,int]:
        return (self.x - (self.sq * x), self.y)

    
    def right(self, x) -> Tuple[int,int]: 
        return (self.x + (self.sq * x), self.y)


    def diagonals(self, left_up=True, left_down=True, right_up=True, right_down=True) -> Dict[str, List[Tuple[int,int]]]:
        arr = {'leftup': [], 'leftdown': [], 'rightup': [], 'rightdown': []}
        for i in range(1, self.max_move + 1):
            left, right = self.left(i)[0], self.right(i)[0]
            up, down = self.up(i)[1], self.down(i)[1]

            if left_up:
                arr['leftup'].append((left, up))
            if left_down:
                arr['leftdown'].append((left, down))
            if right_up:
                arr['rightup'].append((right, up))
            if right_down:
                arr['rightdown'].append((right, down))
        return arr
            

    def cross(self) -> Dict[str, List[Tuple[int,int]]]:
        arr = {'up': [], 'down': [], 'left': [], 'right': []}
        for i in range(1, self.max_move + 1):
            arr['up'].append(self.up(i))
            arr['down'].append(self.down(i))
            arr['left'].append(self.left(i))
            arr['right'].append(self.right(i))
        return arr


    def lshape(self) -> Dict[str, List[Tuple[int,int]]]:
        arr = {'leftup': [], 'leftdown': [], 'rightup': [], 'rightdown': []}
        for i in range(1, 3):
            left, right = self.left(3-i)[0], self.right(3-i)[0]
            up, down = self.up(i)[1], self.down(i)[1]
            arr['leftup'].append((left, up))
            arr['leftdown'].append((left, down))
            arr['rightup'].append((right, up))
            arr['rightdown'].append((right, down))
        return arr