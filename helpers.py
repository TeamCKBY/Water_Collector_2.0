def simplify_log_message(text):
    replacements = {
        "Water Collector 2.0 Bot Started!": "Bot started.",
        "TAP F8 ONCE TO STOP THE BOT GRACEFULLY.": "",
        "Starting bot cycle in 5 seconds...": "Starting in 5 seconds...",
        "Scanning screen for water...": "Looking for water...x",
        "Water found at": "Water detected!",
        "Harvest action completed.": "Harvest complete.",
        "Traveling from": "Traveling to next map...",
        "Arrived at": "Arrived at new map!",
        "Water not found": "Water not found!",
        "Waiting for map transition": "Transitioning...",
        "Map transition successful": "Map loaded.",
        "Map transition timeout": "Map load failed.",
        "Correct starting map confirmed": "Starting map confirmed!",
        "Could not confirm starting map": "Invalid starting map.",
        "Bot has stopped": "Bot stopped.",
        "Bot stopped by user": "Stopped by user.",
        "Incorrect map": "Wrong map.",
        "Currently on MAP_": "Currently on map.",
        "Ready!": "Ready!",
    }

        # Handle partial match manually
    if "Water not found!" in text:
        return "Water not found."

    # Fallback loop
    for key, val in replacements.items():
        if key in text:
            return val
    return text  # fallback if no match