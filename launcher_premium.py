# launcher.py
import ctypes
import sys
import os
import hashlib # <--- NEW: Added for hashing keys
import re

# --- NEW: Define paths for activation files ---
# This file will be created after successful activation
ACTIVATION_FILE = "activation.dat" 
# This file contains the list of all valid key hashes
HASHES_FILE = "clickberry_hashes.txt" 

def resource_path(relative_path):
    """Get absolute path to resource (works for dev and .exe)"""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# --- NEW: Function for writable data files ---
def data_path(relative_path):
    """ Get absolute path to data file (works for dev and .exe) """
    if getattr(sys, 'frozen', False):
        # If the application is run as a bundle, the frozen flag is set
        base_path = os.path.dirname(sys.executable)
    else:
        # If run as a script, just use the current directory
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, relative_path)

from functools import partial
# --- NEW: QLineEdit is added for the key input field ---
from PySide6.QtWidgets import QApplication, QWidget, QLabel, QGridLayout, QHBoxLayout, QPushButton, QLineEdit
from PySide6.QtGui import QMovie, QFont, QPixmap, QIcon
from PySide6.QtCore import Qt, QSize, Signal, QObject, QThread, QTimer, QTime, qInstallMessageHandler

def suppress_qt_warnings(*args):
    pass

qInstallMessageHandler(suppress_qt_warnings)
from utils import log_signals
from helpers import simplify_log_message        

import bot_main
import state
from state import state as state_instance
import config
from utils import log_message

ASSETS_DIR = os.path.join(os.path.dirname(__file__), 'assets')

# --- NEW: Activation Logic Functions ---

def check_if_activated():
    """Check if the activation file exists."""
    # Use data_path to look next to the .exe
    return os.path.exists(data_path(ACTIVATION_FILE))

def load_hashes():
    """Load and clean the hashes from the file using regular expressions."""
    try:
        # Use data_path to look next to the .exe
        with open(data_path(HASHES_FILE), 'r') as f:
            content = f.read()
            hashes = re.findall(r'[a-f0-9]{64}', content)
            return hashes
    except FileNotFoundError:
        print(f"CRITICAL: {HASHES_FILE} not found!")
        return []

def validate_key(key):
    """Hash the input key and check if it's in the valid hashes list."""
    if not key:
        return None, "Key cannot be empty."

    # 1. Hash the user's input key
    encoded_key = key.encode('utf-8')
    hasher = hashlib.sha256(encoded_key)
    hex_hash = hasher.hexdigest()

    # 2. Load all valid hashes
    valid_hashes = load_hashes()
    
    # 3. Check if the user's hash is in the list
    if hex_hash in valid_hashes:
        return hex_hash, "Key is valid!"
    else:
        return None, "Invalid or already used key."

def mark_key_as_used(used_hash):
    """Remove a hash from the list and rewrite the file."""
    current_hashes = load_hashes()
    if used_hash in current_hashes:
        current_hashes.remove(used_hash)
        
        new_content = "[\n"
        for i, h in enumerate(current_hashes):
            new_content += f'    "{h}"'
            if i < len(current_hashes) - 1:
                new_content += ",\n"
        new_content += "\n]"
        
        # Use data_path to write the file next to the .exe
        with open(data_path(HASHES_FILE), 'w') as f:
            f.write(new_content)
        return True
    return False

def create_activation_file():
    """Create the local activation file to remember the user."""
    # Use data_path to write the file next to the .exe
    with open(data_path(ACTIVATION_FILE), 'w') as f:
        f.write("activated")

