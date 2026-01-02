# logic.py
"""
Handles the core game logic for the Tetris game.

This module defines the tetromino shapes, the game board, and the rules for
how pieces move, rotate, and interact with the board. It manages the game state,
including score, game over status, and the current and next pieces.
"""
import random
from settings import *

# Define the seven standard tetromino shapes (I, O, T, S, Z, J, L).
# Each number represents a filled block in the piece's grid.
SHAPES = [
    [[1, 1, 1, 1]],          # I shape
    [[1, 1], [1, 1]],        # O shape
    [[0, 1, 0], [1, 1, 1]],  # T shape
    [[0, 1, 1], [1, 1, 0]],  # S shape
    [[1, 1, 0], [0, 1, 1]],  # Z shape
    [[1, 0, 0], [1, 1, 1]],  # J shape
    [[0, 0, 1], [1, 1, 1]]   # L shape
]

class TetrisLogic:
    """
    Manages the state and mechanics of the Tetris game.
    
    This class encapsulates the game board, the current and next pieces,
    player score, and all the core functions required to play the game.
    """
    def __init__(self):
        """Initializes the Tetris game logic."""
        # This reference is needed for the main loop to render the next piece.
        self.SHAPES = SHAPES 
        self.reset()

    def reset(self):
        """Resets the game to its initial state."""
        self.board = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.score = 0
        self.game_over = False
        self.current_piece = None
        self.current_color_idx = 0
        self.piece_x = 0
        self.piece_y = 0
        # Pre-select the next piece to be displayed in the UI.
        self.next_piece_idx = random.randint(0, len(SHAPES) - 1)
        self.spawn_piece()

    def spawn_piece(self):
        """
        Spawns a new piece at the top of the board.
        
        The new piece becomes the one that was previously the "next" piece,
        and a new "next" piece is randomly chosen. If the new piece collides
        immediately, the game is over.
        """
        self.current_piece = SHAPES[self.next_piece_idx]
        self.current_color_idx = self.next_piece_idx
        
        self.next_piece_idx = random.randint(0, len(SHAPES) - 1)
        
        # Position the new piece horizontally centered at the top of the board.
        self.piece_x = GRID_WIDTH // 2 - len(self.current_piece[0]) // 2
        self.piece_y = 0
        
        # If there's no room for the new piece, the game is over.
        if self.check_collision(self.current_piece, self.piece_x, self.piece_y):
            self.game_over = True

    def check_collision(self, shape, off_x, off_y):
        """
        Checks if a piece at a given position collides with the board boundaries
        or with already locked pieces.

        Args:
            shape (list of lists): The piece's matrix representation.
            off_x (int): The horizontal position (offset) of the piece on the board.
            off_y (int): The vertical position (offset) of the piece on the board.

        Returns:
            bool: True if there is a collision, False otherwise.
        """
        for cy, row in enumerate(shape):
            for cx, val in enumerate(row):
                if val: # Only check filled parts of the piece grid.
                    # Check for collision with the walls or the floor.
                    if off_x + cx < 0 or off_x + cx >= GRID_WIDTH or off_y + cy >= GRID_HEIGHT:
                        return True
                    # Check for collision with other pieces already on the board.
                    # Ensure piece is within the board's vertical bounds before checking array index.
                    if off_y + cy >= 0 and self.board[off_y + cy][off_x + cx]:
                        return True
        return False

    def rotate(self):
        """
        Rotates the current piece 90 degrees clockwise.
        
        The rotation is only applied if the rotated piece does not collide with
        anything.
        """
        if self.game_over: return
        # Pythonic way to rotate a 2D matrix (list of lists) clockwise.
        rotated = [list(row) for row in zip(*self.current_piece[::-1])]
        if not self.check_collision(rotated, self.piece_x, self.piece_y):
            self.current_piece = rotated

    def move(self, dx, dy):
        """
        Moves the current piece horizontally or vertically.

        Args:
            dx (int): The change in horizontal position.
            dy (int): The change in vertical position.

        Returns:
            bool: True if the move was successful, False otherwise.
        """
        if self.game_over: return False
        if not self.check_collision(self.current_piece, self.piece_x + dx, self.piece_y + dy):
            self.piece_x += dx
            self.piece_y += dy
            return True
        return False

    def lock_piece(self):
        """
        Locks the current piece into place on the board.
        
        This transfers the piece's shape from a temporary state to being part
        of the main board grid. It then checks for completed lines and spawns
        the next piece.
        """
        for cy, row in enumerate(self.current_piece):
            for cx, val in enumerate(row):
                if val:
                    # The value stored on the board is the color index + 1,
                    # as 0 is reserved for empty cells.
                    self.board[self.piece_y + cy][self.piece_x + cx] = self.current_color_idx + 1
        self.clear_lines()
        self.spawn_piece()

    def clear_lines(self):
        """
        Checks for and clears any completed horizontal lines on the board.
        
        For each cleared line, the score is increased. The remaining lines
        are shifted down, and new empty lines are added at the top.
        """
        # Create a new board containing only the rows that are not full.
        new_board = [row for row in self.board if any(x == 0 for x in row)]
        
        # Calculate how many lines were cleared.
        lines_cleared = GRID_HEIGHT - len(new_board)
        
        # Add new empty rows at the top of the board for each line cleared.
        for _ in range(lines_cleared):
            new_board.insert(0, [0] * GRID_WIDTH)
            
        self.board = new_board
        
        # Update the score based on the number of cleared lines.
        # A simple scoring model: 100 points per line.
        if lines_cleared > 0:
            self.score += lines_cleared * 100