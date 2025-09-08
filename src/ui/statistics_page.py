"""
Statistics page for Pomodoro Timer application
"""

import sys
from pathlib import Path
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                            QLabel, QFrame, QGridLayout, QGroupBox,
                            QFileDialog, QMessageBox)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QIcon, QPixmap, QFont
import pyqtgraph as pg
from utils.constants import CHART_Y_MAX, CHART_Y_STEP

class StatisticsPage(QWidget):
    """Statistics and analytics page"""
    
    # Signals
    back_clicked = pyqtSignal()
    
    def __init__(self, config_manager, data_manager):
        super().__init__()
        self.config_manager = config_manager
        self.data_manager = data_manager
        
        self.init_ui()
        self.refresh_data()
        
    def init_ui(self):
        """Initialize the user interface"""
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Header with back button
        header_layout = QHBoxLayout()
        
        self.back_btn = QPushButton()
        self.back_btn.setFixedSize(50, 50)
        self.back_btn.setIcon(self.load_icon("back.png", "←"))
        self.back_btn.setToolTip("Back to Timer")
        self.back_btn.clicked.connect(self.back_clicked.emit)
        header_layout.addWidget(self.back_btn)
        
        header_layout.addStretch()
        
        title_label = QLabel("Statistics")
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
        
        # Statistics cards
        stats_container = self.create_stats_cards()
        layout.addWidget(stats_container)
        
        # Weekly chart
        chart_container = self.create_chart_container()
        layout.addWidget(chart_container, 1)  # Give chart more space
        
        # Export buttons
        export_layout = QHBoxLayout()
        
        self.export_csv_btn = QPushButton("Export to CSV")
        self.export_csv_btn.clicked.connect(self.export_to_csv)
        self.export_csv_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                padding: 10px 20px;
                font-size: 14px;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        export_layout.addWidget(self.export_csv_btn)
        
        self.export_chart_btn = QPushButton("Save Chart")
        self.export_chart_btn.clicked.connect(self.save_chart)
        self.export_chart_btn.setStyleSheet("""
            QPushButton {
                background-color: #FF9800;
                color: white;
                padding: 10px 20px;
                font-size: 14px;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #F57C00;
            }
        """)
        export_layout.addWidget(self.export_chart_btn)
        
        export_layout.addStretch()
        
        refresh_btn = QPushButton("Refresh Data")
        refresh_btn.clicked.connect(self.refresh_data)
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 10px 20px;
                font-size: 14px;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        export_layout.addWidget(refresh_btn)
        
        layout.addLayout(export_layout)
        
        self.setLayout(layout)
        
    def create_stats_cards(self) -> QWidget:
        """Create statistics cards container"""
        container = QFrame()
        container.setFrameStyle(QFrame.Shape.Box)
        container.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 8px;
                padding: 15px;
            }
        """)
        
        layout = QGridLayout()
        layout.setSpacing(20)
        
        # Create stat cards
        self.total_sessions_card = self.create_stat_card("Total Sessions", "0", "#4CAF50")
        self.total_focus_time_card = self.create_stat_card("Focus Time", "0 min", "#2196F3")
        self.average_session_card = self.create_stat_card("Avg Session", "0 min", "#FF9800")
        self.current_streak_card = self.create_stat_card("Current Streak", "0 days", "#9C27B0")
        
        # Add cards to grid
        layout.addWidget(self.total_sessions_card, 0, 0)
        layout.addWidget(self.total_focus_time_card, 0, 1)
        layout.addWidget(self.average_session_card, 1, 0)
        layout.addWidget(self.current_streak_card, 1, 1)
        
        container.setLayout(layout)
        return container
        
    def create_stat_card(self, title: str, value: str, color: str) -> QFrame:
        """Create a single statistics card"""
        card = QFrame()
        card.setFixedHeight(100)
        card.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border-left: 4px solid {color};
                border-radius: 6px;
                padding: 10px;
            }}
        """)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(15, 10, 15, 10)
        
        # Title
        title_label = QLabel(title)
        title_label.setStyleSheet("""
            QLabel {
                font-size: 12px;
                color: #6c757d;
                font-weight: bold;
                margin-bottom: 5px;
            }
        """)
        layout.addWidget(title_label)
        
        # Value
        value_label = QLabel(value)
        value_label.setStyleSheet(f"""
            QLabel {{
                font-size: 24px;
                color: {color};
                font-weight: bold;
            }}
        """)
        layout.addWidget(value_label)
        
        card.setLayout(layout)
        
        # Store value label for updates
        card.value_label = value_label
        
        return card
        
    def create_chart_container(self) -> QWidget:
        """Create chart container with weekly focus time"""
        container = QGroupBox("Weekly Focus Time")
        container.setStyleSheet("""
            QGroupBox {
                font-size: 16px;
                font-weight: bold;
                color: #333333;
                border: 2px solid #dee2e6;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 20px;
                padding: 0 10px 0 10px;
                background-color: white;
            }
        """)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(15, 20, 15, 15)
        
        # Create plot widget
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setBackground('w')  # White background
        self.plot_widget.setMinimumHeight(300)
        
        # Configure plot
        self.plot_widget.setLabel('left', 'Minutes', color='#333', size='12pt')
        self.plot_widget.setLabel('bottom', 'Day of Week', color='#333', size='12pt')
        self.plot_widget.showGrid(x=True, y=True, alpha=0.3)
        
        # Set Y-axis range and ticks (0-60 minutes in 5-minute intervals)
        self.plot_widget.setYRange(0, CHART_Y_MAX, padding=0.05)
        y_ticks = [(i, str(i)) for i in range(0, CHART_Y_MAX + 1, CHART_Y_STEP)]
        self.plot_widget.getAxis('left').setTicks([y_ticks])
        
        # Style the plot
        self.plot_widget.getAxis('left').setPen(color='#333', width=1)
        self.plot_widget.getAxis('bottom').setPen(color='#333', width=1)
        self.plot_widget.getAxis('left').setTextPen(color='#333')
        self.plot_widget.getAxis('bottom').setTextPen(color='#333')
        
        layout.addWidget(self.plot_widget)
        container.setLayout(layout)
        
        return container
        
    def load_icon(self, filename: str, fallback: str) -> QIcon:
        """Load icon from resources with fallback"""
        try:
            if hasattr(sys, '_MEIPASS'):
                icon_path = Path(sys._MEIPASS) / "resources" / "icons" / filename
            else:
                icon_path = Path(__file__).parent.parent.parent / "resources" / "icons" / filename
                
            if icon_path.exists() and icon_path.stat().st_size > 0:
                return QIcon(str(icon_path))
        except Exception as e:
            print(f"Error loading icon {filename}: {e}")
            
        # Create fallback text icon
        pixmap = QPixmap(32, 32)
        pixmap.fill(Qt.GlobalColor.transparent)
        return QIcon(pixmap)
        
    def refresh_data(self):
        """Refresh all statistics and chart data"""
        self.update_stats_cards()
        self.update_weekly_chart()
        
    def update_stats_cards(self):
        """Update statistics cards with current data"""
        try:
            monthly_stats = self.data_manager.get_monthly_stats()
            
            # Update card values
            self.total_sessions_card.value_label.setText(str(monthly_stats["total_sessions"]))
            self.total_focus_time_card.value_label.setText(f"{monthly_stats['total_focus_time']} min")
            self.average_session_card.value_label.setText(f"{monthly_stats['average_session_length']:.1f} min")
            self.current_streak_card.value_label.setText(f"{monthly_stats['current_streak']} days")
            
        except Exception as e:
            print(f"Error updating stats cards: {e}")
            # Set default values on error
            self.total_sessions_card.value_label.setText("0")
            self.total_focus_time_card.value_label.setText("0 min")
            self.average_session_card.value_label.setText("0 min")
            self.current_streak_card.value_label.setText("0 days")
            
    def update_weekly_chart(self):
        """Update weekly focus time chart"""
        try:
            self.plot_widget.clear()
            
            # Get weekly data
            weekly_data = self.data_manager.get_weekly_data()
            
            if not weekly_data:
                return
                
            days = list(weekly_data.keys())
            values = list(weekly_data.values())
            
            # Create bar graph
            x_positions = list(range(len(days)))
            
            # Create bar chart with custom styling
            bar_brush = pg.mkBrush(color='#4CAF50')
            bar_pen = pg.mkPen(color='#2E7D32', width=2)
            
            bargraph = pg.BarGraphItem(
                x=x_positions, 
                height=values, 
                width=0.6, 
                brush=bar_brush,
                pen=bar_pen
            )
            
            self.plot_widget.addItem(bargraph)
            
            # Set X-axis labels
            x_ticks = [(i, days[i]) for i in range(len(days))]
            self.plot_widget.getAxis('bottom').setTicks([x_ticks])
            
            # Add value labels on top of bars
            for i, value in enumerate(values):
                if value > 0:
                    text_item = pg.TextItem(
                        text=str(value), 
                        anchor=(0.5, 1.2),
                        color='#333'
                    )
                    text_item.setPos(i, value)
                    self.plot_widget.addItem(text_item)
                    
        except Exception as e:
            print(f"Error updating weekly chart: {e}")
            
    def export_to_csv(self):
        """Export all session data to CSV"""
        try:
            file_path, _ = QFileDialog.getSaveFileName(
                self, 
                "Export Session Data", 
                "pomodoro_sessions_export.csv",
                "CSV Files (*.csv)"
            )
            
            if file_path:
                if self.data_manager.export_all_data(file_path):
                    QMessageBox.information(
                        self, 
                        "Export Success", 
                        f"Session data exported successfully to:\n{file_path}"
                    )
                else:
                    QMessageBox.warning(
                        self,
                        "Export Failed",
                        "No data found to export or export operation failed."
                    )
                    
        except Exception as e:
            QMessageBox.critical(
                self,
                "Export Error",
                f"An error occurred during export:\n{str(e)}"
            )
            
    def save_chart(self):
        """Save the weekly chart as an image"""
        try:
            file_path, _ = QFileDialog.getSaveFileName(
                self, 
                "Save Chart", 
                "weekly_focus_chart.png",
                "PNG Files (*.png);;JPG Files (*.jpg)"
            )
            
            if file_path:
                exporter = pg.exporters.ImageExporter(self.plot_widget.plotItem)
                exporter.parameters()['width'] = 1200
                exporter.parameters()['height'] = 800
                exporter.export(file_path)
                
                QMessageBox.information(
                    self, 
                    "Save Success", 
                    f"Chart saved successfully to:\n{file_path}"
                )
                
        except Exception as e:
            QMessageBox.critical(
                self,
                "Save Error",
                f"An error occurred while saving the chart:\n{str(e)}"
            )
            
    def resizeEvent(self, event):
    """Handle resize event"""
    super().resizeEvent(event)
    
    # Update chart size and font based on window size
    if hasattr(self, 'plot_widget'):
        width = self.width()
        height = self.height()
        
        # Adjust chart height based on available space
        if width < 600:
            self.plot_widget.setMinimumHeight(200)
            self.plot_widget.setMaximumHeight(250)
        elif width < 800:
            self.plot_widget.setMinimumHeight(250)
            self.plot_widget.setMaximumHeight(300)
        else:
            self.plot_widget.setMinimumHeight(300)
            self.plot_widget.setMaximumHeight(400)
        
        # Update font sizes based on window size
        title_font_size = max(12, min(16, width // 50))
        label_font_size = max(9, min(12, width // 70))
        
        # Update plot font sizes if plot exists
        plot_item = self.plot_widget.getPlotItem()
        if plot_item:
            # Update axis font sizes
            plot_item.getAxis('left').setStyle(tickFont=QFont('Arial', label_font_size))
            plot_item.getAxis('bottom').setStyle(tickFont=QFont('Arial', label_font_size))
            
            # Update title font size
            plot_item.setTitle(plot_item.titleLabel.text, size=f"{title_font_size}pt")
    
    # Update stats cards layout if they exist
    if hasattr(self, 'stats_layout') and self.stats_layout:
        # Adjust spacing based on window width
        if width < 600:
            self.stats_layout.setSpacing(5)
        else:
            self.stats_layout.setSpacing(10)
    
    # Update summary cards font sizes
    for i in range(getattr(self, 'summary_layout', QHBoxLayout()).count()):
        item = self.summary_layout.itemAt(i)
        if item and item.widget():
            card = item.widget()
            if hasattr(card, 'findChildren'):
                labels = card.findChildren(QLabel)
                for label in labels:
                    current_font = label.font()
                    if 'value' in label.objectName().lower():
                        # Value labels get larger font
                        current_font.setPointSize(max(14, min(20, width // 40)))
                    else:
                        # Regular labels get smaller font
                        current_font.setPointSize(max(10, min(14, width // 60)))
                    label.setFont(current_font)