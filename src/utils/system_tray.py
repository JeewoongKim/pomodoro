"""
System tray functionality for Pomodoro Timer
"""

import sys
from pathlib import Path
from PyQt6.QtWidgets import QSystemTrayIcon, QMenu, QApplication
from PyQt6.QtGui import QIcon, QPixmap, QAction
from PyQt6.QtCore import QObject, pyqtSignal

class SystemTrayManager(QObject):
    """Manages system tray icon and menu"""
    
    # Signals
    show_main_window = pyqtSignal()
    show_floating_widget = pyqtSignal()
    start_pause_timer = pyqtSignal()
    quit_application = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.tray_icon = None
        self.setup_tray()
        
    def setup_tray(self):
        """Set up system tray icon and menu"""
        if not QSystemTrayIcon.isSystemTrayAvailable():
            print("System tray is not available")
            return
            
        # Create tray icon
        self.tray_icon = QSystemTrayIcon()
        self.tray_icon.setIcon(self.create_tray_icon())
        
        # Create menu
        tray_menu = QMenu()
        
        # Show main window action
        show_action = QAction("Show Main Window", self)
        show_action.triggered.connect(self.show_main_window.emit)
        tray_menu.addAction(show_action)
        
        # Show floating widget action
        widget_action = QAction("Show Floating Widget", self)
        widget_action.triggered.connect(self.show_floating_widget.emit)
        tray_menu.addAction(widget_action)
        
        tray_menu.addSeparator()
        
        # Start/Pause timer action
        self.timer_action = QAction("Start Timer", self)
        self.timer_action.triggered.connect(self.start_pause_timer.emit)
        tray_menu.addAction(self.timer_action)
        
        tray_menu.addSeparator()
        
        # Quit action
        quit_action = QAction("Quit", self)
        quit_action.triggered.connect(self.quit_application.emit)
        tray_menu.addAction(quit_action)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.activated.connect(self.on_tray_icon_activated)
        
    def create_tray_icon(self) -> QIcon:
        """Create tray icon"""
        try:
            # Try to load icon from resources
            if hasattr(sys, '_MEIPASS'):
                # Running as compiled executable
                icon_path = Path(sys._MEIPASS) / "resources" / "icons" / "tray_icon.png"
            else:
                # Running as script
                icon_path = Path(__file__).parent.parent.parent / "resources" / "icons" / "tray_icon.png"
                
            if icon_path.exists():
                return QIcon(str(icon_path))
        except Exception as e:
            print(f"Error loading tray icon: {e}")
            
        # Create simple fallback icon
        pixmap = QPixmap(16, 16)
        pixmap.fill("#34a853")  # Green color
        return QIcon(pixmap)
        
    def show_tray_icon(self):
        """Show the tray icon"""
        if self.tray_icon:
            self.tray_icon.show()
            
    def hide_tray_icon(self):
        """Hide the tray icon"""
        if self.tray_icon:
            self.tray_icon.hide()
            
    def show_message(self, title: str, message: str, icon: QSystemTrayIcon.MessageIcon = None, timeout: int = 3000):
        """Show tray notification message"""
        if self.tray_icon and self.tray_icon.isVisible():
            if icon is None:
                icon = QSystemTrayIcon.MessageIcon.Information
            self.tray_icon.showMessage(title, message, icon, timeout)
            
    def update_timer_action(self, is_running: bool):
        """Update timer action text based on timer state"""
        if hasattr(self, 'timer_action'):
            if is_running:
                self.timer_action.setText("Pause Timer")
            else:
                self.timer_action.setText("Start Timer")
                
    def update_tooltip(self, text: str):
        """Update tray icon tooltip"""
        if self.tray_icon:
            self.tray_icon.setToolTip(text)
            
    def on_tray_icon_activated(self, reason):
        """Handle tray icon activation"""
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.show_main_window.emit()
        elif reason == QSystemTrayIcon.ActivationReason.MiddleClick:
            self.show_floating_widget.emit()
            
    def is_available(self) -> bool:
        """Check if system tray is available"""
        return QSystemTrayIcon.isSystemTrayAvailable()
        
    def is_visible(self) -> bool:
        """Check if tray icon is visible"""
        return self.tray_icon and self.tray_icon.isVisible()
