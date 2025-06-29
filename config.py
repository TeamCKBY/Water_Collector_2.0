# config.py
import os

# --- GENERAL BOT SETTINGS ---
# Confidence level for image matching (e.g., 0.8 means 80% match).
IMAGE_CONFIDENCE_THRESHOLD = 0.80
WATER_IMAGE_NAMES = ["w_elem_01.png", "w_elem_02.png", "w_elem_03.png", "w_elem_04.png", "w_elem_05.png", "w_elem_06.png"]

# --- TIMING & DELAYS ---
# Small delay after each pyautogui action (e.g., press, click).
MOUSE_MOVEMENT_DURATION = 0.1 # Duration for mouse movements in seconds
MIN_DEFAULT_ACTION_DELAY = 0.5
MAX_DEFAULT_ACTION_DELAY = 0.7
DEFAULT_CHECK_DELAY = 0.05
MOVEMENT_KEY_HOLD_DURATION = 0.2 # <--- ADD THIS NEW LINE (start with 0.15 seconds)
POST_TRANSITION_DELAY = 1


# Interval (in seconds) between checks when waiting for screen transitions.
# WAIT_FOR_TRANSITION_INTERVAL = 0.15
# Maximum time (in seconds) to wait for a map to load.
MAP_LOAD_TIMEOUT = 15
# Screen Detection Thresholds
SCREEN_BLACK_COLOR_THRESHOLD = 25 # Average pixel value below which the screen is considered black
# Duration (in seconds) to wait while performing the harvest action.
MIN_HARVEST_DURATION = 4.5
MAX_HARVEST_DURATION = 5.0

# --- ROUTE & MAPS ---
# The specific map the bot expects to start on.
STARTING_MAP_NAME = "MAP_01"
# Total number of maps in the water collection cycle.
NUMBER_OF_MAPS_IN_CYCLE = 12 

# --- DEBUGGING / DEVELOPMENT ---
# If set to True, pyautogui will draw rectangles around found images (useful for debugging).
DEBUG_MODE_HIGHLIGHT = False