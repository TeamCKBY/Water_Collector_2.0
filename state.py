# state.py
from PySide6.QtCore import Signal, QObject

bot_is_running = True
stop_reason = None  # or "" by default
water_collected = 0

class State(QObject):
    water_collected = Signal(int)  # <--- Add this

    def __init__(self):
        super().__init__()
        self.bot_is_running = False
        self.water_counter = 0
        self.stop_reason = None 

    def reset(self):
        self.bot_is_running = False
        self.water_counter = 0
        self.water_collected.emit(0)  # <--- Emit signal on reset
        

    def increment_water(self):
        self.water_counter += 1
        self.water_collected.emit(self.water_counter)  # <--- Emit signal on update

state = State()