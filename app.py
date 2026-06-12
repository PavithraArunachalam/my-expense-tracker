# app.py
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import matplotlib.pyplot as plt
import database

class ExpenseTrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Automated Expense Tracker")
        self.root.geometry("700://500")
        
        # Initialize the database
        database.init_db()
        
        # --- Upper Frame: Input Form ---
        input_frame = ttk.LabelFrame(root, text=" Add New Expense ", padding=15)
        input_frame.pack(fill="x", padx=15, pady=10)
        
        # Category Dropdown
        ttk.Label(input_frame, text="Category:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.category_var = tk.StringVar()
        self.category_box = ttk.Combobox(input_frame, textvariable=self.category_var, state="readonly")
        self.category_box['values'] = ("Food", "Rent/Bills", "Entertainment", "Transport", "Shopping", "Other")
        self.category_box.grid(row=0, column=1, padx=5, pady=5)
        self.category_box.current(0)
        
        # Amount Entry
        ttk.Label(input_frame, text="Amount ($):").grid(row=0, column=2, padx=5, pady=5, sticky="w")
        self.amount_entry = ttk.Entry(input_frame)
        self.amount_entry.grid(row=0, column=3, padx=5, pady=5)
        
        # Description Entry
        ttk.Label(input_frame, text="Description:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.desc_entry = ttk.Entry(input_frame, width=40)
        self.desc_entry.grid(row=1, column=1, columnspan=3, padx=5, pady=5, sticky="w")
        
        # Submit Button
        self.submit_btn = ttk.Button(input_frame, text="Log Expense", command=self.submit_expense)
        self.submit_btn.grid(row=2, column=0, columnspan=4, pady=10)
        
        # --- Middle Frame: History View ---
        view_frame = ttk.LabelFrame(root, text=" Expense History ", padding=10)
        view_frame.pack(fill="both", expand=True, padx=15, pady=5)
        
        # Table Grid (Treeview)
        columns = ("id", "date", "category", "amount", "description")
        self.tree = ttk.Treeview(view_frame, columns=columns, show="headings")
        
        self.tree.heading("id", text="ID")
        self.tree.heading("date", text="Date")
        self.tree.heading("category", text="Category")
        self.tree.heading("amount", text="Amount ($)")
        self.tree.heading("description", text="Description")
        
        self.tree.column("id", width=40, anchor="center")
        self.tree.column("date", width=100, anchor="center")
        self.tree.column("category", width=120, anchor="center")
        self.tree.column("amount", width=80, anchor="e")
        self.tree.column("description", width=250, anchor="w")
        
        self.tree.pack(fill="both", expand=True)
        
        # --- Lower Frame: Actions/Analytics ---
        action_frame = tk.Frame(root, padding=10)
        action_frame.pack(fill="x", padx=15, pady=10)
        
        self.chart_btn = ttk.Button(action_frame, text="Show Spending Breakdown (Pie Chart)", command=self.show_chart)
        self.chart_btn.pack(side="right")
        
        # Load existing records into the table grid
        self.refresh_table()

    def submit_expense(self):
        """Validates input data and saves it to the database."""
        category = self.category_var.get()
        amount_raw = self.amount_entry.get()
        description = self.desc_entry.get().strip()
        date_today = datetime.now().strftime("%Y-%m-%d")
        
        if not amount_raw or not description:
            messagebox.showwarning("Input Error", "Please fill out all fields.")
            return
        
        try:
            amount = float(amount_raw)
            if amount <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Input Error", "Please enter a valid positive number for amount.")
            return
            
        # Save to DB
        database.add_expense(date_today, category, amount, description)
        
        # Reset UI Inputs
        self.amount_entry.delete(0, tk.END)
        self.desc_entry.delete(0, tk.END)
        
        # Refresh Data Table
        self.refresh_table()
        messagebox.showinfo("Success", "Expense logged successfully!")

    def refresh_table(self):
        """Clears the grid table and re-populates it with fresh database records."""
        # Clear existing rows
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        # Re-populate
        for row in database.fetch_all_expenses():
            # Formatting amount to 2 decimal places for standard display
            formatted_row = (row[0], row[1], row[2], f"{row[3]:.2f}", row[4])
            self.tree.insert("", tk.END, values=formatted_row)

    def show_chart(self):
        """Generates and displays a Matplotlib pie chart of categorical spending."""
        data = database.fetch_category_totals()
        
        if not data:
            messagebox.showinfo("No Data", "Log some expenses first to view the chart!")
            return
            
        categories = [item[0] for item in data]
        amounts = [item[1] for item in data]
        
        # Create the matplotlib figure
        plt.figure(figsize=(6, 6))
        plt.pie(amounts, labels=categories, autopct='%1.1f%%', startangle=140, colors=plt.cm.Paired.colors)
        plt.title("Monthly Spending Breakdown")
        plt.tight_layout()
        plt.show()

if __name__ == "__main__":
    root = tk.Tk()
    app = ExpenseTrackerApp(root)
    root.mainloop()
