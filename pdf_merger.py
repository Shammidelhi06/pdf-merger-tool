import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import fitz  # PyMuPDF
import os
from typing import List, Set

class PDFMergerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PDF Merger Tool")
        self.root.geometry("600x400")
        
        # Configure grid weights
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
        # Configure style
        style = ttk.Style()
        style.configure("TButton", padding=5)
        style.configure("TListbox", padding=5)
        
        # Create main frame
        main_frame = ttk.Frame(root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure main frame grid weights
        main_frame.grid_rowconfigure(0, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)
        
        # Create list frame
        list_frame = ttk.Frame(main_frame)
        list_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        list_frame.grid_rowconfigure(0, weight=1)
        list_frame.grid_columnconfigure(0, weight=1)
        
        # File list
        self.file_listbox = tk.Listbox(list_frame, width=60, height=15)
        self.file_listbox.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Scrollbar for listbox
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.file_listbox.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.file_listbox.configure(yscrollcommand=scrollbar.set)
        
        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=1, column=0, pady=5)
        
        # File management buttons
        ttk.Button(button_frame, text="Add PDF Files", command=self.add_files).grid(row=0, column=0, padx=5)
        ttk.Button(button_frame, text="Remove Selected", command=self.remove_selected).grid(row=0, column=1, padx=5)
        ttk.Button(button_frame, text="Move Up", command=self.move_up).grid(row=0, column=2, padx=5)
        ttk.Button(button_frame, text="Move Down", command=self.move_down).grid(row=0, column=3, padx=5)
        
        # Action frame
        action_frame = ttk.Frame(main_frame)
        action_frame.grid(row=2, column=0, pady=10)
        
        # Action buttons
        ttk.Button(action_frame, text="Merge PDFs", command=self.merge_pdfs).grid(row=0, column=0, padx=5)
        ttk.Button(action_frame, text="Close", command=self.root.destroy).grid(row=0, column=1, padx=5)
        
        # Status label - initialize empty
        self.status_label = ttk.Label(main_frame, text="")
        self.status_label.grid(row=3, column=0, pady=5)
        
        # Store selected files
        self.selected_files = []
        
    def add_files(self):
        files = filedialog.askopenfilenames(
            title="Select PDF Files",
            filetypes=[("PDF files", "*.pdf")]
        )
        
        if not files:
            return
            
        # Check for duplicates
        new_files = [f for f in files if f not in self.selected_files]
        if len(new_files) != len(files):
            messagebox.showwarning("Warning", "Some files were already selected and were skipped.")
            
        self.selected_files.extend(new_files)
        self.update_listbox()
        
    def remove_selected(self):
        selection = self.file_listbox.curselection()
        if not selection:
            return
            
        # Remove in reverse order to avoid index issues
        for index in reversed(selection):
            self.selected_files.pop(index)
            
        self.update_listbox()
        
    def move_up(self):
        selection = self.file_listbox.curselection()
        if not selection or selection[0] == 0:
            return
            
        index = selection[0]
        self.selected_files[index], self.selected_files[index - 1] = \
            self.selected_files[index - 1], self.selected_files[index]
        self.update_listbox()
        self.file_listbox.selection_set(index - 1)
        
    def move_down(self):
        selection = self.file_listbox.curselection()
        if not selection or selection[0] == len(self.selected_files) - 1:
            return
            
        index = selection[0]
        self.selected_files[index], self.selected_files[index + 1] = \
            self.selected_files[index + 1], self.selected_files[index]
        self.update_listbox()
        self.file_listbox.selection_set(index + 1)
        
    def update_listbox(self):
        self.file_listbox.delete(0, tk.END)
        for file in self.selected_files:
            self.file_listbox.insert(tk.END, os.path.basename(file))
            
    def merge_pdfs(self):
        if not self.selected_files:
            messagebox.showerror("Error", "Please select at least one PDF file to merge.")
            return
            
        output_file = filedialog.asksaveasfilename(
            title="Save Merged PDF",
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")]
        )
        
        if not output_file:
            return
            
        try:
            # Create a new PDF document
            merged_pdf = fitz.open()
            
            # Add pages from each PDF
            for pdf_path in self.selected_files:
                if not os.path.exists(pdf_path):
                    raise FileNotFoundError(f"File not found: {pdf_path}")
                    
                pdf = fitz.open(pdf_path)
                merged_pdf.insert_pdf(pdf)
                pdf.close()
                
            # Save the merged PDF
            merged_pdf.save(output_file)
            merged_pdf.close()
            
            self.status_label.config(text=f"Successfully merged {len(self.selected_files)} PDFs")
            messagebox.showinfo("Success", "PDFs merged successfully!")
            
        except Exception as e:
            self.status_label.config(text="Error during merge")
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

def main():
    root = tk.Tk()
    app = PDFMergerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main() 