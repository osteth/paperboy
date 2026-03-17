#!/usr/bin/env python3
"""
Paperboy - Configuration GUI
A Tkinter app for managing print routing rules.
"""

import json
import subprocess
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

CONFIG_PATH = Path.home() / ".config" / "paperboy" / "config.json"

PAPER_SIZES = {
    "4x6 Label":         (288.0, 432.0),
    "4x4 Label":         (288.0, 288.0),
    "3x3 Label":         (216.0, 216.0),
    "2x7 Label":         (144.0, 504.0),
    "5x7":               (360.0, 504.0),
    "Letter (8.5x11)":   (612.0, 792.0),
    "A4":                (595.0, 842.0),
    "Legal (8.5x14)":    (612.0, 1008.0),
    "Any (default)":     (None,  None),
}

COLOR_OPTIONS = {
    "Any":                "any",
    "Color only":         "color",
    "Black & White only": "bw",
}

TERMINALS = ["gnome-terminal", "xterm", "konsole", "xfce4-terminal", "lxterminal"]

# Catppuccin Mocha
C = {
    "base":     "#1e1e2e",
    "mantle":   "#181825",
    "crust":    "#11111b",
    "surface0": "#313244",
    "surface1": "#45475a",
    "surface2": "#585b70",
    "overlay0": "#6c7086",
    "overlay1": "#7f849c",
    "text":     "#cdd6f4",
    "subtext0": "#a6adc8",
    "subtext1": "#bac2de",
    "blue":     "#89b4fa",
    "green":    "#a6e3a1",
    "red":      "#f38ba8",
    "yellow":   "#f9e2af",
}


# ---------------------------------------------------------------------------
# Theme
# ---------------------------------------------------------------------------

