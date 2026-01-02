# network.py
import requests
import json
import os
import sys
from settings import API_URL

class NetworkManager:
    def __init__(self):
        self.username = None
        
        # پیدا کردن مسیر دقیق فایلی که داره اجرا میشه
        base_path = os.path.dirname(os.path.abspath(sys.argv[0]))
        self.credential_file = os.path.join(base_path, "user_credential.json")
        
        self.load_local_credentials()

    def load_local_credentials(self):
        """لود کردن یوزرنیم ذخیره شده"""
        if os.path.exists(self.credential_file):
            try:
                with open(self.credential_file, "r") as f:
                    data = json.load(f)
                    saved_name = data.get("username")
                    if saved_name:
                        self.username = saved_name
                        print(f"[NETWORK] Loaded credentials for: {self.username}")
            except Exception as e:
                print(f"[NETWORK] Error reading credential file: {e}")
        else:
            print("[NETWORK] No credential file found.")

    def save_local_credentials(self, username):
        """ذخیره یوزرنیم به صورت ایمن"""
        try:
            with open(self.credential_file, "w") as f:
                json.dump({"username": username}, f)
            print(f"[NETWORK] Credentials saved to: {self.credential_file}")
        except Exception as e:
            print(f"[NETWORK] Save Error: {e}")

    def register_user(self, username):
        """ثبت نام در سرور"""
        if not username or not username.strip():
            return False, "EMPTY NAME"

        try:
            print(f"[NETWORK] Connecting to: {API_URL}/register")
            response = requests.post(f"{API_URL}/register", json={'username': username}, timeout=5)
            
            # کد 200 (ساخت موفق) یا 409 (کاربر قبلاً بوده) هر دو یعنی لاگین موفق
            if response.status_code == 200 or response.status_code == 409:
                self.username = username
                self.save_local_credentials(username)
                
                if response.status_code == 200:
                    return True, "SUCCESS"
                else:
                    return True, "WELCOME BACK"

            elif response.status_code == 400:
                return False, "INVALID NAME"
                
            else:
                return False, f"ERROR {response.status_code}"

        except requests.exceptions.ConnectionError:
            print("[NETWORK] Server unreachable. Switching to OFFLINE.")
            self.username = username
            self.save_local_credentials(username)
            return True, "OFFLINE MODE"
            
        except Exception as e:
            print(f"[NETWORK] Error: {e}")
            return False, "CONNECTION ERROR"

    def submit_score(self, score):
        if not self.username: return
        try:
            requests.post(f"{API_URL}/submit", json={'username': self.username, 'score': score}, timeout=2)
        except:
            pass # سکوت در زمان بازی

    def get_leaderboard(self):
        try:
            response = requests.get(f"{API_URL}/leaderboard", timeout=3)
            if response.status_code == 200:
                data = response.json()
                return [{"name": item["username"], "score": item["high_score"]} for item in data]
        except:
            pass
        return [{"name": "Loading...", "score": 0}]