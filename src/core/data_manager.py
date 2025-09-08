"""
Data management for Pomodoro Timer sessions and statistics
"""

import csv
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from PyQt6.QtCore import QObject, pyqtSignal

class DataManager(QObject):
    """Manages session data storage and statistics"""
    
    data_updated = pyqtSignal()
    
    def __init__(self, config_manager):
        super().__init__()
        self.config_manager = config_manager
        self.data_dir = config_manager.get_data_directory()
        
    def save_session(self, session_type: str, duration_minutes: int) -> None:
        """Save a completed session"""
        today = datetime.now()
        data_file = self.data_dir / f"sessions_{today.year}_{today.month:02d}.csv"
        
        # Create file with headers if it doesn't exist
        if not data_file.exists():
            with open(data_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(["Date", "Time", "Duration (minutes)", "Type"])
                
        # Append session data
        try:
            with open(data_file, 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([
                    today.strftime("%Y-%m-%d"),
                    today.strftime("%H:%M:%S"),
                    duration_minutes,
                    session_type.title()
                ])
            self.data_updated.emit()
        except Exception as e:
            print(f"Error saving session data: {e}")
            
    def get_weekly_data(self) -> Dict[str, int]:
        """Get weekly focus data for current week"""
        today = datetime.now()
        week_start = today - timedelta(days=today.weekday())
        
        weekly_data = {}
        for i in range(7):
            day = week_start + timedelta(days=i)
            weekly_data[day.strftime("%a")] = 0
            
        # Read data from current month's file
        data_file = self.data_dir / f"sessions_{today.year}_{today.month:02d}.csv"
        if data_file.exists():
            try:
                with open(data_file, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        try:
                            session_date = datetime.strptime(row["Date"], "%Y-%m-%d")
                            if week_start <= session_date <= today:
                                day_name = session_date.strftime("%a")
                                if day_name in weekly_data and row["Type"].lower() == "work":
                                    weekly_data[day_name] += int(float(row["Duration (minutes)"]))
                        except (ValueError, KeyError) as e:
                            print(f"Error parsing row {row}: {e}")
                            continue
            except Exception as e:
                print(f"Error reading weekly data: {e}")
                
        return weekly_data
        
    def get_monthly_stats(self) -> Dict[str, any]:
        """Get monthly statistics"""
        today = datetime.now()
        month_start = today.replace(day=1)
        
        stats = {
            "total_sessions": 0,
            "total_focus_time": 0,
            "total_break_time": 0,
            "average_session_length": 0,
            "most_productive_day": "N/A",
            "current_streak": 0
        }
        
        data_file = self.data_dir / f"sessions_{today.year}_{today.month:02d}.csv"
        if not data_file.exists():
            return stats
            
        try:
            daily_sessions = {}
            with open(data_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    try:
                        session_date = datetime.strptime(row["Date"], "%Y-%m-%d")
                        if session_date >= month_start:
                            session_type = row["Type"].lower()
                            duration = int(float(row["Duration (minutes)"]))
                            
                            stats["total_sessions"] += 1
                            
                            if session_type == "work":
                                stats["total_focus_time"] += duration
                                
                                # Track daily sessions for productivity
                                date_str = session_date.strftime("%Y-%m-%d")
                                if date_str not in daily_sessions:
                                    daily_sessions[date_str] = 0
                                daily_sessions[date_str] += duration
                            else:
                                stats["total_break_time"] += duration
                                
                    except (ValueError, KeyError) as e:
                        print(f"Error parsing row {row}: {e}")
                        continue
                        
            # Calculate average session length
            if stats["total_sessions"] > 0:
                total_time = stats["total_focus_time"] + stats["total_break_time"]
                stats["average_session_length"] = total_time / stats["total_sessions"]
                
            # Find most productive day
            if daily_sessions:
                most_productive_date = max(daily_sessions, key=daily_sessions.get)
                most_productive_day = datetime.strptime(most_productive_date, "%Y-%m-%d")
                stats["most_productive_day"] = most_productive_day.strftime("%A, %B %d")
                
            # Calculate current streak (consecutive days with sessions)
            stats["current_streak"] = self._calculate_current_streak(daily_sessions)
            
        except Exception as e:
            print(f"Error calculating monthly stats: {e}")
            
        return stats
        
    def _calculate_current_streak(self, daily_sessions: Dict[str, int]) -> int:
        """Calculate current streak of consecutive days with sessions"""
        if not daily_sessions:
            return 0
            
        today = datetime.now().date()
        current_streak = 0
        
        # Check each day backwards from today
        for days_back in range(len(daily_sessions) + 1):
            check_date = today - timedelta(days=days_back)
            date_str = check_date.strftime("%Y-%m-%d")
            
            if date_str in daily_sessions and daily_sessions[date_str] > 0:
                current_streak += 1
            else:
                break
                
        return current_streak
        
    def export_all_data(self, file_path: str) -> bool:
        """Export all session data to a single CSV file"""
        try:
            all_data = []
            
            # Collect data from all monthly files
            for csv_file in self.data_dir.glob("sessions_*.csv"):
                with open(csv_file, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    all_data.extend(list(reader))
                    
            if not all_data:
                return False
                
            # Sort by date and time
            all_data.sort(key=lambda x: f"{x['Date']} {x['Time']}")
            
            # Write combined data
            with open(file_path, 'w', newline='', encoding='utf-8') as f:
                if all_data:
                    writer = csv.DictWriter(f, fieldnames=all_data[0].keys())
                    writer.writeheader()
                    writer.writerows(all_data)
                    
            return True
            
        except Exception as e:
            print(f"Error exporting data: {e}")
            return False
            
    def get_data_files(self) -> List[Path]:
        """Get list of all data files"""
        return list(self.data_dir.glob("sessions_*.csv"))
        
    def cleanup_old_data(self, months_to_keep: int = 12) -> None:
        """Clean up data files older than specified months"""
        if months_to_keep <= 0:
            return
            
        cutoff_date = datetime.now() - timedelta(days=months_to_keep * 30)
        
        for data_file in self.get_data_files():
            try:
                # Extract date from filename: sessions_YYYY_MM.csv
                filename = data_file.stem
                parts = filename.split('_')
                if len(parts) >= 3:
                    year = int(parts[1])
                    month = int(parts[2])
                    file_date = datetime(year, month, 1)
                    
                    if file_date < cutoff_date:
                        data_file.unlink()
                        print(f"Cleaned up old data file: {data_file}")
                        
            except (ValueError, IndexError) as e:
                print(f"Error processing file {data_file}: {e}")
