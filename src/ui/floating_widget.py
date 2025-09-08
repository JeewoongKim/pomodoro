"""
Floating widget for always-on-top timer display
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton
from PyQt6.QtCore import Qt, QPoint, QSize, pyqtSignal
from PyQt6.QtGui import QPainter, QColor, QPainterPath, QMouseEvent

from widgets.circular_progress import CircularProgress
from utils.icon_manager import IconManager

class FloatingWidget(QWidget):
    """Floating widget for always-on-top timer display"""
    
    # Signals
    show_main_window = pyqtSignal()
    start_pause_clicked = pyqtSignal()
    reset_clicked = pyqtSignal()
    
    def __init__(self, config_manager, parent=None):
        super().__init__(parent)
        self.config_manager = config_manager
        self.icon_manager = IconManager(config_manager)
        
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | 
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setWindowOpacity(0.9)
        
        # Dragging and resizing
        self.dragging = False
        self.drag_position = QPoint()
        self.resizing = False
        self.resize_start_pos = QPoint()
        self.resize_start_size = QSize()
        
        # Minimum size
        self.min_size = QSize(120, 120)
        
        # Current state for button updates
        self.current_state = "Start"  # Start, Pause, Resume
        
        self.init_ui()
        self.resize(180, 200)
        
    def init_ui(self):
        """Initialize the user interface"""
        layout = QVBoxLayout()
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)
        
        # Progress circle
        self.progress = CircularProgress(self)
        self.progress.setMinimumSize(100, 100)
        layout.addWidget(self.progress, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # Control buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(5)
        
        # Start/Pause button
        self.start_pause_btn = QPushButton()
        self.start_pause_btn.setFixedSize(30, 30)
        self.start_pause_btn.clicked.connect(self.start_pause_clicked.emit)
        self.update_start_pause_button()
        
        # Reset button
        self.reset_btn = QPushButton()
        self.reset_btn.setFixedSize(30, 30)
        self.reset_btn.clicked.connect(self.reset_clicked.emit)
        self.reset_btn.setIcon(self.icon_manager.get_icon('refresh'))
        self.reset_btn.setToolTip("Reset Timer")
        self.reset_btn.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                border: none;
                border-radius: 15px;
                color: white;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
        """)
        
        button_layout.addWidget(self.start_pause_btn)
        button_layout.addWidget(self.reset_btn)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
    def update_start_pause_button(self):
        """Update start/pause button icon and style based on current state"""
        if self.current_state == "Start":
            icon = self.icon_manager.get_icon('play')
            color = "#4CAF50"
            hover_color = "#45a049"
            tooltip = "Start Timer"
        elif self.current_state == "Pause":
            icon = self.icon_manager.get_icon('pause')
            color = "#ff9800"
            hover_color = "#e68900"
            tooltip = "Pause Timer"
        else:  # Resume
            icon = self.icon_manager.get_icon('play')
            color = "#4CAF50"
            hover_color = "#45a049"
            tooltip = "Resume Timer"
            
        self.start_pause_btn.setIcon(icon)
        self.start_pause_btn.setToolTip(tooltip)
        self.start_pause_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                border: none;
                border-radius: 15px;
                color: white;
                font-size: 14px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {hover_color};
            }}
        """)
        
    def update_theme(self):
        """Update icons when theme changes"""
        # Reload icon manager with current theme
        self.icon_manager = IconManager(self.config_manager)
        
        # Update button icons
        self.update_start_pause_button()
        self.reset_btn.setIcon(self.icon_manager.get_icon('refresh'))
        
        # Force repaint
        self.update()
        
    def paintEvent(self, event):
        """Paint the widget background"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Get theme-aware background color
        theme = self.config_manager.get("theme", "light")
        if theme == "dark":
            bg_color = QColor(45, 45, 48, 220)  # Dark background
            border_color = QColor(70, 70, 70, 150)
        else:
            bg_color = QColor(255, 255, 255, 220)  # Light background
            border_color = QColor(200, 200, 200, 100)
        
        # Draw rounded rectangle background
        path = QPainterPath()
        path.addRoundedRect(0, 0, self.width(), self.height(), 15, 15)
        painter.fillPath(path, bg_color)
        
        # Draw border
        painter.setPen(border_color)
        painter.drawPath(path)
        
    def mousePressEvent(self, event: QMouseEvent):
        """Handle mouse press for dragging and resizing"""
        if event.button() == Qt.MouseButton.LeftButton:
            # Check if near bottom-right corner for resizing
            edge_threshold = 15
            if (self.width() - event.position().x() < edge_threshold and 
                self.height() - event.position().y() < edge_threshold):
                self.resizing = True
                self.resize_start_pos = event.globalPosition().toPoint()
                self.resize_start_size = self.size()
                self.setCursor(Qt.CursorShape.SizeFDiagCursor)
            else:
                self.dragging = True
                self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
                self.setCursor(Qt.CursorShape.ClosedHandCursor)
                
    def mouseMoveEvent(self, event: QMouseEvent):
        """Handle mouse move for dragging and resizing"""
        if self.resizing and event.buttons() == Qt.MouseButton.LeftButton:
            delta = event.globalPosition().toPoint() - self.resize_start_pos
            new_width = max(self.min_size.width(), self.resize_start_size.width() + delta.x())
            new_height = max(self.min_size.height(), self.resize_start_size.height() + delta.y())
            self.resize(new_width, new_height)
            
        elif self.dragging and event.buttons() == Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self.drag_position)
        else:
            # Check if near resize corner for cursor change
            edge_threshold = 15
            if (self.width() - event.position().x() < edge_threshold and 
                self.height() - event.position().y() < edge_threshold):
                self.setCursor(Qt.CursorShape.SizeFDiagCursor)
            else:
                self.setCursor(Qt.CursorShape.ArrowCursor)
            
    def mouseReleaseEvent(self, event: QMouseEvent):
        """Handle mouse release"""
        self.dragging = False
        self.resizing = False
        self.setCursor(Qt.CursorShape.ArrowCursor)
        
    def mouseDoubleClickEvent(self, event: QMouseEvent):
        """Handle double click to show main window"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.show_main_window.emit()
            
    def enterEvent(self, event):
        """Handle mouse enter - check for resize cursor"""
        super().enterEvent(event)
        
    def leaveEvent(self, event):
        """Handle mouse leave"""
        if not self.dragging and not self.resizing:
            self.setCursor(Qt.CursorShape.ArrowCursor)
            
    def setValue(self, value: int):
        """Set progress value"""
        self.progress.setValue(value)
        
    def setMaxValue(self, max_value: int):
        """Set maximum progress value"""
        self.progress.setMaxValue(max_value)
        
    def setColor(self, color: QColor):
        """Set progress color"""
        self.progress.setColor(color)
        
    def setStartPauseText(self, text: str):
        """Set start/pause button state and update icon"""
        self.current_state = text
        self.update_start_pause_button()
        
    def setMinimumSize(self, size: QSize):
        """Set minimum size"""
        self.min_size = size
        super().setMinimumSize(size)
        
    def sizeHint(self):
        """Return preferred size"""
        return QSize(180, 200)
        
    def resizeEvent(self, event):
        """Handle resize event to update progress widget"""
        super().resizeEvent(event)
        
        # Update progress widget font size based on widget size
        if hasattr(self, 'progress'):
            size = min(self.width(), self.height())
            font_size = max(12, int(size * 0.08))
            self.progress.setFontSize(font_size)
            
        # Update button icon sizes based on widget size
        if hasattr(self, 'start_pause_btn') and hasattr(self, 'reset_btn'):
            # Calculate button size based on widget size (minimum 24x24, maximum 40x40)
            button_size = max(24, min(40, int(min(self.width(), self.height()) * 0.15)))
            self.start_pause_btn.setFixedSize(button_size, button_size)
            self.reset_btn.setFixedSize(button_size, button_size)
            
            # Update border radius to match button size
            border_radius = button_size // 2
            
            # Update start/pause button style with new size
            self.update_start_pause_button()
            
            # Update reset button style with new size
            self.reset_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: #f44336;
                    border: none;
                    border-radius: {border_radius}px;
                    color: white;
                    font-size: 14px;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background-color: #da190b;
                }}
            """)
            
    def set_session_type(self, session_type: str):
        """Set current session type for theme-aware styling"""
        # This can be used to change colors based on work/break sessions
        if session_type == "work":
            work_color = self.config_manager.get("work_color", "#34a853")
            self.setColor(QColor(work_color))
        else:  # break
            break_color = self.config_manager.get("break_color", "#4285f4")
            self.setColor(QColor(break_color))