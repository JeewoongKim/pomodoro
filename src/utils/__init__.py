"""
Utilities Module

Contains utility functions, constants, and system integration features.
"""

from .constants import *
from .system_tray import SystemTray
from .icon_manager import IconManager, icon_manager

__all__ = ['SystemTray', 'IconManager', 'icon_manager']
