# main.py
import pygame
import sys
from discord_manager import DiscordHandler
from settings import *
from ui import ArcadeUI
from logic import TetrisLogic
from network import NetworkManager

class DummySound:
    def play(self, name):
        pass # هیچ کاری نمیکنه، فقط جلوی ارور رو میگیره

class MainApp:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
        self.canvas = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        
        pygame.display.set_caption("TETRIS: NEON ARCADE")
        self.clock = pygame.time.Clock()
        
        self.ui = ArcadeUI(self.canvas)
        self.logic = TetrisLogic()
        self.network = NetworkManager()
        
        # --- اینجا صدای الکی رو میسازیم که ارور نده ---
        self.sound = DummySound() 
        # ---------------------------------------------

        # تنظیمات دیسکورد
        YOUR_APP_ID = "1456684566101102592" 
        YOUR_GITHUB = "https://github.com/AliReza/Tetris/releases"
        self.discord = DiscordHandler(YOUR_APP_ID, YOUR_GITHUB)
        self.discord.update_presence("In Menu", "Waiting to start...")

        if self.network.username:
            print(f"Auto-login successful: {self.network.username}")
            self.state = "CONTROLS"
            self.input_text = self.network.username
        else:
            self.state = "LOGIN" 
            self.input_text = "PLAYER 1"
        
        self.leaderboard = self.network.get_leaderboard()

    def run(self):
        # یکبار زورکی اول کاری لیست رو بگیر (اگر توی init نگرفته بود)
        if not self.leaderboard or len(self.leaderboard) == 0:
             self.leaderboard = self.network.get_leaderboard()

        while True:
            self.handle_input()
            self.update()
            
            # 1. رسم همه چیز روی بوم مجازی
            self.draw_on_canvas()
            
            # 2. انتقال هوشمند بوم به پنجره (با حفظ نسبت تصویر)
            self.render_to_screen_preserve_aspect()
            
            self.clock.tick(FPS)

    def handle_input(self):
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            
            # --- LOGIN STATE ---
            if self.state == "LOGIN":
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        if self.input_text:
                            self.network.register_user(self.input_text)
                            self.state = "CONTROLS"
                            # صدای خوش‌آمدگویی یا ورود (اختیاری)
                            self.sound.play('level') 
                    elif event.key == pygame.K_BACKSPACE:
                        self.input_text = self.input_text[:-1]
                    else:
                        if len(self.input_text) < 12:
                            self.input_text += event.unicode.upper()
            
            # --- CONTROLS INFO STATE ---
            elif self.state == "CONTROLS":
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        self.state = "PLAYING"
                        self.logic.reset()
                        self.sound.play('level') # صدای شروع بازی

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
                    
                    elif event.key == pygame.K_DOWN: 
                        if self.logic.move(0, 1): self.sound.play('move')
                    
                    elif event.key == pygame.K_SPACE: 
                        while self.logic.move(0, 1): pass
                        self.logic.lock_piece()
                        self.sound.play('drop')
                        
                        # --- آپدیت دیسکورد وقتی امتیاز زیاد میشه (Hard Drop) ---
                        current_name = self.network.username if self.network.username else "Guest"
                        self.discord.update_presence(f"Score: {self.logic.score}", f"Pilot: {current_name}")

                    elif event.key == pygame.K_p:
                        self.state = "PAUSED"
                        self.discord.update_presence("Paused", "Taking a break")

            # --- OTHER STATES ---
            elif self.state in ["PAUSED", "GAMEOVER"]:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r: 
                        self.logic.reset()
                        self.state = "PLAYING"
                        self.sound.play('level')
                        # آپدیت دیسکورد برای شروع مجدد
                        current_name = self.network.username if self.network.username else "Guest"
                        self.discord.update_presence("Score: 0", f"Pilot: {current_name}")
                        
                    elif event.key == pygame.K_q:
                        self.state = "LOGIN"

    def update(self):
        self.ui.update_animation() 
        
        if self.state == "PLAYING":
            if self.logic.game_over:
                self.sound.play('gameover') # صدای باخت
                self.network.submit_score(self.logic.score)
                self.leaderboard = self.network.get_leaderboard() 
                
                # --- آپدیت دیسکورد برای گیم اور ---
                self.discord.update_presence("GAME OVER", f"Final Score: {self.logic.score}")
                
                self.state = "GAMEOVER"
                return # از فانکشن خارج شو که دیگه قطعه حرکت نکنه

            # سرعت سقوط
            speed = 50 if pygame.key.get_pressed()[pygame.K_DOWN] else 500
            
            if pygame.time.get_ticks() % speed < 17: 
                 if not self.logic.move(0, 1):
                     self.logic.lock_piece()
                     self.sound.play('drop') # صدای برخورد
                     
                     # --- آپدیت دیسکورد وقتی قطعه آروم میشینه و امتیاز میگیری ---
                     current_name = self.network.username if self.network.username else "Guest"
                     self.discord.update_presence(f"Score: {self.logic.score}", f"Pilot: {current_name}")

    def draw_on_canvas(self):
        """رسم اجزای بازی روی بوم با سایز ثابت"""
        self.ui.draw_background_grid()
        
        layout_margin_left = 30
        game_x = layout_margin_left
        game_y = (SCREEN_HEIGHT - GAME_AREA_HEIGHT) // 2 
        
        # رسم زمین بازی
        game_rect = (game_x - 5, game_y - 5, GAME_AREA_WIDTH + 10, GAME_AREA_HEIGHT + 10)
        self.ui.draw_neon_border(game_rect)
        pygame.draw.rect(self.canvas, (10, 10, 20), (game_x, game_y, GAME_AREA_WIDTH, GAME_AREA_HEIGHT))

        # محتوای بازی
        self.draw_game_content(game_x, game_y)

        # سایدبار
        sidebar_x = game_x + GAME_AREA_WIDTH + 40
        
        # --- فیکس: پیدا کردن نام کاربر برای ارسال به UI ---
        current_name = self.network.username if self.network.username else "GUEST"
        
        self.ui.draw_sidebar(
            sidebar_x, 
            game_y, 
            self.logic.score, 
            self.leaderboard, 
            self.logic, 
            current_name  # <--- این آرگومان جا افتاده بود!
        )

        # اورلی‌ها
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
        این تابع جادویی برای حفظ نسبت تصویر است!
        محاسبه می‌کند که چقدر باید زوم کند تا تصویر فیت شود،
        بدون اینکه دفرمه شود. جاهای خالی را سیاه می‌کند.
        """
        window_w, window_h = self.screen.get_size()
        canvas_w, canvas_h = self.canvas.get_size()

        # محاسبه نسبت مقیاس
        scale_w = window_w / canvas_w
        scale_h = window_h / canvas_h
        scale = min(scale_w, scale_h) # کمترین مقیاس رو انتخاب می‌کنیم تا همه چی جا بشه

        # سایز جدید بوم
        new_w = int(canvas_w * scale)
        new_h = int(canvas_h * scale)

        # محاسبه فاصله برای وسط‌چین کردن
        offset_x = (window_w - new_w) // 2
        offset_y = (window_h - new_h) // 2

        # 1. صفحه رو سیاه کن (برای حاشیه‌ها)
        self.screen.fill((0, 0, 0))

        # 2. تغییر سایز بوم
        scaled_surf = pygame.transform.scale(self.canvas, (new_w, new_h))

        # 3. رسم بوم وسط صفحه
        self.screen.blit(scaled_surf, (offset_x, offset_y))

        pygame.display.flip()

    def draw_game_content(self, start_x, start_y):
        # رسم گرید و قطعات (مثل قبل)
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                val = self.logic.board[y][x]
                if val > 0:
                    color_tuple = SHAPE_COLORS[(val-1) % len(SHAPE_COLORS)]
                    px = start_x + x*BLOCK_SIZE
                    py = start_y + y*BLOCK_SIZE
                    self.ui.draw_3d_block(px, py, color_tuple)
                else:
                    rect = (start_x + x*BLOCK_SIZE, start_y + y*BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE)
                    pygame.draw.rect(self.canvas, (20, 20, 40), rect, 1)

        if self.logic.current_piece and self.state == "PLAYING":
            for cy, row in enumerate(self.logic.current_piece):
                for cx, val in enumerate(row):
                    if val:
                        color_tuple = SHAPE_COLORS[self.logic.current_color_idx]
                        px = start_x + (self.logic.piece_x + cx) * BLOCK_SIZE
                        py = start_y + (self.logic.piece_y + cy) * BLOCK_SIZE
                        self.ui.draw_3d_block(px, py, color_tuple)

    def draw_overlay_login(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(200); overlay.fill((0,0,0))
        self.canvas.blit(overlay, (0,0))

        center_x, center_y = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
        rect = (center_x - 200, center_y - 100, 400, 200)
        self.ui.draw_neon_border(rect)
        pygame.draw.rect(self.canvas, COLOR_PANEL_BG, rect)

        self.ui.draw_text_pulsing("WELCOME PLAYER", (center_x, center_y - 60), (0, 255, 255), "title")
        
        input_rect = pygame.Rect(center_x - 150, center_y, 300, 50)
        pygame.draw.rect(self.canvas, (255, 255, 255), input_rect, border_radius=5)
        
        text_surf = self.ui.font_title.render(self.input_text, True, (0, 0, 0))
        text_rect = text_surf.get_rect(center=input_rect.center)
        self.canvas.blit(text_surf, text_rect)
        
        msg = self.ui.font_pixel.render("PRESS ENTER", True, (150, 150, 150))
        self.canvas.blit(msg, (center_x - 100, center_y + 70))

    def draw_overlay_message(self, title, msg, sub_text=""):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(180); overlay.fill((0,0,0))
        self.canvas.blit(overlay, (0,0))

        center_x, center_y = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
        self.ui.draw_text_pulsing(title, (center_x, center_y - 50), (255, 50, 50), "title")
        
        msg_surf = self.ui.font_main.render(msg, True, (255, 255, 255))
        msg_rect = msg_surf.get_rect(center=(center_x, center_y + 20))
        self.canvas.blit(msg_surf, msg_rect)

        if sub_text:
             sub = self.ui.font_pixel.render(sub_text, True, (200, 200, 200))
             self.canvas.blit(sub, (center_x - 100, center_y + 60))

if __name__ == "__main__":
    app = MainApp()
    app.run()