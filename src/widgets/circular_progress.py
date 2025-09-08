"""
Circular progress widget for Pomodoro Timer
"""

from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPainter, QColor, QPen, QFont, QPaintEvent

class CircularProgress(QWidget):
    """Custom widget for circular progress visualization"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.value = 0
        self.max_value = 100
        self.thickness = 12
        self.color = QColor(52, 168, 83)  # Green
        self.bg_color = QColor(240, 240, 240)
        self.text_color = QColor(50, 50, 50)
        self.font_size = 24
        self.setMinimumSize(150, 150)
        
    def setValue(self, value: int) -> None:
        """Set current progress value"""
        self.value = max(0, min(value, self.max_value))
        self.update()
        
    def setMaxValue(self, max_value: int) -> None:
        """Set maximum progress value"""
        self.max_value = max(1, max_value)
        self.update()
        
    def setColor(self, color: QColor) -> None:
        """Set progress color"""
        self.color = color
        self.update()
        
    def setFontSize(self, size: int) -> None:
        """Set font size for time display"""
        self.font_size = size
        self.update()
        
    def setThickness(self, thickness: int) -> None:
        """Set progress bar thickness"""
        self.thickness = max(1, thickness)
        self.update()
        
    def sizeHint(self):
        """Return preferred size"""
        return self.size()
        
    def paintEvent(self, event: QPaintEvent) -> None:
        """Paint the circular progress"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Get dimensions and scale thickness based on widget size
        width = self.width()
        height = self.height()
        size = min(width, height)
        scaled_thickness = max(8, int(size * 0.08))  # Scale thickness with size
        
        diameter = size - scaled_thickness * 2
        
        # Center position
        x = (width - diameter) // 2
        y = (height - diameter) // 2
        
        # Draw background circle
        painter.setPen(QPen(self.bg_color, scaled_thickness))
        painter.drawArc(x, y, diameter, diameter, 0, 360 * 16)
        
        # Draw progress arc
        if self.max_value > 0:
            painter.setPen(QPen(self.color, scaled_thickness))
            angle = int(360 * (self.value / self.max_value) * 16)
            painter.drawArc(x, y, diameter, diameter, 90 * 16, -angle)
        
        # Draw time text
        painter.setPen(self.text_color)
        scaled_font_size = max(12, int(size * 0.15))  # Scale font with size
        font = QFont("Arial", scaled_font_size, QFont.Weight.Bold)
        painter.setFont(font)
        
        minutes = int(self.value // 60)
        seconds = int(self.value % 60)
        time_text = f"{minutes:02d}:{seconds:02d}"
        
        text_rect = painter.fontMetrics().boundingRect(time_text)
        text_x = (width - text_rect.width()) // 2
        text_y = (height + text_rect.height()) // 2 - text_rect.height() // 4
        
        painter.drawText(text_x, text_y, time_text)
