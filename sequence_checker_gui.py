import tkinter as tk
from tkinter import ttk, messagebox
from tkinter.filedialog import asksaveasfilename
from tkcalendar import DateEntry
from datetime import datetime, timedelta
import threading
import time
import pandas as pd


class SequenceCheckerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Missing Sequence Checker")
        self.root.geometry("900x700")

        # Apply theme
        self.style = ttk.Style()
        self.style.theme_use("clam")

        self.style.configure("TButton", font=("Helvetica", 10), padding=6)
        self.style.configure("TLabel", font=("Helvetica", 10))
        self.style.configure("TNotebook", padding=10)
        self.style.configure("TNotebook.Tab", padding=(12, 8))

        self.sequence_groups = [
            "GGSN", "GPRS", "SMSC", "PAM", "PAM_TDF",
            "SGSN", "MSC", "AIR", "ERS", "PPS-CCN", "SDP_DA"
        ]

        self.create_tabs()
        self.create_footer()
        self.loading_tabs = {}  # Track which tabs are loading

        # Populate the GGSN tab with records
        self.populate_table("GGSN")

    def create_tabs(self):
        self.tab_control = ttk.Notebook(self.root)
        self.tabs = {}

        for group in self.sequence_groups:
            tab = ttk.Frame(self.tab_control, style="TFrame")
            self.tab_control.add(tab, text=group)
            self.tabs[group] = tab
            self.create_group_tab(tab, group)

        self.tab_control.pack(expand=1, fill="both", padx=10, pady=10)

    def create_group_tab(self, tab, group):
        # Date Range Selection
        date_frame = ttk.Frame(tab)
        date_frame.pack(fill="x", padx=20, pady=10)

        ttk.Label(date_frame, text="Start Date:").pack(side="left", padx=(0, 10))
        start_date_entry = DateEntry(date_frame, date_pattern="yyyy-mm-dd", width=12)
        start_date_entry.pack(side="left", padx=(0, 10))

        ttk.Label(date_frame, text="End Date:").pack(side="left", padx=(10, 10))
        end_date_entry = DateEntry(date_frame, date_pattern="yyyy-mm-dd", width=12)
        end_date_entry.pack(side="left", padx=(0, 10))

        # Action Buttons
        button_frame = ttk.Frame(tab)
        button_frame.pack(fill="x", pady=20, padx=20)

        elapsed_label = ttk.Label(tab, text="Time Elapsed: 00:00:00", font=("Helvetica", 10))
        elapsed_label.pack(anchor="w", padx=20, pady=(5, 0))

        ttk.Button(button_frame, text="Check Only", command=lambda: self.start_check(group, start_date_entry.get(), end_date_entry.get(), elapsed_label)).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Export Results", command=lambda: self.export_results(group)).pack(side="left", padx=5)

        cancel_button = tk.Button(button_frame, text="Cancel", command=lambda: self.clear_fields(tab), fg="white", bg="#8B0000", relief="flat", font=("Helvetica", 10))
        cancel_button.pack(side="left", padx=5)

        # Results Table
        results_label = ttk.Label(tab, text="Results:", font=("Helvetica", 12))
        results_label.pack(anchor="w", padx=20, pady=(10, 0))

        columns = ("CDR_DATE", "NODE", "MISSINGSEQ")
        results_table = ttk.Treeview(tab, columns=columns, show="headings", height=17)
        results_table.pack(fill="both", padx=20, pady=(0, 10))

        # Customize column widths and alignments
        results_table.heading("CDR_DATE", text="CDR_DATE")
        results_table.column("CDR_DATE", width=100, anchor="w")

        results_table.heading("NODE", text="NODE")
        results_table.column("NODE", width=100, anchor="w")

        results_table.heading("MISSINGSEQ", text="MISSINGSEQ")
        results_table.column("MISSINGSEQ", width=500, anchor="w")

        # Store widgets for later access
        tab.widgets = {
            "start_date": start_date_entry,
            "end_date": end_date_entry,
            "results_table": results_table,
            "elapsed_label": elapsed_label
        }

    def populate_table(self, group):
        # Sample records
        sample_records = [
            ("20240801", "NYOCC1A", "CONTENT_CDR_CHARGINGCDR-NYOCC1A-240801*02920*"),
            ("20240801", "NYOCC1B", "CONTENT_CDR_CHARGINGCDR-NYOCC1B-240801*92407*"),
            ("20240801", "RMOCC4", "CONTENT_CDR_CHARGINGCDR-RMOCC4-240801*52407*"),
            ("20240802", "NYOCC3", "CONTENT_CDR_CHARGINGCDR-NYOCC3-240802*52407*"),
            ("20240802", "RMOCC2A", "CONTENT_CDR_CHARGINGCDR-RMOCC2A-240802*22407*"),
            ("20240802", "RMOCC2A", "CONTENT_CDR_CHARGINGCDR-RMOCC2A-240802*24070*"),
            ("20240802", "RMOCC2A", "CONTENT_CDR_CHARGINGCDR-RMOCC2A-240802*24071*"),
            ("20240802", "RMOCC2A", "CONTENT_CDR_CHARGINGCDR-RMOCC2A-240802*24072*"),
            ("20240802", "RMOCC2A", "CONTENT_CDR_CHARGINGCDR-RMOCC2A-240802*24073*"),
            ("20240802", "RMOCC2A", "CONTENT_CDR_CHARGINGCDR-RMOCC2A-240802*24074*")
        ]

        # Find the corresponding tab and table
        if group in self.tabs:
            tab = self.tabs[group]
            results_table = tab.widgets["results_table"]

            # Insert data into the table
            for record in sample_records:
                results_table.insert("", "end", values=record)

    def export_results(self, group):
        tab = self.tabs[group]
        results_table = tab.widgets["results_table"]

        # Check if there are any records in the table
        rows = results_table.get_children()
        if not rows:
            messagebox.showwarning("Warning", f"No results to export for {group}.")
            return

        # Retrieve data from the results table
        data = []
        for row in rows:
            data.append(results_table.item(row)["values"])

        # Convert data to a DataFrame
        columns = ["CDR_DATE", "NODE", "MISSINGSEQ"]
        df = pd.DataFrame(data, columns=columns)

        # Retrieve start and end dates
        start_date = tab.widgets["start_date"].get()
        end_date = tab.widgets["end_date"].get()

        # Format the filename
        filename = f"{group}_MissingSequence_{start_date}_{end_date}.xlsx"

        # Ask the user for a file save location
        file_path = asksaveasfilename(
            initialfile=filename,
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx")],
            title="Save Results as Excel File"
        )

        if not file_path:  # User canceled the save dialog
            return

        try:
            # Save DataFrame to an Excel file
            df.to_excel(file_path, index=False, engine="openpyxl")
            messagebox.showinfo("Export Success", f"Results exported successfully to {file_path}")
        except Exception as e:
            messagebox.showerror("Export Error", f"An error occurred while exporting: {e}")

    def create_footer(self):
        footer_frame = ttk.Frame(self.root)
        footer_frame.pack(fill="x", side="bottom", pady=10)

        cancel_all_button = tk.Button(footer_frame, text="Cancel All", fg="white", bg="#8B0000", command=self.cancel_all, relief="flat", font=("Helvetica", 10))
        cancel_all_button.pack(side="right", padx=20)

        ttk.Label(footer_frame, text="© 2025 MTN Revenue Assurance - V20240110", font=("Helvetica", 9)).pack(side="bottom")

    def start_check(self, group, start_date, end_date, elapsed_label):
        if not start_date or not end_date:
            messagebox.showerror("Error", f"Please fill in all fields for {group}.")
            return

        try:
            datetime.strptime(start_date, "%Y-%m-%d")
            datetime.strptime(end_date, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Error", f"Invalid date format for {group}. Please use YYYY-MM-DD.")
            return

        # Start the timer in a separate thread
        self.loading_tabs[group] = True
        threading.Thread(target=self.update_elapsed_time, args=(group, elapsed_label)).start()

        # Simulate backend process
        threading.Thread(target=self.simulate_backend_process, args=(group,)).start()

    def update_elapsed_time(self, group, elapsed_label):
        start_time = time.time()
        original_title = group

        while self.loading_tabs.get(group, False):
            elapsed_time = time.time() - start_time
            elapsed_label.config(text=f"Time Elapsed: {timedelta(seconds=int(elapsed_time))}")

            # Animate circular loader on tab title
            for loader in ["◐", "◓", "◑", "◒"]:
                if not self.loading_tabs.get(group, False):
                    break
                self.tab_control.tab(self.tabs[group], text=f"{original_title} {loader}")
                time.sleep(0.2)

        # After loading, show checkmark
        self.tab_control.tab(self.tabs[group], text=f"{original_title} ✅")

    def simulate_backend_process(self, group):
        time.sleep(10)  # Simulating backend delay
        self.loading_tabs[group] = False

    def clear_fields(self, tab):
        tab.widgets["start_date"].set_date(datetime.now())
        tab.widgets["end_date"].set_date(datetime.now())
        results_table = tab.widgets["results_table"]
        results_table.delete(*results_table.get_children())
        tab.widgets["elapsed_label"].config(text="Time Elapsed: 00:00:00")

    def cancel_all(self):
        for tab in self.tabs.values():
            self.clear_fields(tab)