# --- NEW: Activation Window GUI ---
class ActivationWindow(QWidget):
    activation_successful = Signal()

    def __init__(self):
        super().__init__()
        self.initializeUI()
    
    def add_background_image(self):
        self.background_label = QLabel(self)
        pixmap = QPixmap(resource_path(os.path.join("assets", "bg_01.png")))
        self.background_label.setPixmap(pixmap)
        self.background_label.setScaledContents(True)
        self.background_label.resize(self.size())
        self.background_label.lower()

    def resizeEvent(self, event):
        if hasattr(self, "background_label"):
            self.background_label.resize(self.size())
        super().resizeEvent(event)

    def initializeUI(self):
        self.add_background_image()
        self.setFixedSize(210, 210) # Same size as main app
        self.setWindowTitle("ckby - Premium Activation")
        self.setWindowIcon(QIcon(os.path.join(ASSETS_DIR, "ckby_icon.ico")))
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)

        layout = QGridLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)

        title_label = QLabel("Premium Activation")
        title_label.setFont(QFont("Arial", 14, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label, 0, 0)
        
        info_label = QLabel("Please enter your key:")
        info_label.setFont(QFont("Arial", 10))
        info_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(info_label, 1, 0)

        self.key_input = QLineEdit()
        self.key_input.setPlaceholderText("CKBY-XXXX-XXXX")
        self.key_input.setFont(QFont("Arial", 10))
        self.key_input.setStyleSheet("color: grey;")
        self.key_input.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.key_input, 2, 0)

        self.activate_button = QPushButton("Activate")
        self.activate_button.setFont(QFont("Arial", 12, QFont.Bold))
        self.activate_button.clicked.connect(self.on_activate_clicked)
        layout.addWidget(self.activate_button, 3, 0)

        self.status_label = QLabel("")
        self.status_label.setFont(QFont("Arial", 10))
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label, 4, 0)

        footer_label = QLabel("Made with ❤️ by ckby")
        footer_label.setAlignment(Qt.AlignCenter)
        footer_label.setStyleSheet("color: #888888; font-size: 10px;")
        footer_label.setFont(QFont("Segoe UI", 10))
        layout.addWidget(footer_label, 5, 0)
        
        self.apply_styles()

    def apply_styles(self):
        # Using similar colors from the main app for consistency
        lime_green, black, white = "#a7e9af", "#000000", "#FFFFFF"
        self.setStyleSheet(f"""
            QWidget {{ background-color: transparent; }}
            QLabel {{ color: {black}; }}
            QLineEdit {{
                background-color: {white}; 
                border: 2px solid {black};
                border-radius: 8px; 
                padding: 5px;
            }}
            QPushButton {{
                background-color: {lime_green}; border: 2px solid {black};
                border-radius: 8px; color: {black}; padding: 5px;
            }}
            QPushButton:hover {{ background-color: #c1f0c7; }}
        """)

    def on_activate_clicked(self):
        user_key = self.key_input.text().strip()
        validated_hash, message = validate_key(user_key)
        
        if validated_hash:
            # Key is valid, now mark it as used
            mark_key_as_used(validated_hash)
            # Create the local activation file
            create_activation_file()
            
            self.status_label.setText("✅ Success! App will start...")
            self.activate_button.setEnabled(False)
            
            # Close this window and signal success after a short delay
            QTimer.singleShot(1500, self.on_success)
        else:
            self.status_label.setText(f"⛔ {message}")

    def on_success(self):
        self.activation_successful.emit()
        self.close()

# --- Worker Thread for Bot Execution --- (No Changes Here)
class BotWorker(QObject):
    finished = Signal()
    status_updated = Signal(str)

    def run(self):
        try:
            bot_main.run_bot()
        except Exception as e:
            print(f"An error occurred in the bot thread: {e}")
        finally:
            self.finished.emit()


