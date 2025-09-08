"""
Settings page for Pomodoro Timer application
"""

import sys
from pathlib import Path
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                            QLabel, QSpinBox, QSlider, QGroupBox, QGridLayout,
                            QCheckBox, QColorDialog, QFileDialog, QMessageBox,
                            QFrame, QScrollArea, QComboBox)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QIcon, QPixmap, QColor

from utils.icon_manager import IconManager

class SettingsPage(QWidget):
    """Settings configuration page"""
    
    # Signals
    back_clicked = pyqtSignal()
    settings_saved = pyqtSignal()
    theme_changed = pyqtSignal(str)  # Emit theme name when changed
    
    def __init__(self, config_manager):
        super().__init__()
        self.config_manager = config_manager
        self.icon_manager = IconManager(config_manager)
        
        self.init_ui()
        self.load_current_settings()
        
    def init_ui(self):
        """Initialize the user interface"""
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Header with back button
        header_layout = QHBoxLayout()
        
        self.back_btn = QPushButton()
        self.back_btn.setFixedSize(50, 50)
        self.back_btn.setIcon(self.icon_manager.get_icon('back'))
        self.back_btn.setToolTip("Back to Timer")
        self.back_btn.clicked.connect(self.back_clicked.emit)
        self.back_btn.setStyleSheet("""
            QPushButton {
                background-color: #6c757d;
                border: none;
                border-radius: 25px;
                color: white;
            }
            QPushButton:hover {
                background-color: #5a6268;
            }
        """)
        header_layout.addWidget(self.back_btn)
        
        header_layout.addStretch()
        
        title_label = QLabel("Settings")
        title_label.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: #333333;
            }
        """)
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        layout.addLayout(header_layout)
        
        # Scrollable content
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        
        settings_widget = QWidget()
        settings_layout = QVBoxLayout()
        settings_layout.setSpacing(20)
        
        # Timer Settings Group
        timer_group = self.create_timer_settings_group()
        settings_layout.addWidget(timer_group)
        
        # Appearance Settings Group
        appearance_group = self.create_appearance_settings_group()
        settings_layout.addWidget(appearance_group)
        
        # Behavior Settings Group
        behavior_group = self.create_behavior_settings_group()
        settings_layout.addWidget(behavior_group)
        
        # Data Settings Group
        data_group = self.create_data_settings_group()
        settings_layout.addWidget(data_group)
        
        settings_layout.addStretch()
        settings_widget.setLayout(settings_layout)
        scroll_area.setWidget(settings_widget)
        
        layout.addWidget(scroll_area)
        
        # Save and Reset buttons
        button_layout = QHBoxLayout()
        
        self.reset_btn = QPushButton("Reset to Defaults")
        self.reset_btn.setIcon(self.icon_manager.get_icon('refresh'))
        self.reset_btn.clicked.connect(self.reset_to_defaults)
        self.reset_btn.setStyleSheet("""
            QPushButton {
                background-color: #ff9800;
                color: white;
                padding: 12px 20px;
                font-size: 14px;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #e68900;
            }
        """)
        button_layout.addWidget(self.reset_btn)
        
        button_layout.addStretch()
        
        self.save_btn = QPushButton("Save Settings")
        self.save_btn.setIcon(self.icon_manager.get_icon('save'))
        self.save_btn.clicked.connect(self.save_settings)
        self.save_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 12px 20px;
                font-size: 14px;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        button_layout.addWidget(self.save_btn)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
    def create_timer_settings_group(self) -> QGroupBox:
        """Create timer settings group"""
        group = QGroupBox("Timer Settings")
        layout = QGridLayout()
        layout.setSpacing(15)
        
        # Work Time
        layout.addWidget(QLabel("Work Time (minutes):"), 0, 0)
        self.work_spin = QSpinBox()
        self.work_spin.setRange(1, 120)
        self.work_spin.setSuffix(" min")
        layout.addWidget(self.work_spin, 0, 1)
        
        # Break Time
        layout.addWidget(QLabel("Short Break (minutes):"), 1, 0)
        self.break_spin = QSpinBox()
        self.break_spin.setRange(1, 60)
        self.break_spin.setSuffix(" min")
        layout.addWidget(self.break_spin, 1, 1)
        
        # Long Break Time
        layout.addWidget(QLabel("Long Break (minutes):"), 2, 0)
        self.long_break_spin = QSpinBox()
        self.long_break_spin.setRange(5, 120)
        self.long_break_spin.setSuffix(" min")
        layout.addWidget(self.long_break_spin, 2, 1)
        
        # Sessions until long break
        layout.addWidget(QLabel("Sessions until long break:"), 3, 0)
        self.sessions_spin = QSpinBox()
        self.sessions_spin.setRange(1, 10)
        layout.addWidget(self.sessions_spin, 3, 1)
        
        group.setLayout(layout)
        return group
        
    def create_appearance_settings_group(self) -> QGroupBox:
        """Create appearance settings group"""
        group = QGroupBox("Appearance")
        layout = QGridLayout()
        layout.setSpacing(15)
        
        # Theme Selection
        layout.addWidget(QLabel("Theme:"), 0, 0)
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Light", "Dark"])
        self.theme_combo.currentTextChanged.connect(self.on_theme_changed)
        layout.addWidget(self.theme_combo, 0, 1)
        
        # Font Size
        layout.addWidget(QLabel("Font Size:"), 1, 0)
        font_layout = QHBoxLayout()
        
        self.font_slider = QSlider(Qt.Orientation.Horizontal)
        self.font_slider.setRange(10, 28)
        self.font_slider.valueChanged.connect(self.update_font_preview)
        font_layout.addWidget(self.font_slider)
        
        self.font_preview = QLabel("14")
        self.font_preview.setMinimumWidth(30)
        self.font_preview.setStyleSheet("font-weight: bold; color: #666;")
        font_layout.addWidget(self.font_preview)
        
        font_widget = QWidget()
        font_widget.setLayout(font_layout)
        layout.addWidget(font_widget, 1, 1)
        
        # Work Color
        layout.addWidget(QLabel("Work Session Color:"), 2, 0)
        color_layout = QHBoxLayout()
        
        self.work_color_btn = QPushButton("Choose Color")
        self.work_color_btn.clicked.connect(lambda: self.choose_color("work"))
        color_layout.addWidget(self.work_color_btn)
        
        self.work_color_preview = QLabel()
        self.work_color_preview.setFixedSize(30, 30)
        self.work_color_preview.setStyleSheet("border: 1px solid #ccc; border-radius: 4px;")
        color_layout.addWidget(self.work_color_preview)
        
        work_color_widget = QWidget()
        work_color_widget.setLayout(color_layout)
        layout.addWidget(work_color_widget, 2, 1)
        
        # Break Color
        layout.addWidget(QLabel("Break Session Color:"), 3, 0)
        break_color_layout = QHBoxLayout()
        
        self.break_color_btn = QPushButton("Choose Color")
        self.break_color_btn.clicked.connect(lambda: self.choose_color("break"))
        break_color_layout.addWidget(self.break_color_btn)
        
        self.break_color_preview = QLabel()
        self.break_color_preview.setFixedSize(30, 30)
        self.break_color_preview.setStyleSheet("border: 1px solid #ccc; border-radius: 4px;")
        break_color_layout.addWidget(self.break_color_preview)
        
        break_color_widget = QWidget()
        break_color_widget.setLayout(break_color_layout)
        layout.addWidget(break_color_widget, 3, 1)
        
        # Responsive UI
        self.responsive_ui_check = QCheckBox("Responsive UI (auto-scale)")
        self.responsive_ui_check.setToolTip("Automatically adjust UI size based on window size")
        layout.addWidget(self.responsive_ui_check, 4, 0, 1, 2)
        
        group.setLayout(layout)
        return group
        
    def create_behavior_settings_group(self) -> QGroupBox:
        """Create behavior settings group"""
        group = QGroupBox("Behavior")
        layout = QGridLayout()
        layout.setSpacing(15)
        
        # Auto start breaks
        self.auto_start_breaks_check = QCheckBox("Auto-start break sessions")
        self.auto_start_breaks_check.setToolTip("Automatically start break timer after work session")
        layout.addWidget(self.auto_start_breaks_check, 0, 0, 1, 2)
        
        # Auto start work
        self.auto_start_work_check = QCheckBox("Auto-start work sessions after break")
        self.auto_start_work_check.setToolTip("Automatically start work timer after break session")
        layout.addWidget(self.auto_start_work_check, 1, 0, 1, 2)
        
        # Notifications
        self.notifications_check = QCheckBox("Show system notifications")
        self.notifications_check.setToolTip("Show popup notifications when sessions complete")
        layout.addWidget(self.notifications_check, 2, 0, 1, 2)
        
        # Sound notifications
        self.sound_check = QCheckBox("Play notification sounds")
        self.sound_check.setToolTip("Play sound when sessions complete")
        layout.addWidget(self.sound_check, 3, 0, 1, 2)
        
        group.setLayout(layout)
        return group
        
    def create_data_settings_group(self) -> QGroupBox:
        """Create data settings group"""
        group = QGroupBox("Data & Storage")
        layout = QGridLayout()
        layout.setSpacing(15)
        
        # Data directory
        layout.addWidget(QLabel("Data Directory:"), 0, 0)
        
        dir_layout = QHBoxLayout()
        self.dir_label = QLabel()
        self.dir_label.setStyleSheet("""
            QLabel {
                padding: 8px;
                background-color: #f0f0f0;
                border: 1px solid #ccc;
                border-radius: 4px;
                font-family: monospace;
            }
        """)
        dir_layout.addWidget(self.dir_label)
        
        self.browse_btn = QPushButton("Browse...")
        self.browse_btn.setIcon(self.icon_manager.get_icon('folder'))
        self.browse_btn.clicked.connect(self.choose_data_directory)
        dir_layout.addWidget(self.browse_btn)
        
        dir_widget = QWidget()
        dir_widget.setLayout(dir_layout)
        layout.addWidget(dir_widget, 0, 1)
        
        # Data management
        data_btn_layout = QHBoxLayout()
        
        self.export_btn = QPushButton("Export All Data")
        self.export_btn.setIcon(self.icon_manager.get_icon('download'))
        self.export_btn.clicked.connect(self.export_data)
        self.export_btn.setToolTip("Export all session data to CSV file")
        data_btn_layout.addWidget(self.export_btn)
        
        self.cleanup_btn = QPushButton("Cleanup Old Data")
        self.cleanup_btn.setIcon(self.icon_manager.get_icon('trash'))
        self.cleanup_btn.clicked.connect(self.cleanup_data)
        self.cleanup_btn.setToolTip("Remove data files older than 12 months")
        data_btn_layout.addWidget(self.cleanup_btn)
        
        data_btn_widget = QWidget()
        data_btn_widget.setLayout(data_btn_layout)
        layout.addWidget(data_btn_widget, 1, 0, 1, 2)
        
        group.setLayout(layout)
        return group
        
    def on_theme_changed(self, theme_text: str):
        """Handle theme change"""
        theme_value = theme_text.lower()
        
        # Update config immediately for preview
        self.config_manager.set("theme", theme_value)
        
        # Recreate icon manager with new theme
        self.icon_manager = IconManager(self.config_manager)
        
        # Update all icons in the settings page
        self.update_all_icons()
        
        # Emit signal to update other components
        self.theme_changed.emit(theme_value)
        
    def update_all_icons(self):
        """Update all icons in the settings page with current theme"""
        # Update header icons
        self.back_btn.setIcon(self.icon_manager.get_icon('back'))
        
        # Update button icons
        self.reset_btn.setIcon(self.icon_manager.get_icon('refresh'))
        self.save_btn.setIcon(self.icon_manager.get_icon('save'))
        
        # Update data management icons
        if hasattr(self, 'browse_btn'):
            self.browse_btn.setIcon(self.icon_manager.get_icon('folder'))
        if hasattr(self, 'export_btn'):
            self.export_btn.setIcon(self.icon_manager.get_icon('download'))
        if hasattr(self, 'cleanup_btn'):
            self.cleanup_btn.setIcon(self.icon_manager.get_icon('trash'))
            
        # Apply theme-specific styling
        self.apply_theme_styles()
        
    def apply_theme_styles(self):
        """Apply theme-specific styles to the settings page"""
        theme = self.config_manager.get("theme", "light")
        
        if theme == "dark":
            # Dark theme styles
            self.setStyleSheet("""
                QWidget {
                    background-color: #2b2b2b;
                    color: #ffffff;
                }
                QGroupBox {
                    font-weight: bold;
                    border: 2px solid #555555;
                    border-radius: 8px;
                    margin-top: 10px;
                    padding-top: 10px;
                    background-color: #3c3c3c;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    left: 10px;
                    padding: 0 8px 0 8px;
                    color: #ffffff;
                }
                QLabel {
                    color: #ffffff;
                }
                QSpinBox, QSlider, QComboBox, QCheckBox {
                    background-color: #404040;
                    border: 1px solid #555555;
                    color: #ffffff;
                }
                QScrollArea {
                    background-color: #2b2b2b;
                    border: none;
                }
            """)
            
            # Update title label for dark theme
            title_label = self.findChild(QLabel)
            if title_label and title_label.text() == "Settings":
                title_label.setStyleSheet("""
                    QLabel {
                        font-size: 24px;
                        font-weight: bold;
                        color: #ffffff;
                    }
                """)
        else:
            # Light theme styles (default)
            self.setStyleSheet("")
            
            # Restore original title style
            title_label = self.findChild(QLabel)
            if title_label and title_label.text() == "Settings":
                title_label.setStyleSheet("""
                    QLabel {
                        font-size: 24px;
                        font-weight: bold;
                        color: #333333;
                    }
                """)
        
    def load_current_settings(self):
        """Load current settings into UI elements"""
        # Timer settings
        self.work_spin.setValue(self.config_manager.get("work_time", 25))
        self.break_spin.setValue(self.config_manager.get("break_time", 5))
        self.long_break_spin.setValue(self.config_manager.get("long_break_time", 15))
        self.sessions_spin.setValue(self.config_manager.get("sessions_until_long_break", 4))
        
        # Appearance settings
        theme = self.config_manager.get("theme", "light")
        self.theme_combo.setCurrentText(theme.capitalize())
        
        font_size = self.config_manager.get("font_size", 14)
        self.font_slider.setValue(font_size)
        self.update_font_preview()
        
        work_color = self.config_manager.get("work_color", "#34a853")
        self.update_color_preview("work", work_color)
        
        break_color = self.config_manager.get("break_color", "#4285f4")
        self.update_color_preview("break", break_color)
        
        self.responsive_ui_check.setChecked(self.config_manager.get("responsive_ui", True))
        
        # Behavior settings
        self.auto_start_breaks_check.setChecked(self.config_manager.get("auto_start_breaks", True))
        self.auto_start_work_check.setChecked(self.config_manager.get("auto_start_work", False))
        self.notifications_check.setChecked(self.config_manager.get("notifications_enabled", True))
        self.sound_check.setChecked(self.config_manager.get("sound_enabled", True))
        
        # Data settings
        data_dir = self.config_manager.get_data_directory()
        self.dir_label.setText(str(data_dir))
        
        # Apply initial theme
        self.apply_theme_styles()
        
    def update_font_preview(self):
        """Update font size preview"""
        size = self.font_slider.value()
        self.font_preview.setText(str(size))
        
    def update_color_preview(self, color_type: str, color_hex: str):
        """Update color preview widget"""
        if color_type == "work":
            self.work_color_preview.setStyleSheet(f"""
                QLabel {{
                    background-color: {color_hex};
                    border: 1px solid #ccc;
                    border-radius: 4px;
                }}
            """)
        else:
            self.break_color_preview.setStyleSheet(f"""
                QLabel {{
                    background-color: {color_hex};
                    border: 1px solid #ccc;
                    border-radius: 4px;
                }}
            """)
        
    def choose_color(self, color_type: str):
        """Open color picker dialog"""
        current_color = QColor(self.config_manager.get(f"{color_type}_color"))
        color = QColorDialog.getColor(current_color, self, f"Choose {color_type.title()} Color")
        
        if color.isValid():
            color_hex = color.name()
            self.config_manager.set(f"{color_type}_color", color_hex)
            self.update_color_preview(color_type, color_hex)
                
    def choose_data_directory(self):
        """Choose directory for data storage"""
        current_dir = str(self.config_manager.get_data_directory())
        directory = QFileDialog.getExistingDirectory(
            self, 
            "Choose Data Directory", 
            current_dir
        )
        
        if directory:
            self.config_manager.set_data_directory(directory)
            self.dir_label.setText(directory)
            
    def export_data(self):
        """Export all session data"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, 
            "Export Session Data", 
            f"pomodoro_data_{self.config_manager.get('export_timestamp', 'export')}.csv",
            "CSV Files (*.csv)"
        )
        
        if file_path:
            try:
                from core.data_manager import DataManager
                data_manager = DataManager(self.config_manager)
                
                if data_manager.export_all_data(file_path):
                    QMessageBox.information(
                        self, 
                        "Export Success", 
                        f"Data exported successfully to:\n{file_path}"
                    )
                else:
                    QMessageBox.warning(
                        self,
                        "Export Failed",
                        "No data found to export or export failed."
                    )
            except ImportError:
                QMessageBox.warning(
                    self,
                    "Export Unavailable",
                    "Data export feature is not available."
                )
                
    def cleanup_data(self):
        """Clean up old data files"""
        reply = QMessageBox.question(
            self,
            "Cleanup Data",
            "This will remove data files older than 12 months.\n"
            "Are you sure you want to continue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                from core.data_manager import DataManager
                data_manager = DataManager(self.config_manager)
                data_manager.cleanup_old_data(12)
                
                QMessageBox.information(
                    self,
                    "Cleanup Complete",
                    "Old data files have been cleaned up."
                )
            except ImportError:
                QMessageBox.information(
                    self,
                    "Cleanup Unavailable",
                    "Data cleanup feature is not available."
                )
            
    def reset_to_defaults(self):
        """Reset all settings to default values"""
        reply = QMessageBox.question(
            self,
            "Reset Settings",
            "This will reset all settings to their default values.\n"
            "Are you sure you want to continue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.config_manager.reset_to_defaults()
            self.load_current_settings()
            
            # Update icons after reset
            self.icon_manager = IconManager(self.config_manager)
            self.update_all_icons()
            
            # Emit theme change signal
            theme = self.config_manager.get("theme", "light")
            self.theme_changed.emit(theme)
            
            QMessageBox.information(
                self,
                "Reset Complete",
                "All settings have been reset to defaults."
            )
            
    def save_settings(self):
        """Save all current settings"""
        # Timer settings
        self.config_manager.set("work_time", self.work_spin.value())
        self.config_manager.set("break_time", self.break_spin.value())
        self.config_manager.set("long_break_time", self.long_break_spin.value())
        self.config_manager.set("sessions_until_long_break", self.sessions_spin.value())
        
        # Appearance settings
        theme = self.theme_combo.currentText().lower()
        self.config_manager.set("theme", theme)
        self.config_manager.set("font_size", self.font_slider.value())
        self.config_manager.set("responsive_ui", self.responsive_ui_check.isChecked())
        
        # Behavior settings
        self.config_manager.set("auto_start_breaks", self.auto_start_breaks_check.isChecked())
        self.config_manager.set("auto_start_work", self.auto_start_work_check.isChecked())
        self.config_manager.set("notifications_enabled", self.notifications_check.isChecked())
        self.config_manager.set("sound_enabled", self.sound_check.isChecked())
        
        # Save to file
        self.config_manager.save_config()
        
        # Show success message
        QMessageBox.information(
            self,
            "Settings Saved",
            "Settings have been saved successfully!"
        )
        
        # Emit signal to update main application
        self.settings_saved.emit()
        
    def resizeEvent(self, event):
        """Handle resize event for responsive design"""
        super().resizeEvent(event)
        
        # Adjust spacing and sizes based on window size
        if hasattr(self, 'font_slider'):
            width = self.width()
            if width < 500:
                # Compact layout for small windows
                compact_style = """
                    QGroupBox { font-size: 12px; }
                    QLabel { font-size: 11px; }
                    QPushButton { padding: 8px 15px; font-size: 12px; }
                """
                current_style = self.styleSheet()
                if "QGroupBox { font-size: 12px; }" not in current_style:
                    self.setStyleSheet(current_style + compact_style)
            else:
                # Normal layout - reapply theme styles
                self.apply_theme_styles()