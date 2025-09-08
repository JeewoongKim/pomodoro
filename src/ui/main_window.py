"""
Main window for Pomodoro Timer application
"""

import sys
from pathlib import Path
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QStackedWidget, 
                            QApplication, QMessageBox)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QCloseEvent, QResizeEvent

from config.config_manager import ConfigManager
from core.timer_logic import TimerLogic
from core.data_manager import DataManager
from utils.system_tray import SystemTrayManager
from utils.constants import (MIN_WINDOW_WIDTH, MIN_WINDOW_HEIGHT, 
                           DEFAULT_WINDOW_WIDTH, DEFAULT_WINDOW_HEIGHT)
from utils.icon_manager import icon_manager

from .timer_page import TimerPage
from .settings_page import SettingsPage
from .statistics_page import StatisticsPage
from .floating_widget import FloatingWidget

class PomodoroMainWindow(QMainWindow):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        
        # Initialize managers
        self.config_manager = ConfigManager()
        self.timer_logic = TimerLogic(self.config_manager)
        self.data_manager = DataManager(self.config_manager)
        self.system_tray = SystemTrayManager()
        
        # UI components
        self.floating_widget = None
        self.auto_widget_timer = QTimer()
        self.auto_widget_timer.setSingleShot(True)
        self.auto_widget_timer.timeout.connect(self.show_floating_widget)
        
        self.init_ui()
        self.connect_signals()
        self.load_settings()
        
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("Pomodoro Timer")
        self.setMinimumSize(MIN_WINDOW_WIDTH, MIN_WINDOW_HEIGHT)
        self.resize(DEFAULT_WINDOW_WIDTH, DEFAULT_WINDOW_HEIGHT)
        
        # Set application icon
        app_icon = icon_manager.get_icon('timer', size=(32, 32))
        self.setWindowIcon(app_icon)
        
        # Load and apply stylesheet
        self.load_stylesheet()
        
        # Central widget with stacked layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Stacked widget for different pages
        self.stacked_widget = QStackedWidget()
        layout.addWidget(self.stacked_widget)
        
        central_widget.setLayout(layout)
        
        # Create pages
        self.timer_page = TimerPage(self.config_manager, self.timer_logic)
        self.settings_page = SettingsPage(self.config_manager)
        self.statistics_page = StatisticsPage(self.config_manager, self.data_manager)
        
        # Add pages to stack
        self.stacked_widget.addWidget(self.timer_page)     # Index 0
        self.stacked_widget.addWidget(self.settings_page)  # Index 1
        self.stacked_widget.addWidget(self.statistics_page)  # Index 2
        
        # Set initial page
        self.stacked_widget.setCurrentIndex(0)
        
    def load_stylesheet(self):
        """Load application stylesheet"""
        try:
            if hasattr(sys, '_MEIPASS'):
                # Running as compiled executable
                style_path = Path(sys._MEIPASS) / "resources" / "styles" / "main.qss"
            else:
                # Running as script
                style_path = Path(__file__).parent.parent.parent / "resources" / "styles" / "main.qss"
                
            if style_path.exists():
                with open(style_path, 'r', encoding='utf-8') as f:
                    self.setStyleSheet(f.read())
            else:
                # Fallback stylesheet
                self.setStyleSheet(self.get_fallback_stylesheet())
                
        except Exception as e:
            print(f"Error loading stylesheet: {e}")
            self.setStyleSheet(self.get_fallback_stylesheet())
            
    def get_fallback_stylesheet(self) -> str:
        """Get fallback stylesheet if file loading fails"""
        return """
        QMainWindow {
            background-color: white;
            border-radius: 15px;
        }
        QPushButton {
            background-color: #4CAF50;
            border: none;
            color: white;
            padding: 10px 20px;
            text-align: center;
            font-size: 14px;
            border-radius: 8px;
            font-weight: bold;
        }
        QPushButton:hover {
            background-color: #45a049;
        }
        QPushButton:pressed {
            background-color: #3d8b40;
        }
        """
        
    def connect_signals(self):
        """Connect all signals and slots"""
        # Timer page signals
        self.timer_page.show_settings.connect(lambda: self.stacked_widget.setCurrentIndex(1))
        self.timer_page.show_statistics.connect(lambda: self.stacked_widget.setCurrentIndex(2))
        self.timer_page.minimize_to_widget.connect(self.show_floating_widget)
        self.timer_page.start_pause_clicked.connect(self.on_start_pause_with_auto_minimize)
        
        # Settings page signals
        self.settings_page.back_clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))
        self.settings_page.settings_saved.connect(self.on_settings_saved)
        
        # Statistics page signals
        self.statistics_page.back_clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))
        
        # Timer logic signals
        self.timer_logic.session_completed.connect(self.on_session_completed)
        self.timer_logic.timer_finished.connect(self.on_timer_finished)
        self.timer_logic.state_changed.connect(self.update_ui_state)
        
        # System tray signals
        self.system_tray.show_main_window.connect(self.show_main_window)
        self.system_tray.show_floating_widget.connect(self.show_floating_widget)
        self.system_tray.start_pause_timer.connect(self.timer_logic.start_timer)
        self.system_tray.quit_application.connect(self.quit_application)
        
        # Data manager signals
        self.data_manager.data_updated.connect(self.statistics_page.refresh_data)
        
    def load_settings(self):
        """Load and apply saved settings"""
        # Apply font size
        font_size = self.config_manager.get("font_size", 14)
        self.apply_font_size(font_size)
        
        # Update system tray with icon
        try:
            tray_icon = icon_manager.get_icon('timer', size=(16, 16))
            self.system_tray.set_icon(tray_icon)
        except:
            pass  # Fallback to system default
        
        # Update system tray
        self.system_tray.show_tray_icon()
        
    def apply_font_size(self, font_size: int):
        """Apply font size to the application"""
        font = self.font()
        font.setPointSize(font_size)
        self.setFont(font)
        
        # Apply to all pages
        self.timer_page.setFont(font)
        self.settings_page.setFont(font)
        self.statistics_page.setFont(font)
        
        # Update progress widget font sizes
        self.timer_page.update_font_size(font_size)
        
    def update_all_icons(self):
        """Update all icons in the application - called when theme changes"""
        # Update window icon
        app_icon = icon_manager.get_icon('timer', size=(32, 32))
        self.setWindowIcon(app_icon)
        
        # Update system tray icon
        try:
            tray_icon = icon_manager.get_icon('timer', size=(16, 16))
            self.system_tray.set_icon(tray_icon)
        except:
            pass
        
        # Update timer page icons
        if hasattr(self.timer_page, 'update_button_icons'):
            self.timer_page.update_button_icons()
        
        # Update floating widget icons if exists
        if self.floating_widget and hasattr(self.floating_widget, 'update_button_icons'):
            self.floating_widget.update_button_icons()
        
    def on_start_pause_with_auto_minimize(self):
        """Handle start/pause with auto minimize to widget"""
        if not self.timer_logic.is_running():
            # Starting timer - auto minimize after 2 seconds
            self.timer_logic.start_timer()
            self.auto_widget_timer.start(2000)  # 2 second delay
        else:
            # Pausing timer
            self.timer_logic.pause_timer()
            
    def on_session_completed(self):
        """Handle session completion"""
        session_type = "work" if self.timer_logic.get_current_state() == "work" else "break"
        duration = self.config_manager.get("work_time" if session_type == "work" else "break_time")
        self.data_manager.save_session(session_type, duration)
        
    def on_timer_finished(self, timer_type: str):
        """Handle timer completion with notifications"""
        if timer_type == "work":
            self.system_tray.show_message(
                "Pomodoro Timer", 
                "Work session completed! Time for a break.",
                timeout=5000
            )
        else:
            self.system_tray.show_message(
                "Pomodoro Timer",
                "Break finished! Ready for another session?",
                timeout=5000
            )
            
    def update_ui_state(self, state: str):
        """Update UI based on timer state"""
        self.system_tray.update_timer_action(self.timer_logic.is_running())
        
        # Update tooltip
        remaining = self.timer_logic.get_remaining_time()
        minutes = remaining // 60
        seconds = remaining % 60
        status = state.replace("_", " ").title()
        tooltip = f"Pomodoro Timer - {status} ({minutes:02d}:{seconds:02d})"
        self.system_tray.update_tooltip(tooltip)
        
    def on_settings_saved(self):
        """Handle settings save"""
        # Clear icon cache to apply theme changes
        icon_manager._icons.clear()
        
        # Update all icons
        self.update_all_icons()
        
        # Reload settings
        self.load_settings()
        
        # Reset timer with new settings
        self.timer_logic.reset_timer()
        
        # Return to timer page
        self.stacked_widget.setCurrentIndex(0)
        
    def show_floating_widget(self):
        """Show floating widget and hide main window"""
        if not self.floating_widget:
            self.floating_widget = FloatingWidget()
            
            # Connect floating widget signals
            self.floating_widget.show_main_window.connect(self.show_main_window)
            self.floating_widget.start_pause_clicked.connect(self.timer_logic.start_timer)
            self.floating_widget.reset_clicked.connect(self.timer_logic.reset_timer)
            
        # Update floating widget with current timer state
        self.timer_page.update_floating_widget(self.floating_widget)
        
        # Show floating widget and hide main window
        self.floating_widget.show()
        self.hide()
        self.system_tray.show_tray_icon()
        
    def show_main_window(self):
        """Show main window and hide floating widget"""
        self.show()
        self.raise_()
        self.activateWindow()
        
        if self.floating_widget:
            self.floating_widget.hide()
            
    def quit_application(self):
        """Quit the application"""
        # Save current window geometry
        self.config_manager.set("window_geometry", {
            "x": self.x(),
            "y": self.y(),
            "width": self.width(),
            "height": self.height()
        })
        self.config_manager.save_config()
        
        QApplication.quit()
        
    def resizeEvent(self, event: QResizeEvent):
        """Handle window resize"""
        super().resizeEvent(event)
        
        # Update font sizes based on window size if responsive mode is enabled
        if self.config_manager.get("responsive_ui", True):
            self.update_responsive_sizing()
            
    def update_responsive_sizing(self):
        """Update UI element sizes based on window size"""
        width = self.width()
        height = self.height()
        
        # Calculate scale factor (1.0 at default size)
        width_scale = width / DEFAULT_WINDOW_WIDTH
        height_scale = height / DEFAULT_WINDOW_HEIGHT
        scale = min(width_scale, height_scale)
        
        # Apply scaled font size
        base_font_size = self.config_manager.get("font_size", 14)
        scaled_font_size = max(10, int(base_font_size * scale))
        
        font = self.font()
        font.setPointSize(scaled_font_size)
        
        # Apply to current page
        current_page = self.stacked_widget.currentWidget()
        if current_page:
            current_page.setFont(font)
            
        # Update progress widget if on timer page
        if isinstance(current_page, TimerPage):
            current_page.update_font_size(scaled_font_size)
            
    def changeEvent(self, event):
        """Handle window state changes"""
        if event.type() == event.Type.WindowStateChange:
            if self.isMinimized():
                # Auto-minimize to widget on minimize
                self.show_floating_widget()
        super().changeEvent(event)
        
    def closeEvent(self, event: QCloseEvent):
        """Handle close event"""
        if self.system_tray.is_available():
            event.ignore()
            self.show_floating_widget()
            self.system_tray.show_message(
                "Pomodoro Timer", 
                "Application minimized to system tray",
                timeout=2000
            )
        else:
            # No system tray available, ask user
            reply = QMessageBox.question(
                self, 
                "Pomodoro Timer",
                "Close application?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                self.quit_application()
            else:
                event.ignore()