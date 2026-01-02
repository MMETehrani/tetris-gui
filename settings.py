# settings.py
"""
Central configuration file for the Tetris: Neon Arcade game.

This file contains all the core constants, such as screen dimensions,
game grid size, colors, and network settings. Centralizing these values
makes it easier to tweak the game's look and feel.
"""
import pygame

# --- Core Display & Performance ---
# The game is designed for this internal "virtual" resolution. All game elements
# are drawn onto a canvas of this size, which is then scaled to fit the actual
# window, preserving the aspect ratio.
SCREEN_WIDTH = 750  
SCREEN_HEIGHT = 800 
FPS = 60

# --- Tetris Game Grid Dimensions ---
BLOCK_SIZE = 35         # Size of a single block in pixels.
GRID_WIDTH = 10         # Number of blocks horizontally.
GRID_HEIGHT = 20        # Number of blocks vertically.
GAME_AREA_WIDTH = GRID_WIDTH * BLOCK_SIZE
GAME_AREA_HEIGHT = GRID_HEIGHT * BLOCK_SIZE

# --- Network Settings ---
# The base URL for the backend API server.
API_URL = "https://tetris-py-api-5unr.vercel.app"

# --- "Neon Arcade" Color Palette ---
# This palette defines the visual theme of the game.
COLOR_BG_DARK = (10, 10, 25)          # Deep blue background.
COLOR_GRID_LINE = (30, 30, 50)        # Faint grid lines on the background.
COLOR_PANEL_BG = (20, 20, 35)         # Background for UI panels (sidebar, popups).
COLOR_BORDER_GLOW = (0, 200, 255)     # Glowing cyan for borders and highlights.

# --- Text Colors ---
TEXT_COLOR_MAIN = (255, 255, 255)     # Default white for most text.
TEXT_COLOR_ACCENT = (255, 215, 0)     # Gold/Yellow for scores and important highlights.

# --- Tetromino Color Palette (Arcade Vivid) ---
# Each piece has a unique color scheme, defined as a tuple of three colors:
# (base_color, light_highlight_color, dark_shadow_color)
# This allows for a pseudo-3D effect on the blocks.
SHAPE_COLORS = [
    ((0, 255, 255), (150, 255, 255), (0, 150, 150)),      # Cyan (I)
    ((255, 220, 0), (255, 255, 150), (180, 150, 0)),      # Yellow (O)
    ((180, 0, 255), (220, 150, 255), (100, 0, 150)),      # Purple (T)
    ((0, 255, 0),   (150, 255, 150), (0, 150, 0)),        # Green (S)
    ((255, 0, 60),  (255, 150, 150), (150, 0, 0)),        # Red (Z)
    ((0, 80, 255),  (100, 150, 255), (0, 0, 150)),        # Blue (J)
    ((255, 120, 0), (255, 180, 100), (180, 80, 0)),       # Orange (L)
]