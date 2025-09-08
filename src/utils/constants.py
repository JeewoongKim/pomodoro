"""
Constants for the Pomodoro Timer application
"""

# Default configuration values
DEFAULT_CONFIG = {
    "work_time": 25,      # minutes
    "break_time": 5,      # minutes
    "long_break_time": 15,  # minutes
    "sessions_until_long_break": 4,
    "font_size": 14,
    "work_color": "#34a853",
    "break_color": "#4285f4",
    "bg_color": "#f0f0f0",
    "auto_start_breaks": True,
    "auto_start_work": False,
    "sound_enabled": True,
    "notifications_enabled": True,
    "widget_style": "circular"
}

# UI Constants
MIN_WINDOW_WIDTH = 400
MIN_WINDOW_HEIGHT = 500
DEFAULT_WINDOW_WIDTH = 450
DEFAULT_WINDOW_HEIGHT = 600

# Timer states
TIMER_STATE_WORK = "work"
TIMER_STATE_BREAK = "break"
TIMER_STATE_LONG_BREAK = "long_break"
TIMER_STATE_PAUSED = "paused"
TIMER_STATE_STOPPED = "stopped"

# File extensions
DATA_FILE_EXTENSION = ".csv"
CONFIG_FILE_EXTENSION = ".json"

# Chart settings
CHART_Y_MAX = 60  # minutes
CHART_Y_STEP = 5  # 5-minute intervals
CHART_DAYS = 7    # week view

# Animation durations (milliseconds)
FADE_DURATION = 300
SLIDE_DURATION = 250

# Icon sizes
SMALL_ICON_SIZE = 20
MEDIUM_ICON_SIZE = 32
LARGE_ICON_SIZE = 48