def apply_theme(root: tk.Tk) -> None:
    style = ttk.Style(root)
    style.theme_use("clam")

    root.configure(bg=C["base"])

    # Combobox dropdown colours (Tk Listbox, not ttk)
    root.option_add("*TCombobox*Listbox.background",       C["surface0"])
    root.option_add("*TCombobox*Listbox.foreground",       C["text"])
    root.option_add("*TCombobox*Listbox.selectBackground", C["blue"])
    root.option_add("*TCombobox*Listbox.selectForeground", C["crust"])

    style.configure(".",
        background=C["base"],
        foreground=C["text"],
        fieldbackground=C["mantle"],
        bordercolor=C["surface1"],
        darkcolor=C["surface0"],
        lightcolor=C["surface0"],
        troughcolor=C["surface0"],
        selectbackground=C["blue"],
        selectforeground=C["crust"],
        insertcolor=C["text"],
        relief="flat",
        font=("Helvetica", 10),
    )

    style.configure("TFrame",      background=C["base"])
    style.configure("TLabel",      background=C["base"], foreground=C["text"])
    style.configure("TSeparator",  background=C["surface1"])

    style.configure("TLabelframe",
        background=C["base"],
        bordercolor=C["surface1"],
        relief="groove",
    )
    style.configure("TLabelframe.Label",
        background=C["base"],
        foreground=C["subtext1"],
        font=("Helvetica", 9, "bold"),
    )

    style.configure("TButton",
        background=C["surface0"],
        foreground=C["text"],
        bordercolor=C["surface1"],
        focuscolor=C["surface0"],
        padding=(8, 5),
    )
    style.map("TButton",
        background=[("active", C["surface1"]), ("pressed", C["surface2"])],
        foreground=[("active", C["text"]), ("pressed", C["text"])],
        bordercolor=[("active", C["overlay0"])],
    )

    style.configure("Accent.TButton",
        background=C["blue"],
        foreground=C["crust"],
        bordercolor=C["blue"],
        font=("Helvetica", 10, "bold"),
        padding=(14, 8),
    )
    style.map("Accent.TButton",
        background=[("active", C["subtext1"]), ("pressed", C["overlay1"])],
        foreground=[("active", C["crust"]), ("pressed", C["crust"])],
    )

    style.configure("TEntry",
        fieldbackground=C["mantle"],
        foreground=C["text"],
        bordercolor=C["surface1"],
        insertcolor=C["text"],
        padding=6,
    )
    style.map("TEntry",
        fieldbackground=[("focus", C["surface0"])],
        bordercolor=[("focus", C["blue"])],
    )

    style.configure("TCombobox",
        fieldbackground=C["mantle"],
        background=C["surface0"],
        foreground=C["text"],
        bordercolor=C["surface1"],
        arrowcolor=C["subtext0"],
        padding=5,
    )
    style.map("TCombobox",
        fieldbackground=[("focus", C["surface0"]), ("readonly", C["mantle"])],
        bordercolor=[("focus", C["blue"])],
        arrowcolor=[("hover", C["text"])],
    )

    style.configure("TCheckbutton",
        background=C["base"],
        foreground=C["text"],
        focuscolor=C["base"],
        indicatorcolor=C["surface0"],
    )
    style.map("TCheckbutton",
        indicatorcolor=[("selected", C["blue"]), ("active", C["surface1"])],
        background=[("active", C["base"])],
        foreground=[("active", C["text"])],
    )

    style.configure("TRadiobutton",
        background=C["base"],
        foreground=C["text"],
        focuscolor=C["base"],
        indicatorcolor=C["surface0"],
    )
    style.map("TRadiobutton",
        indicatorcolor=[("selected", C["blue"]), ("active", C["surface1"])],
        background=[("active", C["base"])],
        foreground=[("active", C["text"])],
    )

    style.configure("Treeview",
        background=C["mantle"],
        foreground=C["text"],
        fieldbackground=C["mantle"],
        bordercolor=C["surface1"],
        rowheight=30,
    )
    style.configure("Treeview.Heading",
        background=C["surface0"],
        foreground=C["subtext1"],
        relief="flat",
        font=("Helvetica", 9, "bold"),
        padding=(4, 6),
    )
    style.map("Treeview",
        background=[("selected", C["surface1"])],
        foreground=[("selected", C["text"])],
    )
    style.map("Treeview.Heading",
        background=[("active", C["surface1"])],
        relief=[("active", "flat")],
    )

    style.configure("TScrollbar",
        background=C["surface0"],
        troughcolor=C["mantle"],
        bordercolor=C["mantle"],
        arrowcolor=C["overlay0"],
        gripcount=0,
    )
    style.map("TScrollbar",
        background=[("active", C["surface1"])],
    )

    # Named label styles for dynamic status colours
    style.configure("Running.TLabel",
        background=C["mantle"], foreground=C["green"], font=("Helvetica", 10, "bold"),
    )
    style.configure("Stopped.TLabel",
        background=C["mantle"], foreground=C["red"],   font=("Helvetica", 10, "bold"),
    )
    style.configure("Dim.TLabel",
        background=C["base"], foreground=C["subtext0"], font=("Helvetica", 9),
    )
    style.configure("Hint.TLabel",
        background=C["surface0"], foreground=C["subtext0"], font=("Helvetica", 9),
    )


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def get_printers() -> list[str]:
    try:
        result = subprocess.run(["lpstat", "-p"], capture_output=True, text=True)
        printers = []
        for line in result.stdout.splitlines():
            if line.startswith("printer "):
                parts = line.split()
                if len(parts) > 1:
                    printers.append(parts[1])
        return printers
    except Exception:
        return []


def load_config() -> dict:
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH) as f:
            return json.load(f)
    return {
        "watch_dir": str(Path.home() / "Documents" / "PrintQueue"),
        "delete_after_print": True,
        "rules": [],
    }


def save_config(config: dict) -> None:
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_PATH, "w") as f:
        json.dump(config, f, indent=2)


def size_label(width_pt, height_pt) -> str:
    if width_pt is None:
        return "Any (default)"
    for name, (w, h) in PAPER_SIZES.items():
        if w is not None and abs(w - width_pt) < 5 and abs(h - height_pt) < 5:
            return name
    return f'Custom ({width_pt/72:.2f}" x {height_pt/72:.2f}")'


