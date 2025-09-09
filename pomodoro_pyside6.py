#!/usr/bin/env python3
"""
Cross-platform Pomodoro Timer Application (PySide6 버전)
Supports Windows and macOS with GUI
"""

import sys
import os
import json
import csv
from datetime import datetime, timedelta
from pathlib import Path
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QPushButton, QLabel, QSpinBox,
                            QSystemTrayIcon, QMenu, QFileDialog, QColorDialog,
                            QStackedWidget, QGridLayout, QGroupBox, QSlider,
                            QCheckBox, QTableWidget, QTableWidgetItem,
                            QHeaderView, QMessageBox, QSizePolicy)
from PySide6.QtCore import (Qt, QTimer, QPoint, QPropertyAnimation, QRect,
                          QEasingCurve, Signal, QDateTime, QSize)
from PySide6.QtGui import (QPainter, QColor, QPen, QBrush, QIcon, QPixmap,
                         QPainterPath, QFont, QAction, QFontMetrics)
import pyqtgraph as pg
from typing import Optional, Dict, List, Tuple

class CircularProgress(QWidget):
    """Custom widget for circular progress visualization"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.value = 0
        self.max_value = 100
        self.thickness = 10
        self.color = QColor(52, 168, 83)  # Green
        self.bg_color = QColor(240, 240, 240)
        self.text_color = QColor(50, 50, 50)
        self.setMinimumSize(200, 200)
        self.font_size = 24
        
    def setValue(self, value):
        self.value = value
        self.update()
        
    def setMaxValue(self, max_value):
        self.max_value = max_value
        self.update()
        
    def setColor(self, color):
        self.color = color
        self.update()
        
    def setFontSize(self, font_size):
        self.font_size = font_size
        self.update()
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Get dimensions
        width = self.width()
        height = self.height()
        diameter = min(width, height) - self.thickness * 2
        
        # Center position
        rect = QRect((width - diameter) // 2, (height - diameter) // 2, 
                     diameter, diameter)
        
        # Draw background circle
        painter.setPen(QPen(self.bg_color, self.thickness))
        painter.drawArc(rect, 0, 360 * 16)
        
        # Draw progress arc
        painter.setPen(QPen(self.color, self.thickness))
        angle = int(360 * (self.value / self.max_value * 16)) if self.max_value > 0 else 0
        painter.drawArc(rect, 90 * 16, -angle)
        
        # Draw time text
        painter.setPen(self.text_color)
        font = QFont("Arial", self.font_size, QFont.Weight.Bold)
        painter.setFont(font)
        
        minutes = int(self.value // 60)
        seconds = int(self.value % 60)
        time_text = f"{minutes:02d}:{seconds:02d}"
        
        painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, time_text)

class FloatingWidget(QWidget):
    """Floating widget for always-on-top timer display"""
    
    clicked = Signal()
    toggle_timer = Signal()  # New signal for toggle timer
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | 
                           Qt.WindowType.WindowStaysOnTopHint |
                           Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setWindowOpacity(0.9)
        
        self.dragging = False
        self.drag_position = QPoint()
        self.resizing = False
        self.resize_start_pos = QPoint()
        self.resize_start_size = QSize()
        self.is_running = False  # Track running state
        self.hover_opacity = 0.9
        self.normal_opacity = 0.7
        
        self.progress = CircularProgress(self)
        layout = QVBoxLayout()
        layout.addWidget(self.progress)
        layout.setContentsMargins(10, 10, 10, 10)
        self.setLayout(layout)
        
        self.resize(150, 150)
        
        # Enable mouse tracking for hover effects
        self.setMouseTracking(True)
        
    def setRunningState(self, is_running):
        """Update the running state of the widget"""
        self.is_running = is_running
        self.update()
        
    def enterEvent(self, event):
        """Mouse enters widget area - show hover effect"""
        self.setWindowOpacity(self.hover_opacity)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        super().enterEvent(event)
        
    def leaveEvent(self, event):
        """Mouse leaves widget area - remove hover effect"""
        self.setWindowOpacity(self.normal_opacity)
        self.setCursor(Qt.CursorShape.ArrowCursor)
        super().leaveEvent(event)
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Draw rounded rectangle background
        path = QPainterPath()
        path.addRoundedRect(0, 0, self.width(), self.height(), 15, 15)
        painter.fillPath(path, QColor(255, 255, 255, 220))
        
        # Draw play/pause indicator in top-left corner
        indicator_size = 20
        indicator_rect = QRect(5, 5, indicator_size, indicator_size)
        
        if self.is_running:
            # Draw pause icon (two bars)
            painter.fillRect(9, 9, 4, 12, QColor(100, 100, 100, 150))
            painter.fillRect(15, 9, 4, 12, QColor(100, 100, 100, 150))
        else:
            # Draw play icon (triangle)
            painter.setBrush(QColor(100, 100, 100, 150))
            triangle = QPainterPath()
            triangle.moveTo(10, 9)
            triangle.lineTo(10, 21)
            triangle.lineTo(20, 15)
            triangle.closeSubpath()
            painter.drawPath(triangle)
        
        # Draw resize corner indicator
        corner_size = 12
        corner_rect = QRect(self.width() - corner_size, self.height() - corner_size, 
                          corner_size, corner_size)
        painter.fillRect(corner_rect, QColor(150, 150, 150, 100))
        
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.click_pos = event.position().toPoint()
            self.has_moved = False  # Track if mouse has actually moved
            # Check if near edge for resizing
            edge_threshold = 15
            if (self.width() - event.position().x() < edge_threshold and 
                self.height() - event.position().y() < edge_threshold):
                self.resizing = True
                self.resize_start_pos = event.globalPosition().toPoint()
                self.resize_start_size = self.size()
                self.dragging = False
            else:
                self.dragging = True
                self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
                self.resizing = False
                
    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton:
            if self.resizing:
                self.has_moved = True
                delta = event.globalPosition().toPoint() - self.resize_start_pos
                new_width = max(100, self.resize_start_size.width() + delta.x())
                new_height = max(100, self.resize_start_size.height() + delta.y())
                self.resize(new_width, new_height)
            elif self.dragging:
                # Check if mouse moved significantly (more than 3 pixels)
                if hasattr(self, 'click_pos'):
                    move_distance = (event.position().toPoint() - self.click_pos).manhattanLength()
                    if move_distance > 3:
                        self.has_moved = True
                        self.move(event.globalPosition().toPoint() - self.drag_position)
            
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            # Only trigger toggle if:
            # 1. Mouse hasn't moved significantly during drag
            # 2. Not clicking near resize corner
            # 3. Was not in resize mode
            should_toggle = (
                not getattr(self, 'has_moved', True) and  # No significant movement
                not self.resizing  # Not resizing
            )
            
            # Check resize corner
            if should_toggle:
                edge_threshold = 15
                near_corner = (self.width() - event.position().x() < edge_threshold and 
                              self.height() - event.position().y() < edge_threshold)
                should_toggle = not near_corner
            
            # Reset flags
            self.dragging = False
            self.resizing = False
            self.has_moved = False
            
            # Emit toggle signal only if it's a clean click
            if should_toggle:
                self.toggle_timer.emit()
        
    def mouseDoubleClickEvent(self, event):
        """Double click to return to main window"""
        self.clicked.emit()
        
    def setValue(self, value):
        self.progress.setValue(value)
        
    def setMaxValue(self, max_value):
        self.progress.setMaxValue(max_value)
        
    def setColor(self, color):
        self.progress.setColor(color)
        
    def setFontSize(self, font_size):
        self.progress.setFontSize(font_size)

class PomodoroTimer(QMainWindow):
    """Main Pomodoro Timer Application"""
    
    def __init__(self):
        super().__init__()
        self.config_file = Path.home() / ".pomodoro" / "config.json"
        self.data_dir = Path.home() / "PomodoroData"
        self.load_config()
        
        self.work_time = self.config.get("work_time", 25) * 60  # in seconds
        self.break_time = self.config.get("break_time", 5) * 60
        self.current_time = self.work_time
        self.is_working = True
        self.is_running = False
        self.sessions_completed = 0
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_timer)
        
        self.floating_widget = None
        self.init_ui()
        self.load_weekly_data()
        
    def load_config(self):
        """Load configuration from file"""
        self.config = {
            "work_time": 25,
            "break_time": 5,
            "font_size": 12,
            "work_color": "#34a853",
            "break_color": "#4285f4",
            "bg_color": "#f0f0f0",
            "data_dir": str(Path.home() / "PomodoroData"),
            "widget_style": "circular",
            "auto_start_break": True
        }
        
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    saved_config = json.load(f)
                    self.config.update(saved_config)
            except Exception as e:
                print(f"Error loading config: {e}")
                
        self.data_dir = Path(self.config["data_dir"])
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
    def save_config(self):
        """Save configuration to file"""
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
            
    def create_icon_button(self, text, icon_text):
        """Create a button with icon and text"""
        btn = QPushButton(f"{icon_text} {text}")
        return btn
            
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("Pomodoro Timer (PySide6)")
        self.setMinimumSize(400, 500)
        self.resize(500, 600)
        
        # Apply dynamic font size to main window
        base_font_size = self.config.get("font_size", 12)
        
        # Set rounded corners and responsive styling
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: white;
                border-radius: 15px;
                font-size: {base_font_size}px;
            }}
            QPushButton {{
                background-color: #4CAF50;
                border: none;
                color: white;
                padding: {max(8, base_font_size//2)}px {max(16, base_font_size)}px;
                text-align: center;
                font-size: {base_font_size + 2}px;
                border-radius: 8px;
                min-height: {max(30, base_font_size * 2)}px;
            }}
            QPushButton:hover {{
                background-color: #45a049;
            }}
            QPushButton:pressed {{
                background-color: #3d8b40;
            }}
            QLabel {{
                font-size: {base_font_size + 2}px;
            }}
            QGroupBox {{
                font-size: {base_font_size}px;
                font-weight: bold;
                margin-top: 10px;
                padding-top: 10px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }}
        """)
        
        # Central widget with stacked layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        central_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        self.stacked_widget = QStackedWidget()
        self.stacked_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.stacked_widget)
        central_widget.setLayout(main_layout)
        
        # Create pages
        self.create_timer_page()
        self.create_settings_page()
        self.create_statistics_page()
        
        # System tray
        self.create_system_tray()
        
    def resizeEvent(self, event):
        """Handle window resize events"""
        super().resizeEvent(event)
        if hasattr(self, 'progress_widget'):
            # Update font size based on window size
            base_size = max(16, min(32, self.width() // 20))
            self.progress_widget.setFontSize(base_size)
        
    def create_timer_page(self):
        """Create the main timer page"""
        timer_page = QWidget()
        timer_page.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Header with settings button
        header_layout = QHBoxLayout()
        header_layout.addStretch()
        
        settings_btn = self.create_icon_button("Settings", "⚙️")
        settings_btn.setFixedSize(120, 40)
        settings_btn.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(1))
        header_layout.addWidget(settings_btn)
        
        stats_btn = self.create_icon_button("Stats", "📊")
        stats_btn.setFixedSize(100, 40)
        stats_btn.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(2))
        header_layout.addWidget(stats_btn)
        
        layout.addLayout(header_layout)
        
        # Circular progress - make it responsive
        self.progress_widget = CircularProgress()
        self.progress_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.progress_widget.setMaxValue(self.work_time)
        self.progress_widget.setValue(self.work_time)
        self.progress_widget.setFontSize(self.config.get("font_size", 12) + 8)
        layout.addWidget(self.progress_widget, alignment=Qt.AlignmentFlag.AlignCenter, stretch=2)
        
        # Status label
        self.status_label = QLabel("Ready to focus")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        status_font_size = self.config.get("font_size", 12) + 6
        self.status_label.setStyleSheet(f"font-size: {status_font_size}px; margin: 10px; font-weight: bold;")
        layout.addWidget(self.status_label)
        
        # Control buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        self.start_btn = QPushButton("▶️ Start")
        self.start_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.start_btn.clicked.connect(self.toggle_timer)
        button_layout.addWidget(self.start_btn)
        
        self.reset_btn = QPushButton("Reset")
        self.reset_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.reset_btn.clicked.connect(self.reset_timer)
        button_layout.addWidget(self.reset_btn)
        
        layout.addLayout(button_layout)
        
        # Widget mode button
        self.minimize_btn = QPushButton("🔽 Widget Mode")
        self.minimize_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.minimize_btn.clicked.connect(self.show_floating_widget)
        layout.addWidget(self.minimize_btn)
        
        # Sessions counter
        self.sessions_label = QLabel(f"Sessions completed: {self.sessions_completed}")
        self.sessions_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.sessions_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        layout.addWidget(self.sessions_label)
        
        timer_page.setLayout(layout)
        self.stacked_widget.addWidget(timer_page)
        
    def create_settings_page(self):
        """Create the settings page"""
        settings_page = QWidget()
        settings_page.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Back button
        back_btn = self.create_icon_button("Back", "←")
        back_btn.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))
        layout.addWidget(back_btn)
        
        # Timer settings
        timer_group = QGroupBox("Timer Settings")
        timer_group.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        timer_layout = QGridLayout()
        
        timer_layout.addWidget(QLabel("Work Time (minutes):"), 0, 0)
        self.work_spin = QSpinBox()
        self.work_spin.setRange(1, 60)
        self.work_spin.setValue(self.config["work_time"])
        self.work_spin.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        timer_layout.addWidget(self.work_spin, 0, 1)
        
        timer_layout.addWidget(QLabel("Break Time (minutes):"), 1, 0)
        self.break_spin = QSpinBox()
        self.break_spin.setRange(1, 30)
        self.break_spin.setValue(self.config["break_time"])
        self.break_spin.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        timer_layout.addWidget(self.break_spin, 1, 1)
        
        # Auto start break option
        self.auto_start_checkbox = QCheckBox("Auto start break after work session")
        self.auto_start_checkbox.setChecked(self.config.get("auto_start_break", True))
        timer_layout.addWidget(self.auto_start_checkbox, 2, 0, 1, 2)
        
        timer_group.setLayout(timer_layout)
        layout.addWidget(timer_group)
        
        # Appearance settings
        appearance_group = QGroupBox("Appearance")
        appearance_group.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        appearance_layout = QGridLayout()
        
        appearance_layout.addWidget(QLabel("Font Size:"), 0, 0)
        self.font_slider = QSlider(Qt.Orientation.Horizontal)
        self.font_slider.setRange(10, 24)
        self.font_slider.setValue(self.config["font_size"])
        self.font_slider.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        
        self.font_value_label = QLabel(str(self.config["font_size"]))
        self.font_slider.valueChanged.connect(lambda v: self.font_value_label.setText(str(v)))
        
        font_layout = QHBoxLayout()
        font_layout.addWidget(self.font_slider)
        font_layout.addWidget(self.font_value_label)
        appearance_layout.addLayout(font_layout, 0, 1)
        
        appearance_layout.addWidget(QLabel("Work Color:"), 1, 0)
        self.work_color_btn = QPushButton("Choose Color")
        self.work_color_btn.setStyleSheet(f"background-color: {self.config['work_color']}; color: white;")
        self.work_color_btn.clicked.connect(lambda: self.choose_color("work"))
        self.work_color_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        appearance_layout.addWidget(self.work_color_btn, 1, 1)
        
        appearance_layout.addWidget(QLabel("Break Color:"), 2, 0)
        self.break_color_btn = QPushButton("Choose Color")
        self.break_color_btn.setStyleSheet(f"background-color: {self.config['break_color']}; color: white;")
        self.break_color_btn.clicked.connect(lambda: self.choose_color("break"))
        self.break_color_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        appearance_layout.addWidget(self.break_color_btn, 2, 1)
        
        appearance_group.setLayout(appearance_layout)
        layout.addWidget(appearance_group)
        
        # Data settings
        data_group = QGroupBox("Data Settings")
        data_group.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        data_layout = QVBoxLayout()
        
        dir_layout = QHBoxLayout()
        self.dir_label = QLabel(str(self.data_dir))
        self.dir_label.setWordWrap(True)
        self.dir_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        dir_layout.addWidget(self.dir_label)
        
        browse_btn = QPushButton("📁 Browse")
        browse_btn.clicked.connect(self.choose_data_directory)
        browse_btn.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Preferred)
        dir_layout.addWidget(browse_btn)
        
        data_layout.addLayout(dir_layout)
        data_group.setLayout(data_layout)
        layout.addWidget(data_group)
        
        # Save button
        save_btn = QPushButton("💾 Save Settings")
        save_btn.clicked.connect(self.save_settings)
        save_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        layout.addWidget(save_btn)
        
        layout.addStretch()
        settings_page.setLayout(layout)
        self.stacked_widget.addWidget(settings_page)
        
    def create_statistics_page(self):
        """Create the statistics page"""
        stats_page = QWidget()
        stats_page.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Back button
        back_btn = self.create_icon_button("Back", "←")
        back_btn.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))
        layout.addWidget(back_btn)
        
        # Weekly chart
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.plot_widget.setBackground('w')
        self.plot_widget.setTitle("Weekly Focus Time", color='b', size='16pt')
        self.plot_widget.setLabel('left', 'Minutes', color='b', size='12pt')
        self.plot_widget.setLabel('bottom', 'Day', color='b', size='12pt')
        
        # Set Y-axis range from 0 to 60 with 5-minute intervals
        self.plot_widget.setYRange(0, 65)
        y_ticks = [(i, str(i)) for i in range(0, 65, 5)]
        self.plot_widget.getAxis('left').setTicks([y_ticks])
        
        layout.addWidget(self.plot_widget, stretch=1)
        
        # Export buttons
        export_layout = QHBoxLayout()
        export_layout.setSpacing(10)
        
        export_csv_btn = QPushButton("📄 Export to CSV")
        export_csv_btn.clicked.connect(self.export_to_csv)
        export_csv_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        export_layout.addWidget(export_csv_btn)
        
        export_chart_btn = QPushButton("📸 Save Chart")
        export_chart_btn.clicked.connect(self.save_chart)
        export_chart_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        export_layout.addWidget(export_chart_btn)
        
        layout.addLayout(export_layout)
        
        stats_page.setLayout(layout)
        self.stacked_widget.addWidget(stats_page)
        
    def create_system_tray(self):
        """Create system tray icon"""
        self.tray_icon = QSystemTrayIcon(self)
        
        # Create a simple icon
        pixmap = QPixmap(16, 16)
        pixmap.fill(QColor(self.config["work_color"]))
        self.tray_icon.setIcon(QIcon(pixmap))
        
        # Tray menu
        tray_menu = QMenu()
        
        show_action = QAction("Show", self)
        show_action.triggered.connect(self.show_main_window)
        tray_menu.addAction(show_action)
        
        start_action = QAction("Start/Pause", self)
        start_action.triggered.connect(self.toggle_timer)
        tray_menu.addAction(start_action)
        
        reset_action = QAction("Reset", self)
        reset_action.triggered.connect(self.reset_timer)
        tray_menu.addAction(reset_action)
        
        tray_menu.addSeparator()
        
        quit_action = QAction("Quit", self)
        quit_action.triggered.connect(QApplication.quit)
        tray_menu.addAction(quit_action)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.activated.connect(self.tray_icon_activated)
        
    def tray_icon_activated(self, reason):
        """Handle tray icon activation"""
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.show_main_window()
            
    def show_main_window(self):
        """Show main window and hide floating widget"""
        if self.floating_widget:
            self.floating_widget.hide()
        self.show()
        self.raise_()
        self.activateWindow()
        
    def toggle_timer(self):
        """Start or pause the timer"""
        if self.is_running:
            self.timer.stop()
            self.start_btn.setText("▶️ Start")
            self.status_label.setText("Paused")
        else:
            self.timer.start(1000)  # Update every second
            self.start_btn.setText("⏸️ Pause")
            self.status_label.setText("Working..." if self.is_working else "Break time!")
            
            # Auto switch to widget mode when starting
            if not self.floating_widget or not self.floating_widget.isVisible():
                self.show_floating_widget()
            
        self.is_running = not self.is_running
        
        # Update floating widget state if it exists
        if self.floating_widget:
            self.floating_widget.setRunningState(self.is_running)
        
    def update_timer(self):
        """Update timer countdown"""
        if self.current_time > 0:
            self.current_time -= 1
            self.progress_widget.setValue(self.current_time)
            
            if self.floating_widget:
                self.floating_widget.setValue(self.current_time)
                
        else:
            self.timer_finished()
            
    def timer_finished(self):
        """Handle timer completion"""
        self.timer.stop()
        self.is_running = False
        
        # Update floating widget state
        if self.floating_widget:
            self.floating_widget.setRunningState(self.is_running)
        
        if self.is_working:
            self.sessions_completed += 1
            self.sessions_label.setText(f"Sessions completed: {self.sessions_completed}")
            self.save_session_data()
            
            # Switch to break
            self.is_working = False
            self.current_time = self.break_time
            self.progress_widget.setMaxValue(self.break_time)
            self.progress_widget.setColor(QColor(self.config["break_color"]))
            
            if self.floating_widget:
                self.floating_widget.setMaxValue(self.break_time)
                self.floating_widget.setColor(QColor(self.config["break_color"]))
                
            self.status_label.setText("Break time!")
            
            # Show notification
            self.tray_icon.showMessage("Pomodoro Timer", "Work session completed! Time for a break.", 
                                       QSystemTrayIcon.MessageIcon.Information, 3000)
            
            # Auto-start break if enabled
            if self.config.get("auto_start_break", True):
                self.is_running = True
                self.timer.start(1000)
                self.start_btn.setText("⏸️ Pause")
                self.status_label.setText("Break time!")
                if self.floating_widget:
                    self.floating_widget.setRunningState(self.is_running)
            else:
                self.start_btn.setText("▶️ Start")
                
        else:
            # Switch back to work
            self.is_working = True
            self.current_time = self.work_time
            self.progress_widget.setMaxValue(self.work_time)
            self.progress_widget.setColor(QColor(self.config["work_color"]))
            
            if self.floating_widget:
                self.floating_widget.setMaxValue(self.work_time)
                self.floating_widget.setColor(QColor(self.config["work_color"]))
                
            self.status_label.setText("Ready to focus")
            self.start_btn.setText("▶️ Start")
            
            # Show notification
            self.tray_icon.showMessage("Pomodoro Timer", "Break finished! Ready for another session?", 
                                       QSystemTrayIcon.MessageIcon.Information, 3000)
            
        self.progress_widget.setValue(self.current_time)
        if self.floating_widget:
            self.floating_widget.setValue(self.current_time)
        
    def reset_timer(self):
        """Reset the timer to initial state"""
        self.timer.stop()
        self.is_running = False
        self.is_working = True
        self.current_time = self.work_time
        
        self.progress_widget.setMaxValue(self.work_time)
        self.progress_widget.setValue(self.work_time)
        self.progress_widget.setColor(QColor(self.config["work_color"]))
        
        if self.floating_widget:
            self.floating_widget.setMaxValue(self.work_time)
            self.floating_widget.setValue(self.work_time)
            self.floating_widget.setColor(QColor(self.config["work_color"]))
            self.floating_widget.setRunningState(self.is_running)
            
        self.start_btn.setText("▶️ Start")
        self.status_label.setText("Ready to focus")
        
    def show_floating_widget(self):
        """Show floating widget and hide main window"""
        if not self.floating_widget:
            self.floating_widget = FloatingWidget()
            self.floating_widget.clicked.connect(self.show_main_window)
            self.floating_widget.toggle_timer.connect(self.toggle_timer)  # Connect the toggle signal
            
        self.floating_widget.setMaxValue(self.work_time if self.is_working else self.break_time)
        self.floating_widget.setValue(self.current_time)
        self.floating_widget.setColor(QColor(self.config["work_color"] if self.is_working else self.config["break_color"]))
        self.floating_widget.setFontSize(self.config.get("font_size", 12))
        self.floating_widget.setRunningState(self.is_running)  # Set the running state
        self.floating_widget.show()
        
        self.hide()
        self.tray_icon.show()
        
    def save_session_data(self):
        """Save completed session data"""
        today = datetime.now()
        data_file = self.data_dir / f"sessions_{today.year}_{today.month:02d}.csv"
        
        # Create file with headers if it doesn't exist
        if not data_file.exists():
            with open(data_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(["Date", "Time", "Duration (minutes)", "Type"])
                
        # Append session data
        with open(data_file, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                today.strftime("%Y-%m-%d"),
                today.strftime("%H:%M:%S"),
                self.config["work_time"],
                "Work"
            ])
            
        self.load_weekly_data()
        
    def load_weekly_data(self):
        """Load weekly focus data for statistics"""
        today = datetime.now()
        week_start = today - timedelta(days=today.weekday())
        
        weekly_data = {}
        for i in range(7):
            day = week_start + timedelta(days=i)
            weekly_data[day.strftime("%a")] = 0
            
        # Read data from current month's file
        data_file = self.data_dir / f"sessions_{today.year}_{today.month:02d}.csv"
        if data_file.exists():
            with open(data_file, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    try:
                        session_date = datetime.strptime(row["Date"], "%Y-%m-%d")
                        if week_start <= session_date <= today:
                            day_name = session_date.strftime("%a")
                            if day_name in weekly_data:
                                weekly_data[day_name] += int(row["Duration (minutes)"])
                    except (ValueError, KeyError):
                        continue
                            
        # Update chart
        if hasattr(self, 'plot_widget'):
            self.plot_widget.clear()
            days = list(weekly_data.keys())
            values = list(weekly_data.values())
            
            x = list(range(len(days)))
            bargraph = pg.BarGraphItem(x=x, height=values, width=0.6, brush='g')
            self.plot_widget.addItem(bargraph)
            
            self.plot_widget.getAxis('bottom').setTicks([[(i, days[i]) for i in range(len(days))]])
            
    def choose_color(self, color_type):
        """Open color picker dialog"""
        color = QColorDialog.getColor()
        if color.isValid():
            if color_type == "work":
                self.config["work_color"] = color.name()
                self.work_color_btn.setStyleSheet(f"background-color: {color.name()}; color: white;")
            else:
                self.config["break_color"] = color.name()
                self.break_color_btn.setStyleSheet(f"background-color: {color.name()}; color: white;")
                
    def choose_data_directory(self):
        """Choose directory for data storage"""
        directory = QFileDialog.getExistingDirectory(self, "Choose Data Directory")
        if directory:
            self.data_dir = Path(directory)
            self.config["data_dir"] = str(self.data_dir)
            self.dir_label.setText(str(self.data_dir))
            
    def save_settings(self):
        """Save all settings"""
        self.config["work_time"] = self.work_spin.value()
        self.config["break_time"] = self.break_spin.value()
        self.config["font_size"] = self.font_slider.value()
        self.config["auto_start_break"] = self.auto_start_checkbox.isChecked()
        
        self.work_time = self.config["work_time"] * 60
        self.break_time = self.config["break_time"] * 60
        
        if self.is_working:
            self.current_time = self.work_time
            self.progress_widget.setMaxValue(self.work_time)
            self.progress_widget.setValue(self.work_time)
        
        # Apply font size changes
        self.apply_font_settings()
        
        self.save_config()
        QMessageBox.information(self, "Settings", "Settings saved successfully!")
        self.stacked_widget.setCurrentIndex(0)
        
    def apply_font_settings(self):
        """Apply font size settings to UI elements"""
        base_font_size = self.config.get("font_size", 12)
        
        # Update main window stylesheet
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: white;
                border-radius: 15px;
                font-size: {base_font_size}px;
            }}
            QPushButton {{
                background-color: #4CAF50;
                border: none;
                color: white;
                padding: {max(8, base_font_size//2)}px {max(16, base_font_size)}px;
                text-align: center;
                font-size: {base_font_size + 2}px;
                border-radius: 8px;
                min-height: {max(30, base_font_size * 2)}px;
            }}
            QPushButton:hover {{
                background-color: #45a049;
            }}
            QPushButton:pressed {{
                background-color: #3d8b40;
            }}
            QLabel {{
                font-size: {base_font_size + 2}px;
            }}
            QGroupBox {{
                font-size: {base_font_size}px;
                font-weight: bold;
                margin-top: 10px;
                padding-top: 10px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }}
        """)
        
        # Update progress widget font
        if hasattr(self, 'progress_widget'):
            self.progress_widget.setFontSize(base_font_size + 8)
            
        # Update status label font
        if hasattr(self, 'status_label'):
            status_font_size = base_font_size + 6
            self.status_label.setStyleSheet(f"font-size: {status_font_size}px; margin: 10px; font-weight: bold;")
            
        # Update floating widget if exists
        if self.floating_widget:
            self.floating_widget.setFontSize(base_font_size)
        
    def export_to_csv(self):
        """Export all session data to CSV"""
        file_path, _ = QFileDialog.getSaveFileName(self, "Save CSV", "", "CSV Files (*.csv)")
        if file_path:
            # Combine all monthly files
            all_data = []
            for csv_file in self.data_dir.glob("sessions_*.csv"):
                try:
                    with open(csv_file, 'r') as f:
                        reader = csv.DictReader(f)
                        all_data.extend(list(reader))
                except Exception as e:
                    print(f"Error reading {csv_file}: {e}")
                    
            # Write combined data
            if all_data:
                with open(file_path, 'w', newline='') as f:
                    writer = csv.DictWriter(f, fieldnames=["Date", "Time", "Duration (minutes)", "Type"])
                    writer.writeheader()
                    writer.writerows(all_data)
                    
                QMessageBox.information(self, "Export", "Data exported successfully!")
            else:
                QMessageBox.warning(self, "Export", "No data to export!")
                
    def save_chart(self):
        """Save the weekly chart as an image"""
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Chart", "", "PNG Files (*.png)")
        if file_path:
            try:
                exporter = pg.exporters.ImageExporter(self.plot_widget.plotItem)
                exporter.parameters()['width'] = 800
                exporter.export(file_path)
                QMessageBox.information(self, "Save", "Chart saved successfully!")
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to save chart: {str(e)}")
            
    def closeEvent(self, event):
        """Handle close event - automatically switch to widget mode"""
        event.ignore()
        self.show_floating_widget()
        self.tray_icon.showMessage("Pomodoro Timer", "Application minimized to widget mode", 
                                   QSystemTrayIcon.MessageIcon.Information, 2000)
    
    def changeEvent(self, event):
        """Handle window state changes"""
        if event.type() == event.Type.WindowStateChange:
            if self.windowState() & Qt.WindowState.WindowMinimized:
                # Auto switch to widget mode when minimized
                QTimer.singleShot(100, self.show_floating_widget)
        super().changeEvent(event)

def main():
    """Main entry point"""
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    # Set application name and organization for proper config storage
    app.setApplicationName("PomodoroTimer")
    app.setOrganizationName("PomodoroApps")
    
    # Prevent app from quitting when last window is closed (for tray icon)
    app.setQuitOnLastWindowClosed(False)
    
    timer = PomodoroTimer()
    timer.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
