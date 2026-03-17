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
        self.grab_set()

        pad = {"padx": 12, "pady": 6}

        tk.Label(self, text="Rule Name:").grid(row=0, column=0, sticky="w", **pad)
        self.name_var = tk.StringVar(value=rule.get("name", "") if rule else "")
        tk.Entry(self, textvariable=self.name_var, width=32).grid(row=0, column=1, **pad)

        tk.Label(self, text="Filename Pattern:").grid(row=1, column=0, sticky="w", **pad)
        self.filename_var = tk.StringVar(value=rule.get("filename_pattern", "") if rule else "")
        tk.Entry(self, textvariable=self.filename_var, width=32).grid(row=1, column=1, **pad)
        tk.Label(
            self, text='e.g. *shipping*, invoice_*.pdf  (leave blank to match any filename)',
            fg="#888888", font=("Helvetica", 8),
        ).grid(row=2, column=1, sticky="w", padx=12, pady=(0, 4))

        tk.Label(self, text="Paper Size:").grid(row=3, column=0, sticky="w", **pad)
        self.size_var = tk.StringVar()
        size_cb = ttk.Combobox(
            self, textvariable=self.size_var,
            values=list(PAPER_SIZES.keys()), state="readonly", width=30,
        )
        size_cb.grid(row=3, column=1, **pad)
        self.size_var.set(
            size_label(rule.get("width_pt"), rule.get("height_pt")) if rule else "4x6 Label"
        )

        tk.Label(self, text="Color:").grid(row=4, column=0, sticky="w", **pad)
        self.color_var = tk.StringVar()
        color_cb = ttk.Combobox(
            self, textvariable=self.color_var,
            values=list(COLOR_OPTIONS.keys()), state="readonly", width=30,
        )
        color_cb.grid(row=4, column=1, **pad)
        self.color_var.set(color_label(rule.get("color", "any")) if rule else "Any")

        tk.Label(self, text="Printer:").grid(row=5, column=0, sticky="w", **pad)
        self.printer_var = tk.StringVar()
        printer_cb = ttk.Combobox(
            self, textvariable=self.printer_var,
            values=printers, state="readonly", width=30,
        )
        printer_cb.grid(row=5, column=1, **pad)
        if rule and rule.get("printer") in printers:
            self.printer_var.set(rule["printer"])
        elif printers:
            self.printer_var.set(printers[0])

        btn_frame = tk.Frame(self)
        btn_frame.grid(row=6, column=0, columnspan=2, pady=12)
        tk.Button(btn_frame, text="Save",   command=self._save,   width=12).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Cancel", command=self.destroy, width=12).pack(side="left", padx=5)

        self.wait_window()

    def _save(self):
        if not self.printer_var.get():
            messagebox.showerror("Error", "Please select a printer.", parent=self)
            return

        size_name = self.size_var.get()
        w, h      = PAPER_SIZES.get(size_name, (None, None))
        color     = COLOR_OPTIONS.get(self.color_var.get(), "any")
        printer   = self.printer_var.get()

        self.result = {
            "name":             self.name_var.get() or f"{size_name} -> {printer}",
            "filename_pattern": self.filename_var.get().strip() or None,
            "width_pt":         w,
            "height_pt":        h,
            "color":            color,
            "printer":          printer,
        }
        self.destroy()


# ---------------------------------------------------------------------------
# Main app window
# ---------------------------------------------------------------------------

class PaperboyApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Paperboy  —  Print Router")
        self.resizable(False, False)

        self.config_data = load_config()
        self.printers    = get_printers()

        self._build_ui()
        self._populate_ui()
        self._poll_daemon_status()

    # --- UI construction ---------------------------------------------------

    def _build_ui(self):
        # Header
        header = tk.Frame(self, bg="#1e1e2e")
        header.pack(fill="x")
        tk.Label(
            header, text="Paperboy", font=("Helvetica", 20, "bold"),
            bg="#1e1e2e", fg="#cdd6f4",
        ).pack(pady=(12, 2))
        tk.Label(
            header, text="Automatic PDF Print Router",
            bg="#1e1e2e", fg="#6c7086", font=("Helvetica", 10),
        ).pack(pady=(0, 12))

        # Settings
        sf = tk.LabelFrame(self, text="Settings", padx=10, pady=8)
        sf.pack(fill="x", padx=12, pady=(10, 4))

        tk.Label(sf, text="Watch Directory:").grid(row=0, column=0, sticky="w")
        self.watch_dir_var = tk.StringVar()
        tk.Entry(sf, textvariable=self.watch_dir_var, width=42).grid(
            row=0, column=1, padx=6,
        )
        tk.Button(sf, text="Browse", command=self._browse_dir).grid(row=0, column=2)

        self.delete_var = tk.BooleanVar()
        tk.Checkbutton(
            sf, text="Delete PDF after successful print",
            variable=self.delete_var,
        ).grid(row=1, column=0, columnspan=3, sticky="w", pady=(6, 0))

        # Rules
        rf = tk.LabelFrame(self, text="Routing Rules", padx=10, pady=8)
        rf.pack(fill="both", expand=True, padx=12, pady=4)

        cols = ("name", "filename", "size", "color", "printer")
        self.tree = ttk.Treeview(rf, columns=cols, show="headings", height=8)
        self.tree.heading("name",     text="Rule Name")
        self.tree.heading("filename", text="Filename Pattern")
        self.tree.heading("size",     text="Paper Size")
        self.tree.heading("color",    text="Color")
        self.tree.heading("printer",  text="Printer")
        self.tree.column("name",     width=160)
        self.tree.column("filename", width=130)
        self.tree.column("size",     width=120)
        self.tree.column("color",    width=90)
        self.tree.column("printer",  width=180)
        self.tree.pack(side="left", fill="both", expand=True)

        sb = ttk.Scrollbar(rf, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=sb.set)
        sb.pack(side="right", fill="y")

        self.tree.bind("<Double-1>", lambda _: self._edit_rule())

        # Rule buttons
        rbf = tk.Frame(self)
        rbf.pack(fill="x", padx=12, pady=2)
        for text, cmd in [
            ("Add",       self._add_rule),
            ("Edit",      self._edit_rule),
            ("Remove",    self._remove_rule),
            ("Move Up",   self._move_up),
            ("Move Down", self._move_down),
        ]:
            tk.Button(rbf, text=text, command=cmd, width=10).pack(side="left", padx=2)

        tk.Label(
            self,
            text="Rules are matched top-to-bottom  —  first match wins. "
                 "Put specific rules above defaults.",
            fg="#888888", font=("Helvetica", 9),
        ).pack(padx=12, anchor="w", pady=(2, 0))

        # Daemon status
        df = tk.LabelFrame(self, text="Daemon", padx=10, pady=8)
        df.pack(fill="x", padx=12, pady=(6, 4))

        status_row = tk.Frame(df)
        status_row.pack(fill="x")
        tk.Label(status_row, text="Status:").pack(side="left")
        self.status_label = tk.Label(status_row, text="checking...", fg="gray")
        self.status_label.pack(side="left", padx=6)

        dbf = tk.Frame(df)
        dbf.pack(fill="x", pady=(6, 0))
        for text, cmd in [
            ("Start",    self._start),
            ("Stop",     self._stop),
            ("Restart",  self._restart),
            ("View Log", self._view_log),
        ]:
            tk.Button(dbf, text=text, command=cmd, width=10).pack(side="left", padx=2)

        # Save button
        bf = tk.Frame(self)
        bf.pack(fill="x", padx=12, pady=10)
        tk.Button(
            bf, text="Save Configuration",
            command=self._save,
            bg="#40a02b", fg="white",
            activebackground="#2d7a1f",
            width=22, height=2,
        ).pack(side="right")

    # --- UI population & tree refresh --------------------------------------

    def _populate_ui(self):
        self.watch_dir_var.set(self.config_data.get("watch_dir", ""))
        self.delete_var.set(self.config_data.get("delete_after_print", True))
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

    def _save(self):
        self.config_data["watch_dir"]          = self.watch_dir_var.get()
        self.config_data["delete_after_print"] = self.delete_var.get()
        save_config(self.config_data)
        messagebox.showinfo(
            "Saved",
            "Configuration saved.\nRestart the daemon to apply changes.",
        )

    # --- Daemon controls ---------------------------------------------------

    def _systemctl(self, *args):
        subprocess.run(["systemctl", "--user"] + list(args), capture_output=True)
        self.after(600, self._poll_daemon_status)

    def _start(self):
        self._systemctl("start", "paperboy")

    def _stop(self):
        self._systemctl("stop", "paperboy")

    def _restart(self):
        self._systemctl("restart", "paperboy")

    def _view_log(self):
        log_path = Path.home() / ".local" / "share" / "paperboy" / "paperboy.log"
        open_terminal_tail(log_path)

    def _poll_daemon_status(self):
        result = subprocess.run(
            ["systemctl", "--user", "is-active", "paperboy"],
            capture_output=True, text=True,
        )
        if result.stdout.strip() == "active":
            self.status_label.config(text="Running", fg="#40a02b")
        else:
            self.status_label.config(text="Stopped", fg="#d20f39")
        self.after(5000, self._poll_daemon_status)


# ---------------------------------------------------------------------------

def main():
    app = PaperboyApp()
    app.mainloop()


if __name__ == "__main__":
    main()
