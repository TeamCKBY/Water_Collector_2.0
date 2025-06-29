# routes/travel_routes.py

# --- TRAVEL ROUTES ---
# This dictionary holds the specific sequences of directional keys
# for the bot to travel from one map to the next in the cycle.
# Each key is the starting map name (e.g., "MAP_01"), and its value
# is a list of constants.MOVE_ directions.

# Import constants to use the defined directional keys
import constants

TRAVEL_ROUTES = {
    "MAP_01_TO_MAP_02": [
        constants.MOVE_SOUTH,
        constants.MOVE_WEST,
    ],
    
    "MAP_02_TO_MAP_03": [
        constants.MOVE_NORTH,
        constants.MOVE_EAST,
        constants.MOVE_SOUTH,
        constants.MOVE_EAST,
    ],

    "MAP_03_TO_MAP_04": [
        constants.MOVE_SOUTH,
        constants.MOVE_SOUTH,
        constants.MOVE_SOUTH,
        constants.MOVE_SOUTH,
        constants.MOVE_EAST,
     ],

    "MAP_04_TO_MAP_05": [
        constants.MOVE_SOUTH,
        constants.MOVE_SOUTH,
        constants.MOVE_SOUTH,
        constants.MOVE_EAST,
    ],

    "MAP_05_TO_MAP_06": [
        constants.MOVE_SOUTH,
        constants.MOVE_SOUTH,
        constants.MOVE_EAST,
    ],

    "MAP_06_TO_MAP_07": [
        constants.MOVE_EAST,
        constants.MOVE_EAST,
    ],

    "MAP_07_TO_MAP_08": [
        constants.MOVE_NORTH,
        constants.MOVE_NORTH,
        constants.MOVE_NORTH,
    ],

    "MAP_08_TO_MAP_09": [
        constants.MOVE_EAST,
        constants.MOVE_EAST,
        constants.MOVE_EAST,
        constants.MOVE_EAST,
        constants.MOVE_NORTH,
        constants.MOVE_NORTH,
        constants.MOVE_NORTH,
        constants.MOVE_NORTH,
    ],

    "MAP_09_TO_MAP_10": [
        constants.MOVE_NORTH,
        constants.MOVE_WEST,
        constants.MOVE_WEST,
        constants.MOVE_WEST,
        constants.MOVE_WEST,
        constants.MOVE_WEST,
    ],

    "MAP_10_TO_MAP_11": [
        constants.MOVE_NORTH,
        constants.MOVE_EAST,
        constants.MOVE_EAST,
    ],
    
    "MAP_11_TO_MAP_12": [
        constants.MOVE_NORTH,
    ],

    "MAP_12_TO_MAP_01": [
        constants.MOVE_WEST,
        constants.MOVE_WEST,
        constants.MOVE_WEST,
        constants.MOVE_WEST,
        constants.MOVE_WEST,
        constants.MOVE_WEST,
        constants.MOVE_WEST,
    ]
}

# --- MAP ORDER ---
# A list defining the sequential order of maps in your collection route.
MAP_ORDER = [
    "MAP_01", "MAP_02", "MAP_03", "MAP_04", "MAP_05", "MAP_06",
    "MAP_07", "MAP_08", "MAP_09", "MAP_10", "MAP_11", "MAP_12"
]