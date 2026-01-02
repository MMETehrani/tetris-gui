# settings.py
import pygame

# ابعاد پایه (Virtual Resolution)
# ما بازی رو روی این ابعاد می‌سازیم، ولی پنجره می‌تونه هر سایزی باشه
SCREEN_WIDTH = 750  # عرض کمتر شد (قبلا 950 بود)
SCREEN_HEIGHT = 800 
FPS = 60

# ابعاد تتریس
BLOCK_SIZE = 35
GRID_WIDTH = 10
GRID_HEIGHT = 20
GAME_AREA_WIDTH = GRID_WIDTH * BLOCK_SIZE
GAME_AREA_HEIGHT = GRID_HEIGHT * BLOCK_SIZE

# تنظیمات شبکه
API_URL = "https://tetris-py-api-5unr.vercel.app"

# --- پالت رنگی نئون آرکید ---
COLOR_BG_DARK = (10, 10, 25) 
COLOR_GRID_LINE = (30, 30, 50) 
COLOR_PANEL_BG = (20, 20, 35)
COLOR_BORDER_GLOW = (0, 200, 255) 

# متن‌ها
TEXT_COLOR_MAIN = (255, 255, 255)
TEXT_COLOR_ACCENT = (255, 215, 0) 

# رنگ‌بندی قطعات (Arcade Vivid)
SHAPE_COLORS = [
    ((0, 255, 255), (150, 255, 255), (0, 150, 150)),      # Cyan
    ((255, 220, 0), (255, 255, 150), (180, 150, 0)),      # Yellow
    ((180, 0, 255), (220, 150, 255), (100, 0, 150)),      # Purple
    ((0, 255, 0),   (150, 255, 150), (0, 150, 0)),        # Green
    ((255, 0, 60),  (255, 150, 150), (150, 0, 0)),        # Red
    ((0, 80, 255),  (100, 150, 255), (0, 0, 150)),        # Blue
    ((255, 120, 0), (255, 180, 100), (180, 80, 0)),       # Orange
]