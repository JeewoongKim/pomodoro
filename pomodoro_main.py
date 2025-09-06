#!/usr/bin/env python3
"""
Cross-platform Pomodoro Timer Application
Supports Windows and macOS with GUI
"""

import sys
import os
import json
import csv
from datetime import datetime, timedelta
from pathlib import Path
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QPushButton, QLabel, QSpinBox,
                            QSystemTrayIcon, QMenu, QFileDialog, QColorDialog,
                            QStackedWidget, QGridLayout, QGroupBox, QSlider,
                            QCheckBox, QTableWidget, QTableWidgetItem,
                            QHeaderView, QMessageBox)
from PyQt6.QtCore import (Qt, QTimer, QPoint, QPropertyAnimation, QRect,
                          QEasingCurve, pyqtSignal, QDateTime, QSize)
from PyQt6.QtGui import (QPainter, QColor, QPen, QBrush, QIcon, QPixmap,
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
        
    def setValue(self, value):
        self.value = value
        self.update()
        
    def setMaxValue(self, max_value):
        self.max_value = max_value
        self.update()
        
    def setColor(self, color):
        self.color = color
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
        font = QFont("Arial", 24, QFont.Weight.Bold)
        painter.setFont(font)
        
        minutes = int(self.value // 60)
        seconds = int(self.value % 60)
        time_text = f"{minutes:02d}:{seconds:02d}"
        
        painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, time_text)

class FloatingWidget(QWidget):
    """Floating widget for always-on-top timer display"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | 
                           Qt.WindowType.WindowStaysOnTopHint |
                           Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setWindowOpacity(0.8)
        
        self.dragging = False
        self.drag_position = QPoint()
        self.resizing = False
        self.resize_start_pos = QPoint()
        self.resize_start_size = QSize()
        
        self.progress = CircularProgress(self)
        layout = QVBoxLayout()
        layout.addWidget(self.progress)
        layout.setContentsMargins(10, 10, 10, 10)
        self.setLayout(layout)
        
        self.resize(150, 150)
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Draw rounded rectangle background
        path = QPainterPath()
        path.addRoundedRect(0, 0, self.width(), self.height(), 15, 15)
        painter.fillPath(path, QColor(255, 255, 255, 200))
        
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            # Check if near edge for resizing
            edge_threshold = 10
            if (self.width() - event.position().x() < edge_threshold and 
                self.height() - event.position().y() < edge_threshold):
                self.resizing = True
                self.resize_start_pos = event.globalPosition().toPoint()
                self.resize_start_size = self.size()
            else:
                self.dragging = True
                self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
                
    def mouseMoveEvent(self, event):
        if self.resizing and event.buttons() == Qt.MouseButton.LeftButton:
            delta = event.globalPosition().toPoint() - self.resize_start_pos
            new_width = max(100, self.resize_start_size.width() + delta.x())
            new_height = max(100, self.resize_start_size.height() + delta.y())
            self.resize(new_width, new_height)
        elif self.dragging and event.buttons() == Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self.drag_position)
            
    def mouseReleaseEvent(self, event):
        self.dragging = False
        self.resizing = False
        
    def setValue(self, value):
        self.progress.setValue(value)
        
    def setMaxValue(self, max_value):
        self.progress.setMaxValue(max_value)
        
    def setColor(self, color):
        self.progress.setColor(color)

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
            "widget_style": "circular"  # circular or digital
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
            
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("Pomodoro Timer")
        self.setFixedSize(400, 500)
        
        # Set rounded corners
        self.setStyleSheet("""
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
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
        """)
        
        # Central widget with stacked layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        self.stacked_widget = QStackedWidget()
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.stacked_widget)
        central_widget.setLayout(main_layout)
        
        # Create pages
        self.create_timer_page()
        self.create_settings_page()
        self.create_statistics_page()
        
        # System tray
        self.create_system_tray()
        
    def create_timer_page(self):
        """Create the main timer page"""
        timer_page = QWidget()
        layout = QVBoxLayout()
        
        # Header with settings button
        header_layout = QHBoxLayout()
        header_layout.addStretch()
        
        settings_btn = QPushButton("⚙")
        settings_btn.setFixedSize(40, 40)
        settings_btn.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(1))
        header_layout.addWidget(settings_btn)
        
        stats_btn = QPushButton("📊")
        stats_btn.setFixedSize(40, 40)
        stats_btn.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(2))
        header_layout.addWidget(stats_btn)
        
        layout.addLayout(header_layout)
        
        # Circular progress
        self.progress_widget = CircularProgress()
        self.progress_widget.setMaxValue(self.work_time)
        self.progress_widget.setValue(self.work_time)
        layout.addWidget(self.progress_widget, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # Status label
        self.status_label = QLabel("Ready to focus")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("font-size: 18px; margin: 10px;")
        layout.addWidget(self.status_label)
        
        # Control buttons
        button_layout = QHBoxLayout()
        
        self.start_btn = QPushButton("Start")
        self.start_btn.clicked.connect(self.toggle_timer)
        button_layout.addWidget(self.start_btn)
        
        self.reset_btn = QPushButton("Reset")
        self.reset_btn.clicked.connect(self.reset_timer)
        button_layout.addWidget(self.reset_btn)
        
        self.minimize_btn = QPushButton("Minimize to Widget")
        self.minimize_btn.clicked.connect(self.show_floating_widget)
        button_layout.addWidget(self.minimize_btn)
        
        layout.addLayout(button_layout)
        
        # Sessions counter
        self.sessions_label = QLabel(f"Sessions completed: {self.sessions_completed}")
        self.sessions_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.sessions_label)
        
        timer_page.setLayout(layout)
        self.stacked_widget.addWidget(timer_page)
        
    def create_settings_page(self):
        """Create the settings page"""
        settings_page = QWidget()
        layout = QVBoxLayout()
        
        # Back button
        back_btn = QPushButton("← Back")
        back_btn.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))
        layout.addWidget(back_btn)
        
        # Timer settings
        timer_group = QGroupBox("Timer Settings")
        timer_layout = QGridLayout()
        
        timer_layout.addWidget(QLabel("Work Time (minutes):"), 0, 0)
        self.work_spin = QSpinBox()
        self.work_spin.setRange(1, 60)
        self.work_spin.setValue(self.config["work_time"])
        timer_layout.addWidget(self.work_spin, 0, 1)
        
        timer_layout.addWidget(QLabel("Break Time (minutes):"), 1, 0)
        self.break_spin = QSpinBox()
        self.break_spin.setRange(1, 30)
        self.break_spin.setValue(self.config["break_time"])
        timer_layout.addWidget(self.break_spin, 1, 1)
        
        timer_group.setLayout(timer_layout)
        layout.addWidget(timer_group)
        
        # Appearance settings
        appearance_group = QGroupBox("Appearance")
        appearance_layout = QGridLayout()
        
        appearance_layout.addWidget(QLabel("Font Size:"), 0, 0)
        self.font_slider = QSlider(Qt.Orientation.Horizontal)
        self.font_slider.setRange(10, 24)
        self.font_slider.setValue(self.config["font_size"])
        appearance_layout.addWidget(self.font_slider, 0, 1)
        
        appearance_layout.addWidget(QLabel("Work Color:"), 1, 0)
        self.work_color_btn = QPushButton()
        self.work_color_btn.setStyleSheet(f"background-color: {self.config['work_color']}")
        self.work_color_btn.clicked.connect(lambda: self.choose_color("work"))
        appearance_layout.addWidget(self.work_color_btn, 1, 1)
        
        appearance_layout.addWidget(QLabel("Break Color:"), 2, 0)
        self.break_color_btn = QPushButton()
        self.break_color_btn.setStyleSheet(f"background-color: {self.config['break_color']}")
        self.break_color_btn.clicked.connect(lambda: self.choose_color("break"))
        appearance_layout.addWidget(self.break_color_btn, 2, 1)
        
        appearance_group.setLayout(appearance_layout)
        layout.addWidget(appearance_group)
        
        # Data settings
        data_group = QGroupBox("Data Settings")
        data_layout = QVBoxLayout()
        
        dir_layout = QHBoxLayout()
        self.dir_label = QLabel(str(self.data_dir))
        dir_layout.addWidget(self.dir_label)
        
        browse_btn = QPushButton("Browse")
        browse_btn.clicked.connect(self.choose_data_directory)
        dir_layout.addWidget(browse_btn)
        
        data_layout.addLayout(dir_layout)
        data_group.setLayout(data_layout)
        layout.addWidget(data_group)
        
        # Save button
        save_btn = QPushButton("Save Settings")
        save_btn.clicked.connect(self.save_settings)
        layout.addWidget(save_btn)
        
        layout.addStretch()
        settings_page.setLayout(layout)
        self.stacked_widget.addWidget(settings_page)
        
    def create_statistics_page(self):
        """Create the statistics page"""
        stats_page = QWidget()
        layout = QVBoxLayout()
        
        # Back button
        back_btn = QPushButton("← Back")
        back_btn.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))
        layout.addWidget(back_btn)
        
        # Weekly chart
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setBackground('w')
        self.plot_widget.setTitle("Weekly Focus Time", color='b', size='16pt')
        self.plot_widget.setLabel('left', 'Minutes', color='b', size='12pt')
        self.plot_widget.setLabel('bottom', 'Day', color='b', size='12pt')
        layout.addWidget(self.plot_widget)
        
        # Export buttons
        export_layout = QHBoxLayout()
        
        export_csv_btn = QPushButton("Export to CSV")
        export_csv_btn.clicked.connect(self.export_to_csv)
        export_layout.addWidget(export_csv_btn)
        
        export_chart_btn = QPushButton("Save Chart")
        export_chart_btn.clicked.connect(self.save_chart)
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
        show_action.triggered.connect(self.show)
        tray_menu.addAction(show_action)
        
        quit_action = QAction("Quit", self)
        quit_action.triggered.connect(QApplication.quit)
        tray_menu.addAction(quit_action)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.activated.connect(self.tray_icon_activated)
        
    def tray_icon_activated(self, reason):
        """Handle tray icon activation"""
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.show()
            
    def toggle_timer(self):
        """Start or pause the timer"""
        if self.is_running:
            self.timer.stop()
            self.start_btn.setText("Start")
            self.status_label.setText("Paused")
        else:
            self.timer.start(1000)  # Update every second
            self.start_btn.setText("Pause")
            self.status_label.setText("Working..." if self.is_working else "Break time!")
            
        self.is_running = not self.is_running
        
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
            
            # Show notification
            self.tray_icon.showMessage("Pomodoro Timer", "Break finished! Ready for another session?", 
                                       QSystemTrayIcon.MessageIcon.Information, 3000)
            
        self.progress_widget.setValue(self.current_time)
        if self.floating_widget:
            self.floating_widget.setValue(self.current_time)
        self.start_btn.setText("Start")
        
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
            
        self.start_btn.setText("Start")
        self.status_label.setText("Ready to focus")
        
    def show_floating_widget(self):
        """Show floating widget and hide main window"""
        if not self.floating_widget:
            self.floating_widget = FloatingWidget()
            
        self.floating_widget.setMaxValue(self.work_time if self.is_working else self.break_time)
        self.floating_widget.setValue(self.current_time)
        self.floating_widget.setColor(QColor(self.config["work_color"] if self.is_working else self.config["break_color"]))
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
                    session_date = datetime.strptime(row["Date"], "%Y-%m-%d")
                    if week_start <= session_date <= today:
                        day_name = session_date.strftime("%a")
                        if day_name in weekly_data:
                            weekly_data[day_name] += int(row["Duration (minutes)"])
                            
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
                self.work_color_btn.setStyleSheet(f"background-color: {color.name()}")
            else:
                self.config["break_color"] = color.name()
                self.break_color_btn.setStyleSheet(f"background-color: {color.name()}")
                
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
        
        self.work_time = self.config["work_time"] * 60
        self.break_time = self.config["break_time"] * 60
        
        if self.is_working:
            self.current_time = self.work_time
            self.progress_widget.setMaxValue(self.work_time)
            self.progress_widget.setValue(self.work_time)
        
        self.save_config()
        QMessageBox.information(self, "Settings", "Settings saved successfully!")
        self.stacked_widget.setCurrentIndex(0)
        
    def export_to_csv(self):
        """Export all session data to CSV"""
        file_path, _ = QFileDialog.getSaveFileName(self, "Save CSV", "", "CSV Files (*.csv)")
        if file_path:
            # Combine all monthly files
            all_data = []
            for csv_file in self.data_dir.glob("sessions_*.csv"):
                with open(csv_file, 'r') as f:
                    reader = csv.DictReader(f)
                    all_data.extend(list(reader))
                    
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
            exporter = pg.exporters.ImageExporter(self.plot_widget.plotItem)
            exporter.parameters()['width'] = 800
            exporter.export(file_path)
            QMessageBox.information(self, "Save", "Chart saved successfully!")
            
    def closeEvent(self, event):
        """Handle close event"""
        event.ignore()
        self.hide()
        self.tray_icon.show()
        self.tray_icon.showMessage("Pomodoro Timer", "Application minimized to tray", 
                                   QSystemTrayIcon.MessageIcon.Information, 2000)

def main():
    """Main entry point"""
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    # Set application name and organization for proper config storage
    app.setApplicationName("PomodoroTimer")
    app.setOrganizationName("PomodoroApps")
    
    timer = PomodoroTimer()
    timer.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()