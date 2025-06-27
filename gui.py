"""
GUI module for Smart File Organizer
Provides a graphical user interface using tkinter
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from pathlib import Path
import threading
from file_organizer import FileOrganizer


class SmartFileOrganizerGUI:
    """Main GUI application for Smart File Organizer"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Smart File Organizer")
        self.root.geometry("800x600")
        self.root.minsize(600, 400)
        
        # Configure style
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # File organizer instance
        self.organizer = FileOrganizer()
        self.selected_directory = None
        
        # Create GUI components
        self.create_widgets()
        self.update_ui_state()
    
    def create_widgets(self):
        """Create and arrange all GUI widgets"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(4, weight=1)
        
        # Title
        title_label = ttk.Label(
            main_frame, 
            text="Smart File Organizer", 
            font=("Arial", 16, "bold")
        )
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Directory selection frame
        dir_frame = ttk.LabelFrame(main_frame, text="Select Directory", padding="10")
        dir_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        dir_frame.columnconfigure(1, weight=1)
        
        ttk.Label(dir_frame, text="Directory:").grid(row=0, column=0, sticky=tk.W)
        
        self.directory_var = tk.StringVar()
        self.directory_entry = ttk.Entry(
            dir_frame, 
            textvariable=self.directory_var, 
            state='readonly'
        )
        self.directory_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(10, 10))
        
        self.browse_button = ttk.Button(
            dir_frame, 
            text="Browse", 
            command=self.browse_directory
        )
        self.browse_button.grid(row=0, column=2, sticky=tk.E)
        
        # Action buttons frame
        action_frame = ttk.Frame(main_frame)
        action_frame.grid(row=2, column=0, columnspan=3, pady=(0, 10))
        
        self.preview_button = ttk.Button(
            action_frame, 
            text="Preview", 
            command=self.show_preview
        )
        self.preview_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.organize_button = ttk.Button(
            action_frame, 
            text="Start Organization", 
            command=self.start_organization
        )
        self.organize_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.undo_button = ttk.Button(
            action_frame, 
            text="Undo Last Operation", 
            command=self.undo_operation
        )
        self.undo_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # Progress frame
        progress_frame = ttk.LabelFrame(main_frame, text="Progress", padding="10")
        progress_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        progress_frame.columnconfigure(0, weight=1)
        
        self.progress_var = tk.StringVar(value="Ready to organize files")
        self.progress_label = ttk.Label(progress_frame, textvariable=self.progress_var)
        self.progress_label.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        self.progress_bar = ttk.Progressbar(
            progress_frame, 
            mode='determinate'
        )
        self.progress_bar.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(5, 0))
        
        # Results/Log area
        log_frame = ttk.LabelFrame(main_frame, text="Log", padding="10")
        log_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        self.log_text = scrolledtext.ScrolledText(
            log_frame, 
            height=10, 
            wrap=tk.WORD
        )
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Clear log button
        clear_button = ttk.Button(
            log_frame, 
            text="Clear Log", 
            command=self.clear_log
        )
        clear_button.grid(row=1, column=0, sticky=tk.E, pady=(5, 0))
    
    def browse_directory(self):
        """Open directory selection dialog"""
        directory = filedialog.askdirectory(
            title="Select directory to organize"
        )
        
        if directory:
            self.selected_directory = directory
            self.directory_var.set(directory)
            try:
                self.organizer.set_target_directory(directory)
                self.log_message(f"Selected directory: {directory}")
                self.update_ui_state()
            except Exception as e:
                messagebox.showerror("Error", f"Error setting directory: {str(e)}")
                self.log_message(f"Error: {str(e)}")
    
    def show_preview(self):
        """Show preview of files to be organized"""
        if not self.selected_directory:
            messagebox.showwarning("Warning", "Please select a directory first")
            return
        
        try:
            preview = self.organizer.get_preview()
            
            if not preview:
                messagebox.showinfo("Preview", "No files to organize in the selected directory")
                return
            
            # Create preview window
            preview_window = tk.Toplevel(self.root)
            preview_window.title("Organization Preview")
            preview_window.geometry("600x400")
            preview_window.transient(self.root)
            preview_window.grab_set()
            
            # Preview content
            frame = ttk.Frame(preview_window, padding="10")
            frame.pack(fill=tk.BOTH, expand=True)
            
            ttk.Label(
                frame, 
                text="Files will be organized as follows:", 
                font=("Arial", 12, "bold")
            ).pack(anchor=tk.W, pady=(0, 10))
            
            preview_text = scrolledtext.ScrolledText(frame, wrap=tk.WORD)
            preview_text.pack(fill=tk.BOTH, expand=True)
            
            total_files = 0
            for category, files in preview.items():
                preview_text.insert(tk.END, f"\n📁 {category} ({len(files)} files):\n")
                for file in files:
                    preview_text.insert(tk.END, f"  • {file}\n")
                total_files += len(files)
            
            preview_text.insert(tk.END, f"\nTotal files: {total_files}")
            preview_text.config(state='disabled')
            
            # Close button
            ttk.Button(
                frame, 
                text="Close", 
                command=preview_window.destroy
            ).pack(pady=(10, 0))
            
        except Exception as e:
            messagebox.showerror("Error", f"Error generating preview: {str(e)}")
            self.log_message(f"Preview error: {str(e)}")
    
    def start_organization(self):
        """Start the file organization process"""
        if not self.selected_directory:
            messagebox.showwarning("Warning", "Please select a directory first")
            return
        
        # Confirm action
        result = messagebox.askyesno(
            "Confirm Organization", 
            "This will move files in the selected directory. Do you want to continue?"
        )
        
        if not result:
            return
        
        # Disable buttons during operation
        self.set_buttons_state(False)
        self.progress_bar['value'] = 0
        
        # Start organization in a separate thread
        thread = threading.Thread(target=self._organize_files_thread)
        thread.daemon = True
        thread.start()
    
    def _organize_files_thread(self):
        """Run file organization in a separate thread"""
        try:
            def progress_callback(current, total, filename):
                progress = (current / total) * 100 if total > 0 else 0
                self.root.after(0, self._update_progress, progress, f"Processing: {filename}")
            
            success, message, results = self.organizer.organize_files(progress_callback)
            
            # Update UI in main thread
            self.root.after(0, self._organization_complete, success, message, results)
            
        except Exception as e:
            self.root.after(0, self._organization_error, str(e))
    
    def _update_progress(self, progress, message):
        """Update progress bar and message"""
        self.progress_bar['value'] = progress
        self.progress_var.set(message)
    
    def _organization_complete(self, success, message, results):
        """Handle completion of organization"""
        self.set_buttons_state(True)
        self.progress_var.set("Organization complete")
        self.progress_bar['value'] = 100
        
        if success:
            self.log_message(f"✅ {message}")
            
            # Show detailed results
            if results:
                self.log_message(f"Total files processed: {results.get('total_files', 0)}")
                self.log_message(f"Successfully moved: {results.get('moved_files', 0)}")
                if results.get('failed_files', 0) > 0:
                    self.log_message(f"Failed: {results.get('failed_files', 0)}")
                
                for category, info in results.get('categories', {}).items():
                    self.log_message(f"  📁 {category}: {info['moved']} files")
            
            messagebox.showinfo("Success", message)
        else:
            self.log_message(f"❌ {message}")
            messagebox.showerror("Error", message)
        
        self.update_ui_state()
    
    def _organization_error(self, error_message):
        """Handle organization error"""
        self.set_buttons_state(True)
        self.progress_var.set("Error occurred")
        self.log_message(f"❌ Error: {error_message}")
        messagebox.showerror("Error", f"Organization failed: {error_message}")
        self.update_ui_state()
    
    def undo_operation(self):
        """Undo the last organization operation"""
        if not self.organizer.can_undo():
            messagebox.showinfo("Undo", "No operations to undo")
            return
        
        result = messagebox.askyesno(
            "Confirm Undo", 
            "This will move files back to their original locations. Do you want to continue?"
        )
        
        if not result:
            return
        
        try:
            success, message = self.organizer.undo_last_organization()
            
            if success:
                self.log_message(f"✅ Undo: {message}")
                messagebox.showinfo("Undo Successful", message)
            else:
                self.log_message(f"❌ Undo failed: {message}")
                messagebox.showerror("Undo Failed", message)
            
            self.update_ui_state()
            
        except Exception as e:
            error_msg = f"Error during undo: {str(e)}"
            self.log_message(f"❌ {error_msg}")
            messagebox.showerror("Error", error_msg)
    
    def set_buttons_state(self, enabled):
        """Enable or disable action buttons"""
        state = 'normal' if enabled else 'disabled'
        self.organize_button.config(state=state)
        self.preview_button.config(state=state)
        self.undo_button.config(state=state)
        self.browse_button.config(state=state)
    
    def update_ui_state(self):
        """Update UI state based on current conditions"""
        has_directory = bool(self.selected_directory)
        can_undo = self.organizer.can_undo() if has_directory else False
        
        self.preview_button.config(state='normal' if has_directory else 'disabled')
        self.organize_button.config(state='normal' if has_directory else 'disabled')
        self.undo_button.config(state='normal' if can_undo else 'disabled')
    
    def log_message(self, message):
        """Add a message to the log area"""
        import datetime
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
    
    def clear_log(self):
        """Clear the log area"""
        self.log_text.delete(1.0, tk.END)
    
    def run(self):
        """Start the GUI application"""
        # Center the window
        self.root.eval('tk::PlaceWindow . center')
        
        # Show welcome message
        self.log_message("Welcome to Smart File Organizer!")
        self.log_message("Select a directory and click 'Preview' to see what will be organized.")
        
        # Start the main loop
        self.root.mainloop()


def main():
    """Main function to run the application"""
    app = SmartFileOrganizerGUI()
    app.run()


if __name__ == "__main__":
    main()
