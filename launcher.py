# launcher.py
import ctypes
import sys

try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except Exception:
        pass
import os

def resource_path(relative_path):
    """Get absolute path to resource (works for dev and .exe)"""
    try:
        base_path = sys._MEIPASS  # PyInstaller sets this in .exe mode
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

from functools import partial
from PySide6.QtWidgets import QApplication, QWidget, QLabel, QGridLayout, QHBoxLayout, QPushButton
from PySide6.QtGui import QMovie, QFont, QPixmap, QIcon
from PySide6.QtCore import Qt, QSize, Signal, QObject, QThread, QTimer, QTime, qInstallMessageHandler
def suppress_qt_warnings(*args):
    pass

qInstallMessageHandler(suppress_qt_warnings)
from utils import log_signals
from helpers import simplify_log_message        


# --- Import Your Bot Logic ---
import bot_main
import state
from state import state as state_instance # Import the instance for signals
import config
from utils import log_message

ASSETS_DIR = os.path.join(os.path.dirname(__file__), 'assets')


# --- Worker Thread for Bot Execution ---
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


# --- Main GUI ---
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
        self.background_label.lower()  # Send it to the back
        
    def initializeUI(self):
        # Increased height slightly for the new counter
        self.add_background_image()
        self.setFixedSize(210, 210)
        self.setWindowTitle("ckby - Water Collector 2.0")
        self.setWindowIcon(QIcon(os.path.join(ASSETS_DIR, "ckby_icon.ico")))
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)

        main_layout = QGridLayout(self)
        main_layout.setContentsMargins(5, 5, 5, 5)


        # Mascot Animation ------- # REDUCED TO SIZE 0 TO HIDE
        self.mascot_label = QLabel(self)
        self.mascot_label.setAlignment(Qt.AlignCenter)
        self.sleep_movie = QMovie(resource_path(os.path.join("assets", "mascot_sleep.gif")))
        self.active_movie = QMovie(resource_path(os.path.join("assets", "mascot_active.gif")))
        self.sleep_movie.setScaledSize(QSize(0, 0))
        self.active_movie.setScaledSize(QSize(0, 0))
        self.mascot_label.setMovie(self.sleep_movie)
        self.sleep_movie.start()
        main_layout.addWidget(self.mascot_label, 0, 0, 0, 2)

        # Timer Buttons
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

        # Start/Stop Buttons
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

        # Runtime & Status Labels
        self.runtime_label = QLabel("00:00:00")
        self.runtime_label.setFont(QFont("Arial", 10, QFont.Bold))
        self.runtime_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.runtime_label, 4, 0, 1, 2)

        # --- NEW: Water Counter Label ---
        self.water_counter_label = QLabel("💧 0 💧")
        self.water_counter_label.setFont(QFont("Arial", 10))
        self.water_counter_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.water_counter_label, 5, 0, 1, 2) # Added at row 5

        # --- Status Label (now at row 6) ---
        self.status_label = QLabel("Ready!")
        self.status_label.setFont(QFont("Arial", 10))
        self.status_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.status_label, 6, 0, 1, 2)

        main_layout.setRowStretch(7, 1)

        self.apply_styles()
        self.on_timer_button_clicked(self.selected_duration)
        self.show()

        # Connect signals
        log_signals.new_log.connect(self.update_status_from_log)
        # --- NEW: Connect to the water collected signal ---
        state_instance.water_collected.connect(self.update_water_display)

        # --- Footer: Made with ♥ by ckby ---
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
        self.apply_styles() # Re-apply styles to update button look

    def start_bot(self):
        # --- NEW: Reset the state counter when the bot starts ---
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
        self.update_runtime() # Final update to show total time

    def update_runtime(self):
        self.start_time = self.start_time.addSecs(1)
        self.runtime_label.setText(f"{self.start_time.toString('hh:mm:ss')}")

    def update_status_from_log(self, message):
        friendly_text = simplify_log_message(message)
        self.status_label.setText(friendly_text)

    # --- NEW: Function to update the water counter display ---
    def update_water_display(self, count):
        self.water_counter_label.setText(f"💧 {count} 💧")

    def get_selected_duration_seconds(self):
        mapping = {
            "30m": 30 * 60,
            "1h": 60 * 60,
            "2h": 2 * 60 * 60,
            "Max": None
        }
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


# --- Launch App ---
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ClickBerryApp()
    sys.exit(app.exec())
