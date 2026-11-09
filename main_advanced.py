import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
from datetime import datetime
import json
import csv

import advanced_core as dbcore

from forensic_core import (
    load_events,
    merge_sort,
    binary_search,
    hash_statistics,
    top_n_events,
    merge_sorted_sources,
    incident_windows
)

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

BASE = Path(__file__).resolve().parent
AUTHOR = "ABDUL SAMAD"
UNIVERSITY = "AROR UNIVERSITY OF ART, ARCHITECTURE, DESIGN & HERITAGE, SUKKUR"

BG = "#080F1B"
PANEL = "#111F30"
PANEL2 = "#172B40"
ACCENT = "#18B9A5"
TEXT = "#EAF2FA"
MUTED = "#91A6BA"
RED = "#FF6573"
ORANGE = "#F5AD50"
GREEN = "#36C995"
BLUE = "#4D9BFF"


class ForensicApp(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.title("FORENSICTIMELINE PRO | Digital Forensics Suite")
        self.geometry("1500x900")
        self.minsize(1150, 720)
        self.configure(fg_color=BG)

        self.events = []
        self.dataset_name = "No dataset imported"
        self.selected_case = None
        self.selected_evidence = None

        self.build_sidebar()
        self.build_workspace()
        self.show_page("Dashboard")

    # ---------------- COMMON UI ----------------

    def build_sidebar(self):
        side = ctk.CTkFrame(self, width=245, fg_color="#0C1725", corner_radius=0)
        side.pack(side="left", fill="y")
        side.pack_propagate(False)

        logo = ctk.CTkFrame(
            side, width=62, height=62,
            fg_color=ACCENT, corner_radius=17
        )
        logo.pack(pady=(25, 9))
        logo.pack_propagate(False)

        ctk.CTkLabel(
            logo, text="AS", text_color="#06151B",
            font=("Arial", 25, "bold")
        ).place(relx=.5, rely=.5, anchor="center")

        ctk.CTkLabel(
            side, text="FORENSICTIMELINE",
            font=("Arial", 17, "bold"), text_color=TEXT
        ).pack()

        ctk.CTkLabel(
            side, text="PRO  •  ADVANCED EDITION",
            font=("Arial", 10), text_color=ACCENT
        ).pack(pady=(3, 22))

        self.nav = {}
        pages = [
            ("Dashboard", "▦"),
            ("Case Management", "▣"),
            ("Evidence Integrity", "◈"),
            ("Chain of Custody", "⇄"),
            ("Event Timeline", "◷"),
            ("Threat Analytics", "▥"),
            ("Incident Detection", "⚠"),
            ("Reports Center", "▤"),
            ("Audit Trail", "≡"),
            ("Project Information", "ⓘ")
        ]

        for name, symbol in pages:
            button = ctk.CTkButton(
                side, text=f"  {symbol}    {name}",
                anchor="w", height=39,
                fg_color="transparent", hover_color=PANEL2,
                text_color=TEXT, corner_radius=8,
                font=("Arial", 12),
                command=lambda p=name: self.show_page(p)
            )
            button.pack(fill="x", padx=12, pady=2)
            self.nav[name] = button

        ctk.CTkButton(
            side, text="+  IMPORT LOG CSV",
            fg_color=ACCENT, hover_color="#109887",
            text_color="#06151B", height=42,
            font=("Arial", 12, "bold"),
            command=self.import_csv
        ).pack(fill="x", padx=12, pady=(18, 8))

        ctk.CTkLabel(
            side,
            text="DEVELOPED BY\nABDUL SAMAD\n\nAROR UNIVERSITY\nSUKKUR",
            text_color=MUTED, font=("Arial", 10),
            justify="left"
        ).pack(side="bottom", anchor="w", padx=18, pady=22)

    def build_workspace(self):
        self.workspace = ctk.CTkFrame(self, fg_color=BG, corner_radius=0)
        self.workspace.pack(side="right", fill="both", expand=True)

        header = ctk.CTkFrame(self.workspace, fg_color=BG, height=72)
        header.pack(fill="x", padx=28, pady=(12, 3))
        header.pack_propagate(False)

        self.page_title = ctk.CTkLabel(
            header, text="Dashboard",
            font=("Arial", 25, "bold"), text_color=TEXT
        )
        self.page_title.pack(side="left", anchor="center")

        self.system_status = ctk.CTkLabel(
            header, text="● DATABASE ONLINE",
            font=("Arial", 11, "bold"), text_color=GREEN
        )
        self.system_status.pack(side="right", padx=12)

        self.dataset_label = ctk.CTkLabel(
            self.workspace, text="Dataset: No dataset imported",
            font=("Arial", 10), text_color=MUTED
        )
        self.dataset_label.pack(anchor="w", padx=31, pady=(0, 5))

        self.body = ctk.CTkFrame(self.workspace, fg_color=BG)
        self.body.pack(fill="both", expand=True, padx=25, pady=10)

    def clear(self):
        for widget in self.body.winfo_children():
            widget.destroy()

    def heading(self, title, subtitle=""):
        ctk.CTkLabel(
            self.body, text=title,
            font=("Arial", 18, "bold"), text_color=TEXT
        ).pack(anchor="w", padx=5, pady=(5, 2))

        if subtitle:
            ctk.CTkLabel(
                self.body, text=subtitle,
                font=("Arial", 11), text_color=MUTED
            ).pack(anchor="w", padx=5, pady=(0, 10))

    def button(self, parent, text, command, color=ACCENT, width=150):
        return ctk.CTkButton(
            parent, text=text, command=command,
            fg_color=color,
            hover_color="#108C7E" if color == ACCENT else PANEL2,
            text_color="#06151B" if color == ACCENT else TEXT,
            width=width, height=36, corner_radius=8,
            font=("Arial", 11, "bold")
        )

    def entry(self, parent, placeholder, width=220):
        return ctk.CTkEntry(
            parent, placeholder_text=placeholder,
            width=width, height=36
        )

    def table(self, parent, columns, headings=None, height=12):
        frame = ctk.CTkFrame(parent, fg_color=PANEL, corner_radius=10)
        frame.pack(fill="both", expand=True, padx=5, pady=7)

        tree = ttk.Treeview(
            frame, columns=columns, show="headings", height=height
        )

        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "Treeview", background=PANEL, foreground=TEXT,
            fieldbackground=PANEL, rowheight=29,
            borderwidth=0, font=("Arial", 10)
        )
        style.configure(
            "Treeview.Heading", background=PANEL2,
            foreground=TEXT, font=("Arial", 10, "bold")
        )
        style.map("Treeview", background=[("selected", "#176A78")])

        for col in columns:
            tree.heading(col, text=(headings or {}).get(col, col.upper()))
            tree.column(col, width=145, minwidth=75)

        ybar = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        xbar = ttk.Scrollbar(frame, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=ybar.set, xscrollcommand=xbar.set)

        tree.pack(side="top", fill="both", expand=True, padx=7, pady=(7, 0))
        xbar.pack(side="bottom", fill="x", padx=7)
        ybar.pack(side="right", fill="y", pady=7)

        return tree

    def stat_card(self, parent, title, value, color=ACCENT):
        card = ctk.CTkFrame(parent, fg_color=PANEL, corner_radius=12)
        card.pack(side="left", fill="both", expand=True, padx=5)
        ctk.CTkLabel(
            card, text=title.upper(), text_color=MUTED,
            font=("Arial", 10, "bold")
        ).pack(anchor="w", padx=14, pady=(13, 3))
        ctk.CTkLabel(
            card, text=str(value), text_color=color,
            font=("Arial", 27, "bold")
        ).pack(anchor="w", padx=14, pady=(0, 13))
        return card

    def show_page(self, name):
        for page, btn in self.nav.items():
            btn.configure(fg_color=PANEL2 if page == name else "transparent")

        self.page_title.configure(text=name)

        methods = {
            "Dashboard": self.page_dashboard,
            "Case Management": self.page_cases,
            "Evidence Integrity": self.page_evidence,
            "Chain of Custody": self.page_custody,
            "Event Timeline": self.page_timeline,
            "Threat Analytics": self.page_analytics,
            "Incident Detection": self.page_incidents,
            "Reports Center": self.page_reports,
            "Audit Trail": self.page_audit,
            "Project Information": self.page_info
        }
        methods[name]()

    # ---------------- DASHBOARD ----------------

    def page_dashboard(self):
        self.clear()
        self.heading(
            "Investigation Command Center",
            "Overview of cases, evidence records and imported forensic events."
        )

        cases = dbcore.list_cases()
        evidence = dbcore.list_evidence()
        audit = dbcore.list_audit()

        stats = hash_statistics(self.events) if self.events else {
            "sources": {}, "event_types": {}, "severities": {}
        }

        row = ctk.CTkFrame(self.body, fg_color=BG)
        row.pack(fill="x", pady=8)

        self.stat_card(row, "Investigation Cases", len(cases), BLUE)
        self.stat_card(row, "Evidence Records", len(evidence), ACCENT)
        self.stat_card(row, "Imported Events", len(self.events), GREEN)
        self.stat_card(
            row, "Critical Events",
            stats["severities"].get("CRITICAL", 0), RED
        )

        row2 = ctk.CTkFrame(self.body, fg_color=BG)
        row2.pack(fill="x", pady=3)
        self.stat_card(row2, "Log Sources", len(stats["sources"]), BLUE)
        self.stat_card(row2, "Audit Entries", len(audit), ORANGE)
        self.stat_card(
            row2, "Open Cases",
            sum(c["status"] == "Open" for c in cases), GREEN
        )

        self.heading("Recent Forensic Events", "Latest imported CSV records.")
        tree = self.table(
            self.body,
            ("timestamp", "source", "event_type", "severity", "details"),
            height=8
        )

        for event in sorted(
            self.events, key=lambda x: x["timestamp"], reverse=True
        )[:8]:
            tree.insert("", "end", values=(
                event["timestamp"], event["source"],
                event["event_type"], event["severity"],
                event["details"]
            ))

    # ---------------- CASE MANAGEMENT ----------------

    def page_cases(self):
        self.clear()
        self.heading(
            "Case Management",
            "Create and manage local investigation case records."
        )

        form = ctk.CTkFrame(self.body, fg_color=PANEL, corner_radius=10)
        form.pack(fill="x", padx=5, pady=8)

        title = self.entry(form, "Investigation title", 240)
        title.pack(side="left", padx=8, pady=12)

        investigator = self.entry(form, "Investigator name", 190)
        investigator.pack(side="left", padx=8, pady=12)

        description = self.entry(form, "Short case description", 260)
        description.pack(side="left", padx=8, pady=12)

        tree = self.table(
            self.body,
            ("case_id", "title", "investigator", "status", "created_at"),
            height=13
        )

        def refresh():
            tree.delete(*tree.get_children())
            for case in dbcore.list_cases():
                tree.insert("", "end", values=(
                    case["case_id"], case["title"],
                    case["investigator"], case["status"],
                    case["created_at"]
                ))

        def create():
            if not title.get().strip():
                messagebox.showwarning("Missing title", "Enter a case title.")
                return
            try:
                case_id = dbcore.create_case(
                    title.get().strip(),
                    investigator.get().strip() or AUTHOR,
                    description.get().strip()
                )
                messagebox.showinfo("Case created", f"Case ID:\n{case_id}")
                title.delete(0, "end")
                investigator.delete(0, "end")
                description.delete(0, "end")
                refresh()
            except Exception as exc:
                messagebox.showerror("Case error", str(exc))

        def change_status(status):
            selected = tree.selection()
            if not selected:
                messagebox.showwarning("Select case", "Select a case first.")
                return
            case_id = tree.item(selected[0], "values")[0]
            dbcore.update_case_status(case_id, status)
            refresh()

        self.button(form, "Create Case", create).pack(side="left", padx=8)

        controls = ctk.CTkFrame(self.body, fg_color=BG)
        controls.pack(fill="x", padx=5)

        self.button(
            controls, "Mark Under Review",
            lambda: change_status("Under Review"), BLUE
        ).pack(side="left", padx=4, pady=5)

        self.button(
            controls, "Close Case",
            lambda: change_status("Closed"), ORANGE
        ).pack(side="left", padx=4, pady=5)

        self.button(
            controls, "Reopen Case",
            lambda: change_status("Open"), GREEN
        ).pack(side="left", padx=4, pady=5)

        refresh()

    # ---------------- EVIDENCE INTEGRITY ----------------

    def page_evidence(self):
        self.clear()
        self.heading(
            "Evidence Integrity Laboratory",
            "Register evidence files and verify their SHA-256 integrity."
        )

        cases = dbcore.list_cases()
        if not cases:
            ctk.CTkLabel(
                self.body, text="Create an investigation case first.",
                text_color=ORANGE
            ).pack(pady=30)
            return

        case_options = [
            f'{c["case_id"]} | {c["title"]}' for c in cases
        ]

        case_menu = ctk.CTkOptionMenu(
            self.body, values=case_options, width=360
        )
        case_menu.pack(anchor="w", padx=8, pady=6)

        person = self.entry(self.body, "Registered by / investigator", 300)
        person.pack(anchor="w", padx=8, pady=6)
        person.insert(0, AUTHOR)

        selected_path = {"value": None}
        path_label = ctk.CTkLabel(
            self.body, text="No evidence file selected",
            text_color=MUTED
        )
        path_label.pack(anchor="w", padx=8, pady=4)

        tree = self.table(
            self.body,
            ("evidence_id", "case_id", "filename", "sha256", "size_bytes", "added_at"),
            {"evidence_id": "ID", "case_id": "CASE",
             "filename": "FILENAME", "sha256": "SHA-256",
             "size_bytes": "SIZE (BYTES)", "added_at": "REGISTERED"},
            height=9
        )

        def refresh():
            tree.delete(*tree.get_children())
            for item in dbcore.list_evidence():
                tree.insert("", "end", values=(
                    item["evidence_id"], item["case_id"], item["filename"],
                    item["sha256"], item["size_bytes"], item["added_at"]
                ))

        def choose_file():
            path = filedialog.askopenfilename(title="Select evidence file")
            if path:
                selected_path["value"] = path
                path_label.configure(text=path, text_color=TEXT)

        def register():
            path = selected_path["value"]
            if not path:
                messagebox.showwarning("Select file", "Choose a file first.")
                return
            case_id = case_menu.get().split(" | ")[0]
            try:
                evidence_id, digest = dbcore.add_evidence(
                    case_id, path, person.get().strip() or AUTHOR
                )
                messagebox.showinfo(
                    "Evidence registered",
                    f"Evidence ID: {evidence_id}\n\nSHA-256:\n{digest}"
                )
                selected_path["value"] = None
                path_label.configure(text="No evidence file selected")
                refresh()
            except Exception as exc:
                messagebox.showerror("Registration error", str(exc))

        def verify():
            selected = tree.selection()
            if not selected:
                messagebox.showwarning("Select evidence", "Select a record.")
                return
            evidence_id = int(tree.item(selected[0], "values")[0])
            try:
                result = dbcore.verify_evidence(evidence_id)
                if not result["exists"]:
                    messagebox.showwarning(
                        "File unavailable",
                        "Original evidence file cannot be found at its saved path."
                    )
                elif result["match"]:
                    messagebox.showinfo(
                        "Integrity verified",
                        "SHA-256 MATCH\nThe current file hash matches the registered hash."
                    )
                else:
                    messagebox.showerror(
                        "Integrity mismatch",
                        "SHA-256 MISMATCH\nThe file differs from its registered state."
                    )
            except Exception as exc:
                messagebox.showerror("Verification error", str(exc))

        controls = ctk.CTkFrame(self.body, fg_color=BG)
        controls.pack(fill="x", padx=5, pady=4)

        self.button(controls, "Choose Evidence File", choose_file, BLUE).pack(
            side="left", padx=4
        )
        self.button(controls, "Register & Hash", register).pack(
            side="left", padx=4
        )
        self.button(controls, "Verify Selected Hash", verify, ORANGE).pack(
            side="left", padx=4
        )

        tree.bind(
            "<<TreeviewSelect>>",
            lambda event: setattr(
                self, "selected_evidence",
                tree.item(tree.selection()[0], "values")[0]
            ) if tree.selection() else None
        )

        refresh()

    # ---------------- CHAIN OF CUSTODY ----------------

    def page_custody(self):
        self.clear()
        self.heading(
            "Chain of Custody",
            "Record evidence handling actions and review their history."
        )

        evidence = dbcore.list_evidence()
        if not evidence:
            ctk.CTkLabel(
                self.body, text="Register evidence before adding custody records.",
                text_color=ORANGE
            ).pack(pady=30)
            return

        options = [
            f'{e["evidence_id"]} | {e["filename"]}' for e in evidence
        ]

        selector = ctk.CTkOptionMenu(
            self.body, values=options, width=360
        )
        selector.pack(anchor="w", padx=8, pady=6)

        action = ctk.CTkOptionMenu(
            self.body,
            values=["TRANSFERRED", "ACCESSED", "EXAMINED", "STORED", "RETURNED"],
            width=220
        )
        action.pack(anchor="w", padx=8, pady=6)

        person = self.entry(self.body, "Person handling evidence", 300)
        person.pack(anchor="w", padx=8, pady=6)
        person.insert(0, AUTHOR)

        notes = self.entry(self.body, "Notes about this action", 450)
        notes.pack(anchor="w", padx=8, pady=6)

        tree = self.table(
            self.body,
            ("custody_id", "evidence_id", "action", "person", "notes", "action_time"),
            {"custody_id": "RECORD", "evidence_id": "EVIDENCE ID",
             "action": "ACTION", "person": "PERSON",
             "notes": "NOTES", "action_time": "TIME"},
            height=11
        )

        def refresh():
            tree.delete(*tree.get_children())
            for item in dbcore.list_custody():
                tree.insert("", "end", values=(
                    item["custody_id"], item["evidence_id"],
                    item["action"], item["person"],
                    item["notes"], item["action_time"]
                ))

        def record():
            try:
                evidence_id = int(selector.get().split(" | ")[0])
                dbcore.add_custody(
                    evidence_id, action.get(),
                    person.get().strip() or AUTHOR,
                    notes.get().strip()
                )
                messagebox.showinfo("Recorded", "Custody action saved.")
                notes.delete(0, "end")
                refresh()
            except Exception as exc:
                messagebox.showerror("Custody error", str(exc))

        self.button(self.body, "Record Custody Action", record).pack(
            anchor="w", padx=8, pady=8
        )
        refresh()

    # ---------------- CSV EVENT TIMELINE ----------------

    def import_csv(self):
        path = filedialog.askopenfilename(
            title="Import forensic CSV",
            filetypes=[("CSV files", "*.csv")]
        )
        if not path:
            return
        try:
            self.events = load_events(path)
            self.dataset_name = Path(path).name
            self.dataset_label.configure(
                text=f"Dataset: {self.dataset_name} | {len(self.events)} events"
            )
            dbcore.audit("CSV IMPORTED", f"{self.dataset_name}: {len(self.events)} events")
            messagebox.showinfo(
                "Import successful", f"{len(self.events)} events loaded."
            )
            self.show_page("Dashboard")
        except Exception as exc:
            messagebox.showerror("CSV import failed", str(exc))

    def page_timeline(self):
        self.clear()
        self.heading(
            "Forensic Event Timeline",
            "Sort, search and filter imported CSV events."
        )

        controls = ctk.CTkFrame(self.body, fg_color=PANEL, corner_radius=10)
        controls.pack(fill="x", pady=6)

        search = self.entry(controls, "Search events...", 280)
        search.pack(side="left", padx=8, pady=10)

        severity = ctk.CTkOptionMenu(
            controls, values=["ALL", "LOW", "MEDIUM", "HIGH", "CRITICAL"]
        )
        severity.pack(side="left", padx=8)

        tree = self.table(
            self.body,
            ("timestamp", "source", "event_type", "severity", "details"),
            height=16
        )

        def populate():
            tree.delete(*tree.get_children())
            term = search.get().lower().strip()
            level = severity.get()

            for event in merge_sort(self.events):
                combined = " ".join(str(v) for v in event.values()).lower()
                if term and term not in combined:
                    continue
                if level != "ALL" and event["severity"] != level:
                    continue
                tree.insert("", "end", values=(
                    event["timestamp"], event["source"],
                    event["event_type"], event["severity"],
                    event["details"]
                ))

        self.button(controls, "Apply", populate).pack(side="left", padx=5)
        self.button(
            controls, "Reset",
            lambda: (search.delete(0, "end"), severity.set("ALL"), populate()),
            BLUE
        ).pack(side="left", padx=5)

        populate()

    # ---------------- ANALYTICS ----------------

    def page_analytics(self):
        self.clear()
        self.heading(
            "Threat Analytics",
            "Charts are generated from the currently imported CSV dataset."
        )

        if not self.events:
            ctk.CTkLabel(
                self.body, text="Import a CSV dataset to view analytics.",
                text_color=ORANGE
            ).pack(pady=35)
            return

        from matplotlib.figure import Figure
        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

        stats = hash_statistics(self.events)
        figure = Figure(figsize=(10, 5.5), dpi=100, facecolor=PANEL)

        ax1 = figure.add_subplot(221)
        ax2 = figure.add_subplot(222)
        ax3 = figure.add_subplot(212)

        levels = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
        values = [stats["severities"].get(x, 0) for x in levels]

        ax1.bar(levels, values, color=["#36C995", "#4D9BFF", "#F5AD50", "#FF6573"])
        ax1.set_title("Severity Distribution", color="white")
        ax1.tick_params(colors="white")
        ax1.set_facecolor(PANEL)

        sources = list(stats["sources"].keys())
        counts = list(stats["sources"].values())
        ax2.bar(sources, counts, color="#18B9A5")
        ax2.set_title("Events by Source", color="white")
        ax2.tick_params(colors="white", labelrotation=15)
        ax2.set_facecolor(PANEL)

        types = list(stats["event_types"].keys())
        type_counts = list(stats["event_types"].values())
        ax3.bar(types, type_counts, color="#6689CF")
        ax3.set_title("Event Type Frequency", color="white")
        ax3.tick_params(colors="white", labelrotation=15)
        ax3.set_facecolor(PANEL)

        figure.tight_layout(pad=2)

        canvas = FigureCanvasTkAgg(figure, master=self.body)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=8, pady=8)

    # ---------------- INCIDENT DETECTION ----------------

    def page_incidents(self):
        self.clear()
        self.heading(
            "Incident Detection",
            "Time-window grouping identifies candidate event clusters for manual review."
        )

        if not self.events:
            ctk.CTkLabel(
                self.body, text="Import CSV to run incident detection.",
                text_color=ORANGE
            ).pack(pady=35)
            return

        controls = ctk.CTkFrame(self.body, fg_color=PANEL, corner_radius=10)
        controls.pack(fill="x", pady=6)

        minutes = self.entry(controls, "Window minutes", 160)
        minutes.pack(side="left", padx=8, pady=10)
        minutes.insert(0, "10")

        tree = self.table(
            self.body,
            ("start", "end", "event_count", "sources"),
            height=15
        )

        def detect():
            try:
                size = int(minutes.get())
                if size < 1:
                    raise ValueError("Window must be at least one minute.")

                tree.delete(*tree.get_children())
                windows = incident_windows(
                    self.events, minutes=size, min_events=2
                )

                for window in windows:
                    grouped = window.get("events", [])
                    sources = ", ".join(sorted({
                        str(e.get("source", "")) for e in grouped
                    }))
                    tree.insert("", "end", values=(
                        window.get("start", ""),
                        window.get("end", ""),
                        len(grouped), sources
                    ))

                dbcore.audit(
                    "INCIDENT ANALYSIS",
                    f"{len(windows)} candidate windows, {size} minutes"
                )
                messagebox.showinfo(
                    "Analysis complete",
                    f"{len(windows)} candidate windows found."
                )
            except Exception as exc:
                messagebox.showerror("Detection error", str(exc))

        self.button(controls, "Run Detection", detect).pack(
            side="left", padx=8
        )
        detect()

    # ---------------- REPORTS ----------------

    def page_reports(self):
        self.clear()
        self.heading(
            "Reports Center",
            "Generate local investigation snapshots in PDF, JSON or CSV format."
        )

        ctk.CTkLabel(
            self.body,
            text="Case database records and imported event data can be exported.",
            text_color=MUTED
        ).pack(anchor="w", padx=8, pady=8)

        def export_json():
            path = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("JSON report", "*.json")]
            )
            if not path:
                return
            with open(path, "w", encoding="utf-8") as file:
                json.dump(dbcore.report_snapshot(), file, indent=4)
            dbcore.audit("JSON REPORT EXPORTED", path)
            messagebox.showinfo("Export", "JSON report saved.")

        def export_csv():
            path = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV report", "*.csv")]
            )
            if not path:
                return
            fields = ["timestamp", "source", "event_type", "severity", "details"]
            with open(path, "w", newline="", encoding="utf-8") as file:
                writer = csv.DictWriter(file, fieldnames=fields)
                writer.writeheader()
                writer.writerows(self.events)
            dbcore.audit("EVENT CSV EXPORTED", path)
            messagebox.showinfo("Export", "Event CSV report saved.")

        def export_pdf():
            try:
                from reportlab.lib import colors
                from reportlab.lib.pagesizes import A4, landscape
                from reportlab.lib.styles import getSampleStyleSheet
                from reportlab.platypus import (
                    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
                )
            except ImportError:
                messagebox.showerror(
                    "Missing library",
                    "Install reportlab using: pip install reportlab"
                )
                return

            path = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                filetypes=[("PDF report", "*.pdf")]
            )
            if not path:
                return

            snapshot = dbcore.report_snapshot()
            styles = getSampleStyleSheet()
            doc = SimpleDocTemplate(
                path, pagesize=landscape(A4),
                rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30
            )

            story = [
                Paragraph("FORENSICTIMELINE PRO", styles["Title"]),
                Paragraph("Digital Forensics Investigation Report", styles["Heading2"]),
                Spacer(1, 10),
                Paragraph(f"Developer: {AUTHOR}", styles["Normal"]),
                Paragraph(UNIVERSITY, styles["Normal"]),
                Paragraph(f"Generated: {snapshot['generated_at']}", styles["Normal"]),
                Spacer(1, 12),
                Paragraph("Investigation Cases", styles["Heading2"])
            ]

            case_data = [["Case ID", "Title", "Investigator", "Status"]]
            for c in snapshot["cases"]:
                case_data.append([
                    c["case_id"], c["title"], c["investigator"], c["status"]
                ])

            if len(case_data) == 1:
                case_data.append(["No cases", "-", "-", "-"])

            case_table = Table(case_data, repeatRows=1)
            case_table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#17334A")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("GRID", (0, 0), (-1, -1), .4, colors.grey),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1),
                 [colors.white, colors.HexColor("#EAF1F5")])
            ]))
            story.extend([case_table, Spacer(1, 14)])

            story.append(Paragraph("Registered Evidence", styles["Heading2"]))
            evidence_data = [["ID", "Case", "Filename", "SHA-256"]]
            for e in snapshot["evidence"]:
                evidence_data.append([
                    str(e["evidence_id"]), e["case_id"],
                    e["filename"], e["sha256"]
                ])
            if len(evidence_data) == 1:
                evidence_data.append(["-", "-", "No evidence", "-"])

            evidence_table = Table(
                evidence_data, repeatRows=1,
                colWidths=[35, 125, 170, 390]
            )
            evidence_table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#17334A")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("GRID", (0, 0), (-1, -1), .4, colors.grey),
                ("FONTSIZE", (0, 0), (-1, -1), 7),
                ("WORDWRAP", (0, 0), (-1, -1), True)
            ]))
            story.extend([evidence_table, Spacer(1, 14)])

            story.append(Paragraph("Imported Event Summary", styles["Heading2"]))
            if self.events:
                stats = hash_statistics(self.events)
                story.append(Paragraph(
                    f"Total events: {len(self.events)} | "
                    f"Unique sources: {len(stats['sources'])} | "
                    f"Event types: {len(stats['event_types'])}",
                    styles["Normal"]
                ))
                severity_data = [["Severity", "Count"]]
                for level in ["LOW", "MEDIUM", "HIGH", "CRITICAL"]:
                    severity_data.append([
                        level, str(stats["severities"].get(level, 0))
                    ])
                story.append(Table(severity_data))
            else:
                story.append(Paragraph("No CSV event dataset currently loaded.", styles["Normal"]))

            story.extend([
                Spacer(1, 16),
                Paragraph(
                    "Educational prototype. Report contents reflect locally registered records "
                    "and the currently imported CSV dataset. Validate evidence and findings "
                    "independently before relying on them.",
                    styles["Italic"]
                )
            ])

            doc.build(story)
            dbcore.audit("PDF REPORT EXPORTED", path)
            messagebox.showinfo("PDF generated", "Investigation PDF saved.")

        self.button(
            self.body, "Export Full PDF Report", export_pdf, ACCENT, 250
        ).pack(anchor="w", padx=10, pady=8)

        self.button(
            self.body, "Export Database Snapshot (JSON)", export_json, BLUE, 250
        ).pack(anchor="w", padx=10, pady=8)

        self.button(
            self.body, "Export Imported Events (CSV)", export_csv, ORANGE, 250
        ).pack(anchor="w", padx=10, pady=8)

    # ---------------- AUDIT TRAIL ----------------

    def page_audit(self):
        self.clear()
        self.heading(
            "Application Audit Trail",
            "Review recorded case, evidence, verification and export actions."
        )

        tree = self.table(
            self.body,
            ("audit_id", "action", "details", "action_time"),
            {"audit_id": "ID", "action": "ACTION",
             "details": "DETAILS", "action_time": "TIMESTAMP"},
            height=17
        )

        for item in dbcore.list_audit():
            tree.insert("", "end", values=(
                item["audit_id"], item["action"],
                item["details"], item["action_time"]
            ))

    # ---------------- INFORMATION ----------------

    def page_info(self):
        self.clear()
        self.heading(
            "Project Information",
            "Technical profile and application information."
        )

        details = [
            ("APPLICATION", "ForensicTimeline PRO"),
            ("EDITION", "Advanced Digital Forensics Suite"),
            ("DEVELOPER", AUTHOR),
            ("UNIVERSITY", UNIVERSITY),
            ("INTERFACE", "Python + CustomTkinter"),
            ("DATABASE", "SQLite"),
            ("VISUALIZATION", "Matplotlib"),
            ("INTEGRITY", "SHA-256"),
            ("DSA", "Merge Sort, Binary Search, Hash Map, Top-N Heap, Min-Heap Merge, Incident Windows"),
            ("INPUT", "User-imported CSV and registered local evidence files"),
            ("PURPOSE", "Educational digital forensics and log analysis")
        ]

        for label, value in details:
            row = ctk.CTkFrame(self.body, fg_color=PANEL, corner_radius=8)
            row.pack(fill="x", padx=6, pady=4)

            ctk.CTkLabel(
                row, text=label, width=155, anchor="w",
                text_color=ACCENT, font=("Arial", 10, "bold")
            ).pack(side="left", padx=13, pady=12)

            ctk.CTkLabel(
                row, text=value, anchor="w",
                text_color=TEXT, font=("Arial", 10)
            ).pack(side="left", padx=8)

        ctk.CTkLabel(
            self.body,
            text="EDUCATIONAL PROTOTYPE • CSV-BASED ANALYSIS • NOT LIVE MONITORING",
            text_color=ORANGE, font=("Arial", 11, "bold")
        ).pack(anchor="w", padx=10, pady=18)


if __name__ == "__main__":
    app = ForensicApp()
    app.mainloop()
