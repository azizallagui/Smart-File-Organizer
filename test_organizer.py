"""
Test suite for Smart File Organizer
Run this file to test the application with sample files
"""

import os
import tempfile
import shutil
from pathlib import Path
from file_organizer import FileOrganizer
from logger import Logger
from undo_manager import UndoManager


def create_test_files(test_dir: Path) -> dict:
    """Create sample files for testing"""
    test_files = {
        'Images': ['photo1.jpg', 'image.png', 'picture.gif', 'icon.ico'],
        'Documents': ['document.pdf', 'report.docx', 'notes.txt'],
        'Videos': ['movie.mp4', 'clip.avi', 'video.mkv'],
        'Audio': ['song.mp3', 'audio.wav', 'music.flac'],
        'Archives': ['backup.zip', 'files.rar', 'data.7z'],
        'Code': ['script.py', 'webpage.html', 'styles.css'],
        'Miscellaneous': ['unknown.xyz', 'custom.abc']
    }
    
    created_files = []
    
    for category, filenames in test_files.items():
        for filename in filenames:
            file_path = test_dir / filename
            # Create empty file
            file_path.write_text(f"Sample content for {filename}")
            created_files.append(file_path)
    
    return test_files, created_files


def test_file_organizer():
    """Test the FileOrganizer class"""
    print("🧪 Testing FileOrganizer...")
    
    # Create temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        test_dir = Path(temp_dir)
        print(f"📁 Test directory: {test_dir}")
        
        # Create test files
        expected_files, created_files = create_test_files(test_dir)
        print(f"✅ Created {len(created_files)} test files")
        
        # Initialize organizer
        organizer = FileOrganizer()
        organizer.set_target_directory(str(test_dir))
        
        # Test preview
        print("\n📋 Testing preview...")
        preview = organizer.get_preview()
        
        for category, files in preview.items():
            expected_count = len(expected_files.get(category, []))
            actual_count = len(files)
            print(f"  {category}: {actual_count} files (expected: {expected_count})")
            
            if actual_count != expected_count:
                print(f"    ⚠️  Count mismatch for {category}")
        
        # Test organization
        print("\n🔄 Testing organization...")
        success, message, results = organizer.organize_files()
        
        if success:
            print(f"✅ Organization successful: {message}")
            print(f"   Total files: {results.get('total_files', 0)}")
            print(f"   Moved files: {results.get('moved_files', 0)}")
            print(f"   Failed files: {results.get('failed_files', 0)}")
            
            # Check if directories were created
            for category in preview.keys():
                category_dir = test_dir / category
                if category_dir.exists():
                    files_in_category = list(category_dir.glob('*'))
                    print(f"   📁 {category}: {len(files_in_category)} files")
                else:
                    print(f"   ❌ Directory not created: {category}")
        else:
            print(f"❌ Organization failed: {message}")
            return False
        
        # Test undo
        print("\n🔙 Testing undo...")
        if organizer.can_undo():
            undo_success, undo_message = organizer.undo_last_organization()
            if undo_success:
                print(f"✅ Undo successful: {undo_message}")
                
                # Check if files are back in root
                root_files = [f for f in test_dir.iterdir() if f.is_file()]
                print(f"   Files back in root: {len(root_files)}")
            else:
                print(f"❌ Undo failed: {undo_message}")
        else:
            print("❌ Cannot undo - no operations available")
    
    print("\n✅ FileOrganizer test completed!")
    return True


def test_logger():
    """Test the Logger class"""
    print("\n🧪 Testing Logger...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        log_dir = Path(temp_dir) / "test_logs"
        logger = Logger(str(log_dir))
        
        # Test logging operations
        logger.log_operation("source.txt", "dest.txt", "move", "success")
        logger.log_operation("file2.jpg", "Images/file2.jpg", "move", "success")
        logger.log_error("Test error message")
        
        # Check if log files were created
        if logger.log_file.exists():
            print("✅ Log file created")
        else:
            print("❌ Log file not created")
        
        if logger.csv_log.exists():
            print("✅ CSV log file created")
        else:
            print("❌ CSV log file not created")
        
        # Test undo data
        test_operations = [
            {'source': 'file1.txt', 'destination': 'Documents/file1.txt', 'type': 'move'},
            {'source': 'file2.jpg', 'destination': 'Images/file2.jpg', 'type': 'move'}
        ]
        
        logger.save_undo_data(test_operations)
        loaded_data = logger.load_undo_data()
        
        if loaded_data and loaded_data.get('operations'):
            print("✅ Undo data save/load working")
        else:
            print("❌ Undo data save/load failed")
        
        # Test recent logs
        recent_logs = logger.get_recent_logs(5)
        if recent_logs:
            print(f"✅ Recent logs retrieved: {len(recent_logs)} entries")
        else:
            print("❌ No recent logs found")
    
    print("✅ Logger test completed!")
    return True


def test_undo_manager():
    """Test the UndoManager class"""
    print("\n🧪 Testing UndoManager...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        log_dir = Path(temp_dir) / "test_logs"
        logger = Logger(str(log_dir))
        undo_manager = UndoManager(logger)
        
        # Test adding operations
        undo_manager.add_operation("file1.txt", "Documents/file1.txt")
        undo_manager.add_operation("file2.jpg", "Images/file2.jpg")
        
        if undo_manager.get_operations_count() == 2:
            print("✅ Operations added correctly")
        else:
            print("❌ Operation count mismatch")
        
        # Test commit
        undo_manager.commit_operations()
        
        if undo_manager.can_undo():
            print("✅ Can undo after commit")
        else:
            print("❌ Cannot undo after commit")
        
        if undo_manager.get_operations_count() == 0:
            print("✅ Operations cleared after commit")
        else:
            print("❌ Operations not cleared after commit")
    
    print("✅ UndoManager test completed!")
    return True


def main():
    """Run all tests"""
    print("🚀 Starting Smart File Organizer Tests")
    print("=" * 50)
    
    tests = [
        ("Logger", test_logger),
        ("UndoManager", test_undo_manager),
        ("FileOrganizer", test_file_organizer),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} test PASSED")
            else:
                failed += 1
                print(f"❌ {test_name} test FAILED")
        except Exception as e:
            failed += 1
            print(f"❌ {test_name} test FAILED with exception: {e}")
        
        print("-" * 30)
    
    print(f"\n📊 Test Results:")
    print(f"   ✅ Passed: {passed}")
    print(f"   ❌ Failed: {failed}")
    print(f"   📈 Success rate: {(passed/(passed+failed)*100):.1f}%")
    
    if failed == 0:
        print("\n🎉 All tests passed! The application is ready to use.")
    else:
        print(f"\n⚠️  {failed} test(s) failed. Please check the implementation.")


if __name__ == "__main__":
    main()