# --- Main GUI --- (No Changes Here)
class ClickBerryApp(QWidget):

    def resizeEvent(self, event):
        if hasattr(self, "background_label"):
            self.background_label.resize(self.size())
        super().resizeEvent(event)

    def __init__(self):
        super().__init__()
        self.bot_thread = None
        self.bot_worker = None
        self.selected_duration = "Max"
        self.runtime_timer = QTimer()
        self.runtime_timer.timeout.connect(self.update_runtime)
        self.start_time = QTime(0, 0, 0)
        self.initializeUI()
        self.auto_stop_timer = QTimer()
        self.auto_stop_timer.setSingleShot(True)
        self.auto_stop_timer.timeout.connect(self.stop_bot)

    def add_background_image(self):
        self.background_label = QLabel(self)
        pixmap = QPixmap(resource_path(os.path.join("assets", "bg_01.png")))
        self.background_label.setPixmap(pixmap)
        self.background_label.setScaledContents(True)
        self.background_label.resize(self.size())
        self.background_label.lower()
        
    def initializeUI(self):
        self.add_background_image()
        self.setFixedSize(210, 210)
        self.setWindowTitle("ckby - Water Collector 2.0")
        self.setWindowIcon(QIcon(os.path.join(ASSETS_DIR, "ckby_icon.ico")))
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)

        main_layout = QGridLayout(self)
        main_layout.setContentsMargins(5, 5, 5, 5)

        self.mascot_label = QLabel(self)
        self.mascot_label.setAlignment(Qt.AlignCenter)
        self.sleep_movie = QMovie(resource_path(os.path.join("assets", "mascot_sleep.gif")))
        self.active_movie = QMovie(resource_path(os.path.join("assets", "mascot_active.gif")))
        self.sleep_movie.setScaledSize(QSize(0, 0))
        self.active_movie.setScaledSize(QSize(0, 0))
        self.mascot_label.setMovie(self.sleep_movie)
        self.sleep_movie.start()
        main_layout.addWidget(self.mascot_label, 0, 0, 0, 2)

        timer_button_layout = QHBoxLayout()
        timer_button_layout.setSpacing(5)
        self.timer_buttons = {}
        timer_options = ["30m", "1h", "2h", "Max"]
        for text in timer_options:
            button = QPushButton(text)
            button.setFont(QFont("Arial", 9.5, QFont.Bold))
            button.setFixedSize(40, 30)
            button.clicked.connect(partial(self.on_timer_button_clicked, text))
            self.timer_buttons[text] = button
            timer_button_layout.addWidget(button)
        main_layout.addLayout(timer_button_layout, 1, 0, 1, 2, Qt.AlignCenter)

        self.start_button = QPushButton("Start")
        self.start_button.setFont(QFont("Arial", 12, QFont.Bold))
        self.start_button.setFixedSize(175, 30)
        self.start_button.clicked.connect(self.start_bot)
        main_layout.addWidget(self.start_button, 2, 0, 1, 2, Qt.AlignCenter)

        self.stop_button = QPushButton("Stop")
        self.stop_button.setFont(QFont("Arial", 12, QFont.Bold))
        self.stop_button.setFixedSize(175, 30)
        self.stop_button.clicked.connect(self.stop_bot)
        main_layout.addWidget(self.stop_button, 3, 0, 1, 2, Qt.AlignCenter)
        self.stop_button.setEnabled(False)

        self.runtime_label = QLabel("00:00:00")
        self.runtime_label.setFont(QFont("Arial", 10, QFont.Bold))
        self.runtime_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.runtime_label, 4, 0, 1, 2)

        self.water_counter_label = QLabel("💧0💧")
        self.water_counter_label.setFont(QFont("Arial", 10))
        self.water_counter_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.water_counter_label, 5, 0, 1, 2)

        friendly_text = simplify_log_message("Ready!")
        self.status_label = QLabel(friendly_text)
        self.status_label.setFont(QFont("Arial", 10))
        self.status_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.status_label, 6, 0, 1, 2)

        main_layout.setRowStretch(7, 1)

        self.apply_styles()
        self.on_timer_button_clicked(self.selected_duration)
        
        log_signals.new_log.connect(self.update_status_from_log)
        state_instance.water_collected.connect(self.update_water_display)

        footer_label = QLabel("Made with ❤️ by ckby")
        footer_label.setAlignment(Qt.AlignCenter)
        footer_label.setStyleSheet("color: #888888; font-size: 10px;")
        footer_label.setFont(QFont("Segoe UI", 10))
        main_layout.addWidget(footer_label, 99, 0, 1, 2)

    def apply_styles(self):
        lime_green, light_lime, dark_lime = "#a7e9af", "#c1f0c7", "#8ccb95"
        red, light_red, dark_red = "#f0a1a1", "#f5b7b7", "#d98a8a"
        yellow, black, white = "#fdeca6", "#000000", "#FFFFFF"
        self.setStyleSheet(f"""
            QLabel {{ color: {black}; }}
            QPushButton {{
                background-color: {white}; border: 2px solid {black};
                border-radius: 8px; color: {black};
            }}
            QPushButton:hover {{ background-color: #f5f5f5; }}
            QPushButton:disabled {{ background-color: #d3d3d3; color: #808080; }}
            QPushButton[selected="true"] {{ background-color: {yellow}; }}
            QPushButton#start_button {{ background-color: {lime_green}; }}
            QPushButton#start_button:hover {{ background-color: {light_lime}; }}
            QPushButton#start_button:pressed {{ background-color: {dark_lime}; }}
            QPushButton#stop_button {{ background-color: {red}; }}
            QPushButton#stop_button:hover {{ background-color: {light_red}; }}
            QPushButton#stop_button:pressed {{ background-color: {dark_red}; }}
        """)
        self.start_button.setObjectName("start_button")
        self.stop_button.setObjectName("stop_button")

    def on_timer_button_clicked(self, selected_text):
        self.selected_duration = selected_text
        for text, button in self.timer_buttons.items():
            button.setProperty("selected", str(text == selected_text).lower())
        self.apply_styles()

    def start_bot(self):
        state_instance.reset()
        self.mascot_label.setMovie(self.active_movie)
        self.active_movie.start()
        self.runtime_label.setText("00:00:00")
        self.start_runtime_timer()
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.bot_thread = QThread()
        self.bot_worker = BotWorker()
        self.bot_worker.moveToThread(self.bot_thread)
        self.bot_thread.started.connect(self.bot_worker.run)
        self.bot_worker.finished.connect(self.bot_thread.quit)
        self.bot_worker.finished.connect(self.bot_worker.deleteLater)
        self.bot_thread.finished.connect(self.bot_thread.deleteLater)
        self.bot_worker.status_updated.connect(self.status_label.setText)
        self.bot_thread.finished.connect(self.on_bot_finished)
        duration_seconds = self.get_selected_duration_seconds()
        if duration_seconds:
            self.auto_stop_timer.start(duration_seconds * 1000)
        self.bot_thread.start()

    def stop_bot(self):
        self.auto_stop_timer.stop()
        print("Stop button pressed. Updating state to stop bot.")
        state_instance.bot_is_running = False
        self.status_label.setText("Stopping... ")
        self.stop_runtime_timer()
        self.mascot_label.setMovie(self.sleep_movie)
        self.sleep_movie.start()
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)

    def on_bot_finished(self):
        self.auto_stop_timer.stop()
        self.stop_runtime_timer()
        self.mascot_label.setMovie(self.sleep_movie)
        self.sleep_movie.start()
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        if state.stop_reason:
            self.status_label.setText(state.stop_reason)
            state.stop_reason = None
        else:
            self.status_label.setText("Stopped collecting water")

    def start_runtime_timer(self):
        self.start_time = QTime(0, 0, 0)
        self.runtime_timer.start(1000)

    def stop_runtime_timer(self):
        self.runtime_timer.stop()
        self.update_runtime()

    def update_runtime(self):
        self.start_time = self.start_time.addSecs(1)
        self.runtime_label.setText(f"{self.start_time.toString('hh:mm:ss')}")

    def update_status_from_log(self, message):
        friendly_text = simplify_log_message(message)
        self.status_label.setText(friendly_text) 

    def update_water_display(self, count):
        self.water_counter_label.setText(f"💧{count}💧")

    def get_selected_duration_seconds(self):
        mapping = {"30m": 30*60, "1h": 60*60, "2h": 2*60*60, "Max": None}
        return mapping.get(self.selected_duration, None)

    def update_map_visual(self, map_name):
        if map_name.startswith("MAP_"):
            try:
                index = int(map_name.split("_")[1]) - 1
                for i, label in enumerate(self.map_dots):
                    dot_file = "map_dot_on_16.png" if i == index else "map_dot_off_16.png"
                    label.setPixmap(QPixmap(os.path.join(ASSETS_DIR, dot_file)))
            except (IndexError, ValueError):
                pass

# --- NEW: Updated Launch Logic ---
if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    main_app_window = None

    def show_main_app():
        global main_app_window
        main_app_window = ClickBerryApp()
        main_app_window.show()

    if check_if_activated():
        show_main_app()
    else:
        activation_win = ActivationWindow()
        # When activation is successful, launch the main app
        activation_win.activation_successful.connect(show_main_app)
        activation_win.show()

    sys.exit(app.exec())