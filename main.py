import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
from collections import Counter
from datetime import datetime
from pathlib import Path
import csv
import json

from forensic_core import (
    load_events,
    merge_sort,
    binary_search,
    hash_statistics,
    top_n_events,
    merge_sorted_sources,
    incident_windows
)

# ---------------- CONFIGURATION ----------------

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

APP_NAME = "FORENSICTIMELINE PRO"
AUTHOR = "ABDUL SAMAD"
UNIVERSITY = "AROR UNIVERSITY OF ART, ARCHITECTURE, DESIGN & HERITAGE, SUKKUR"

BG = "#080F1B"
SIDEBAR = "#0D1726"
CARD = "#111F30"
CARD2 = "#16283D"
ACCENT = "#18B9A5"
BLUE = "#3988FF"
TEXT = "#EAF2FA"
MUTED = "#8DA3B8"
RED = "#FF5B68"
ORANGE = "#F5A64A"
GREEN = "#36C995"

project = Path(__file__).resolve().parent if "__file__" in globals() else Path.cwd()

# ---------------- APPLICATION ----------------

class ForensicApp(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.title(APP_NAME + " | Advanced Investigation Suite")
        self.geometry("1450x850")
        self.minsize(1100, 700)
        self.configure(fg_color=BG)

        self.events = []
        self.current_page = "Dashboard"
        self.current_file = "No file imported"

        self.create_sidebar()
        self.create_main_area()
        self.show_dashboard()

    # ---------------- SIDEBAR ----------------

    def create_sidebar(self):

        self.sidebar = ctk.CTkFrame(
            self, width=235, corner_radius=0, fg_color=SIDEBAR
        )
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        logo = ctk.CTkFrame(
            self.sidebar, fg_color=ACCENT, width=55, height=55,
            corner_radius=15
        )
        logo.pack(pady=(28, 8))
        logo.pack_propagate(False)

        ctk.CTkLabel(
            logo, text="AS", font=("Arial", 23, "bold"),
            text_color="#06151B"
        ).place(relx=.5, rely=.5, anchor="center")

        ctk.CTkLabel(
            self.sidebar, text="FORENSIC TIMELINE",
            font=("Arial", 17, "bold"), text_color=TEXT
        ).pack(pady=(4, 0))

        ctk.CTkLabel(
            self.sidebar, text="ADVANCED INVESTIGATION SUITE",
            font=("Arial", 9), text_color=MUTED
        ).pack(pady=(2, 25))

        self.nav_buttons = {}

        pages = [
            ("Dashboard", "▦"),
            ("Event Timeline", "◷"),
            ("Evidence Explorer", "⌕"),
            ("Threat Analytics", "◈"),
            ("Incident Detection", "⚠"),
            ("Investigation Reports", "▤"),
            ("Project Information", "ⓘ")
        ]

        for page, icon in pages:
            button = ctk.CTkButton(
                self.sidebar,
                text=f"  {icon}    {page}",
                anchor="w",
                height=43,
                corner_radius=9,
                fg_color="transparent",
                hover_color=CARD2,
                text_color=TEXT,
                font=("Arial", 13),
                command=lambda p=page: self.navigate(p)
            )
            button.pack(fill="x", padx=13, pady=3)
            self.nav_buttons[page] = button

        ctk.CTkFrame(
            self.sidebar, height=2, fg_color=CARD2
        ).pack(fill="x", padx=15, pady=20)

        ctk.CTkButton(
            self.sidebar, text="＋  Import CSV",
            fg_color=ACCENT, hover_color="#109887",
            text_color="#04151A", font=("Arial", 13, "bold"),
            height=43, command=self.import_csv
        ).pack(fill="x", padx=13, pady=4)

        ctk.CTkLabel(
            self.sidebar,
            text="DEVELOPED BY\nABDUL SAMAD\n\nAROR UNIVERSITY\nSUKKUR",
            text_color=MUTED, font=("Arial", 10),
            justify="left"
        ).pack(side="bottom", anchor="w", padx=20, pady=25)

    # ---------------- MAIN AREA ----------------

    def create_main_area(self):

        self.main = ctk.CTkFrame(
            self, fg_color=BG, corner_radius=0
        )
        self.main.pack(side="right", fill="both", expand=True)

        self.header = ctk.CTkFrame(
            self.main, fg_color=BG, height=75
        )
        self.header.pack(fill="x", padx=28, pady=(17, 5))
        self.header.pack_propagate(False)

        self.page_title = ctk.CTkLabel(
            self.header, text="Dashboard",
            font=("Arial", 25, "bold"), text_color=TEXT
        )
        self.page_title.pack(side="left", anchor="center")

        self.status_label = ctk.CTkLabel(
            self.header, text="● SYSTEM READY",
            text_color=GREEN, font=("Arial", 11, "bold")
        )
        self.status_label.pack(side="right", padx=12)

        self.file_label = ctk.CTkLabel(
            self.main, text="Dataset: No file imported",
            text_color=MUTED, font=("Arial", 11)
        )
        self.file_label.pack(anchor="w", padx=30, pady=(0, 8))

        self.content = ctk.CTkFrame(
            self.main, fg_color=BG
        )
        self.content.pack(fill="both", expand=True, padx=25, pady=10)

    def clear_content(self):
        for widget in self.content.winfo_children():
            widget.destroy()

    def navigate(self, page):
        self.current_page = page

        for name, button in self.nav_buttons.items():
            button.configure(
                fg_color=CARD2 if name == page else "transparent"
            )

        self.page_title.configure(text=page)

        pages = {
            "Dashboard": self.show_dashboard,
            "Event Timeline": self.show_timeline,
            "Evidence Explorer": self.show_evidence,
            "Threat Analytics": self.show_analytics,
            "Incident Detection": self.show_incidents,
            "Investigation Reports": self.show_reports,
            "Project Information": self.show_information
        }

        pages[page]()

    # ---------------- REUSABLE COMPONENTS ----------------

    def section_title(self, parent, title, subtitle=""):
        ctk.CTkLabel(
            parent, text=title, font=("Arial", 17, "bold"),
            text_color=TEXT
        ).pack(anchor="w", padx=5, pady=(5, 2))

        if subtitle:
            ctk.CTkLabel(
                parent, text=subtitle, font=("Arial", 11),
                text_color=MUTED
            ).pack(anchor="w", padx=5, pady=(0, 12))

    def make_card(self, parent, title, value, color=ACCENT):
        card = ctk.CTkFrame(
            parent, fg_color=CARD, corner_radius=13
        )
        card.pack(side="left", fill="both", expand=True, padx=6)

        ctk.CTkLabel(
            card, text=title.upper(), text_color=MUTED,
            font=("Arial", 10, "bold")
        ).pack(anchor="w", padx=16, pady=(15, 4))

        ctk.CTkLabel(
            card, text=str(value), text_color=color,
            font=("Arial", 28, "bold")
        ).pack(anchor="w", padx=16, pady=(0, 14))

        return card

    def get_table(self, parent, columns, headings=None, height=12):
        table_frame = ctk.CTkFrame(parent, fg_color=CARD, corner_radius=12)
        table_frame.pack(fill="both", expand=True, padx=5, pady=8)

        tree = tk.ttk.Treeview(
            table_frame, columns=columns, show="headings",
            height=height
        )

        style = tk.ttk.Style()
        style.theme_use("clam")
        style.configure(
            "Treeview", background="#111F30",
            foreground="#EAF2FA", fieldbackground="#111F30",
            rowheight=31, borderwidth=0, font=("Arial", 10)
        )
        style.configure(
            "Treeview.Heading", background="#1C3047",
            foreground="#EAF2FA", font=("Arial", 10, "bold")
        )
        style.map(
            "Treeview", background=[("selected", "#176A78")]
        )

        for col in columns:
            tree.heading(col, text=(headings or {}).get(col, col.upper()))
            tree.column(col, width=145, minwidth=80)

        scrollbar = tk.ttk.Scrollbar(
            table_frame, orient="vertical", command=tree.yview
        )
        tree.configure(yscrollcommand=scrollbar.set)

        tree.pack(side="left", fill="both", expand=True, padx=8, pady=8)
        scrollbar.pack(side="right", fill="y", pady=8)

        return tree

    def event_values(self, event):
        return (
            event.get("timestamp", ""),
            event.get("source", ""),
            event.get("event_type", ""),
            event.get("severity", ""),
            event.get("details", "")
        )

    # ---------------- IMPORT CSV ----------------

    def import_csv(self):

        path = filedialog.askopenfilename(
            title="Select Forensic Log CSV",
            filetypes=[("CSV files", "*.csv")]
        )

        if not path:
            return

        try:
            loaded = load_events(path)
            self.events = loaded
            self.current_file = Path(path).name
            self.file_label.configure(
                text=f"Dataset: {self.current_file} | {len(self.events)} events"
            )
            self.status_label.configure(
                text="● DATASET LOADED", text_color=GREEN
            )
            messagebox.showinfo(
                "Import Successful",
                f"{len(self.events)} events imported successfully."
            )
            self.navigate("Dashboard")

        except Exception as error:
            messagebox.showerror("Import Error", str(error))

    # ---------------- DASHBOARD ----------------

    def show_dashboard(self):

        self.clear_content()
        self.section_title(
            self.content, "Investigation Overview",
            "Central command dashboard for digital forensic log analysis."
        )

        stats = hash_statistics(self.events) if self.events else {
            "sources": {}, "event_types": {}, "severities": {}
        }

        critical = stats["severities"].get("CRITICAL", 0)
        high = stats["severities"].get("HIGH", 0)

        cards = ctk.CTkFrame(self.content, fg_color=BG)
        cards.pack(fill="x", pady=10)

        self.make_card(cards, "Total Events", len(self.events), BLUE)
        self.make_card(cards, "Critical Alerts", critical, RED)
        self.make_card(cards, "High Alerts", high, ORANGE)
        self.make_card(cards, "Log Sources", len(stats["sources"]), GREEN)

        self.section_title(
            self.content, "Recent Security Events",
            "Latest records from the imported dataset."
        )

        tree = self.get_table(
            self.content,
            ("timestamp", "source", "event_type", "severity", "details"),
            {"timestamp": "TIMESTAMP", "source": "SOURCE",
             "event_type": "EVENT TYPE", "severity": "SEVERITY",
             "details": "DETAILS"},
            height=9
        )

        recent = sorted(
            self.events, key=lambda e: e["timestamp"], reverse=True
        )[:10]

        for event in recent:
            tree.insert("", "end", values=self.event_values(event))

    # ---------------- TIMELINE ----------------

    def show_timeline(self):

        self.clear_content()
        self.section_title(
            self.content, "Event Timeline",
            "Chronological investigation and event filtering."
        )

        controls = ctk.CTkFrame(self.content, fg_color=CARD, corner_radius=10)
        controls.pack(fill="x", pady=8)

        search = ctk.CTkEntry(
            controls, placeholder_text="Search source, event type or details...",
            width=330, height=36
        )
        search.pack(side="left", padx=10, pady=10)

        severity = ctk.CTkOptionMenu(
            controls, values=["ALL", "LOW", "MEDIUM", "HIGH", "CRITICAL"]
        )
        severity.pack(side="left", padx=8)

        tree = self.get_table(
            self.content,
            ("timestamp", "source", "event_type", "severity", "details"),
            height=16
        )

        def populate():
            tree.delete(*tree.get_children())

            term = search.get().lower().strip()
            level = severity.get()

            for event in merge_sort(self.events):
                text = " ".join(str(v) for v in event.values()).lower()

                if term and term not in text:
                    continue
                if level != "ALL" and event["severity"] != level:
                    continue

                tree.insert("", "end", values=self.event_values(event))

        ctk.CTkButton(
            controls, text="Apply Filters", command=populate,
            fg_color=ACCENT, text_color="#06151B"
        ).pack(side="left", padx=8)

        ctk.CTkButton(
            controls, text="Reset", command=lambda: (
                search.delete(0, "end"),
                severity.set("ALL"),
                populate()
            )
        ).pack(side="left", padx=5)

        populate()

    # ---------------- EVIDENCE EXPLORER ----------------

    def show_evidence(self):

        self.clear_content()
        self.section_title(
            self.content, "Evidence Explorer",
            "Inspect individual log records and their metadata."
        )

        if not self.events:
            ctk.CTkLabel(
                self.content, text="Import a CSV dataset to explore evidence.",
                text_color=MUTED
            ).pack(pady=50)
            return

        tree = self.get_table(
            self.content,
            ("timestamp", "source", "event_type", "severity", "details"),
            height=12
        )

        for event in merge_sort(self.events):
            tree.insert("", "end", values=self.event_values(event))

        detail = ctk.CTkTextbox(
            self.content, height=130, fg_color=CARD,
            text_color=TEXT, font=("Consolas", 12)
        )
        detail.pack(fill="x", padx=5, pady=8)

        def inspect(event=None):
            selected = tree.selection()
            if not selected:
                return

            values = tree.item(selected[0], "values")
            detail.delete("1.0", "end")

            labels = ["Timestamp", "Source", "Event Type", "Severity", "Details"]
            for label, value in zip(labels, values):
                detail.insert("end", f"{label}: {value}\n")

        tree.bind("<<TreeviewSelect>>", inspect)

    # ---------------- ANALYTICS ----------------

    def show_analytics(self):

        self.clear_content()
        self.section_title(
            self.content, "Threat Analytics",
            "Severity and source distribution based on imported evidence."
        )

        if not self.events:
            ctk.CTkLabel(
                self.content, text="Import CSV to generate analytics.",
                text_color=MUTED
            ).pack(pady=50)
            return

        from matplotlib.figure import Figure
        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

        stats = hash_statistics(self.events)

        figure = Figure(figsize=(10, 4.8), dpi=100, facecolor="#111F30")

        ax1 = figure.add_subplot(121)
        ax2 = figure.add_subplot(122)

        levels = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
        values = [stats["severities"].get(x, 0) for x in levels]

        ax1.bar(levels, values, color=[
            "#36C995", "#3988FF", "#F5A64A", "#FF5B68"
        ])
        ax1.set_title("Severity Distribution", color="white")
        ax1.tick_params(colors="white")
        ax1.set_facecolor("#111F30")

        sources = list(stats["sources"].keys())
        counts = list(stats["sources"].values())

        ax2.barh(sources, counts, color="#18B9A5")
        ax2.set_title("Events by Source", color="white")
        ax2.tick_params(colors="white")
        ax2.set_facecolor("#111F30")

        figure.tight_layout()

        canvas = FigureCanvasTkAgg(figure, master=self.content)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)

        ctk.CTkLabel(
            self.content,
            text=f"Total events: {len(self.events)}  |  "
                 f"Unique sources: {len(sources)}",
            text_color=MUTED
        ).pack(pady=8)

    # ---------------- INCIDENT DETECTION ----------------

    def show_incidents(self):

        self.clear_content()
        self.section_title(
            self.content, "Incident Detection",
            "Identify groups of related events within configured time windows."
        )

        controls = ctk.CTkFrame(self.content, fg_color=CARD, corner_radius=10)
        controls.pack(fill="x", pady=8)

        minutes = ctk.CTkEntry(
            controls, placeholder_text="Window minutes (default 10)", width=200
        )
        minutes.pack(side="left", padx=10, pady=10)
        minutes.insert(0, "10")

        tree = self.get_table(
            self.content,
            ("start", "end", "event_count", "sources"),
            height=13
        )

        def detect():
            try:
                window_size = int(minutes.get())
                if window_size < 1:
                    raise ValueError("Minutes must be greater than zero.")

                tree.delete(*tree.get_children())

                windows = incident_windows(
                    self.events, minutes=window_size, min_events=2
                )

                for window in windows:
                    items = window.get("events", [])
                    sources = ", ".join(sorted({
                        str(e.get("source", "")) for e in items
                    }))

                    tree.insert("", "end", values=(
                        window.get("start", ""),
                        window.get("end", ""),
                        len(items),
                        sources
                    ))

                messagebox.showinfo(
                    "Detection Complete",
                    f"{len(windows)} candidate time windows detected."
                )

            except Exception as error:
                messagebox.showerror("Detection Error", str(error))

        ctk.CTkButton(
            controls, text="Detect Incidents",
            fg_color=ACCENT, text_color="#06151B",
            command=detect
        ).pack(side="left", padx=8)

        detect()

    # ---------------- REPORTS ----------------

    def show_reports(self):

        self.clear_content()
        self.section_title(
            self.content, "Investigation Reports",
            "Export the currently imported evidence and summary statistics."
        )

        if not self.events:
            ctk.CTkLabel(
                self.content, text="Import a CSV dataset before exporting.",
                text_color=MUTED
            ).pack(pady=40)
            return

        stats = hash_statistics(self.events)

        ctk.CTkLabel(
            self.content,
            text=f"Records ready for export: {len(self.events)}",
            text_color=TEXT, font=("Arial", 16, "bold")
        ).pack(anchor="w", padx=10, pady=15)

        def export_csv():
            path = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV Report", "*.csv")]
            )
            if not path:
                return

            with open(path, "w", newline="", encoding="utf-8") as file:
                writer = csv.DictWriter(
                    file,
                    fieldnames=[
                        "timestamp", "source", "event_type",
                        "severity", "details"
                    ]
                )
                writer.writeheader()
                writer.writerows(self.events)

            messagebox.showinfo("Export", "CSV report saved successfully.")

        def export_json():
            path = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("JSON Report", "*.json")]
            )
            if not path:
                return

            report = {
                "application": APP_NAME,
                "developer": AUTHOR,
                "university": UNIVERSITY,
                "generated_at": datetime.now().isoformat(),
                "total_events": len(self.events),
                "statistics": stats,
                "events": self.events
            }

            with open(path, "w", encoding="utf-8") as file:
                json.dump(report, file, indent=4, default=str)

            messagebox.showinfo("Export", "JSON report saved successfully.")

        ctk.CTkButton(
            self.content, text="Export CSV Report",
            height=45, width=240, command=export_csv,
            fg_color=ACCENT, text_color="#06151B"
        ).pack(anchor="w", padx=10, pady=10)

        ctk.CTkButton(
            self.content, text="Export JSON Investigation",
            height=45, width=240, command=export_json
        ).pack(anchor="w", padx=10, pady=10)

    # ---------------- INFORMATION ----------------

    def show_information(self):

        self.clear_content()

        self.section_title(
            self.content, "Project Information",
            "Developer identity, university and technical overview."
        )

        details = [
            ("PROJECT", APP_NAME),
            ("EDITION", "Advanced Digital Forensics GUI"),
            ("DEVELOPER", AUTHOR),
            ("UNIVERSITY", UNIVERSITY),
            ("CORE", "Python / CustomTkinter / Matplotlib"),
            ("DSA", "Merge Sort, Binary Search, Hash Map, Heap"),
            ("PURPOSE", "Educational CSV-based forensic log analysis"),
            ("DATA SOURCE", "User-imported CSV log files")
        ]

        for label, value in details:
            card = ctk.CTkFrame(
                self.content, fg_color=CARD, corner_radius=9
            )
            card.pack(fill="x", padx=7, pady=5)

            ctk.CTkLabel(
                card, text=label, width=140, anchor="w",
                text_color=ACCENT, font=("Arial", 11, "bold")
            ).pack(side="left", padx=15, pady=12)

            ctk.CTkLabel(
                card, text=value, anchor="w",
                text_color=TEXT, font=("Arial", 11)
            ).pack(side="left", padx=10)

        ctk.CTkLabel(
            self.content,
            text="EDUCATIONAL PROTOTYPE • NOT A LIVE MONITORING SYSTEM",
            text_color=ORANGE, font=("Arial", 11, "bold")
        ).pack(anchor="w", padx=10, pady=20)


if __name__ == "__main__":
    app = ForensicApp()
    app.mainloop()
