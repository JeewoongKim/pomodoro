"""
Timer page for Pomodoro Timer application
"""

import sys
from pathlib import Path
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                            QLabel, QFrame)
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QFont, QIcon, QPixmap, QColor

from widgets.circular_progress import CircularProgress
from utils.constants import TIMER_STATE_WORK, TIMER_STATE_BREAK, TIMER_STATE_LONG_BREAK
from utils.icon_manager import icon_manager

class TimerPage(QWidget):
    """Main timer page with circular progress and controls"""
    
    # Signals
    show_settings = pyqtSignal()
    show_statistics = pyqtSignal()
    minimize_to_widget = pyqtSignal()
    start_pause_clicked = pyqtSignal()
    
    def __init__(self, config_manager, timer_logic):
        super().__init__()
        self.config_manager = config_manager
        self.timer_logic = timer_logic
        
        self.init_ui()
        self.connect_signals()
        self.update_display()
        
    def init_ui(self):
        """Initialize the user interface"""
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Header with navigation buttons
        header_layout = QHBoxLayout()
        header_layout.addStretch()
        
        # Get icon color based on theme
        theme = self.config_manager.get('theme', 'light')
        icon_color = QColor("#666666") if theme == 'light' else QColor("#cccccc")
        
        # Settings button with icon
        self.settings_btn = QPushButton()
        self.settings_btn.setFixedSize(50, 50)
        self.settings_btn.setIcon(icon_manager.get_icon('settings', QSize(24, 24), icon_color))
        self.settings_btn.setToolTip("Settings")
        self.settings_btn.clicked.connect(self.show_settings.emit)
        header_layout.addWidget(self.settings_btn)
        
        # Statistics button with icon
        self.stats_btn = QPushButton()
        self.stats_btn.setFixedSize(50, 50)
        self.stats_btn.setIcon(icon_manager.get_icon('statistics', QSize(24, 24), icon_color))
        self.stats_btn.setToolTip("Statistics")
        self.stats_btn.clicked.connect(self.show_statistics.emit)
        header_layout.addWidget(self.stats_btn)
        
        layout.addLayout(header_layout)
        
        # Progress circle
        progress_container = QFrame()
        progress_layout = QVBoxLayout()
        progress_layout.setContentsMargins(0, 0, 0, 0)
        
        self.progress_widget = CircularProgress()
        self.progress_widget.setMinimumSize(200, 200)
        progress_layout.addWidget(self.progress_widget, alignment=Qt.AlignmentFlag.AlignCenter)
        
        progress_container.setLayout(progress_layout)
        layout.addWidget(progress_container)
        
        # Status label
        self.status_label = QLabel("Ready to focus")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("""
            QLabel {
                font-size: 18px; 
                font-weight: bold;
                color: #333333;
                margin: 10px;
                padding: 10px;
                background-color: rgba(240, 240, 240, 0.5);
                border-radius: 8px;
            }
        """)
        layout.addWidget(self.status_label)
        
        # Control buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)
        
        # Control button icon color (usually darker for better visibility on buttons)
        button_icon_color = QColor("#333333") if theme == 'light' else QColor("#ffffff")
        
        self.start_pause_btn = QPushButton("Start")
        self.start_pause_btn.setMinimumSize(100, 50)
        self.start_pause_btn.clicked.connect(self.start_pause_clicked.emit)
        button_layout.addWidget(self.start_pause_btn)
        
        self.reset_btn = QPushButton()
        self.reset_btn.setIcon(icon_manager.get_icon('reset', QSize(20, 20), button_icon_color))
        self.reset_btn.setMinimumSize(100, 50)
        self.reset_btn.setToolTip("Reset Timer")
        self.reset_btn.clicked.connect(self.timer_logic.reset_timer)
        button_layout.addWidget(self.reset_btn)
        
        self.widget_btn = QPushButton()
        self.widget_btn.setIcon(icon_manager.get_icon('float', QSize(18, 18), button_icon_color))
        self.widget_btn.setMinimumSize(100, 50)
        self.widget_btn.setToolTip("Floating Widget")
        self.widget_btn.clicked.connect(self.minimize_to_widget.emit)
        button_layout.addWidget(self.widget_btn)
        
        layout.addLayout(button_layout)
        
        # Sessions counter
        self.sessions_label = QLabel("Sessions completed: 0")
        self.sessions_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.sessions_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                color: #666666;
                margin: 10px;
                padding: 8px;
                background-color: rgba(240, 240, 240, 0.3);
                border-radius: 5px;
            }
        """)
        layout.addWidget(self.sessions_label)
        
        layout.addStretch()
        self.setLayout(layout)
        
    def load_icon(self, filename: str, fallback: str) -> QIcon:
        """Load icon from resources with fallback - DEPRECATED, kept for compatibility"""
        # This method is now deprecated, but kept to avoid breaking existing code
        # The icon_manager should be used instead
        try:
            if hasattr(sys, '_MEIPASS'):
                # Running as compiled executable
                icon_path = Path(sys._MEIPASS) / "resources" / "icons" / filename
            else:
                # Running as script
                icon_path = Path(__file__).parent.parent.parent / "resources" / "icons" / filename
                
            if icon_path.exists() and icon_path.stat().st_size > 0:
                return QIcon(str(icon_path))
        except Exception as e:
            print(f"Error loading icon {filename}: {e}")
            
        # Create fallback text icon
        pixmap = QPixmap(32, 32)
        pixmap.fill(Qt.GlobalColor.transparent)
        return QIcon(pixmap)
        
    def connect_signals(self):
        """Connect timer logic signals"""
        self.timer_logic.timer_updated.connect(self.update_progress)
        self.timer_logic.state_changed.connect(self.update_state)
        self.timer_logic.session_completed.connect(self.update_sessions)
        
    def update_progress(self, remaining_seconds: int):
        """Update progress display"""
        self.progress_widget.setValue(remaining_seconds)
        
    def update_state(self, state: str):
        """Update UI based on timer state"""
        # Update progress colors and max values
        if state == TIMER_STATE_WORK:
            max_time = self.config_manager.get_work_time_seconds()
            color = self.config_manager.get("work_color", "#34a853")
            self.status_label.setText("Working... Stay focused!")
        elif state == TIMER_STATE_BREAK:
            max_time = self.config_manager.get_break_time_seconds()
            color = self.config_manager.get("break_color", "#4285f4")
            self.status_label.setText("Break time! Relax and recharge.")
        elif state == TIMER_STATE_LONG_BREAK:
            max_time = self.config_manager.get_long_break_time_seconds()
            color = self.config_manager.get("break_color", "#4285f4")
            self.status_label.setText("Long break! Take some time off.")
        else:
            # Stopped or paused
            max_time = self.config_manager.get_work_time_seconds()
            color = self.config_manager.get("work_color", "#34a853")
            if state == "paused":
                self.status_label.setText("Timer paused")
            else:
                self.status_label.setText("Ready to focus")
                
        self.progress_widget.setMaxValue(max_time)
        self.progress_widget.setColor(color)
        
        # Update start/pause button with icon
        self.update_start_pause_button(state)
            
    def update_start_pause_button(self, state: str = None):
        """Update start/pause button text and icon"""
        theme = self.config_manager.get('theme', 'light')
        icon_color = QColor("#333333") if theme == 'light' else QColor("#ffffff")
        
        if self.timer_logic.is_running():
            self.start_pause_btn.setIcon(icon_manager.get_icon('pause', QSize(20, 20), icon_color))
            self.start_pause_btn.setText(" Pause")
        else:
            self.start_pause_btn.setIcon(icon_manager.get_icon('play', QSize(20, 20), icon_color))
            if state == "paused":
                self.start_pause_btn.setText(" Resume")
            else:
                self.start_pause_btn.setText(" Start")
        
    def update_sessions(self):
        """Update sessions counter"""
        count = self.timer_logic.get_sessions_completed()
        self.sessions_label.setText(f"Sessions completed: {count}")
        
    def update_display(self):
        """Update all display elements"""
        remaining = self.timer_logic.get_remaining_time()
        state = self.timer_logic.get_current_state()
        
        self.update_progress(remaining)
        self.update_state(state)
        self.update_sessions()
        
    def update_button_icons(self):
        """Update all button icons - called when theme changes"""
        theme = self.config_manager.get('theme', 'light')
        header_icon_color = QColor("#666666") if theme == 'light' else QColor("#cccccc")
        button_icon_color = QColor("#333333") if theme == 'light' else QColor("#ffffff")
        
        # Update header buttons
        self.settings_btn.setIcon(icon_manager.get_icon('settings', QSize(24, 24), header_icon_color))
        self.stats_btn.setIcon(icon_manager.get_icon('statistics', QSize(24, 24), header_icon_color))
        
        # Update control buttons
        self.reset_btn.setIcon(icon_manager.get_icon('reset', QSize(20, 20), button_icon_color))
        self.widget_btn.setIcon(icon_manager.get_icon('float', QSize(18, 18), button_icon_color))
        
        # Update start/pause button
        self.update_start_pause_button()
        
    def update_font_size(self, font_size: int):
        """Update font sizes for responsive design"""
        # Update progress widget font
        self.progress_widget.setFontSize(max(16, int(font_size * 1.5)))
        
        # Update button fonts
        button_font = QFont()
        button_font.setPointSize(max(12, font_size))
        
        self.start_pause_btn.setFont(button_font)
        self.reset_btn.setFont(button_font)
        self.widget_btn.setFont(button_font)
        
        # Update label fonts
        status_font = QFont()
        status_font.setPointSize(max(14, int(font_size * 1.2)))
        status_font.setBold(True)
        self.status_label.setFont(status_font)
        
        sessions_font = QFont()
        sessions_font.setPointSize(max(10, int(font_size * 0.9)))
        self.sessions_label.setFont(sessions_font)
        
    def update_floating_widget(self, floating_widget):
        """Update floating widget with current timer state"""
        remaining = self.timer_logic.get_remaining_time()
        state = self.timer_logic.get_current_state()
        
        # Set progress values
        floating_widget.setValue(remaining)
        
        if state == TIMER_STATE_WORK:
            floating_widget.setMaxValue(self.config_manager.get_work_time_seconds())
            floating_widget.setColor(self.config_manager.get("work_color", "#34a853"))
        elif state in [TIMER_STATE_BREAK, TIMER_STATE_LONG_BREAK]:
            if state == TIMER_STATE_LONG_BREAK:
                floating_widget.setMaxValue(self.config_manager.get_long_break_time_seconds())
            else:
                floating_widget.setMaxValue(self.config_manager.get_break_time_seconds())
            floating_widget.setColor(self.config_manager.get("break_color", "#4285f4"))
        else:
            floating_widget.setMaxValue(self.config_manager.get_work_time_seconds())
            floating_widget.setColor(self.config_manager.get("work_color", "#34a853"))
            
        # Set button text
        if self.timer_logic.is_running():
            floating_widget.setStartPauseText("Pause")
        else:
            floating_widget.setStartPauseText("Start" if state != "paused" else "Resume")
            
    def resizeEvent(self, event):
        """Handle resize event"""
        super().resizeEvent(event)
        
        # Update progress widget size
        if hasattr(self, 'progress_widget'):
            # Scale progress widget based on available space
            available_height = self.height() - 200  # Account for other elements
            available_width = self.width() - 40     # Account for margins
            
            size = min(available_width, available_height, 300)  # Max size 300px
            size = max(size, 150)  # Minimum size 150px
            
            self.progress_widget.setMinimumSize(size, size)
            self.progress_widget.setMaximumSize(size, size)