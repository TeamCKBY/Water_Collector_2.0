# utils.py

import random
import keyboard
import pydirectinput
import os
import logging
os.makedirs("logs", exist_ok=True)
import time
import pyautogui
from PIL import ImageGrab 
import sys
import state
from PySide6.QtCore import Signal, QObject
from helpers import simplify_log_message


class LogSignalEmitter(QObject):
    new_log = Signal(str)

log_signals = LogSignalEmitter()

# Import constants and config for shared values
import constants
import config

# --- LOGGING SETUP ---
logger = logging.getLogger("WaterCollectorBot")
logger.setLevel(logging.DEBUG) 
if not logger.handlers:
    file_handler = logging.FileHandler(constants.LOG_FILE_PATH)
    file_handler.setLevel(logging.DEBUG)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

logging.addLevelName(25, 'SUCCESS')
def success(self, message, *args, **kwargs):
    if self.isEnabledFor(25):
        self._log(25, message, args, **kwargs)
logging.Logger.success = success

def log_message(level, message, **kwargs):
    """Logs to file and emits only friendly messages to GUI."""
    if not state.bot_is_running:
        return

    # Always log full info to file/terminal
    if level == constants.LOG_INFO:
        logger.info(message, **kwargs)
    elif level == constants.LOG_SUCCESS:
        logger.success(message, **kwargs)
    elif level == constants.LOG_WARNING:
        logger.warning(message, **kwargs)
    elif level == constants.LOG_ERROR:
        logger.error(message, **kwargs)
    elif level == constants.LOG_DEBUG:
        logger.debug(message, **kwargs)
    else:
        logger.info(message, **kwargs)

    # --- Emit simplified message to GUI ---
    simplified = simplify_for_gui(message)
    if simplified:  # only emit important messages
        log_signals.new_log.emit(simplified)

def simplify_for_gui(raw_text):
    """Converts raw log to a friendly status message, or returns None to suppress."""
    print(f"Raw log: {raw_text}")  # Debugging line to see raw logs
    keyword_map = [
        ("Starting bot cycle in 5 seconds", "Starting in 5 seconds..."),
        ("Confirming starting map", "Confirming starting map..."),
        ("Correct starting map confirmed", "Map confirmed!"),
        ("Could not confirm starting map", "Invalid starting map."),
        ("Scanning screen for water", "Looking for water..."),
        ("Water found at", "Water found!"),
        ("Water not found", "Water not found."),
        ("Harvest action completed", "Harvest complete!"),
        ("Traveling from", "Traveling to next map..."),

        ("Map transition timeout", "Map load failed."),
        ("Arrived at", "Arrived at new map."),
        ("Bot has stopped", "Bot stopped."),
    ]

    for keyword, friendly in keyword_map:
        if keyword.lower() in raw_text.lower():
            return friendly

    return None  # suppress all other logs        

# --- AUTOMATION FUNCTIONS ---

def press_key(key):
    """Uses the best library for each key type."""
    if not state.bot_is_running: return # <--- Added safety check
    if key in [constants.MOVE_NORTH, constants.MOVE_SOUTH, constants.MOVE_EAST, constants.MOVE_WEST]:
        log_message(constants.LOG_DEBUG, f"Holding movement key: {key} (using 'keyboard' library)")
        keyboard.press(key)
        time.sleep(config.MOVEMENT_KEY_HOLD_DURATION)
        keyboard.release(key)
    else:
        log_message(constants.LOG_DEBUG, f"Tapping action key: {key} (using 'pydirectinput' library)")
        pydirectinput.press(key)
    time.sleep(random.uniform(config.MIN_DEFAULT_ACTION_DELAY, config.MAX_DEFAULT_ACTION_DELAY))

def click_at(x, y):
    """Moves the mouse to (x, y) and performs a click."""
    if not state.bot_is_running: return # <--- Added safety check
    pyautogui.moveTo(x, y, duration=config.MOUSE_MOVEMENT_DURATION)
    pyautogui.click()
    time.sleep(random.uniform(config.MIN_DEFAULT_ACTION_DELAY, config.MAX_DEFAULT_ACTION_DELAY))
    log_message(constants.LOG_DEBUG, f"Clicked at: ({x}, {y})")

def wait_for_map_transition():
    """
    Waits for the screen to turn black (1 frame), then visible again.
    Returns 'success', 'stopped', or 'timeout'.
    """
    log_message(constants.LOG_INFO, "Waiting for map transition...")
    
    # Optional: A tiny delay before starting checks
    #time.sleep(0.05)
    
    start_time = time.time()

    # --- Phase 1: Wait for screen to become black ---
    log_message(constants.LOG_DEBUG, "Waiting for screen to turn black...")
    screen_turned_black = False
    
    while time.time() - start_time < config.MAP_LOAD_TIMEOUT:
        if not state.bot_is_running:
            log_message(constants.LOG_INFO, "Map transition cancelled by user.")
            return 'stopped'

        screenshot = ImageGrab.grab(bbox=(
            pyautogui.size().width * 0.4, 
            pyautogui.size().height * 0.4, 
            pyautogui.size().width * 0.6, 
            pyautogui.size().height * 0.6
        ))
        pixels = list(screenshot.getdata())
        avg_brightness = sum(sum(p[:3]) for p in pixels) / (len(pixels) * 3)

        # --- REVERTED LOGIC ---
        # Now only requires seeing black ONCE to proceed.
        if avg_brightness < config.SCREEN_BLACK_COLOR_THRESHOLD:
            log_message(constants.LOG_DEBUG, "Screen is black. Waiting for it to become visible again.")
            screen_turned_black = True
            break  # Exit the loop to proceed to Phase 2
        
        time.sleep(config.DEFAULT_CHECK_DELAY)

    if not screen_turned_black:
        log_message(constants.LOG_WARNING, "Map transition timeout: Screen did not turn black.")
        return 'timeout'

    # --- Phase 2: Wait for screen to become visible again ---
    start_time_phase2 = time.time()
    while time.time() - start_time_phase2 < config.MAP_LOAD_TIMEOUT:
        if not state.bot_is_running:
            log_message(constants.LOG_INFO, "Map transition cancelled by user.")
            return 'stopped'

        screenshot = ImageGrab.grab(bbox=(
            pyautogui.size().width * 0.45, # Starts 45% from the left
            pyautogui.size().height * 0.45, # Starts 45% from the top
            pyautogui.size().width * 0.55,  # Ends 55% from the left
            pyautogui.size().height * 0.55  # Ends 55% from the top
        ))
        pixels = list(screenshot.getdata())
        avg_brightness = sum(sum(p[:3]) for p in pixels) / (len(pixels) * 3)

        # --- REVERTED LOGIC ---
        # Also only requires seeing a visible screen ONCE to succeed.
        if avg_brightness > config.SCREEN_BLACK_COLOR_THRESHOLD:
            log_message(constants.LOG_DEBUG, "Screen is visible again. Map transition complete.")
            return 'success'
            
        time.sleep(config.DEFAULT_CHECK_DELAY)

    log_message(constants.LOG_WARNING, "Map transition timeout: Screen did not become visible again.")
    return 'timeout'