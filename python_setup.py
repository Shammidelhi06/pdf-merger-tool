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

class PythonSetupTool:
    def __init__(self):
        # Configure logging
        self.setup_logging()
        
        # Check for admin privileges
        self.is_admin = self.check_admin_privileges()
        
        # Initialize GUI
        self.root = tk.Tk()
        self.root.title("Python Environment Setup Tool")
        self.root.geometry("600x400")
        
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
        self.status_text = tk.Text(self.main_frame, height=15, width=60)
        self.status_text.grid(row=0, column=0, columnspan=2, pady=5, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Progress bar
        self.progress = ttk.Progressbar(self.main_frame, mode='determinate')
        self.progress.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # Button frame
        button_frame = ttk.Frame(self.main_frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=10)
        
        # Start button
        self.start_button = ttk.Button(button_frame, text="Start Setup", command=self.start_setup)
        self.start_button.grid(row=0, column=0, padx=5)
        
        # System info
        self.system_info = ttk.Label(self.main_frame, text="")
        self.system_info.grid(row=3, column=0, columnspan=2, pady=5)
        
        # Initialize system info
        self.update_system_info()
        
    def check_admin_privileges(self):
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False
            
    def setup_logging(self):
        log_file = "python_setup.log"
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
        info = f"OS: {platform.system()} {platform.release()}\n"
        info += f"Python: {sys.version.split()[0] if sys.version else 'Not installed'}\n"
        info += f"Pip: {self.get_pip_version() if self.check_pip() else 'Not installed'}"
        self.system_info.config(text=info)
        
    def log_and_update(self, message):
        self.logger.info(message)
        self.status_text.insert(tk.END, f"{message}\n")
        self.status_text.see(tk.END)
        self.root.update()
        
    def check_pip(self):
        try:
            subprocess.run([sys.executable, "-m", "pip", "--version"], 
                         capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
            
    def get_pip_version(self):
        try:
            result = subprocess.run([sys.executable, "-m", "pip", "--version"],
                                  capture_output=True, text=True)
            # Extract just the version number from pip output
            version = result.stdout.split()[1]
            return version
        except Exception as e:
            logging.error(f"Error getting pip version: {e}")
            return "Unknown"
            
    def download_python_installer(self):
        # Get latest Python version from python.org
        try:
            response = urllib.request.urlopen("https://www.python.org/ftp/python/")
            versions = [v for v in response.read().decode().split() if v.startswith("3.")]
            latest_version = max(versions)
            
            # Determine installer URL based on system
            if platform.system() == "Windows":
                if platform.machine().endswith('64'):
                    installer_url = f"https://www.python.org/ftp/python/{latest_version}/python-{latest_version}-amd64.exe"
                else:
                    installer_url = f"https://www.python.org/ftp/python/{latest_version}/python-{latest_version}.exe"
            else:
                raise NotImplementedError("Non-Windows platforms not supported yet")
                
            # Download installer
            self.log_and_update(f"Downloading Python {latest_version} installer...")
            temp_dir = tempfile.gettempdir()
            installer_path = os.path.join(temp_dir, "python_installer.exe")
            
            urllib.request.urlretrieve(installer_url, installer_path)
            return installer_path
            
        except Exception as e:
            self.log_and_update(f"Error downloading Python installer: {str(e)}")
            raise
            
    def install_python(self, installer_path):
        try:
            self.log_and_update("Installing Python...")
            # Run installer with /quiet for silent installation
            subprocess.run([installer_path, "/quiet", "InstallAllUsers=1", "PrependPath=1"],
                         check=True)
            self.log_and_update("Python installation completed successfully")
        except subprocess.CalledProcessError as e:
            self.log_and_update(f"Error installing Python: {str(e)}")
            raise
            
    def install_pip(self):
        try:
            self.log_and_update("Installing pip...")
            # Download get-pip.py
            get_pip_url = "https://bootstrap.pypa.io/get-pip.py"
            temp_dir = tempfile.gettempdir()
            get_pip_path = os.path.join(temp_dir, "get-pip.py")
            
            urllib.request.urlretrieve(get_pip_url, get_pip_path)
            
            # Install pip
            subprocess.run([sys.executable, get_pip_path], check=True)
            self.log_and_update("Pip installation completed successfully")
            
            # Clean up
            os.remove(get_pip_path)
            
        except Exception as e:
            self.log_and_update(f"Error installing pip: {str(e)}")
            raise
            
    def upgrade_pip(self):
        try:
            self.log_and_update("Upgrading pip...")
            # Use --user flag if not running as admin
            cmd = [sys.executable, "-m", "pip", "install", "--upgrade", "pip"]
            if not self.is_admin:
                cmd.append("--user")
                
            subprocess.run(cmd, check=True)
            self.log_and_update("Pip upgrade completed successfully")
        except subprocess.CalledProcessError as e:
            self.log_and_update(f"Error upgrading pip: {str(e)}")
            raise
            
    def install_requirements(self):
        try:
            self.log_and_update("Installing requirements...")
            # Use --user flag if not running as admin
            cmd = [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"]
            if not self.is_admin:
                cmd.append("--user")
                
            subprocess.run(cmd, check=True)
            self.log_and_update("Requirements installation completed successfully")
        except subprocess.CalledProcessError as e:
            self.log_and_update(f"Error installing requirements: {str(e)}")
            raise
            
    def start_setup(self):
        try:
            if not self.is_admin:
                self.log_and_update("Warning: Running without administrator privileges. Some operations may fail.")
                if not messagebox.askyesno("Warning", 
                    "The tool is not running with administrator privileges. Some operations may fail.\n"
                    "Do you want to continue?"):
                    return
                    
            self.start_button.config(state='disabled')
            self.progress['value'] = 0
            
            # Check Python installation
            if not sys.executable:
                self.log_and_update("Python not found. Downloading installer...")
                installer_path = self.download_python_installer()
                self.progress['value'] = 30
                self.install_python(installer_path)
                self.progress['value'] = 60
                
            # Check and upgrade pip
            if not self.check_pip():
                self.log_and_update("Pip not found. Installing pip...")
                self.install_pip()
            else:
                self.log_and_update("Upgrading pip...")
                self.upgrade_pip()
            self.progress['value'] = 80
            
            # Install requirements
            self.install_requirements()
            self.progress['value'] = 100
            
            self.log_and_update("Setup completed successfully!")
            messagebox.showinfo("Success", "Python environment setup completed successfully!")
            
            # Close the window after a short delay
            self.root.after(1500, self.root.destroy)
            
        except Exception as e:
            self.log_and_update(f"Error during setup: {str(e)}")
            messagebox.showerror("Error", f"Setup failed: {str(e)}")
        finally:
            self.start_button.config(state='normal')
            
    def run(self):
        self.root.mainloop()

def main():
    app = PythonSetupTool()
    app.run()

if __name__ == "__main__":
    main() 