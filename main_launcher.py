import os
import sys
import subprocess
import platform
import logging
import tkinter as tk
from tkinter import ttk, messagebox
import urllib.request
import json
import tempfile
import shutil
from pathlib import Path
import ctypes
import threading

class ProjectLauncher:
    def __init__(self):
        # Configure logging
        self.setup_logging()
        
        # Check for admin privileges
        self.is_admin = self.check_admin_privileges()
        
        # Initialize GUI
        self.root = tk.Tk()
        self.root.title("Project Launcher")
        self.root.geometry("800x600")
        
        # Configure grid weights
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
        # Create main frame
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure main frame grid weights
        self.main_frame.grid_rowconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)
        
        # Status text
        self.status_text = tk.Text(self.main_frame, height=20, width=80)
        self.status_text.grid(row=0, column=0, columnspan=3, pady=5, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Progress bar
        self.progress = ttk.Progressbar(self.main_frame, mode='determinate')
        self.progress.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        # Button frame
        button_frame = ttk.Frame(self.main_frame)
        button_frame.grid(row=2, column=0, columnspan=3, pady=10)
        
        # Buttons
        self.start_button = ttk.Button(button_frame, text="Start Setup & Launch", command=self.start_process_thread)
        self.start_button.grid(row=0, column=0, padx=5)
        
        self.pdf_merger_button = ttk.Button(button_frame, text="Launch PDF Merger", command=self.launch_pdf_merger)
        self.pdf_merger_button.grid(row=0, column=1, padx=5)
        
        self.close_button = ttk.Button(button_frame, text="Close", command=self.root.destroy)
        self.close_button.grid(row=0, column=2, padx=5)
        
        # System info
        self.system_info = ttk.Label(self.main_frame, text="")
        self.system_info.grid(row=3, column=0, columnspan=3, pady=5)
        
        # Script execution order (removed python_setup.py since we handle it separately)
        self.script_order = [
            "pdf_merger.py",    # PDF merger tool
            # Add more scripts here in desired order
        ]
        
        # Initialize system info
        self.update_system_info()
        
    def check_admin_privileges(self):
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False
            
    def setup_logging(self):
        log_file = "project_launcher.log"
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def update_system_info(self):
        """Update the system information display."""
        os_info = f"OS: {platform.system()} {platform.release()}"
        python_version = f"Python: {platform.python_version()}"
        pip_version = f"Pip: {self.get_pip_version()}"
        
        system_info = f"{os_info}\n{python_version}\n{pip_version}"
        self.system_info.config(text=system_info)
        
    def log_and_update(self, message):
        self.logger.info(message)
        self.root.after(0, lambda: self.status_text.insert(tk.END, f"{message}\n"))
        self.root.after(0, self.status_text.see, tk.END)
        
    def check_pip(self):
        try:
            subprocess.run([sys.executable, "-m", "pip", "--version"], 
                         capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
            
    def get_pip_version(self):
        """Get pip version without the full path."""
        try:
            result = subprocess.run([sys.executable, '-m', 'pip', '--version'], 
                                 capture_output=True, text=True)
            # Extract just the version number from pip output
            version = result.stdout.split()[1]
            return version
        except Exception as e:
            logging.error(f"Error getting pip version: {e}")
            return "Unknown"
            
    def ensure_python_environment(self):
        """Ensure Python and pip are installed and configured"""
        try:
            # Import and run python_setup if it exists
            if os.path.exists("python_setup.py"):
                self.log_and_update("Setting up Python environment...")
                subprocess.run([sys.executable, "python_setup.py"], check=True)
            else:
                self.log_and_update("Warning: python_setup.py not found. Skipping environment setup.")
        except Exception as e:
            self.log_and_update(f"Error setting up Python environment: {str(e)}")
            raise
            
    def install_requirements(self):
        """Install project dependencies"""
        try:
            self.log_and_update("Installing requirements...")
            cmd = [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"]
            if not self.is_admin:
                cmd.append("--user")
            subprocess.run(cmd, check=True)
            self.log_and_update("Requirements installed successfully")
        except subprocess.CalledProcessError as e:
            self.log_and_update(f"Error installing requirements: {str(e)}")
            raise
            
    def execute_script(self, script_path):
        """Execute a Python script"""
        try:
            self.log_and_update(f"Executing {script_path}...")
            if os.path.exists(script_path):
                subprocess.run([sys.executable, script_path], check=True)
                self.log_and_update(f"Successfully executed {script_path}")
            else:
                self.log_and_update(f"Warning: Script {script_path} not found")
        except Exception as e:
            self.log_and_update(f"Error executing {script_path}: {str(e)}")
            raise
            
    def launch_pdf_merger(self):
        """Launch the PDF merger tool"""
        try:
            if os.path.exists("pdf_merger.py"):
                subprocess.Popen([sys.executable, "pdf_merger.py"])
            else:
                self.log_and_update("Error: PDF merger tool not found")
                messagebox.showerror("Error", "PDF merger tool not found")
        except Exception as e:
            self.log_and_update(f"Error launching PDF merger: {str(e)}")
            messagebox.showerror("Error", f"Failed to launch PDF merger: {str(e)}")
            
    def start_process_thread(self):
        """Start the process in a separate thread"""
        thread = threading.Thread(target=self.start_process)
        thread.daemon = True
        thread.start()
            
    def start_process(self):
        """Start the entire process"""
        try:
            self.root.after(0, lambda: self.start_button.config(state='disabled'))
            self.root.after(0, lambda: self.pdf_merger_button.config(state='disabled'))
            self.root.after(0, lambda: self.progress.configure(value=0))
            
            # Step 1: Ensure Python environment
            self.ensure_python_environment()
            self.root.after(0, lambda: self.progress.configure(value=50))
            
            # Step 2: Execute scripts in order
            total_scripts = len(self.script_order)
            for i, script in enumerate(self.script_order):
                self.execute_script(script)
                progress = 50 + (50 * (i + 1) / total_scripts)
                self.root.after(0, lambda p=progress: self.progress.configure(value=p))
                
            self.log_and_update("All processes completed successfully!")
            self.root.after(0, lambda: messagebox.showinfo("Success", "Setup and launch completed successfully!"))
            
        except Exception as e:
            self.log_and_update(f"Error during process: {str(e)}")
            self.root.after(0, lambda: messagebox.showerror("Error", f"Process failed: {str(e)}"))
        finally:
            self.root.after(0, lambda: self.start_button.config(state='normal'))
            self.root.after(0, lambda: self.pdf_merger_button.config(state='normal'))
            
    def run(self):
        self.root.mainloop()

def main():
    app = ProjectLauncher()
    app.run()

if __name__ == "__main__":
    main() 