def color_label(color_val: str) -> str:
    for name, val in COLOR_OPTIONS.items():
        if val == color_val:
            return name
    return "Any"


def open_terminal_tail(log_path: Path) -> None:
    for term in TERMINALS:
        try:
            if term == "gnome-terminal":
                subprocess.Popen([term, "--", "bash", "-c",
                                   f"tail -f {log_path}; read"])
            else:
                subprocess.Popen([term, "-e", f"tail -f {log_path}"])
            return
        except FileNotFoundError:
            continue
    messagebox.showinfo("Log Location", f"Log file:\n{log_path}")


# ---------------------------------------------------------------------------
# Rule dialog
# ---------------------------------------------------------------------------

class RuleDialog(tk.Toplevel):
    def __init__(self, parent, printers: list[str], rule: dict | None = None):
        super().__init__(parent)
        self.result: dict | None = None
        self.printers = printers

        self.title("Edit Rule" if rule else "Add Rule")
        self.resizable(False, False)
        self.configure(bg=C["base"])
        self.grab_set()

        outer = ttk.Frame(self, padding=20)
        outer.pack(fill="both", expand=True)

        def field(row, label, widget_factory):
            ttk.Label(outer, text=label, foreground=C["text"]).grid(
                row=row, column=0, sticky="w", pady=(0, 8), padx=(0, 16),
            )
            w = widget_factory(outer)
            w.grid(row=row, column=1, sticky="ew", pady=(0, 8))
            return w

        # Rule name
        self.name_var = tk.StringVar(value=rule.get("name", "") if rule else "")
        field(0, "Rule Name", lambda p: ttk.Entry(p, textvariable=self.name_var, width=34))

        # Filename pattern
        self.filename_var = tk.StringVar(
            value=rule.get("filename_pattern", "") if rule else ""
        )
        field(1, "Filename Pattern",
              lambda p: ttk.Entry(p, textvariable=self.filename_var, width=34))
        ttk.Label(
            outer,
            text="Glob pattern, e.g. *shipping*  |  leave blank to match any filename",
            style="Dim.TLabel",
        ).grid(row=2, column=1, sticky="w", pady=(0, 10))

        ttk.Separator(outer, orient="horizontal").grid(
            row=3, column=0, columnspan=2, sticky="ew", pady=(0, 12),
        )

        # Paper size
        self.size_var = tk.StringVar()
        size_cb = ttk.Combobox(
            outer, textvariable=self.size_var,
            values=list(PAPER_SIZES.keys()), state="readonly", width=32,
        )
        field(4, "Paper Size", lambda p: size_cb)
        self.size_var.set(
            size_label(rule.get("width_pt"), rule.get("height_pt")) if rule else "4x6 Label"
        )

        # Color
        self.color_var = tk.StringVar()
        color_cb = ttk.Combobox(
            outer, textvariable=self.color_var,
            values=list(COLOR_OPTIONS.keys()), state="readonly", width=32,
        )
        field(5, "Color", lambda p: color_cb)
        self.color_var.set(color_label(rule.get("color", "any")) if rule else "Any")

        # Printer
        self.printer_var = tk.StringVar()
        printer_cb = ttk.Combobox(
            outer, textvariable=self.printer_var,
            values=printers, state="readonly", width=32,
        )
        field(6, "Printer", lambda p: printer_cb)
        if rule and rule.get("printer") in printers:
            self.printer_var.set(rule["printer"])
        elif printers:
            self.printer_var.set(printers[0])

        ttk.Separator(outer, orient="horizontal").grid(
            row=7, column=0, columnspan=2, sticky="ew", pady=(4, 12),
        )

        btn_row = ttk.Frame(outer)
        btn_row.grid(row=8, column=0, columnspan=2, sticky="e")
        ttk.Button(btn_row, text="Cancel", command=self.destroy).pack(side="left", padx=(0, 8))
        ttk.Button(btn_row, text="Save", style="Accent.TButton",
                   command=self._save).pack(side="left")

        self.wait_window()

    def _save(self):
        if not self.printer_var.get():
            messagebox.showerror("Error", "Please select a printer.", parent=self)
            return

        size_name = self.size_var.get()
        w, h      = PAPER_SIZES.get(size_name, (None, None))

        self.result = {
            "name":             self.name_var.get() or f"{size_name} -> {self.printer_var.get()}",
            "filename_pattern": self.filename_var.get().strip() or None,
            "width_pt":         w,
            "height_pt":        h,
            "color":            COLOR_OPTIONS.get(self.color_var.get(), "any"),
            "printer":          self.printer_var.get(),
        }
        self.destroy()


