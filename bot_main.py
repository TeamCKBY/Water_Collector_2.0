# bot_main.py

import time
import pyautogui
import sys
import os
import random
import keyboard
import state
from state import state

# Import our custom modules
import config
import constants
from utils import log_message, press_key, wait_for_map_transition, click_at
from routes import travel_routes

# --- REMOVED GLOBAL FLAG FROM HERE ---

# --- NEW: The hotkey function now modifies the state file ---
def signal_stop():
    """This function is called when the F8 key is pressed."""
    # We check the state first to prevent this message from printing multiple times
    # if the user spams the F8 key.
    if state.bot_is_running:
        # First, we log a nice message to give the user instant feedback.
        log_message(constants.LOG_SUCCESS, "Stopped collecting water.")
        # Then, we set the flag to false.
        state.bot_is_running = False

def scan_for_water():
    """Scans the screen for water elements based on defined image names."""
    log_message(constants.LOG_INFO, "Scanning screen for water...")
    water_coords = None
    found_image_name = None

    for image_name in config.WATER_IMAGE_NAMES:
        image_path = os.path.join(constants.IMAGES_DIR, image_name)
        if not os.path.exists(image_path):
            log_message(constants.LOG_ERROR, f"Water image file not found: {image_path}")
            continue # Skip to the next image if file is missing

        try:
            # Attempt to locate the image on screen
            location = pyautogui.locateOnScreen(image_path, confidence=config.IMAGE_CONFIDENCE_THRESHOLD, grayscale=True,
                                                region=None) 

            if location:
                # Calculate the center coordinates of the found image
                water_coords = pyautogui.center(location)
                found_image_name = image_name
                log_message(constants.LOG_SUCCESS, f"Water found at {water_coords} using '{found_image_name}'!")
                state.increment_water()
                return True, water_coords, found_image_name
        except pyautogui.ImageNotFoundException:
            # If the image is not found, just continue to the next image in the list
            log_message(constants.LOG_DEBUG, f"'{image_name}' not found on screen with current confidence. Trying next image...")
        except Exception as e:
            # Catch any other unexpected errors during image scanning
            log_message(constants.LOG_ERROR, f"An error occurred while scanning for '{image_name}': {e}", exc_info=True)

    # --- CHANGE IS HERE ---
    # Changed from INFO to WARNING and updated the text for clarity.
    log_message(constants.LOG_INFO, "Water not found")
    time.sleep(0.75)
    return False, None, None # Return False if no water found after checking all images

def harvest_water(water_coords):
    # This function is also fine.
    log_message(constants.LOG_INFO, f"Attempting to harvest water at {water_coords}...")
    click_at(water_coords[0], water_coords[1] - 20)
    harvest_sleep_time = random.uniform(config.MIN_HARVEST_DURATION, config.MAX_HARVEST_DURATION)
    time.sleep(harvest_sleep_time) # The log mute will happen after this sleep.
    log_message(constants.LOG_SUCCESS, "Harvest action completed.")

def navigate_route(route_name):
    """
    Presses the keys for a given route and waits for a map transition
    after EACH key press.
    Returns True on success, False on failure or stop.
    """
    route = travel_routes.TRAVEL_ROUTES.get(route_name)
    if not route:
        log_message(constants.LOG_ERROR, f"Error: Travel route '{route_name}' not found!")
        return False

    log_message(constants.LOG_INFO, "Executing travel route...")

    for key in route:
        if not state.bot_is_running:
            return False

        press_key(key)

        # --- REVERTED LOGIC: Wait for transition after EVERY key press ---
        transition_status = wait_for_map_transition()
        
        if transition_status == 'success':
            # If successful, pause for the character to "settle" before the next action
            log_message(constants.LOG_INFO, f"Map change successful. Pausing ({config.POST_TRANSITION_DELAY}s)...")
            time.sleep(config.POST_TRANSITION_DELAY)
        else:
            # If not successful, log the failure and stop the entire route
            log_message(constants.LOG_ERROR, f"Navigation failed during transition. Status: {transition_status}")
            return False
    
    # If the entire loop of keys and successful transitions completes
    log_message(constants.LOG_SUCCESS, "Route completed successfully!")
    return True

# --- MAIN BOT LOGIC (MODIFIED) ---
def run_bot():
    """Main function to run the water collection bot cycle."""
    state.bot_is_running = True # Set the state to True
    keyboard.add_hotkey('f8', signal_stop)

    log_message(constants.LOG_INFO, "Water Collector 2.0 Bot Started!")
    log_message(constants.LOG_INFO, "TAP F8 ONCE TO STOP THE BOT GRACEFULLY.")
    log_message(constants.LOG_INFO, "Starting bot cycle in 5 seconds...")
    time.sleep(5)

    try:
        current_map_index = travel_routes.MAP_ORDER.index(config.STARTING_MAP_NAME)
        while state.bot_is_running: # The loop now checks the shared state
            current_map = travel_routes.MAP_ORDER[current_map_index]
            log_message(constants.LOG_INFO, f"Currently on {current_map}.")
            water_found, water_coords, _ = scan_for_water()
            if water_found:
                harvest_water(water_coords)

            if not state.bot_is_running: break

            next_map_index = (current_map_index + 1) % len(travel_routes.MAP_ORDER)
            next_map_name = travel_routes.MAP_ORDER[next_map_index]
            route_name = f"{current_map}_TO_{next_map_name}"

            log_message(constants.LOG_INFO, f"Traveling from {current_map} to {next_map_name}.")
            
            # --- MODIFIED LOGIC HERE ---
            # Capture the True/False result from navigate_route
            navigation_successful = navigate_route(route_name)
            
            # Check if navigation succeeded before updating state
            if navigation_successful:
                current_map_index = next_map_index # Only update position on success
                log_message(constants.LOG_INFO, "--- Cycle continues ---")
                time.sleep(1)
            else:
                # If navigation failed or was stopped, stop the bot.
                log_message(constants.LOG_ERROR, "Stopping bot due to navigation failure.")
                state.bot_is_running = False
                break # Exit the main while loop
            # --- END OF MODIFIED LOGIC ---

    except KeyboardInterrupt:
        log_message(constants.LOG_INFO, "Bot stopped by user (Ctrl+C).")
    except Exception as e:
        log_message(constants.LOG_ERROR, f"An unexpected error occurred: {e}", exc_info=True)
    
    finally:
        keyboard.remove_hotkey('f8')
        if state.stop_reason:
            log_message(constants.LOG_ERROR, state.stop_reason)
            state.stop_reason = None
        
        log_message(constants.LOG_INFO, "Bot has stopped. You have full control.")


if __name__ == "__main__":
    run_bot()