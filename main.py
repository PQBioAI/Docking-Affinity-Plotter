import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import threading
import queue
from datetime import datetime
from data_loader import DataLoader
from plot_generator import PlotGenerator
from pdf_generator import PDFGenerator

class DockingAnalyzerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Docking Result Analyzer")
        self.root.geometry("900x650")
        
        try:
            self.root.iconbitmap("logo.ico")
        except:
            pass
        
        self.csv_path = None
        self.df = None
        self.output_dir = None
        self.task_queue = queue.Queue()
        
        self.setup_ui()
        self.check_queue()
    
    def setup_ui(self):
        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        title_label = tk.Label(main_frame, 
                              text="Docking Result Analyzer",
                              font=("Arial", 18, "bold"),
                              fg="#2c3e50")
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 15))
        
        file_frame = ttk.LabelFrame(main_frame, text="1. Select CSV File", padding="10")
        file_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 15))
        
        self.file_label = tk.Label(file_frame, text="No file selected", 
                                  font=("Arial", 9), fg="gray", width=40)
        self.file_label.grid(row=0, column=0, padx=(0, 10))
        
        browse_btn = tk.Button(file_frame, text="Browse CSV", 
                              command=self.browse_file,
                              bg="#3498db", fg="white",
                              font=("Arial", 9, "bold"),
                              padx=15, pady=4)
        browse_btn.grid(row=0, column=1)
        
        preview_frame = ttk.LabelFrame(main_frame, text="Data Preview", padding="8")
        preview_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), 
                          pady=(0, 15))
        
        self.preview_tree = ttk.Treeview(preview_frame, height=6)
        self.preview_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        scrollbar = ttk.Scrollbar(preview_frame, orient="vertical", 
                                 command=self.preview_tree.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.preview_tree.configure(yscrollcommand=scrollbar.set)
        
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=(0, 15))
        
        self.analyze_btn = tk.Button(button_frame, text="Generate Analysis", 
                                    command=self.start_analysis,
                                    bg="#27ae60", fg="white",
                                    font=("Arial", 12, "bold"),
                                    padx=25, pady=8, state=tk.DISABLED)
        self.analyze_btn.pack(side=tk.LEFT, padx=10)
        
        self.open_location_btn = tk.Button(button_frame, text="Open Output Location", 
                                         command=self.open_file_location,
                                         bg="#9b59b6", fg="white",
                                         font=("Arial", 12, "bold"),
                                         padx=25, pady=8, state=tk.DISABLED)
        self.open_location_btn.pack(side=tk.LEFT, padx=10)
        
        info_frame = ttk.LabelFrame(main_frame, text="Output Information", padding="8")
        info_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.output_location_label = tk.Label(info_frame, 
                                             text="Output will be saved to Downloads folder",
                                             font=("Arial", 9),
                                             fg="gray",
                                             wraplength=600,
                                             justify=tk.LEFT)
        self.output_location_label.pack(anchor=tk.W)
        
        self.generated_files_label = tk.Label(info_frame,
                                             text="",
                                             font=("Arial", 9),
                                             fg="green",
                                             wraplength=600,
                                             justify=tk.LEFT)
        self.generated_files_label.pack(anchor=tk.W, pady=(5, 0))
        
        self.progress_label = tk.Label(main_frame, text="", font=("Arial", 9))
        self.progress_label.grid(row=5, column=0, columnspan=2, pady=(5, 0))
        
        self.progress_bar = ttk.Progressbar(main_frame, length=600, mode='determinate')
        self.progress_bar.grid(row=6, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(5, 0))
        
        self.progress_text = tk.Label(main_frame, text="0%", font=("Arial", 8))
        self.progress_text.grid(row=6, column=0, columnspan=2)
        
        self.status_bar = tk.Label(main_frame, text="Ready", bd=1, relief=tk.SUNKEN,
                                  anchor=tk.W, font=("Arial", 8))
        self.status_bar.grid(row=7, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(15, 0))
        
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)
        preview_frame.columnconfigure(0, weight=1)
        preview_frame.rowconfigure(0, weight=1)
    
    def check_queue(self):
        try:
            while True:
                task = self.task_queue.get_nowait()
                if task[0] == 'update_progress':
                    self.update_progress(task[1], task[2])
                elif task[0] == 'analysis_complete':
                    self.analysis_complete()
                elif task[0] == 'analysis_error':
                    self.analysis_error(task[1])
        except queue.Empty:
            pass
        self.root.after(100, self.check_queue)
    
    def browse_file(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if file_path:
            self.csv_path = file_path
            self.file_label.config(text=os.path.basename(file_path), fg="green")
            self.preview_data(file_path)
            self.analyze_btn.config(state=tk.NORMAL)
            self.status_bar.config(text=f"Loaded: {os.path.basename(file_path)}")
    
    def preview_data(self, file_path):
        try:
            for item in self.preview_tree.get_children():
                self.preview_tree.delete(item)
            
            import pandas as pd
            df = pd.read_csv(file_path, nrows=6)
            
            self.preview_tree["columns"] = list(df.columns)
            self.preview_tree["show"] = "headings"
            
            for col in df.columns:
                self.preview_tree.heading(col, text=col)
                self.preview_tree.column(col, width=90)
            
            for index, row in df.iterrows():
                self.preview_tree.insert("", "end", values=list(row))
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to preview file: {str(e)}")
    
    def start_analysis(self):
        if not self.csv_path:
            messagebox.showerror("Error", "Please select a CSV file first")
            return
        
        self.analyze_btn.config(state=tk.DISABLED)
        self.open_location_btn.config(state=tk.DISABLED)
        self.progress_bar['value'] = 0
        self.progress_text.config(text="0%")
        self.generated_files_label.config(text="")
        self.status_bar.config(text="Generating analysis report...")
        
        thread = threading.Thread(target=self.generate_pdf_only, daemon=True)
        thread.start()
    
    def update_progress(self, value, text):
        self.progress_bar['value'] = value
        self.progress_text.config(text=f"{value}%")
        self.progress_label.config(text=text)
        self.status_bar.config(text=text)
    
    def generate_pdf_only(self):
        try:
            self.task_queue.put(('update_progress', 5, "Loading data..."))
            
            loader = DataLoader(self.csv_path)
            self.df = loader.load_data()
            
            self.task_queue.put(('update_progress', 10, "Data loaded"))
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            downloads_path = os.path.join(os.path.expanduser("~"), "Downloads")
            self.output_dir = os.path.join(downloads_path, f"Docking_Analysis_{timestamp}")
            os.makedirs(self.output_dir, exist_ok=True)
            
            self.output_location_label.config(
                text=f"Output location: {self.output_dir}",
                fg="blue"
            )
            
            self.plots_dir = os.path.join(self.output_dir, "plots")
            os.makedirs(self.plots_dir, exist_ok=True)
            
            self.task_queue.put(('update_progress', 15, "Preparing analysis..."))
            
            self.task_queue.put(('update_progress', 20, "Generating plots..."))
            plot_generator = PlotGenerator(self.df, self.plots_dir)
            self.plot_files = plot_generator.generate_all_plots()
            
            self.task_queue.put(('update_progress', 85, "Creating PDF report..."))
            pdf_path = os.path.join(self.output_dir, "Docking_Analysis_Report.pdf")
            
            pdf_generator = PDFGenerator(self.df, self.plot_files, self.plots_dir, self.csv_path)
            pdf_generator.generate_pdf(pdf_path, self.task_queue)
            
            self.task_queue.put(('update_progress', 100, "Analysis completed!"))
            self.task_queue.put(('analysis_complete',))
            
        except Exception as e:
            import traceback
            error_msg = f"{str(e)}\n\n{traceback.format_exc()}"
            self.task_queue.put(('analysis_error', error_msg))
    
    def analysis_complete(self):
        self.open_location_btn.config(state=tk.NORMAL)
        self.status_bar.config(text="Analysis complete! Click 'Open Output Location' to view files.")
        
        pdf_path = os.path.join(self.output_dir, "Docking_Analysis_Report.pdf")
        plot_count = len([f for f in os.listdir(self.plots_dir) if f.endswith('.png')]) if os.path.exists(self.plots_dir) else 0
        
        files_info = f"Generated: • 1 PDF report • {plot_count} plot(s)"
        self.generated_files_label.config(text=files_info, fg="green")
        
        messagebox.showinfo("Success", 
                          f"Analysis complete!\n\n"
                          f"Files saved to:\n{self.output_dir}\n\n"
                          f"Generated:\n"
                          f"• Docking_Analysis_Report.pdf\n"
                          f"• {plot_count} plot(s) in 'plots' folder")
    
    def analysis_error(self, error_msg):
        self.analyze_btn.config(state=tk.NORMAL)
        self.open_location_btn.config(state=tk.DISABLED)
        self.progress_bar['value'] = 0
        self.progress_text.config(text="0%")
        self.progress_label.config(text="")
        self.status_bar.config(text="Analysis failed")
        
        lines = error_msg.split('\n')
        main_error = lines[0] if lines else "Unknown error"
        messagebox.showerror("Error", f"Failed to generate analysis:\n\n{main_error}")
    
    def open_file_location(self):
        if self.output_dir and os.path.exists(self.output_dir):
            try:
                os.startfile(self.output_dir)
                self.status_bar.config(text=f"Opened: {self.output_dir}")
            except Exception as e:
                messagebox.showerror("Error", f"Cannot open file location:\n{str(e)}")
        else:
            messagebox.showinfo("Info", "Please generate analysis first")

def main():
    root = tk.Tk()
    app = DockingAnalyzerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()