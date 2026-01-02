# ui.py
import pygame
import math
from settings import *

class ArcadeUI:
    def __init__(self, screen):
        self.screen = screen 
        self.font_main = pygame.font.SysFont("Consolas", 22, bold=True)
        self.font_title = pygame.font.SysFont("Verdana", 40, bold=True)
        self.font_pixel = pygame.font.SysFont("Comic Sans MS", 16, bold=True) 
        self.font_small = pygame.font.SysFont("Consolas", 14, bold=True)
        
        self.animation_tick = 0

    def update_animation(self):
        self.animation_tick += 0.1

    def truncate_text(self, text, font, max_width):
        if font.size(text)[0] <= max_width:
            return text
        temp = text
        while font.size(temp + "...")[0] > max_width and len(temp) > 0:
            temp = temp[:-1]
        return temp + "..."

    def draw_background_grid(self):
        self.screen.fill(COLOR_BG_DARK)
        for x in range(0, SCREEN_WIDTH, 40):
            pygame.draw.line(self.screen, COLOR_GRID_LINE, (x, 0), (x, SCREEN_HEIGHT))
        for y in range(0, SCREEN_HEIGHT, 40):
            pygame.draw.line(self.screen, COLOR_GRID_LINE, (0, y), (SCREEN_WIDTH, y))

    def draw_3d_block(self, x, y, color_tuple, size=BLOCK_SIZE):
        base_color, light_color, dark_color = color_tuple
        rect = (x, y, size, size)
        pygame.draw.rect(self.screen, base_color, rect)
        pygame.draw.polygon(self.screen, light_color, [(x, y), (x + size, y), (x + size - 4, y + 4), (x + 4, y + 4), (x, y + size)])
        pygame.draw.polygon(self.screen, dark_color, [(x + size, y + size), (x, y + size), (x + 4, y + size - 4), (x + size - 4, y + size - 4), (x + size, y)])
        pygame.draw.rect(self.screen, base_color, (x + 8, y + 8, size - 16, size - 16))

    def draw_neon_border(self, rect):
        pulse = (math.sin(self.animation_tick) + 1) / 2
        r = int(COLOR_BORDER_GLOW[0] * pulse)
        g = int(COLOR_BORDER_GLOW[1] * 0.8 + (pulse * 50))
        b = int(COLOR_BORDER_GLOW[2])
        pygame.draw.rect(self.screen, (r, g, b), (rect[0]-2, rect[1]-2, rect[2]+4, rect[3]+4), 2, border_radius=5)
        pygame.draw.rect(self.screen, (255, 255, 255), rect, 2, border_radius=5)

    def draw_panel(self, rect, title=None):
        pygame.draw.rect(self.screen, COLOR_PANEL_BG, rect, border_radius=10)
        pygame.draw.rect(self.screen, (60, 60, 80), rect, 2, border_radius=10)
        if title:
            text_surf = self.font_main.render(title, True, (255, 255, 255))
            self.screen.blit(text_surf, (rect[0] + 10, rect[1] + 10))

    def draw_text_pulsing(self, text, center_pos, color, font="title"):
        font_obj = self.font_title if font == "title" else self.font_main
        scale = 1.0 + (math.sin(self.animation_tick * 2) * 0.05)
        base_surf = font_obj.render(text, True, color)
        width = int(base_surf.get_width() * scale)
        height = int(base_surf.get_height() * scale)
        scaled_surf = pygame.transform.scale(base_surf, (width, height))
        rect = scaled_surf.get_rect(center=center_pos)
        shadow_surf = font_obj.render(text, True, (0,0,0))
        shadow_surf = pygame.transform.scale(shadow_surf, (width, height))
        self.screen.blit(shadow_surf, (rect.x + 4, rect.y + 4))
        self.screen.blit(scaled_surf, rect)

    def draw_button_circle(self, text, center_pos, color, key_code, size=25):
        """رسم دکمه‌های راهنما"""
        pygame.draw.circle(self.screen, color, center_pos, size)
        pygame.draw.circle(self.screen, (255, 255, 255), (center_pos[0]-6, center_pos[1]-6), 4)
        
        key_surf = self.font_small.render(key_code, True, (0,0,0))
        key_rect = key_surf.get_rect(center=center_pos)
        self.screen.blit(key_surf, key_rect)
        
        # متن توضیحات با فاصله مناسب
        desc_surf = self.font_main.render(text, True, (220, 220, 220))
        desc_rect = desc_surf.get_rect(center=(center_pos[0], center_pos[1] + 35))
        self.screen.blit(desc_surf, desc_rect)

    def draw_sidebar(self, x, y, score, leaderboard, logic, current_username):
        # تنظیم ارتفاع شروع (کمی پایین‌تر بیاد که به سقف نچسبه)
        current_y = y 

        # 1. پنل نام بازیکن (اولین پنل)
        self.draw_panel((x, current_y, 250, 50), "PILOT")
        name_surf = self.font_main.render(current_username, True, (0, 255, 255))
        name_rect = name_surf.get_rect(center=(x + 125, current_y + 30)) # تنظیم دقیق وسط
        self.screen.blit(name_surf, name_rect)
        
        current_y += 60 # فاصله برای پنل بعدی

        # 2. پنل امتیاز (مهم‌تره، آوردمش بالا)
        self.draw_panel((x, current_y, 250, 80), "SCORE")
        self.draw_text_pulsing(str(score), (x + 125, current_y + 45), TEXT_COLOR_ACCENT, "main")
        
        current_y += 90 # فاصله

        # 3. پنل قطعه بعدی
        self.draw_panel((x, current_y, 250, 120), "NEXT")
        if logic.next_piece_idx is not None:
             piece = logic.SHAPES[logic.next_piece_idx]
             color_tuple = SHAPE_COLORS[logic.next_piece_idx]
             # محاسبات وسط چین کردن
             p_width = len(piece[0]) * 25
             p_height = len(piece) * 25
             # محاسبه مرکز پنل برای رسم قطعه
             center_panel_x = x + 125
             center_panel_y = current_y + 70 # کمی پایین‌تر از تایتل پنل
             
             offset_x = center_panel_x - (p_width // 2)
             offset_y = center_panel_y - (p_height // 2)
             
             for cy, row in enumerate(piece):
                 for cx, val in enumerate(row):
                     if val:
                         self.draw_3d_block(offset_x + cx*25, offset_y + cy*25, color_tuple, size=25)
        
        current_y += 130 # فاصله

        # 4. پنل لیدربورد (بقیه فضا رو پر کنه)
        # محاسبه ارتفاع باقی‌مانده تا پایین زمین بازی
        remaining_height = (GAME_AREA_HEIGHT + y) - current_y
        if remaining_height < 200: remaining_height = 300 # حداقل ارتفاع

        self.draw_panel((x, current_y, 250, remaining_height), "TOP PILOTS")
        
        # رسم لیست نفرات
        for i, user in enumerate(leaderboard[:10]): # 10 نفر اول کافیه
            row_y = current_y + 40 + (i * 30)
            if row_y + 20 > current_y + remaining_height: break # اگه جا نبود ننویس
            
            # رنگ‌بندی
            rank_color = (150, 150, 150)
            if i == 0: rank_color = (255, 215, 0) # طلا
            elif i == 1: rank_color = (192, 192, 192) # نقره
            elif i == 2: rank_color = (205, 127, 50) # برنز
            
            rank_str = f"{i+1}."
            name_str = f" {user['name']}"
            
            # رسم رتبه
            rank_surf = self.font_small.render(rank_str, True, rank_color)
            self.screen.blit(rank_surf, (x + 15, row_y))
            
            # رسم نام
            name_surf = self.font_small.render(self.truncate_text(name_str, self.font_small, 130), True, (220, 220, 220))
            self.screen.blit(name_surf, (x + 40, row_y))
            
            # رسم امتیاز
            score_surf = self.font_small.render(str(user['score']), True, rank_color)
            score_rect = score_surf.get_rect(right=x + 235, centery=row_y + 8)
            self.screen.blit(score_surf, score_rect)

    def draw_overlay_controls(self):
        """نمایش راهنما در یک پاپ‌آپ بزرگ و تمیز"""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(220); overlay.fill((0,0,0))
        self.screen.blit(overlay, (0,0))

        center_x, center_y = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
        rect = (center_x - 300, center_y - 200, 600, 400)
        self.draw_neon_border(rect)
        pygame.draw.rect(self.screen, COLOR_PANEL_BG, rect)

        self.draw_text_pulsing("HOW TO PLAY", (center_x, center_y - 150), (0, 255, 255), "title")

        # رسم دکمه‌ها با فاصله زیاد و مرتب
        start_y = center_y - 50
        gap_x = 130
        
        self.draw_button_circle("Rotate", (center_x - 1.5*gap_x, start_y), (100, 100, 255), "UP", 35)
        self.draw_button_circle("Move", (center_x - 0.5*gap_x, start_y), (100, 255, 100), "< >", 35)
        self.draw_button_circle("Drop", (center_x + 0.5*gap_x, start_y), (255, 100, 100), "SPC", 35)
        self.draw_button_circle("Pause", (center_x + 1.5*gap_x, start_y), (255, 200, 50), "P", 35)

        msg = self.font_pixel.render("PRESS ENTER TO START GAME", True, (150, 150, 150))
        self.screen.blit(msg, (center_x - 130, center_y + 120))