"""
Timer logic and state management
"""

from PyQt6.QtCore import QObject, QTimer, pyqtSignal
from typing import Optional
from utils.constants import (TIMER_STATE_WORK, TIMER_STATE_BREAK, TIMER_STATE_LONG_BREAK,
                           TIMER_STATE_PAUSED, TIMER_STATE_STOPPED)

class TimerLogic(QObject):
    """Core timer logic with state management"""
    
    # Signals
    timer_updated = pyqtSignal(int)  # remaining_seconds
    timer_finished = pyqtSignal(str)  # timer_type
    state_changed = pyqtSignal(str)   # new_state
    session_completed = pyqtSignal()
    
    def __init__(self, config_manager):
        super().__init__()
        self.config_manager = config_manager
        
        # Timer state
        self.current_state = TIMER_STATE_STOPPED
        self.remaining_time = 0
        self.sessions_completed = 0
        self.sessions_until_long_break = 0
        
        # Qt Timer
        self.qt_timer = QTimer()
        self.qt_timer.timeout.connect(self._on_timer_tick)
        
        self.reset_timer()
        
    def reset_timer(self) -> None:
        """Reset timer to initial work state"""
        self.qt_timer.stop()
        self.current_state = TIMER_STATE_STOPPED
        self.remaining_time = self.config_manager.get_work_time_seconds()
        self.sessions_until_long_break = self.config_manager.get("sessions_until_long_break", 4)
        self.timer_updated.emit(self.remaining_time)
        self.state_changed.emit(self.current_state)
        
    def start_timer(self) -> None:
        """Start or resume the timer"""
        if self.current_state == TIMER_STATE_STOPPED:
            # Starting fresh work session
            self.current_state = TIMER_STATE_WORK
            self.remaining_time = self.config_manager.get_work_time_seconds()
        elif self.current_state == TIMER_STATE_PAUSED:
            # Resume from pause
            if self._is_work_session():
                self.current_state = TIMER_STATE_WORK
            elif self._is_break_session():
                self.current_state = TIMER_STATE_BREAK
            else:
                self.current_state = TIMER_STATE_LONG_BREAK
                
        self.qt_timer.start(1000)  # Update every second
        self.state_changed.emit(self.current_state)
        
    def pause_timer(self) -> None:
        """Pause the timer"""
        if self.qt_timer.isActive():
            self.qt_timer.stop()
            self.current_state = TIMER_STATE_PAUSED
            self.state_changed.emit(self.current_state)
            
    def stop_timer(self) -> None:
        """Stop and reset the timer"""
        self.qt_timer.stop()
        self.reset_timer()
        
    def skip_session(self) -> None:
        """Skip current session and move to next"""
        self._on_timer_finished()
        
    def _on_timer_tick(self) -> None:
        """Handle timer tick (every second)"""
        if self.remaining_time > 0:
            self.remaining_time -= 1
            self.timer_updated.emit(self.remaining_time)
        else:
            self._on_timer_finished()
            
    def _on_timer_finished(self) -> None:
        """Handle timer completion"""
        self.qt_timer.stop()
        
        if self.current_state == TIMER_STATE_WORK:
            # Work session completed
            self.sessions_completed += 1
            self.sessions_until_long_break -= 1
            self.session_completed.emit()
            self.timer_finished.emit("work")
            
            # Auto-start break if enabled
            if self.config_manager.get("auto_start_breaks", True):
                self._start_break_timer()
            else:
                self._prepare_break_timer()
                
        elif self.current_state in [TIMER_STATE_BREAK, TIMER_STATE_LONG_BREAK]:
            # Break completed
            self.timer_finished.emit("break")
            
            # Auto-start work if enabled
            if self.config_manager.get("auto_start_work", False):
                self._start_work_timer()
            else:
                self._prepare_work_timer()
                
    def _start_break_timer(self) -> None:
        """Start break timer automatically"""
        if self.sessions_until_long_break <= 0:
            # Time for long break
            self.current_state = TIMER_STATE_LONG_BREAK
            self.remaining_time = self.config_manager.get_long_break_time_seconds()
            self.sessions_until_long_break = self.config_manager.get("sessions_until_long_break", 4)
        else:
            # Regular break
            self.current_state = TIMER_STATE_BREAK
            self.remaining_time = self.config_manager.get_break_time_seconds()
            
        self.qt_timer.start(1000)
        self.timer_updated.emit(self.remaining_time)
        self.state_changed.emit(self.current_state)
        
    def _prepare_break_timer(self) -> None:
        """Prepare break timer without starting"""
        if self.sessions_until_long_break <= 0:
            self.current_state = TIMER_STATE_STOPPED
            self.remaining_time = self.config_manager.get_long_break_time_seconds()
            self.sessions_until_long_break = self.config_manager.get("sessions_until_long_break", 4)
        else:
            self.current_state = TIMER_STATE_STOPPED
            self.remaining_time = self.config_manager.get_break_time_seconds()
            
        self.timer_updated.emit(self.remaining_time)
        self.state_changed.emit(self.current_state)
        
    def _start_work_timer(self) -> None:
        """Start work timer automatically"""
        self.current_state = TIMER_STATE_WORK
        self.remaining_time = self.config_manager.get_work_time_seconds()
        self.qt_timer.start(1000)
        self.timer_updated.emit(self.remaining_time)
        self.state_changed.emit(self.current_state)
        
    def _prepare_work_timer(self) -> None:
        """Prepare work timer without starting"""
        self.current_state = TIMER_STATE_STOPPED
        self.remaining_time = self.config_manager.get_work_time_seconds()
        self.timer_updated.emit(self.remaining_time)
        self.state_changed.emit(self.current_state)
        
    def _is_work_session(self) -> bool:
        """Check if current session is work"""
        return self.current_state == TIMER_STATE_WORK
        
    def _is_break_session(self) -> bool:
        """Check if current session is break"""
        return self.current_state in [TIMER_STATE_BREAK, TIMER_STATE_LONG_BREAK]
        
    def is_running(self) -> bool:
        """Check if timer is currently running"""
        return self.qt_timer.isActive()
        
    def is_paused(self) -> bool:
        """Check if timer is paused"""
        return self.current_state == TIMER_STATE_PAUSED
        
    def get_current_state(self) -> str:
        """Get current timer state"""
        return self.current_state
        
    def get_remaining_time(self) -> int:
        """Get remaining time in seconds"""
        return self.remaining_time
        
    def get_sessions_completed(self) -> int:
        """Get number of completed sessions"""
        return self.sessions_completed
        
    def get_progress_percentage(self) -> float:
        """Get progress as percentage (0-100)"""
        if self.current_state == TIMER_STATE_WORK:
            total_time = self.config_manager.get_work_time_seconds()
        elif self.current_state == TIMER_STATE_BREAK:
            total_time = self.config_manager.get_break_time_seconds()
        elif self.current_state == TIMER_STATE_LONG_BREAK:
            total_time = self.config_manager.get_long_break_time_seconds()
        else:
            total_time = self.config_manager.get_work_time_seconds()
            
        if total_time == 0:
            return 0.0
            
        elapsed_time = total_time - self.remaining_time
        return (elapsed_time / total_time) * 100.0