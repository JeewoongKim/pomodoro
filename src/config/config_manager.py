"""
Configuration manager for Pomodoro Timer
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional
from utils.constants import DEFAULT_CONFIG

class ConfigManager:
    """Manages application configuration"""
    
    def __init__(self):
        self.config_dir = Path.home() / ".pomodoro"
        self.config_file = self.config_dir / "config.json"
        self.data_dir = Path.home() / "PomodoroData"
        
        self._config = DEFAULT_CONFIG.copy()
        self.load_config()
        
        # Ensure data directory exists
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
    def load_config(self) -> None:
        """Load configuration from file"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    saved_config = json.load(f)
                    self._config.update(saved_config)
            except Exception as e:
                print(f"Error loading config: {e}")
                # Keep default config if loading fails
                
    def save_config(self) -> None:
        """Save configuration to file"""
        try:
            self.config_dir.mkdir(parents=True, exist_ok=True)
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self._config, f, indent=2)
        except Exception as e:
            print(f"Error saving config: {e}")
            
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        return self._config.get(key, default)
        
    def set(self, key: str, value: Any) -> None:
        """Set configuration value"""
        self._config[key] = value
        
    def update(self, config_dict: Dict[str, Any]) -> None:
        """Update multiple configuration values"""
        self._config.update(config_dict)
        
    def get_all(self) -> Dict[str, Any]:
        """Get all configuration values"""
        return self._config.copy()
        
    def reset_to_defaults(self) -> None:
        """Reset configuration to default values"""
        self._config = DEFAULT_CONFIG.copy()
        
    def get_data_directory(self) -> Path:
        """Get data directory path"""
        data_dir = self.get("data_dir")
        if data_dir:
            return Path(data_dir)
        return self.data_dir
        
    def set_data_directory(self, path: str) -> None:
        """Set data directory path"""
        self.set("data_dir", path)
        self.data_dir = Path(path)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
    def get_work_time_seconds(self) -> int:
        """Get work time in seconds"""
        return self.get("work_time", 25) * 60
        
    def get_break_time_seconds(self) -> int:
        """Get break time in seconds"""
        return self.get("break_time", 5) * 60
        
    def get_long_break_time_seconds(self) -> int:
        """Get long break time in seconds"""
        return self.get("long_break_time", 15) * 60
