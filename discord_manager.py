# discord_manager.py
from pypresence import Presence
import time

class DiscordHandler:
    def __init__(self, app_id, download_url="https://github.com/your-username/your-repo/releases"):
        self.client_id = app_id
        self.download_url = download_url
        self.rpc = None
        self.last_update = 0
        self.connected = False
        
        try:
            self.rpc = Presence(self.client_id)
            self.rpc.connect()
            self.connected = True
            print("[DISCORD] Connected to Rich Presence!")
        except Exception as e:
            print(f"[DISCORD] Connection failed (Is Discord open?): {e}")

    def update_presence(self, state_text, details_text, small_text=None):
        """
        state_text: وضعیت کلی (مثلاً "Score: 1500")
        details_text: جزئیات (مثلاً "Playing as Admin")
        """
        if not self.connected or not self.rpc:
            return

        # دیسکورد محدودیت آپدیت داره (هر 15 ثانیه). ما اینجا چک میکنیم تند تند نفرستیم
        if time.time() - self.last_update < 15:
            return

        try:
            self.rpc.update(
                state=state_text,       # خط دوم: امتیاز یا وضعیت
                details=details_text,   # خط اول: اسم بازیکن
                large_image="logo",     # اسم عکسی که تو پنل دیسکورد آپلود کردی
                large_text="Tetris Neon Arcade", # متنی که وقتی موس میره رو عکس میاد
                small_image="idle",     # (اختیاری) اگر عکس کوچک هم آپلود کردی
                small_text=small_text,
                start=time.time(),      # تایمر (Time Elapsed) رو نشون میده
                
                # --- دکمه دانلود جادویی ---
                buttons=[{"label": "Download Game", "url": self.download_url}]
            )
            self.last_update = time.time()
            print("[DISCORD] Presence updated.")
            
        except Exception as e:
            print(f"[DISCORD] Update error: {e}")
            # اگر ارتباط قطع شد، دوباره تلاش نکنیم که بازی لگ نگیره
            self.connected = False