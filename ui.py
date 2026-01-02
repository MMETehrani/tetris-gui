# ui.py
"""
Manages all graphical user interface (UI) elements and rendering for the game.

This module defines the `ArcadeUI` class, which is responsible for drawing everything
the player sees, including the game board, pieces, sidebar, text, and special effects
like pulsing animations and neon borders.
"""
import pygame
import math
from settings import *

class ArcadeUI:
    """
    Handles all the drawing operations for the game's UI.
    
    This class is instantiated in the main app and is passed the main canvas
    on which to draw all elements.
    """
    def __init__(self, screen):
        """
        Initializes the UI, loading fonts and setting up animation variables.

        Args:
            screen (pygame.Surface): The surface to draw all UI elements onto.
        """
        self.screen = screen 
        # Load various fonts for different UI elements.
        self.font_main = pygame.font.SysFont("Consolas", 22, bold=True)
        self.font_title = pygame.font.SysFont("Verdana", 40, bold=True)
        self.font_pixel = pygame.font.SysFont("Comic Sans MS", 16, bold=True) 
        self.font_small = pygame.font.SysFont("Consolas", 14, bold=True)
        
        # A simple counter that increments each frame to drive animations.
        self.animation_tick = 0

    def update_animation(self):
        """Increments the animation tick on each frame to create pulsing/breathing effects."""
        self.animation_tick += 0.1

    def truncate_text(self, text, font, max_width):
        """
        Truncates a string to fit within a maximum width, adding "..." at the end.

        Args:
            text (str): The text to truncate.
            font (pygame.font.Font): The font used to render the text.
            max_width (int): The maximum allowed width in pixels.

        Returns:
            str: The truncated text.
        """
        if font.size(text)[0] <= max_width:
            return text
        temp = text
        # Remove characters one by one until the text fits.
        while font.size(temp + "...")[0] > max_width and len(temp) > 0:
            temp = temp[:-1]
        return temp + "..."

    def draw_background_grid(self):
        """Draws the dark, futuristic grid on the background."""
        self.screen.fill(COLOR_BG_DARK)
        for x in range(0, SCREEN_WIDTH, 40):
            pygame.draw.line(self.screen, COLOR_GRID_LINE, (x, 0), (x, SCREEN_HEIGHT))
        for y in range(0, SCREEN_HEIGHT, 40):
            pygame.draw.line(self.screen, COLOR_GRID_LINE, (0, y), (SCREEN_WIDTH, y))

    def draw_3d_block(self, x, y, color_tuple, size=BLOCK_SIZE):
        """
        Draws a single Tetris block with a pseudo-3D effect.

        Args:
            x (int): The x-coordinate of the top-left corner.
            y (int): The y-coordinate of the top-left corner.
            color_tuple (tuple): A tuple of (base, light, dark) colors.
            size (int, optional): The size of the block. Defaults to BLOCK_SIZE.
        """
        base_color, light_color, dark_color = color_tuple
        rect = (x, y, size, size)
        pygame.draw.rect(self.screen, base_color, rect)
        # Draw light highlights to create a top/left bevel.
        pygame.draw.polygon(self.screen, light_color, [(x, y), (x + size, y), (x + size - 4, y + 4), (x + 4, y + 4)])
        # Draw dark shadows to create a bottom/right bevel.
        pygame.draw.polygon(self.screen, dark_color, [(x + size, y + size), (x, y + size), (x + 4, y + size - 4)])
        # Draw a slightly smaller inner rectangle to complete the effect.
        pygame.draw.rect(self.screen, base_color, (x + 8, y + 8, size - 16, size - 16))

    def draw_neon_border(self, rect):
        """
        Draws a glowing, pulsing neon border around a rectangle.

        Args:
            rect (tuple): The (x, y, width, height) of the rectangle.
        """
        # Use a sine wave based on the animation tick to create a pulsing glow.
        pulse = (math.sin(self.animation_tick) + 1) / 2  # Normalize to 0-1 range
        r = int(COLOR_BORDER_GLOW[0] * pulse)
        g = int(COLOR_BORDER_GLOW[1] * 0.8 + (pulse * 50))
        b = int(COLOR_BORDER_GLOW[2])
        # Draw the outer glow.
        pygame.draw.rect(self.screen, (r, g, b), (rect[0]-2, rect[1]-2, rect[2]+4, rect[3]+4), 2, border_radius=5)
        # Draw the inner, solid white border.
        pygame.draw.rect(self.screen, (255, 255, 255), rect, 2, border_radius=5)

    def draw_panel(self, rect, title=None):
        """
        Draws a standard UI panel with a background and border.

        Args:
            rect (tuple): The (x, y, width, height) of the panel.
            title (str, optional): A title to display at the top of the panel. Defaults to None.
        """
        pygame.draw.rect(self.screen, COLOR_PANEL_BG, rect, border_radius=10)
        pygame.draw.rect(self.screen, (60, 60, 80), rect, 2, border_radius=10)
        if title:
            text_surf = self.font_main.render(title, True, (255, 255, 255))
            self.screen.blit(text_surf, (rect[0] + 10, rect[1] + 10))

    def draw_text_pulsing(self, text, center_pos, color, font="title"):
        """
        Draws text that gently scales up and down.

        Args:
            text (str): The text to draw.
            center_pos (tuple): The (x, y) center position for the text.
            color (tuple): The RGB color of the text.
            font (str, optional): The font to use ('title' or 'main'). Defaults to "title".
        """
        font_obj = self.font_title if font == "title" else self.font_main
        scale = 1.0 + (math.sin(self.animation_tick * 2) * 0.05)
        base_surf = font_obj.render(text, True, color)
        width = int(base_surf.get_width() * scale)
        height = int(base_surf.get_height() * scale)
        scaled_surf = pygame.transform.scale(base_surf, (width, height))
        rect = scaled_surf.get_rect(center=center_pos)
        
        # Draw a simple black shadow for better readability.
        shadow_surf = font_obj.render(text, True, (0,0,0))
        shadow_surf = pygame.transform.scale(shadow_surf, (width, height))
        self.screen.blit(shadow_surf, (rect.x + 4, rect.y + 4))
        
        self.screen.blit(scaled_surf, rect)

    def draw_button_circle(self, text, center_pos, color, key_code, size=25):
        """
        Draws a circular button indicator for the controls screen.

        Args:
            text (str): The description of the action (e.g., "Rotate").
            center_pos (tuple): The (x, y) center of the circle.
            color (tuple): The RGB color of the circle.
            key_code (str): The key to display inside the circle (e.g., "UP").
            size (int, optional): The radius of the circle. Defaults to 25.
        """
        pygame.draw.circle(self.screen, color, center_pos, size)
        # Add a small white highlight.
        pygame.draw.circle(self.screen, (255, 255, 255), (center_pos[0]-6, center_pos[1]-6), 4)
        
        key_surf = self.font_small.render(key_code, True, (0,0,0))
        key_rect = key_surf.get_rect(center=center_pos)
        self.screen.blit(key_surf, key_rect)
        
        # Display the action text below the button.
        desc_surf = self.font_main.render(text, True, (220, 220, 220))
        desc_rect = desc_surf.get_rect(center=(center_pos[0], center_pos[1] + 35))
        self.screen.blit(desc_surf, desc_rect)

    def draw_sidebar(self, x, y, score, leaderboard, logic, current_username):
        """
        Draws the entire right-hand sidebar, including player name, score, next piece, and leaderboard.
        
        Args:
            x (int): The starting x-coordinate for the sidebar.
            y (int): The starting y-coordinate for the sidebar.
            score (int): The current player's score.
            leaderboard (list): The list of top players and scores.
            logic (TetrisLogic): The game logic object, used to get the next piece.
            current_username (str): The current player's name.
        """
        current_y = y 

        # 1. Player Name Panel
        self.draw_panel((x, current_y, 250, 50), "PILOT")
        name_surf = self.font_main.render(current_username, True, (0, 255, 255))
        name_rect = name_surf.get_rect(center=(x + 125, current_y + 30))
        self.screen.blit(name_surf, name_rect)
        
        current_y += 60 # Add spacing for the next panel

        # 2. Score Panel
        self.draw_panel((x, current_y, 250, 80), "SCORE")
        self.draw_text_pulsing(str(score), (x + 125, current_y + 45), TEXT_COLOR_ACCENT, "main")
        
        current_y += 90

        # 3. Next Piece Panel
        self.draw_panel((x, current_y, 250, 120), "NEXT")
        if logic.next_piece_idx is not None:
             piece = logic.SHAPES[logic.next_piece_idx]
             color_tuple = SHAPE_COLORS[logic.next_piece_idx]
             
             # Center the piece preview inside the panel.
             p_width = len(piece[0]) * 25
             p_height = len(piece) * 25
             center_panel_x = x + 125
             center_panel_y = current_y + 70 # Position below the panel title
             offset_x = center_panel_x - (p_width // 2)
             offset_y = center_panel_y - (p_height // 2)
             
             for cy, row in enumerate(piece):
                 for cx, val in enumerate(row):
                     if val:
                         # Draw smaller blocks for the preview.
                         self.draw_3d_block(offset_x + cx*25, offset_y + cy*25, color_tuple, size=25)
        
        current_y += 130

        # 4. Leaderboard Panel
        # Calculate the remaining height to fill the space down to the bottom of the game area.
        remaining_height = (GAME_AREA_HEIGHT + y) - current_y
        if remaining_height < 200: remaining_height = 300 # Ensure a minimum height.

        self.draw_panel((x, current_y, 250, remaining_height), "TOP PILOTS")
        
        # Draw the top 10 leaderboard entries.
        for i, user in enumerate(leaderboard[:10]):
            row_y = current_y + 40 + (i * 30)
            if row_y + 20 > current_y + remaining_height: break # Stop if there's no more room.
            
            # Color code the top 3 ranks.
            rank_color = (150, 150, 150)
            if i == 0: rank_color = (255, 215, 0) # Gold
            elif i == 1: rank_color = (192, 192, 192) # Silver
            elif i == 2: rank_color = (205, 127, 50) # Bronze
            
            rank_str = f"{i+1}."
            name_str = f" {user['name']}"
            
            # Render rank, name (truncated), and score.
            rank_surf = self.font_small.render(rank_str, True, rank_color)
            self.screen.blit(rank_surf, (x + 15, row_y))
            
            name_surf = self.font_small.render(self.truncate_text(name_str, self.font_small, 130), True, (220, 220, 220))
            self.screen.blit(name_surf, (x + 40, row_y))
            
            score_surf = self.font_small.render(str(user['score']), True, rank_color)
            score_rect = score_surf.get_rect(right=x + 235, centery=row_y + 8)
            self.screen.blit(score_surf, score_rect)

    def draw_overlay_controls(self):
        """Draws the 'How to Play' overlay screen."""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(220)
        overlay.fill((0,0,0))
        self.screen.blit(overlay, (0,0))

        center_x, center_y = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
        rect = (center_x - 300, center_y - 200, 600, 400)
        self.draw_neon_border(rect)
        pygame.draw.rect(self.screen, COLOR_PANEL_BG, rect)

        self.draw_text_pulsing("HOW TO PLAY", (center_x, center_y - 150), (0, 255, 255), "title")

        # Draw the button indicators for each control.
        start_y = center_y - 50
        gap_x = 130
        
        self.draw_button_circle("Rotate", (center_x - 1.5*gap_x, start_y), (100, 100, 255), "UP", 35)
        self.draw_button_circle("Move", (center_x - 0.5*gap_x, start_y), (100, 255, 100), "< >", 35)
        self.draw_button_circle("Drop", (center_x + 0.5*gap_x, start_y), (255, 100, 100), "SPC", 35)
        self.draw_button_circle("Pause", (center_x + 1.5*gap_x, start_y), (255, 200, 50), "P", 35)

        msg = self.font_pixel.render("PRESS ENTER TO START GAME", True, (150, 150, 150))
        self.screen.blit(msg, (center_x - 130, center_y + 120))