"""
FileOrganizer module for Smart File Organizer
Main logic for scanning, organizing, and moving files
"""

import os
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from logger import Logger
from undo_manager import UndoManager


class FileOrganizer:
    """Main class for organizing files by extension"""
    
    # Default file type categories
    FILE_CATEGORIES = {
        # Images
        'Images': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.svg', '.webp', '.ico'],
        
        # Documents
        'Documents': ['.pdf', '.doc', '.docx', '.txt', '.rtf', '.odt', '.pages'],
        
        # Spreadsheets
        'Spreadsheets': ['.xls', '.xlsx', '.csv', '.ods'],
        
        # Presentations
        'Presentations': ['.ppt', '.pptx', '.odp', '.key'],
        
        # Videos
        'Videos': ['.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm', '.m4v'],
        
        # Audio
        'Audio': ['.mp3', '.wav', '.flac', '.aac', '.ogg', '.wma', '.m4a'],
        
        # Archives
        'Archives': ['.zip', '.rar', '.7z', '.tar', '.gz', '.bz2'],
        
        # Code
        'Code': ['.py', '.js', '.html', '.css', '.java', '.cpp', '.c', '.php', '.rb', '.go'],
        
        # Executables
        'Executables': ['.exe', '.msi', '.dmg', '.pkg', '.deb', '.rpm'],
        
        # Others will be put in 'Miscellaneous'
    }
    
    def __init__(self, target_directory: str = None):
        self.target_directory = Path(target_directory) if target_directory else None
        self.logger = Logger()
        self.undo_manager = UndoManager(self.logger)
        self.custom_categories = {}
        
    def set_target_directory(self, directory: str):
        """Set the target directory to organize"""
        self.target_directory = Path(directory)
        if not self.target_directory.exists():
            raise FileNotFoundError(f"Directory does not exist: {directory}")
        if not self.target_directory.is_dir():
            raise NotADirectoryError(f"Path is not a directory: {directory}")
    
    def add_custom_category(self, category_name: str, extensions: List[str]):
        """Add a custom file category"""
        # Ensure extensions start with a dot
        extensions = [ext if ext.startswith('.') else f'.{ext}' for ext in extensions]
        self.custom_categories[category_name] = extensions
    
    def get_file_category(self, file_path: Path) -> str:
        """Determine the category for a file based on its extension"""
        extension = file_path.suffix.lower()
        
        # Check custom categories first
        for category, extensions in self.custom_categories.items():
            if extension in extensions:
                return category
        
        # Check default categories
        for category, extensions in self.FILE_CATEGORIES.items():
            if extension in extensions:
                return category
        
        # Default category for unknown extensions
        return 'Miscellaneous'
    
    def scan_directory(self) -> Dict[str, List[Path]]:
        """
        Scan the target directory and categorize files
        Returns a dictionary with categories as keys and lists of files as values
        """
        if not self.target_directory:
            raise ValueError("Target directory not set")
        
        categorized_files = {}
        
        try:
            # Scan only files in the root directory (not subdirectories)
            for item in self.target_directory.iterdir():
                if item.is_file() and not item.name.startswith('.'):
                    category = self.get_file_category(item)
                    
                    if category not in categorized_files:
                        categorized_files[category] = []
                    
                    categorized_files[category].append(item)
            
            self.logger.log_operation(
                str(self.target_directory), 
                "scan", 
                "scan", 
                f"Found {sum(len(files) for files in categorized_files.values())} files"
            )
            
        except Exception as e:
            self.logger.log_error(f"Error scanning directory {self.target_directory}", e)
            raise
        
        return categorized_files
    
    def create_category_directories(self, categories: List[str]) -> Dict[str, Path]:
        """Create directories for each category"""
        created_dirs = {}
        
        for category in categories:
            category_path = self.target_directory / category
            try:
                # Check if directory exists before creating it
                dir_existed = category_path.exists()
                category_path.mkdir(exist_ok=True)
                created_dirs[category] = category_path
                
                # Log only if we actually created a new directory
                if not dir_existed:
                    self.logger.log_operation(
                        str(self.target_directory), 
                        str(category_path), 
                        "create_dir", 
                        "success"
                    )
            except Exception as e:
                self.logger.log_error(f"Error creating directory {category_path}", e)
                raise
        
        return created_dirs
    
    def move_file_safely(self, source: Path, destination_dir: Path) -> Tuple[bool, str, Optional[Path]]:
        """
        Move a file safely, handling name conflicts
        Returns: (success, message, final_path)
        """
        try:
            destination = destination_dir / source.name
            
            # Handle name conflicts
            if destination.exists():
                destination = self._get_unique_filename(destination)
            
            # Move the file
            final_path = Path(shutil.move(str(source), str(destination)))
            
            # Add to undo manager
            self.undo_manager.add_operation(str(source), str(final_path))
            
            # Log the operation
            self.logger.log_operation(str(source), str(final_path), "move", "success")
            
            return True, f"Moved to {final_path.name}", final_path
            
        except Exception as e:
            error_msg = f"Error moving {source.name}: {str(e)}"
            self.logger.log_error(error_msg, e)
            return False, error_msg, None
    
    def _get_unique_filename(self, filepath: Path) -> Path:
        """Generate a unique filename if the target already exists"""
        base = filepath.stem
        suffix = filepath.suffix
        parent = filepath.parent
        counter = 1
        
        while True:
            new_name = f"{base}_{counter}{suffix}"
            new_path = parent / new_name
            if not new_path.exists():
                return new_path
            counter += 1
    
    def organize_files(self, progress_callback=None) -> Tuple[bool, str, Dict]:
        """
        Organize all files in the target directory
        Returns: (success, message, results_dict)
        """
        if not self.target_directory:
            return False, "Target directory not set", {}
        
        try:
            # Clear any previous operations
            self.undo_manager.clear_current_operations()
            
            # Scan files
            categorized_files = self.scan_directory()
            
            if not categorized_files:
                return True, "No files to organize", {}
            
            # Create category directories
            categories = list(categorized_files.keys())
            category_dirs = self.create_category_directories(categories)
            
            # Move files
            results = {
                'total_files': sum(len(files) for files in categorized_files.values()),
                'moved_files': 0,
                'failed_files': 0,
                'categories': {},
                'errors': []
            }
            
            file_count = 0
            for category, files in categorized_files.items():
                category_results = {'moved': 0, 'failed': 0, 'files': []}
                
                for file_path in files:
                    if progress_callback:
                        progress_callback(file_count, results['total_files'], file_path.name)
                    
                    success, message, final_path = self.move_file_safely(
                        file_path, category_dirs[category]
                    )
                    
                    if success:
                        category_results['moved'] += 1
                        results['moved_files'] += 1
                        category_results['files'].append({
                            'name': file_path.name,
                            'final_path': str(final_path),
                            'status': 'moved'
                        })
                    else:
                        category_results['failed'] += 1
                        results['failed_files'] += 1
                        results['errors'].append(message)
                        category_results['files'].append({
                            'name': file_path.name,
                            'status': 'failed',
                            'error': message
                        })
                    
                    file_count += 1
                
                results['categories'][category] = category_results
            
            # Commit operations for undo
            self.undo_manager.commit_operations()
            
            # Generate final message
            if results['failed_files'] == 0:
                message = f"Successfully organized {results['moved_files']} files into {len(categories)} categories"
                return True, message, results
            else:
                message = f"Organized {results['moved_files']} files with {results['failed_files']} failures"
                return True, message, results
                
        except Exception as e:
            error_msg = f"Error during organization: {str(e)}"
            self.logger.log_error(error_msg, e)
            return False, error_msg, {}
    
    def can_undo(self) -> bool:
        """Check if undo is possible"""
        return self.undo_manager.can_undo()
    
    def undo_last_organization(self) -> Tuple[bool, str]:
        """Undo the last organization operation"""
        return self.undo_manager.undo_last_operation()
    
    def get_preview(self) -> Dict[str, List[str]]:
        """Get a preview of what files would be moved without actually moving them"""
        if not self.target_directory:
            return {}
        
        try:
            categorized_files = self.scan_directory()
            preview = {}
            
            for category, files in categorized_files.items():
                preview[category] = [file.name for file in files]
            
            return preview
            
        except Exception as e:
            self.logger.log_error(f"Error generating preview", e)
            return {}
