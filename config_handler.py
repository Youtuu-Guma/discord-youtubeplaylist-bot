import configparser
import os
import sys

class BotConfig:
    def __init__(self):
        # パス解決の共通化
        if hasattr(sys, '_MEIPASS'):
            self.base_dir = os.path.dirname(sys.executable)
        else:
            self.base_dir = os.path.dirname(os.path.abspath(__file__))
        
        self.config_path = os.path.join(self.base_dir, "config.ini")
        self.db_path = os.path.join(self.base_dir, "bot_data.db")
        
        self.config = configparser.ConfigParser()
        if not os.path.exists(self.config_path):
            self._create_default()
            
        self.config.read(self.config_path, encoding='utf-8')

    def _create_default(self):
        self.config["BOT"] = {
            "discord_token": "ENTER_TOKEN",
            "admin_id": "ENTER_YOUR_ID",
            "whitelist_users": "",
            "cui_mode": "False"
        }
        with open(self.config_path, "w", encoding='utf-8') as f:
            self.config.write(f)

    @property
    def discord_token(self): return self.config.get("BOT", "discord_token", fallback="ENTER_TOKEN")
    @property
    def admin_id(self): return self.config.get("BOT", "admin_id", fallback="")
    @property
    def cui_mode(self): return self.config.getboolean("BOT", "cui_mode", fallback=False)
    @property
    def whitelist(self):
        ws = self.config.get("BOT", "whitelist_users", fallback="")
        return [i.strip() for i in ws.split(",") if i.strip()]