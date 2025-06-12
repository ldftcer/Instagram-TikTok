import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Bot Configuration
TOKEN = os.getenv("TOKEN")
ADMIN_ID = os.getenv("ADMIN_ID")
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME")
BACKUP_CHAT_ID = os.getenv("BACKUP_CHAT_ID")

# File Paths
DATA_FILE = "data/user_data.json"
STATS_FILE = "data/stats.json"
TEMP_DIR = "downloads"
LOG_DIR = "logs"

# Create necessary directories
for directory in [TEMP_DIR, LOG_DIR, "data"]:
    os.makedirs(directory, exist_ok=True)

# Rate Limiting
FREE_USER_DAILY_LIMIT = 5
PREMIUM_PRICE = 5  # in USD

# Download Settings
MAX_FILE_SIZE_FREE = 15  # MB
MAX_FILE_SIZE_PREMIUM = 100  # MB

# Backup Settings
BACKUP_INTERVAL = 3600  # seconds
FILE_CLEANUP_INTERVAL = 3600  # seconds 