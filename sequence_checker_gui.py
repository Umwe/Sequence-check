import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
from datetime import datetime, timedelta
import threading
import time


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

        # Results Table
        columns = ("CDR_DATE", "NODE", "MISSINGSEQ")
        results_table = ttk.Treeview(tab, columns=columns, show="headings", height=17)
        results_table.pack(fill="both", padx=20, pady=(0, 10))

        # Customize column widths and alignments
        results_table.heading("CDR_DATE", text="CDR_DATE")
        results_table.column("CDR_DATE", width=20, anchor="center")

        results_table.heading("NODE", text="NODE")
        results_table.column("NODE", width=20, anchor="center")

        results_table.heading("MISSINGSEQ", text="MISSINGSEQ")
        results_table.column("MISSINGSEQ", width=400, anchor="center")


        # Store widgets for later access
        tab.widgets = {
            "start_date": start_date_entry,
            "end_date": end_date_entry,
            "results_table": results_table,
            "elapsed_label": elapsed_label
        }

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

    def export_results(self, group):
        tab = self.tabs[group]
        results_table = tab.widgets["results_table"]

        if not results_table.get_children():
            messagebox.showwarning("Warning", f"No results to export for {group}.")
            return

        messagebox.showinfo("Export", f"Results for {group} exported successfully (placeholder).")

    def clear_fields(self, tab):
        tab.widgets["start_date"].set_date(datetime.now())
        tab.widgets["end_date"].set_date(datetime.now())
        results_table = tab.widgets["results_table"]
        results_table.delete(*results_table.get_children())
        tab.widgets["elapsed_label"].config(text="Time Elapsed: 00:00:00")

    def cancel_all(self):
        for tab in self.tabs.values():
            self.clear_fields(tab)
