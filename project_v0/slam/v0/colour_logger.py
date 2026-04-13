#!/usr/bin/env python3
"""Run-scoped colour sensor CSV logging utilities."""

from __future__ import annotations

import csv
from datetime import datetime
from pathlib import Path


class ColourRunLogger:
    """Writes colour sensor events to one CSV per run/reset."""

    def __init__(self, base_dir: Path):
        self._base_dir = Path(base_dir)
        self._base_dir.mkdir(parents=True, exist_ok=True)
        self._csv_path: Path | None = None
        self._origin_x_mm = 0.0
        self._origin_y_mm = 0.0

    @property
    def csv_path(self) -> Path | None:
        return self._csv_path

    def start_new_run(self, origin_x_mm: float, origin_y_mm: float) -> Path:
        self._base_dir.mkdir(parents=True, exist_ok=True)
        run_stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self._csv_path = self._base_dir / f"{run_stamp}.csv"
        self._origin_x_mm = float(origin_x_mm)
        self._origin_y_mm = float(origin_y_mm)

        with self._csv_path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                "event_ts",
                "source",
                "r_raw",
                "g_raw",
                "b_raw",
                "x_mm",
                "y_mm",
                "rel_x_mm",
                "rel_y_mm",
            ])
        return self._csv_path

    def log_color(self, source: str, r: int, g: int, b: int, x_mm: float, y_mm: float) -> bool:
        if self._csv_path is None:
            return False

        x = float(x_mm)
        y = float(y_mm)
        rel_x = x - self._origin_x_mm
        rel_y = y - self._origin_y_mm

        with self._csv_path.open("a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                datetime.now().isoformat(timespec="milliseconds"),
                str(source),
                int(r),
                int(g),
                int(b),
                x,
                y,
                rel_x,
                rel_y,
            ])
        return True
