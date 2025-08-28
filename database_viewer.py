#!/usr/bin/env python3
"""
SQLite Database Viewer for Pathology Lab
Simple GUI to view and manage database
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
import os
import pandas as pd
from datetime import datetime

class DatabaseViewer:
    def __init__(self, db_path=None):
        self.root = tk.Tk()
        self.root.title("Pathology Lab Database Viewer")
        self.root.geometry("1200x800")
        
        # Database path
        if db_path is None:
            data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
            self.db_path = os.path.join(data_dir, 'pathology.db')
        else:
            self.db_path = db_path
        
        self.connection = None
        self.setup_ui()
        self.connect_database()
    
    def setup_ui(self):
        """Setup the user interface"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Database info frame
        info_frame = ttk.LabelFrame(main_frame, text="Database Information", padding="5")
        info_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.db_info_label = ttk.Label(info_frame, text="No database connected")
        self.db_info_label.grid(row=0, column=0, sticky=tk.W)
        
        # Buttons frame
        buttons_frame = ttk.Frame(info_frame)
        buttons_frame.grid(row=0, column=1, sticky=tk.E)
        
        ttk.Button(buttons_frame, text="Refresh", command=self.refresh_data).grid(row=0, column=0, padx=2)
        ttk.Button(buttons_frame, text="Backup", command=self.create_backup).grid(row=0, column=1, padx=2)
        ttk.Button(buttons_frame, text="Export", command=self.export_data).grid(row=0, column=2, padx=2)
        
        # Tables list frame
        tables_frame = ttk.LabelFrame(main_frame, text="Tables", padding="5")
        tables_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        tables_frame.rowconfigure(0, weight=1)
        
        # Tables listbox
        self.tables_listbox = tk.Listbox(tables_frame, width=20)
        self.tables_listbox.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.tables_listbox.bind('<<ListboxSelect>>', self.on_table_select)
        
        # Data frame
        data_frame = ttk.LabelFrame(main_frame, text="Data", padding="5")
        data_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        data_frame.columnconfigure(0, weight=1)
        data_frame.rowconfigure(0, weight=1)
        
        # Treeview for data display
        self.tree = ttk.Treeview(data_frame)
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(data_frame, orient="vertical", command=self.tree.yview)
        v_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.tree.configure(yscrollcommand=v_scrollbar.set)
        
        h_scrollbar = ttk.Scrollbar(data_frame, orient="horizontal", command=self.tree.xview)
        h_scrollbar.grid(row=1, column=0, sticky=(tk.W, tk.E))
        self.tree.configure(xscrollcommand=h_scrollbar.set)
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
    
    def connect_database(self):
        """Connect to the SQLite database"""
        try:
            if os.path.exists(self.db_path):
                self.connection = sqlite3.connect(self.db_path)
                self.update_database_info()
                self.load_tables()
                self.status_var.set(f"Connected to: {self.db_path}")
            else:
                self.status_var.set(f"Database not found: {self.db_path}")
                messagebox.showwarning("Database Not Found", f"Database file not found:\n{self.db_path}")
        except Exception as e:
            messagebox.showerror("Connection Error", f"Failed to connect to database:\n{str(e)}")
            self.status_var.set("Connection failed")
    
    def update_database_info(self):
        """Update database information display"""
        if self.connection:
            try:
                file_size = os.path.getsize(self.db_path)
                file_time = datetime.fromtimestamp(os.path.getmtime(self.db_path))
                
                info_text = f"📁 {os.path.basename(self.db_path)} | 📊 {file_size/1024/1024:.2f} MB | 🕒 {file_time.strftime('%Y-%m-%d %H:%M')}"
                self.db_info_label.config(text=info_text)
            except Exception as e:
                self.db_info_label.config(text=f"Error reading database info: {str(e)}")
    
    def load_tables(self):
        """Load table names into the listbox"""
        if not self.connection:
            return
        
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
            tables = cursor.fetchall()
            
            self.tables_listbox.delete(0, tk.END)
            for table in tables:
                table_name = table[0]
                # Get row count
                cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
                count = cursor.fetchone()[0]
                self.tables_listbox.insert(tk.END, f"{table_name} ({count})")
            
            self.status_var.set(f"Loaded {len(tables)} tables")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load tables:\n{str(e)}")
    
    def on_table_select(self, event):
        """Handle table selection"""
        selection = self.tables_listbox.curselection()
        if not selection:
            return
        
        table_info = self.tables_listbox.get(selection[0])
        table_name = table_info.split(' (')[0]  # Extract table name
        self.load_table_data(table_name)
    
    def load_table_data(self, table_name):
        """Load data from selected table"""
        if not self.connection:
            return
        
        try:
            # Clear existing data
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            # Get table data
            cursor = self.connection.cursor()
            cursor.execute(f"SELECT * FROM {table_name} LIMIT 1000;")  # Limit for performance
            rows = cursor.fetchall()
            
            # Get column names
            cursor.execute(f"PRAGMA table_info({table_name});")
            columns_info = cursor.fetchall()
            columns = [col[1] for col in columns_info]
            
            # Configure treeview columns
            self.tree["columns"] = columns
            self.tree["show"] = "headings"
            
            # Setup column headings and widths
            for col in columns:
                self.tree.heading(col, text=col)
                self.tree.column(col, width=100, minwidth=50)
            
            # Insert data
            for row in rows:
                # Convert None to empty string and format data
                formatted_row = []
                for item in row:
                    if item is None:
                        formatted_row.append("")
                    elif isinstance(item, (int, float)):
                        formatted_row.append(str(item))
                    else:
                        formatted_row.append(str(item)[:100])  # Truncate long text
                
                self.tree.insert("", tk.END, values=formatted_row)
            
            self.status_var.set(f"Loaded {len(rows)} rows from {table_name}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load table data:\n{str(e)}")
    
    def refresh_data(self):
        """Refresh the database connection and data"""
        if self.connection:
            self.connection.close()
        self.connect_database()
    
    def create_backup(self):
        """Create a backup of the database"""
        try:
            from backup_system import DatabaseBackup
            backup_system = DatabaseBackup(self.db_path)
            backup_path = backup_system.create_backup('gui')
            
            if backup_path:
                messagebox.showinfo("Backup Created", f"Backup created successfully:\n{backup_path}")
            else:
                messagebox.showerror("Backup Failed", "Failed to create backup")
        except ImportError:
            messagebox.showerror("Error", "Backup system not available")
        except Exception as e:
            messagebox.showerror("Error", f"Backup failed:\n{str(e)}")
    
    def export_data(self):
        """Export current table data to CSV"""
        selection = self.tables_listbox.curselection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a table first")
            return
        
        table_info = self.tables_listbox.get(selection[0])
        table_name = table_info.split(' (')[0]
        
        try:
            # Ask for save location
            filename = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                initialvalue=f"{table_name}_export.csv"
            )
            
            if filename:
                # Export to CSV using pandas
                df = pd.read_sql_query(f"SELECT * FROM {table_name}", self.connection)
                df.to_csv(filename, index=False)
                messagebox.showinfo("Export Complete", f"Data exported to:\n{filename}")
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export data:\n{str(e)}")
    
    def run(self):
        """Start the GUI application"""
        self.root.mainloop()
        if self.connection:
            self.connection.close()

def main():
    """Main function to run the database viewer"""
    try:
        # Check if required packages are available
        import pandas as pd
        
        app = DatabaseViewer()
        app.run()
    except ImportError:
        print("❌ Required package 'pandas' not found.")
        print("Install it with: pip install pandas")
        print("\nAlternatively, you can use a simple SQLite browser like:")
        print("- DB Browser for SQLite (https://sqlitebrowser.org/)")
        print("- SQLiteStudio (https://sqlitestudio.pl/)")
    except Exception as e:
        print(f"❌ Error starting database viewer: {str(e)}")

if __name__ == '__main__':
    main()
