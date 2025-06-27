#!/usr/bin/env python3
"""
Smart File Organizer - Main Application Entry Point

A Python application that automatically organizes files in a directory
by moving them into categorized subfolders based on their file extensions.

Features:
- Automatic file categorization by extension
- GUI interface for easy use
- Undo functionality
- Comprehensive logging
- Progress tracking
- Error handling

Usage:
    python main.py              # Run with GUI
    python main.py --cli        # Run in command line mode
    python main.py --help       # Show help
"""

import sys
import argparse
from pathlib import Path

# Import our modules
from file_organizer import FileOrganizer
from gui import SmartFileOrganizerGUI


def run_cli_mode(directory_path: str):
    """Run the organizer in command line mode"""
    print("🗂️  Smart File Organizer - CLI Mode")
    print("=" * 40)
    
    try:
        # Initialize organizer
        organizer = FileOrganizer()
        organizer.set_target_directory(directory_path)
        
        print(f"📁 Target directory: {directory_path}")
        print()
        
        # Show preview
        print("📋 Preview of files to be organized:")
        print("-" * 30)
        
        preview = organizer.get_preview()
        if not preview:
            print("No files to organize in the specified directory.")
            return
        
        total_files = 0
        for category, files in preview.items():
            print(f"\n📁 {category} ({len(files)} files):")
            for file in files[:5]:  # Show only first 5 files
                print(f"  • {file}")
            if len(files) > 5:
                print(f"  ... and {len(files) - 5} more files")
            total_files += len(files)
        
        print(f"\nTotal files: {total_files}")
        print()
        
        # Ask for confirmation
        response = input("Do you want to proceed with organization? (y/N): ").strip().lower()
        if response not in ['y', 'yes']:
            print("Operation cancelled.")
            return
        
        # Organize files
        print("\n🔄 Organizing files...")
        
        def progress_callback(current, total, filename):
            progress = (current / total) * 100 if total > 0 else 0
            print(f"\rProgress: {progress:.1f}% - {filename}", end="", flush=True)
        
        success, message, results = organizer.organize_files(progress_callback)
        
        print()  # New line after progress
        
        if success:
            print(f"✅ {message}")
            if results:
                print(f"\nResults:")
                print(f"  • Total files: {results.get('total_files', 0)}")
                print(f"  • Successfully moved: {results.get('moved_files', 0)}")
                if results.get('failed_files', 0) > 0:
                    print(f"  • Failed: {results.get('failed_files', 0)}")
                
                print(f"\nFiles organized by category:")
                for category, info in results.get('categories', {}).items():
                    print(f"  📁 {category}: {info['moved']} files")
        else:
            print(f"❌ {message}")
            return
        
        # Ask about undo
        print()
        if organizer.can_undo():
            response = input("Do you want to undo this operation? (y/N): ").strip().lower()
            if response in ['y', 'yes']:
                print("🔄 Undoing operation...")
                undo_success, undo_message = organizer.undo_last_organization()
                if undo_success:
                    print(f"✅ {undo_message}")
                else:
                    print(f"❌ {undo_message}")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        sys.exit(1)


def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description="Smart File Organizer - Organize files by extension",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                    # Run with GUI
  python main.py --cli /path/dir    # Organize directory in CLI mode
  python main.py --cli .            # Organize current directory
        """
    )
    
    parser.add_argument(
        '--cli', 
        metavar='DIRECTORY',
        help='Run in command line mode with specified directory'
    )
    
    parser.add_argument(
        '--version', 
        action='version', 
        version='Smart File Organizer 1.0.0'
    )
    
    args = parser.parse_args()
    
    if args.cli:
        # Command line mode
        directory = Path(args.cli).resolve()
        if not directory.exists():
            print(f"❌ Error: Directory '{directory}' does not exist.")
            sys.exit(1)
        if not directory.is_dir():
            print(f"❌ Error: '{directory}' is not a directory.")
            sys.exit(1)
        
        run_cli_mode(str(directory))
    else:
        # GUI mode
        try:
            app = SmartFileOrganizerGUI()
            app.run()
        except ImportError as e:
            print(f"❌ Error: Cannot start GUI mode. {str(e)}")
            print("Try running with --cli option for command line mode.")
            sys.exit(1)
        except Exception as e:
            print(f"❌ Error starting application: {str(e)}")
            sys.exit(1)


if __name__ == "__main__":
    main()
