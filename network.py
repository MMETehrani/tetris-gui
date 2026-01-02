# network.py
"""
Manages all network interactions for the game.

This module handles communication with the backend server for features like
user registration, score submission, and fetching the online leaderboard.
It also manages local storage of user credentials for auto-login.
"""
import requests
import json
import os
import sys
from settings import API_URL

class NetworkManager:
    """
    Handles API requests and local user credential management.
    """
    def __init__(self):
        """
        Initializes the NetworkManager and loads any saved user credentials.
        """
        self.username = None
        
        # Determine the correct path for the credential file, even when run from an executable.
        # sys.argv[0] is the path to the script or executable.
        base_path = os.path.dirname(os.path.abspath(sys.argv[0]))
        self.credential_file = os.path.join(base_path, "user_credential.json")
        
        self.load_local_credentials()

    def load_local_credentials(self):
        """
        Loads the username from a local JSON file if it exists.
        This allows the user to be automatically logged in on subsequent plays.
        """
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
        """
        Saves the user's username to a local JSON file for future sessions.

        Args:
            username (str): The username to save.
        """
        try:
            with open(self.credential_file, "w") as f:
                json.dump({"username": username}, f)
            print(f"[NETWORK] Credentials saved to: {self.credential_file}")
        except Exception as e:
            print(f"[NETWORK] Save Error: {e}")

    def register_user(self, username):
        """
        Registers a new user or logs in an existing one via the API.

        If the server is unreachable, it falls back to an "offline mode" where
        the username is still saved locally.

        Args:
            username (str): The desired username.

        Returns:
            tuple: (bool, str) indicating success and a status message.
        """
        if not username or not username.strip():
            return False, "EMPTY NAME"

        try:
            print(f"[NETWORK] Connecting to: {API_URL}/register")
            response = requests.post(f"{API_URL}/register", json={'username': username}, timeout=5)
            
            # A 200 (Created) or 409 (Conflict/Already Exists) are both considered successful logins.
            if response.status_code == 200 or response.status_code == 409:
                self.username = username
                self.save_local_credentials(username)
                
                if response.status_code == 200:
                    return True, "SUCCESS"
                else:
                    return True, "WELCOME BACK"

            elif response.status_code == 400: # Bad Request (e.g., invalid name)
                return False, "INVALID NAME"
                
            else:
                return False, f"ERROR {response.status_code}"

        except requests.exceptions.ConnectionError:
            # If the server can't be reached, enter an offline mode.
            print("[NETWORK] Server unreachable. Switching to OFFLINE.")
            self.username = username
            self.save_local_credentials(username)
            return True, "OFFLINE MODE"
            
        except Exception as e:
            print(f"[NETWORK] Error: {e}")
            return False, "CONNECTION ERROR"

    def submit_score(self, score):
        """
        Submits the player's final score to the server.
        Fails silently if the server is unreachable to avoid interrupting the game flow.

        Args:
            score (int): The score to submit.
        """
        if not self.username: return
        try:
            # Use a short timeout to avoid long hangs on game over.
            requests.post(f"{API_URL}/submit", json={'username': self.username, 'score': score}, timeout=2)
        except:
            # Silently pass on any network errors during gameplay.
            pass 

    def get_leaderboard(self):
        """
        Fetches the top scores from the server.

        Returns:
            list: A list of dictionaries, where each dictionary contains
                  a 'name' and 'score'. Returns a placeholder on failure.
        """
        try:
            response = requests.get(f"{API_URL}/leaderboard", timeout=3)
            if response.status_code == 200:
                data = response.json()
                # Standardize the format to what the UI expects.
                return [{"name": item["username"], "score": item["high_score"]} for item in data]
        except:
            # If fetching fails, return a default list to avoid crashing the UI.
            pass
        return [{"name": "Loading...", "score": 0}]