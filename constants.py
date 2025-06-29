# constants.py
import os

# Directories
BASE_DIR = os.path.dirname(os.path.abspath(__file__)) # Gets the directory of constants.py
IMAGES_DIR = os.path.join(BASE_DIR, 'images', 'bot_elements')

# --- KEYBOARD MAPPINGS ---
# Movement Keys (Updated for 'keyboard' library)
# These generally correspond to Numpad keys in games, but use the 'keyboard' library's string names.
MOVE_NORTH = 'up'    # Corresponds to Numpad 8
MOVE_SOUTH = 'down'  # Corresponds to Numpad 2
MOVE_EAST = 'right'  # Corresponds to Numpad 6
MOVE_WEST = 'left'   # Corresponds to Numpad 4

# --- LOGGING ---
# Prefixes for different types of log messages.
LOG_INFO = "[INFO]"
LOG_SUCCESS = "[SUCCESS]"
LOG_WARNING = "[WARNING]"
LOG_ERROR = "[ERROR]"
LOG_DEBUG = "[DEBUG]"

# --- FILE PATHS (Relative to the main bot directory) ---
ORIGINAL_IMAGES_DIR = "images/original_templates"
SCALED_TEMP_DIR = "images/scaled_temp"
BOT_ELEMENTS_DIR = "images/bot_elements"
LOG_FILE_PATH = "logs/bot_activity.log"

# --- GAME/SCREEN ---
# The resolution at which your original template images were captured.
BASE_GAME_RESOLUTION = (3840, 2160)