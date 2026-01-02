# discord_manager.py
"""
Manages Discord Rich Presence integration for the game.

This module uses the 'pypresence' library to connect to a user's Discord client
and display their current in-game status, such as score, current state (in-menu, playing),
and a button to download the game.
"""
from pypresence import Presence
import time

class DiscordHandler:
    """
    Handles the connection and updates for Discord Rich Presence.
    
    Tries to connect to Discord on initialization and provides a method
    to update the presence information, respecting Discord's rate limits.
    """
    def __init__(self, app_id, download_url="https://github.com/MMETehrani/tetris-gui/releases"):
        """
        Initializes the Discord handler and connects to the RPC server.

        Args:
            app_id (str): The Application ID from your Discord Developer Portal.
            download_url (str, optional): The URL for the download button. Defaults to a placeholder.
        """
        self.client_id = app_id
        self.download_url = download_url
        self.rpc = None
        self.last_update = 0
        self.connected = False
        
        try:
            # Attempt to connect to the Discord client's RPC server.
            self.rpc = Presence(self.client_id)
            self.rpc.connect()
            self.connected = True
            print("[DISCORD] Connected to Rich Presence!")
        except Exception as e:
            # This can fail for many reasons, most commonly if Discord is not running.
            print(f"[DISCORD] Connection failed (Is Discord open?): {e}")

    def update_presence(self, state_text, details_text, small_text=None):
        """
        Updates the user's Rich Presence status on Discord.

        This function builds and sends the payload to Discord. It includes a rate-limiting
        check to prevent sending updates too frequently (more than once every 15 seconds),
        as imposed by the Discord API.

        Args:
            state_text (str): The main status text (e.g., "Score: 1500"). Displayed on the second line.
            details_text (str): The details text (e.g., "Playing as Player1"). Displayed on the first line.
            small_text (str, optional): Text to display when hovering over the small image. Defaults to None.
        """
        if not self.connected or not self.rpc:
            return

        # Discord imposes a 15-second rate limit on presence updates.
        # This check prevents sending updates too frequently.
        current_time = time.time()
        if current_time - self.last_update < 15:
            return

        try:
            self.rpc.update(
                state=state_text,       # Second line of text (e.g., score, status)
                details=details_text,   # First line of text (e.g., player name)
                large_image="logo",     # The key for the large image asset uploaded in the Discord Dev Portal.
                large_text="Tetris Neon Arcade", # Tooltip for the large image.
                small_image="idle",     # Optional: The key for the small image asset.
                small_text=small_text,  # Tooltip for the small image.
                start=time.time(),      # Shows "Time Elapsed" since the update.
                
                # Adds a clickable button to the presence.
                buttons=[{"label": "Download Game", "url": self.download_url}]
            )
            self.last_update = current_time
            print("[DISCORD] Presence updated.")
            
        except Exception as e:
            # If the update fails (e.g., Discord was closed), disable further attempts
            # to prevent spamming errors and causing potential game lag.
            print(f"[DISCORD] Update error: {e}")
            self.connected = False