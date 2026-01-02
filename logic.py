# logic.py
import random
from settings import *

# تعریف شکل‌ها
SHAPES = [
    [[1, 1, 1, 1]], 
    [[1, 1], [1, 1]], 
    [[0, 1, 0], [1, 1, 1]],
    [[0, 1, 1], [1, 1, 0]], 
    [[1, 1, 0], [0, 1, 1]],
    [[1, 0, 0], [1, 1, 1]], 
    [[0, 0, 1], [1, 1, 1]]
]

class TetrisLogic:
    def __init__(self):
        # این خط لازمه تا main.py بتونه شکل‌ها رو ببینه و رسم کنه
        self.SHAPES = SHAPES 
        self.reset()

    def reset(self):
        self.board = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.score = 0
        self.game_over = False
        self.current_piece = None
        self.current_color_idx = 0
        self.piece_x = 0
        self.piece_y = 0
        self.next_piece_idx = random.randint(0, len(SHAPES) - 1)
        self.spawn_piece()

    def spawn_piece(self):
        self.current_piece = SHAPES[self.next_piece_idx]
        self.current_color_idx = self.next_piece_idx
        
        self.next_piece_idx = random.randint(0, len(SHAPES) - 1)
        
        self.piece_x = GRID_WIDTH // 2 - len(self.current_piece[0]) // 2
        self.piece_y = 0
        
        if self.check_collision(self.current_piece, self.piece_x, self.piece_y):
            self.game_over = True

    def check_collision(self, shape, off_x, off_y):
        for cy, row in enumerate(shape):
            for cx, val in enumerate(row):
                if val:
                    if off_x + cx < 0 or off_x + cx >= GRID_WIDTH or off_y + cy >= GRID_HEIGHT:
                        return True
                    if off_y + cy >= 0 and self.board[off_y + cy][off_x + cx]:
                        return True
        return False

    def rotate(self):
        if self.game_over: return
        rotated = [list(row) for row in zip(*self.current_piece[::-1])]
        if not self.check_collision(rotated, self.piece_x, self.piece_y):
            self.current_piece = rotated

    def move(self, dx, dy):
        if self.game_over: return False
        if not self.check_collision(self.current_piece, self.piece_x + dx, self.piece_y + dy):
            self.piece_x += dx
            self.piece_y += dy
            return True
        return False

    def lock_piece(self):
        for cy, row in enumerate(self.current_piece):
            for cx, val in enumerate(row):
                if val:
                    # +1 میکنیم چون 0 یعنی خالی، رنگ‌ها از 1 شروع میشن
                    self.board[self.piece_y + cy][self.piece_x + cx] = self.current_color_idx + 1
        self.clear_lines()
        self.spawn_piece()

    def clear_lines(self):
        new_board = [row for row in self.board if any(x == 0 for x in row)]
        lines = GRID_HEIGHT - len(new_board)
        for _ in range(lines):
            new_board.insert(0, [0] * GRID_WIDTH)
        self.board = new_board
        self.score += lines * 100