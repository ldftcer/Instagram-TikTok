import json
import os
import shutil
from datetime import datetime
from typing import Dict, Any, Optional

from config import DATA_FILE, STATS_FILE

class Database:
    def __init__(self):
        self.user_data = self._load_data(DATA_FILE, {"users": {}, "banned": [], "premium": []})
        self.stats = self._load_data(STATS_FILE, {
            "total_downloads": 0,
            "daily": {},
            "users": {},
            "platforms": {"tiktok": 0, "instagram": 0}
        })

    def _load_data(self, file_path: str, default: Dict) -> Dict:
        """Load data from JSON file or return default if file doesn't exist."""
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return default

    def save_data(self) -> None:
        """Save user data with backup."""
        if os.path.exists(DATA_FILE):
            shutil.copy2(DATA_FILE, f"{DATA_FILE}.bak")
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(self.user_data, f, indent=4, ensure_ascii=False)

    def save_stats(self) -> None:
        """Save stats with backup."""
        if os.path.exists(STATS_FILE):
            shutil.copy2(STATS_FILE, f"{STATS_FILE}.bak")
        with open(STATS_FILE, "w", encoding="utf-8") as f:
            json.dump(self.stats, f, indent=4, ensure_ascii=False)

    def update_stats(self, user_id: str, success: bool = True, platform: Optional[str] = None) -> None:
        """Update statistics for a user."""
        today = datetime.now().strftime("%Y-%m-%d")
        if today not in self.stats["daily"]:
            self.stats["daily"][today] = {"success": 0, "failed": 0}
        
        if success:
            self.stats["total_downloads"] += 1
            self.stats["daily"][today]["success"] += 1
            if platform:
                self.stats["platforms"][platform] = self.stats["platforms"].get(platform, 0) + 1
        else:
            self.stats["daily"][today]["failed"] += 1
        
        if user_id not in self.stats["users"]:
            self.stats["users"][user_id] = {"downloads": 0, "failed": 0, "platforms": {}}
        
        if success:
            self.stats["users"][user_id]["downloads"] += 1
            if platform:
                self.stats["users"][user_id]["platforms"][platform] = self.stats["users"][user_id]["platforms"].get(platform, 0) + 1
        else:
            self.stats["users"][user_id]["failed"] += 1
        
        self.save_stats()

    def add_user(self, user_id: str, username: str, first_name: str, last_name: str) -> None:
        """Add new user to database."""
        if user_id not in self.user_data["users"]:
            self.user_data["users"][user_id] = {
                "language": None,
                "username": username,
                "first_name": first_name,
                "last_name": last_name,
                "join_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "last_activity": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            self.save_data()

    def update_user_activity(self, user_id: str) -> None:
        """Update user's last activity timestamp."""
        if user_id in self.user_data["users"]:
            self.user_data["users"][user_id]["last_activity"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.save_data()

    def set_user_language(self, user_id: str, language: str) -> None:
        """Set user's preferred language."""
        if user_id in self.user_data["users"]:
            self.user_data["users"][user_id]["language"] = language
            self.save_data()

    def get_user_language(self, user_id: str) -> str:
        """Get user's preferred language."""
        return self.user_data["users"].get(user_id, {}).get("language", "ru")

    def is_user_banned(self, user_id: str) -> bool:
        """Check if user is banned."""
        return user_id in self.user_data["banned"]

    def is_user_premium(self, user_id: str) -> bool:
        """Check if user has premium status."""
        return user_id in self.user_data.get("premium", [])

    def ban_user(self, user_id: str) -> bool:
        """Ban a user."""
        if user_id in self.user_data["users"] and user_id not in self.user_data["banned"]:
            self.user_data["banned"].append(user_id)
            self.save_data()
            return True
        return False

    def unban_user(self, user_id: str) -> bool:
        """Unban a user."""
        if user_id in self.user_data["banned"]:
            self.user_data["banned"].remove(user_id)
            self.save_data()
            return True
        return False

    def toggle_premium(self, user_id: str) -> bool:
        """Toggle premium status for a user."""
        if user_id in self.user_data["users"]:
            if "premium" not in self.user_data:
                self.user_data["premium"] = []
            
            if user_id in self.user_data["premium"]:
                self.user_data["premium"].remove(user_id)
            else:
                self.user_data["premium"].append(user_id)
            self.save_data()
            return True
        return False

    def get_user_stats(self, user_id: str) -> Dict[str, Any]:
        """Get statistics for a specific user."""
        return self.stats["users"].get(user_id, {"downloads": 0, "failed": 0, "platforms": {}})

    def get_global_stats(self) -> Dict[str, Any]:
        """Get global statistics."""
        return {
            "total_downloads": self.stats["total_downloads"],
            "platforms": self.stats["platforms"],
            "total_users": len(self.user_data["users"]),
            "premium_users": len(self.user_data.get("premium", [])),
            "banned_users": len(self.user_data["banned"])
        }

# Create global database instance
db = Database() 