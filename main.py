# main.py
"""
The main entry point and application class for the Tetris: Neon Arcade game.

This module initializes Pygame and all other game modules (UI, Logic, Network, Discord).
It contains the main application class, `MainApp`, which manages the game's state machine,
the main game loop, event handling, and the rendering pipeline.
"""
import pygame
import sys
from discord_manager import DiscordHandler
from settings import *
from ui import ArcadeUI
from logic import TetrisLogic
from network import NetworkManager

class DummySound:
    """A dummy class to prevent crashes when sound files are not available."""
    def play(self, name):
        """Pretends to play a sound but does nothing."""
        pass 

class MainApp:
    """
    The main application class. Manages the game window, states, loop, and modules.
    """
    def __init__(self):
        """
        Initializes the game window, clocks, and all major components.
        Sets up the initial game state.
        """
        pygame.init()
        # The screen is the actual window, which can be resized.
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
        # The canvas is a fixed-size surface where all game elements are drawn.
        # This canvas is then scaled to fit the window, preserving the aspect ratio.
        self.canvas = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        
        pygame.display.set_caption("TETRIS: NEON ARCADE")
        self.clock = pygame.time.Clock()
        
        # Initialize all game components
        self.ui = ArcadeUI(self.canvas)
        self.logic = TetrisLogic()
        self.network = NetworkManager()
        
        # Use the dummy sound class to avoid errors if sounds are not implemented.
        self.sound = DummySound() 
        
        # --- Discord Rich Presence Setup ---
        # Replace with your actual Discord App ID and GitHub repo URL.
        YOUR_APP_ID = "1456684566101102592" 
        YOUR_GITHUB = "https://github.com/AliReza/Tetris/releases"
        self.discord = DiscordHandler(YOUR_APP_ID, YOUR_GITHUB)
        self.discord.update_presence("In Menu", "Waiting to start...")

        # --- Game State Machine ---
        # The game starts in the 'LOGIN' state if no user is saved,
        # otherwise it jumps straight to the 'CONTROLS' screen.
        if self.network.username:
            print(f"Auto-login successful: {self.network.username}")
            self.state = "CONTROLS"
            self.input_text = self.network.username
        else:
            self.state = "LOGIN" 
            self.input_text = "PLAYER 1"
        
        # Fetch the leaderboard from the server at startup.
        self.leaderboard = self.network.get_leaderboard()

    def run(self):
        """
        The main game loop.
        
        This loop continuously handles input, updates game state, and draws the screen
        until the user quits.
        """
        # A one-time forceful fetch if the initial one in __init__ failed.
        if not self.leaderboard or len(self.leaderboard) == 0:
             self.leaderboard = self.network.get_leaderboard()

        while True:
            self.handle_input()
            self.update()
            
            # --- Rendering Pipeline ---
            # 1. Draw everything onto the fixed-size canvas.
            self.draw_on_canvas()
            
            # 2. Scale the canvas to fit the resizable window while preserving aspect ratio.
            self.render_to_screen_preserve_aspect()
            
            self.clock.tick(FPS)

    def handle_input(self):
        """Processes all user input from Pygame events based on the current game state."""
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            # --- LOGIN STATE ---
            if self.state == "LOGIN":
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        # On Enter, register the user and move to the controls screen.
                        if self.input_text:
                            self.network.register_user(self.input_text)
                            self.state = "CONTROLS"
                            self.sound.play('level') 
                    elif event.key == pygame.K_BACKSPACE:
                        self.input_text = self.input_text[:-1]
                    else:
                        # Limit username length.
                        if len(self.input_text) < 12:
                            self.input_text += event.unicode.upper()
            
            # --- CONTROLS INFO STATE ---
            elif self.state == "CONTROLS":
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        # On Enter, start the game.
                        self.state = "PLAYING"
                        self.logic.reset()
                        self.sound.play('level')

            # --- PLAYING STATE ---
            elif self.state == "PLAYING":
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT: 
                        if self.logic.move(-1, 0): self.sound.play('move')
                    
                    elif event.key == pygame.K_RIGHT: 
                        if self.logic.move(1, 0): self.sound.play('move')
                    
                    elif event.key == pygame.K_UP: 
                        self.logic.rotate()
                        self.sound.play('rotate')
                    
                    elif event.key == pygame.K_DOWN: # Soft drop
                        if self.logic.move(0, 1): self.sound.play('move')
                    
                    elif event.key == pygame.K_SPACE: # Hard drop
                        while self.logic.move(0, 1): pass # Move down until it collides
                        self.logic.lock_piece()
                        self.sound.play('drop')
                        
                        # Update Discord presence after a significant action.
                        current_name = self.network.username if self.network.username else "Guest"
                        self.discord.update_presence(f"Score: {self.logic.score}", f"Pilot: {current_name}")

                    elif event.key == pygame.K_p:
                        self.state = "PAUSED"
                        self.discord.update_presence("Paused", "Taking a break")

            # --- PAUSED / GAMEOVER STATES ---
            elif self.state in ["PAUSED", "GAMEOVER"]:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r: # Restart
                        self.logic.reset()
                        self.state = "PLAYING"
                        self.sound.play('level')
                        current_name = self.network.username if self.network.username else "Guest"
                        self.discord.update_presence("Score: 0", f"Pilot: {current_name}")
                        
                    elif event.key == pygame.K_q: # Quit to menu
                        self.state = "LOGIN"

    def update(self):
        """Updates game logic and animations that happen every frame."""
        self.ui.update_animation() 
        
        if self.state == "PLAYING":
            if self.logic.game_over:
                self.sound.play('gameover')
                self.network.submit_score(self.logic.score)
                self.leaderboard = self.network.get_leaderboard() 
                
                self.discord.update_presence("GAME OVER", f"Final Score: {self.logic.score}")
                
                self.state = "GAMEOVER"
                return # Exit early to prevent piece from moving after game over.

            # --- Automatic Piece Gravity ---
            # The piece falls faster if the down arrow is held.
            speed = 50 if pygame.key.get_pressed()[pygame.K_DOWN] else 500
            
            # Using a time-based tick for consistent fall speed regardless of FPS.
            if pygame.time.get_ticks() % speed < 17: 
                 if not self.logic.move(0, 1):
                     self.logic.lock_piece()
                     self.sound.play('drop')
                     
                     # Update Discord when a piece locks and score might change.
                     current_name = self.network.username if self.network.username else "Guest"
                     self.discord.update_presence(f"Score: {self.logic.score}", f"Pilot: {current_name}")

    def draw_on_canvas(self):
        """Draws all game components onto the fixed-size canvas."""
        self.ui.draw_background_grid()
        
        # Center the main game area on the canvas
        layout_margin_left = 30
        game_x = layout_margin_left
        game_y = (SCREEN_HEIGHT - GAME_AREA_HEIGHT) // 2 
        
        # Draw the neon border around the game area
        game_rect = (game_x - 5, game_y - 5, GAME_AREA_WIDTH + 10, GAME_AREA_HEIGHT + 10)
        self.ui.draw_neon_border(game_rect)
        pygame.draw.rect(self.canvas, (10, 10, 20), (game_x, game_y, GAME_AREA_WIDTH, GAME_AREA_HEIGHT))

        # Draw the Tetris grid, locked pieces, and the current piece.
        self.draw_game_content(game_x, game_y)

        # --- Sidebar ---
        sidebar_x = game_x + GAME_AREA_WIDTH + 40
        current_name = self.network.username if self.network.username else "GUEST"
        
        self.ui.draw_sidebar(
            sidebar_x, 
            game_y, 
            self.logic.score, 
            self.leaderboard, 
            self.logic, # Pass the logic object to access next_piece etc.
            current_name 
        )

        # --- Overlays ---
        # Draw modal pop-ups based on the game state.
        if self.state == "LOGIN":
            self.draw_overlay_login()
        elif self.state == "CONTROLS":
            self.ui.draw_overlay_controls()
        elif self.state == "PAUSED":
            self.draw_overlay_message("PAUSED", "PRESS 'R' TO RESUME")
        elif self.state == "GAMEOVER":
            self.draw_overlay_message("GAME OVER", f"SCORE: {self.logic.score}", "PRESS 'R' TO RESTART")

    def render_to_screen_preserve_aspect(self):
        """
        Scales the canvas to the window size while maintaining the aspect ratio.
        This prevents the game from looking stretched or distorted on different
        window sizes. Any empty space is filled with black bars ("letterboxing").
        """
        window_w, window_h = self.screen.get_size()
        canvas_w, canvas_h = self.canvas.get_size()

        # Calculate the scaling factor for width and height.
        scale_w = window_w / canvas_w
        scale_h = window_h / canvas_h
        # Use the smaller of the two to ensure the whole canvas fits.
        scale = min(scale_w, scale_h)

        # Calculate the new dimensions of the scaled canvas.
        new_w = int(canvas_w * scale)
        new_h = int(canvas_h * scale)

        # Calculate the top-left position to center the scaled canvas.
        offset_x = (window_w - new_w) // 2
        offset_y = (window_h - new_h) // 2

        # 1. Fill the entire window with black (for letterboxing).
        self.screen.fill((0, 0, 0))

        # 2. Scale the canvas to the new dimensions.
        scaled_surf = pygame.transform.scale(self.canvas, (new_w, new_h))

        # 3. Blit (draw) the scaled canvas onto the screen at the centered position.
        self.screen.blit(scaled_surf, (offset_x, offset_y))

        pygame.display.flip()

    def draw_game_content(self, start_x, start_y):
        """Draws the Tetris grid, locked pieces, and the active piece."""
        # Draw the locked pieces on the board.
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                val = self.logic.board[y][x]
                if val > 0: # val > 0 means it's a colored block.
                    color_tuple = SHAPE_COLORS[(val-1) % len(SHAPE_COLORS)]
                    px = start_x + x * BLOCK_SIZE
                    py = start_y + y * BLOCK_SIZE
                    self.ui.draw_3d_block(px, py, color_tuple)
                else: # val == 0 means it's an empty grid cell.
                    rect = (start_x + x*BLOCK_SIZE, start_y + y*BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE)
                    pygame.draw.rect(self.canvas, (20, 20, 40), rect, 1) # Draw grid lines.

        # Draw the currently falling piece if the game is active.
        if self.logic.current_piece and self.state == "PLAYING":
            for cy, row in enumerate(self.logic.current_piece):
                for cx, val in enumerate(row):
                    if val:
                        color_tuple = SHAPE_COLORS[self.logic.current_color_idx]
                        px = start_x + (self.logic.piece_x + cx) * BLOCK_SIZE
                        py = start_y + (self.logic.piece_y + cy) * BLOCK_SIZE
                        self.ui.draw_3d_block(px, py, color_tuple)

    def draw_overlay_login(self):
        """Draws the user login/creation screen."""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill((0,0,0))
        self.canvas.blit(overlay, (0,0))

        center_x, center_y = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
        rect = (center_x - 200, center_y - 100, 400, 200)
        self.ui.draw_neon_border(rect)
        pygame.draw.rect(self.canvas, COLOR_PANEL_BG, rect)

        self.ui.draw_text_pulsing("WELCOME PLAYER", (center_x, center_y - 60), (0, 255, 255), "title")
        
        # Username input box
        input_rect = pygame.Rect(center_x - 150, center_y, 300, 50)
        pygame.draw.rect(self.canvas, (255, 255, 255), input_rect, border_radius=5)
        
        text_surf = self.ui.font_title.render(self.input_text, True, (0, 0, 0))
        text_rect = text_surf.get_rect(center=input_rect.center)
        self.canvas.blit(text_surf, text_rect)
        
        msg = self.ui.font_pixel.render("PRESS ENTER", True, (150, 150, 150))
        self.canvas.blit(msg, (center_x - 100, center_y + 70))

    def draw_overlay_message(self, title, msg, sub_text=""):
        """A generic function to draw a message overlay (e.g., Paused, Game Over)."""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill((0,0,0))
        self.canvas.blit(overlay, (0,0))

        center_x, center_y = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
        self.ui.draw_text_pulsing(title, (center_x, center_y - 50), (255, 50, 50), "title")
        
        msg_surf = self.ui.font_main.render(msg, True, (255, 255, 255))
        msg_rect = msg_surf.get_rect(center=(center_x, center_y + 20))
        self.canvas.blit(msg_surf, msg_rect)

        if sub_text:
             sub = self.ui.font_pixel.render(sub_text, True, (200, 200, 200))
             self.canvas.blit(sub, (center_x - 100, center_y + 60))

# This block ensures the code runs only when the script is executed directly.
if __name__ == "__main__":
    app = MainApp()
    app.run()