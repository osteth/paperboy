#!/usr/bin/env python3
"""
Paperboy - Print Daemon
Watches a directory for PDFs and routes them to the correct printer
based on page size and color content as defined in config.json.
"""

import json
import logging
import subprocess
import sys
import time
from pathlib import Path

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

try:
    from pypdf import PdfReader
except ImportError:
    from PyPDF2 import PdfReader  # fallback

CONFIG_PATH = Path.home() / ".config" / "paperboy" / "config.json"
LOG_PATH    = Path.home() / ".local" / "share" / "paperboy" / "paperboy.log"
TOLERANCE   = 20  # points (~0.28 inch)

DEFAULT_CONFIG = {
    "watch_dir": str(Path.home() / "Documents" / "PrintQueue"),
    "delete_after_print": True,
    "rules": [],
}


def load_config() -> dict:
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH) as f:
            return json.load(f)
    log.warning("No config found at %s — using defaults", CONFIG_PATH)
    return DEFAULT_CONFIG


def get_page_size(path: Path) -> tuple[float, float]:
    reader = PdfReader(str(path))
    page = reader.pages[0]
    return float(page.mediabox.width), float(page.mediabox.height)


def detect_color(path: Path) -> bool | None:
    """
    Use ghostscript ink coverage to detect color content.
    Returns True (color), False (B&W), or None (gs unavailable).
    """
    try:
        result = subprocess.run(
            ["gs", "-q", "-o", "/dev/null", "-sDEVICE=inkcov", str(path)],
            capture_output=True,
            text=True,
            timeout=15,
        )
        for line in result.stdout.strip().splitlines():
            parts = line.strip().split()
            if len(parts) >= 4:
                c, m, y = float(parts[0]), float(parts[1]), float(parts[2])
                if c > 0.001 or m > 0.001 or y > 0.001:
                    return True
        return False
    except FileNotFoundError:
        log.warning("ghostscript (gs) not found — color detection disabled")
        return None
    except Exception as e:
        log.warning("Color detection failed: %s", e)
        return None


def sizes_match(w: float, h: float, rule_w, rule_h) -> bool:
    if rule_w is None or rule_h is None:
        return True  # wildcard / default rule
    short_doc,  long_doc  = sorted([w, h])
    short_rule, long_rule = sorted([rule_w, rule_h])
    return (
        abs(short_doc - short_rule) <= TOLERANCE
        and abs(long_doc - long_rule) <= TOLERANCE
    )


def color_matches(color_detected: bool | None, rule_color: str) -> bool:
    if rule_color == "any" or color_detected is None:
        return True
    if rule_color == "color":
        return color_detected is True
    if rule_color == "bw":
        return color_detected is False
    return True


def match_rule(w: float, h: float, color_detected: bool | None, rules: list) -> dict | None:
    for rule in rules:
        if sizes_match(w, h, rule.get("width_pt"), rule.get("height_pt")):
            if color_matches(color_detected, rule.get("color", "any")):
                return rule
    return None


def wait_for_file(path: Path, timeout: float = 10.0) -> bool:
    """Wait until the file stops growing (i.e. fully written to disk)."""
    deadline = time.time() + timeout
    last_size = -1
    while time.time() < deadline:
        try:
            size = path.stat().st_size
        except FileNotFoundError:
            return False
        if size == last_size and size > 0:
            return True
        last_size = size
        time.sleep(0.3)
    return False


def notify(title: str, body: str) -> None:
    try:
        subprocess.run(
            ["notify-send", "--app-name=Paperboy", title, body],
            timeout=3,
        )
    except Exception:
        pass


def print_pdf(path: Path, printer: str) -> bool:
    result = subprocess.run(
        ["lp", "-d", printer, str(path)],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        log.error("lp error: %s", result.stderr.strip())
    return result.returncode == 0


class PDFHandler(FileSystemEventHandler):
    def __init__(self, config: dict):
        self.config = config

    def on_created(self, event):
        if event.is_directory:
            return
        path = Path(event.src_path)
        if path.suffix.lower() != ".pdf":
            return

        log.info("Detected: %s", path.name)

        if not wait_for_file(path):
            log.warning("File never stabilised, skipping: %s", path.name)
            return

        try:
            w, h = get_page_size(path)
            color = detect_color(path)

            color_str = {True: "color", False: "B&W", None: "unknown"}[color]
            log.info(
                "  Size: %.1f x %.1f pt  (%.2f x %.2f in)  Color: %s",
                w, h, w / 72, h / 72, color_str,
            )

            rule = match_rule(w, h, color, self.config.get("rules", []))
            if rule is None:
                log.warning("  No matching rule — file left in place")
                notify("Paperboy: No Rule Matched", path.name)
                return

            printer = rule["printer"]
            log.info("  Rule: '%s'  ->  %s", rule.get("name", "unnamed"), printer)

            if print_pdf(path, printer):
                log.info("  Sent successfully")
                if self.config.get("delete_after_print", True):
                    path.unlink()
                notify("Paperboy: Printed", f"{color_str} -> {printer}")
            else:
                log.error("  Print failed — file kept for inspection")
                notify("Paperboy: Print Failed", f"Could not send {path.name} to {printer}")

        except Exception:
            log.exception("Unexpected error processing %s", path.name)
            notify("Paperboy Error", f"Failed to process {path.name}")


def main():
    global log

    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(LOG_PATH),
        ],
    )
    log = logging.getLogger(__name__)

    config    = load_config()
    watch_dir = Path(config["watch_dir"]).expanduser()

    if not watch_dir.is_dir():
        log.error("Watch directory does not exist: %s", watch_dir)
        sys.exit(1)

    log.info("Paperboy started  —  watching %s", watch_dir)
    log.info("Rules loaded: %d", len(config.get("rules", [])))

    handler  = PDFHandler(config)
    observer = Observer()
    observer.schedule(handler, str(watch_dir), recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(5)
    except KeyboardInterrupt:
        log.info("Shutting down")
        observer.stop()
    observer.join()


if __name__ == "__main__":
    main()