# ---------------------------------------------------------------------------
# Main app window
# ---------------------------------------------------------------------------

class PaperboyApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Paperboy  —  Print Router")
        self.resizable(True, True)
        self.minsize(740, 580)

        apply_theme(self)

        self.config_data = load_config()
        self.printers    = get_printers()

        self._build_ui()
        self._populate_ui()
        self._poll_daemon_status()

    # --- UI construction ---------------------------------------------------

    def _build_ui(self):
        # Header
        header = tk.Frame(self, bg=C["mantle"])
        header.pack(fill="x")
        tk.Label(
            header, text="Paperboy",
            font=("Helvetica", 22, "bold"),
            bg=C["mantle"], fg=C["text"],
        ).pack(side="left", padx=20, pady=14)
        tk.Label(
            header, text="Automatic PDF Print Router",
            font=("Helvetica", 10),
            bg=C["mantle"], fg=C["subtext0"],
        ).pack(side="left", pady=14)

        # Status pill on the right side of header
        self.status_label = ttk.Label(header, text="checking...", style="Dim.TLabel")
        self.status_label.pack(side="right", padx=20, pady=14)
        tk.Label(
            header, text="Daemon:",
            bg=C["mantle"], fg=C["subtext0"], font=("Helvetica", 10),
        ).pack(side="right", pady=14)

        main = ttk.Frame(self, padding=(16, 12))
        main.pack(fill="both", expand=True)
        main.columnconfigure(0, weight=1)

        # Settings
        sf = ttk.LabelFrame(main, text="Settings", padding=(12, 8))
        sf.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        sf.columnconfigure(1, weight=1)

        ttk.Label(sf, text="Watch Directory:", foreground=C["text"]).grid(
            row=0, column=0, sticky="w", pady=(0, 6),
        )
        dir_row = ttk.Frame(sf)
        dir_row.grid(row=0, column=1, sticky="ew", pady=(0, 6))
        dir_row.columnconfigure(0, weight=1)
        self.watch_dir_var = tk.StringVar()
        ttk.Entry(dir_row, textvariable=self.watch_dir_var).grid(
            row=0, column=0, sticky="ew", padx=(8, 6),
        )
        ttk.Button(dir_row, text="Browse", command=self._browse_dir).grid(
            row=0, column=1,
        )

        ttk.Label(sf, text="After Print:", foreground=C["text"]).grid(
            row=1, column=0, sticky="w", pady=(8, 0),
        )
        after_row = ttk.Frame(sf)
        after_row.grid(row=1, column=1, sticky="w", pady=(8, 0), padx=(8, 0))
        self.after_print_var = tk.StringVar()
        for value, label in [("delete", "Delete"), ("archive", "Archive")]:
            ttk.Radiobutton(
                after_row, text=label,
                variable=self.after_print_var, value=value,
                command=self._on_after_print_change,
            ).pack(side="left", padx=(0, 12))

        ttk.Label(sf, text="Archive Directory:", foreground=C["text"]).grid(
            row=2, column=0, sticky="w", pady=(8, 0),
        )
        archive_row = ttk.Frame(sf)
        archive_row.grid(row=2, column=1, sticky="ew", pady=(8, 0))
        archive_row.columnconfigure(0, weight=1)
        self.archive_dir_var = tk.StringVar()
        self.archive_dir_entry = ttk.Entry(archive_row, textvariable=self.archive_dir_var)
        self.archive_dir_entry.grid(row=0, column=0, sticky="ew", padx=(8, 6))
        self.archive_browse_btn = ttk.Button(
            archive_row, text="Browse", command=self._browse_archive_dir,
        )
        self.archive_browse_btn.grid(row=0, column=1)

        # Rules
        rf = ttk.LabelFrame(main, text="Routing Rules", padding=(12, 8))
        rf.grid(row=1, column=0, sticky="nsew", pady=(0, 8))
        rf.rowconfigure(0, weight=1)
        rf.columnconfigure(0, weight=1)
        main.rowconfigure(1, weight=1)

        cols = ("name", "filename", "size", "color", "printer")
        self.tree = ttk.Treeview(rf, columns=cols, show="headings", height=8)
        self.tree.heading("name",     text="Rule Name")
        self.tree.heading("filename", text="Filename Pattern")
        self.tree.heading("size",     text="Paper Size")
        self.tree.heading("color",    text="Color")
        self.tree.heading("printer",  text="Printer")
        self.tree.column("name",     width=165, minwidth=100)
        self.tree.column("filename", width=135, minwidth=80)
        self.tree.column("size",     width=125, minwidth=80)
        self.tree.column("color",    width=95,  minwidth=60)
        self.tree.column("printer",  width=185, minwidth=100)
        self.tree.grid(row=0, column=0, sticky="nsew")
        self.tree.bind("<Double-1>", lambda _: self._edit_rule())

        sb = ttk.Scrollbar(rf, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=sb.set)
        sb.grid(row=0, column=1, sticky="ns")

        # Rule action buttons
        rbf = ttk.Frame(main)
        rbf.grid(row=2, column=0, sticky="w", pady=(2, 0))
        for text, cmd in [
            ("Add",       self._add_rule),
            ("Edit",      self._edit_rule),
            ("Remove",    self._remove_rule),
            ("Move Up",   self._move_up),
            ("Move Down", self._move_down),
        ]:
            ttk.Button(rbf, text=text, command=cmd).pack(side="left", padx=(0, 4))

        ttk.Label(
            main,
            text="Rules are matched top-to-bottom  —  first match wins. "
                 "Put specific rules above defaults.",
            style="Dim.TLabel",
        ).grid(row=3, column=0, sticky="w", pady=(4, 0))

        ttk.Separator(main, orient="horizontal").grid(
            row=4, column=0, sticky="ew", pady=12,
        )

        # Daemon controls + save button
        bottom = ttk.Frame(main)
        bottom.grid(row=5, column=0, sticky="ew")
        bottom.columnconfigure(0, weight=1)

        df = ttk.LabelFrame(bottom, text="Daemon Controls", padding=(12, 8))
        df.grid(row=0, column=0, sticky="w")
        for text, cmd in [
            ("Start",    self._start),
            ("Stop",     self._stop),
            ("Restart",  self._restart),
            ("View Log", self._view_log),
        ]:
            ttk.Button(df, text=text, command=cmd).pack(side="left", padx=(0, 4))

        ttk.Button(
            bottom, text="Save Configuration",
            style="Accent.TButton",
            command=self._save,
        ).grid(row=0, column=1, sticky="e")

    # --- UI population & tree refresh --------------------------------------

    def _populate_ui(self):
        self.watch_dir_var.set(self.config_data.get("watch_dir", ""))

        # Migrate legacy delete_after_print flag
        if "after_print" not in self.config_data:
            self.config_data["after_print"] = "delete"
        self.after_print_var.set(self.config_data.get("after_print", "delete"))

        default_archive = str(Path.home() / "Documents" / "PrintArchive")
        self.archive_dir_var.set(self.config_data.get("archive_dir", default_archive))

        self._on_after_print_change()
        self._refresh_tree()

    def _refresh_tree(self):
        self.tree.delete(*self.tree.get_children())
        for rule in self.config_data.get("rules", []):
            self.tree.insert("", "end", values=(
                rule.get("name", "Unnamed"),
                rule.get("filename_pattern") or "*",
                size_label(rule.get("width_pt"), rule.get("height_pt")),
                color_label(rule.get("color", "any")),
                rule.get("printer", ""),
            ))

    # --- Rule actions -------------------------------------------------------

    def _selected_index(self) -> int | None:
        sel = self.tree.selection()
        return self.tree.index(sel[0]) if sel else None

    def _add_rule(self):
        dlg = RuleDialog(self, self.printers)
        if dlg.result:
            self.config_data.setdefault("rules", []).append(dlg.result)
            self._refresh_tree()

    def _edit_rule(self):
        idx = self._selected_index()
        if idx is None:
            messagebox.showinfo("Edit Rule", "Select a rule to edit.")
            return
        dlg = RuleDialog(self, self.printers, rule=self.config_data["rules"][idx])
        if dlg.result:
            self.config_data["rules"][idx] = dlg.result
            self._refresh_tree()

    def _remove_rule(self):
        idx = self._selected_index()
        if idx is None:
            messagebox.showinfo("Remove Rule", "Select a rule to remove.")
            return
        name = self.config_data["rules"][idx].get("name", "this rule")
        if messagebox.askyesno("Remove Rule", f"Remove '{name}'?"):
            del self.config_data["rules"][idx]
            self._refresh_tree()

    def _move_up(self):
        idx = self._selected_index()
        if idx is None or idx == 0:
            return
        rules = self.config_data["rules"]
        rules[idx], rules[idx - 1] = rules[idx - 1], rules[idx]
        self._refresh_tree()
        self.tree.selection_set(self.tree.get_children()[idx - 1])

    def _move_down(self):
        idx   = self._selected_index()
        rules = self.config_data["rules"]
        if idx is None or idx >= len(rules) - 1:
            return
        rules[idx], rules[idx + 1] = rules[idx + 1], rules[idx]
        self._refresh_tree()
        self.tree.selection_set(self.tree.get_children()[idx + 1])

    # --- Settings actions --------------------------------------------------

    def _browse_dir(self):
        d = filedialog.askdirectory(initialdir=self.watch_dir_var.get())
        if d:
            self.watch_dir_var.set(d)

    def _browse_archive_dir(self):
        d = filedialog.askdirectory(initialdir=self.archive_dir_var.get())
        if d:
            self.archive_dir_var.set(d)

    def _on_after_print_change(self):
        archiving = self.after_print_var.get() == "archive"
        state = "normal" if archiving else "disabled"
        self.archive_dir_entry.configure(state=state)
        self.archive_browse_btn.configure(state=state)

    def _save(self):
        self.config_data["watch_dir"]   = self.watch_dir_var.get()
        self.config_data["after_print"] = self.after_print_var.get()
        self.config_data["archive_dir"] = self.archive_dir_var.get()
        # Keep legacy key in sync for any external tools
        self.config_data["delete_after_print"] = (self.after_print_var.get() == "delete")
        save_config(self.config_data)
        messagebox.showinfo(
            "Saved",
            "Configuration saved.\nRestart the daemon to apply changes.",
        )

    # --- Daemon controls ---------------------------------------------------

    def _systemctl(self, *args):
        subprocess.run(["systemctl", "--user"] + list(args), capture_output=True)
        self.after(600, self._poll_daemon_status)

    def _start(self):   self._systemctl("start",   "paperboy")
    def _stop(self):    self._systemctl("stop",    "paperboy")
    def _restart(self): self._systemctl("restart", "paperboy")

    def _view_log(self):
        open_terminal_tail(
            Path.home() / ".local" / "share" / "paperboy" / "paperboy.log"
        )

    def _poll_daemon_status(self):
        result = subprocess.run(
            ["systemctl", "--user", "is-active", "paperboy"],
            capture_output=True, text=True,
        )
        if result.stdout.strip() == "active":
            self.status_label.configure(text="Running", style="Running.TLabel")
        else:
            self.status_label.configure(text="Stopped", style="Stopped.TLabel")
        self.after(5000, self._poll_daemon_status)


# ---------------------------------------------------------------------------

def main():
    app = PaperboyApp()
    app.mainloop()


if __name__ == "__main__":
    main()
