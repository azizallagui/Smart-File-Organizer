"""
Logger module for Smart File Organizer
Handles logging of file operations for tracking and undo functionality
"""

import csv
import json
import datetime
from pathlib import Path
from typing import List, Dict, Any


class Logger:
    """Handles logging of file operations"""
    
    def __init__(self, log_dir: str = "logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        # Log files
        self.log_file = self.log_dir / "file_operations.log"
        self.csv_log = self.log_dir / "moved_files.csv"
        self.undo_file = self.log_dir / "undo_data.json"
        
        # Initialize CSV if it doesn't exist
        self._init_csv_log()
    
    def _init_csv_log(self):
        """Initialize CSV log file with headers if it doesn't exist"""
        if not self.csv_log.exists():
            with open(self.csv_log, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(['Timestamp', 'Source', 'Destination', 'Operation', 'Status'])
    
    def log_operation(self, source: str, destination: str, operation: str = "move", status: str = "success"):
        """Log a file operation"""
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Log to text file
        with open(self.log_file, 'a', encoding='utf-8') as file:
            file.write(f"[{timestamp}] {operation.upper()}: {source} -> {destination} ({status})\n")
        
        # Log to CSV
        with open(self.csv_log, 'a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow([timestamp, source, destination, operation, status])
    
    def log_error(self, message: str, error: Exception = None):
        """Log an error message"""
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        error_msg = f"[{timestamp}] ERROR: {message}"
        if error:
            error_msg += f" - {str(error)}"
        
        with open(self.log_file, 'a', encoding='utf-8') as file:
            file.write(error_msg + "\n")
    
    def save_undo_data(self, operations: List[Dict[str, Any]]):
        """Save operations data for undo functionality"""
        undo_data = {
            'timestamp': datetime.datetime.now().isoformat(),
            'operations': operations
        }
        
        with open(self.undo_file, 'w', encoding='utf-8') as file:
            json.dump(undo_data, file, indent=2)
    
    def load_undo_data(self) -> Dict[str, Any]:
        """Load undo data from file"""
        if not self.undo_file.exists():
            return {}
        
        try:
            with open(self.undo_file, 'r', encoding='utf-8') as file:
                return json.load(file)
        except (json.JSONDecodeError, FileNotFoundError):
            return {}
    
    def clear_undo_data(self):
        """Clear undo data file"""
        if self.undo_file.exists():
            self.undo_file.unlink()
    
    def get_recent_logs(self, limit: int = 10) -> List[str]:
        """Get recent log entries"""
        if not self.log_file.exists():
            return []
        
        try:
            with open(self.log_file, 'r', encoding='utf-8') as file:
                lines = file.readlines()
                return [line.strip() for line in lines[-limit:]]
        except FileNotFoundError:
            return []
