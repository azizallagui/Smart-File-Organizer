"""
UndoManager module for Smart File Organizer
Manages undo operations for file movements
"""

import shutil
from pathlib import Path
from typing import List, Dict, Any
from logger import Logger


class UndoManager:
    """Manages undo operations for file movements"""
    
    def __init__(self, logger: Logger):
        self.logger = logger
        self.current_operations = []
    
    def add_operation(self, source: str, destination: str, operation_type: str = "move"):
        """Add an operation to the current batch"""
        operation = {
            'source': source,
            'destination': destination,
            'type': operation_type
        }
        self.current_operations.append(operation)
    
    def commit_operations(self):
        """Save current operations batch for undo and clear the batch"""
        if self.current_operations:
            self.logger.save_undo_data(self.current_operations)
            self.current_operations = []
    
    def can_undo(self) -> bool:
        """Check if undo operation is possible"""
        undo_data = self.logger.load_undo_data()
        return bool(undo_data.get('operations', []))
    
    def undo_last_operation(self) -> tuple[bool, str]:
        """
        Undo the last batch of operations
        Returns: (success: bool, message: str)
        """
        undo_data = self.logger.load_undo_data()
        operations = undo_data.get('operations', [])
        
        if not operations:
            return False, "No operations to undo"
        
        success_count = 0
        error_count = 0
        errors = []
        
        # Reverse the operations to undo them
        for operation in reversed(operations):
            try:
                source = Path(operation['source'])
                destination = Path(operation['destination'])
                
                if operation['type'] == 'move' and destination.exists():
                    # Move file back to original location
                    # Ensure the source directory exists
                    source.parent.mkdir(parents=True, exist_ok=True)
                    
                    # Handle name conflicts
                    if source.exists():
                        source = self._get_unique_filename(source)
                    
                    shutil.move(str(destination), str(source))
                    self.logger.log_operation(
                        str(destination), str(source), "undo", "success"
                    )
                    success_count += 1
                else:
                    error_msg = f"Cannot undo: {destination} does not exist"
                    errors.append(error_msg)
                    self.logger.log_error(error_msg)
                    error_count += 1
                    
            except Exception as e:
                error_msg = f"Error undoing operation {operation}: {str(e)}"
                errors.append(error_msg)
                self.logger.log_error(error_msg, e)
                error_count += 1
        
        # Clear undo data after attempting undo
        self.logger.clear_undo_data()
        
        if error_count == 0:
            message = f"Successfully undone {success_count} operations"
            return True, message
        elif success_count > 0:
            message = f"Partially undone: {success_count} successful, {error_count} failed"
            return True, message
        else:
            message = f"Undo failed: {error_count} errors"
            return False, message
    
    def _get_unique_filename(self, filepath: Path) -> Path:
        """Generate a unique filename if the target already exists"""
        if not filepath.exists():
            return filepath
        
        base = filepath.stem
        suffix = filepath.suffix
        parent = filepath.parent
        counter = 1
        
        while True:
            new_name = f"{base}_restored_{counter}{suffix}"
            new_path = parent / new_name
            if not new_path.exists():
                return new_path
            counter += 1
    
    def clear_current_operations(self):
        """Clear the current operations batch without committing"""
        self.current_operations = []
    
    def get_operations_count(self) -> int:
        """Get the number of operations in the current batch"""
        return len(self.current_operations)
