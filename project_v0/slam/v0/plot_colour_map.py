#!/usr/bin/env python3
"""Plot logged colour sensor points from a run CSV.

Usage:
  python plot_colour_map.py [path/to/run.csv]

If no file is provided, the newest CSV in ./colour_data is used.
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt


def _resolve_csv_path(argv: list[str]) -> Path:
    if len(argv) > 1:
        path = Path(argv[1]).expanduser().resolve()
        if not path.is_file():
            raise FileNotFoundError(f"CSV not found: {path}")
        return path

    base = Path(__file__).with_name("colour_data")
    if not base.exists():
        raise FileNotFoundError("colour_data folder not found")

    csv_files = sorted(base.glob("*.csv"), key=lambda p: p.stat().st_mtime, reverse=True)
    if not csv_files:
        raise FileNotFoundError("No CSV files in colour_data")
    return csv_files[0]


def _load_rows(csv_path: Path):
    rel_x, rel_y = [], []
    r_vals, g_vals, b_vals = [], [], []

    with csv_path.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                rel_x.append(float(row["rel_x_mm"]))
                rel_y.append(float(row["rel_y_mm"]))
                r_vals.append(float(row["r_raw"]))
                g_vals.append(float(row["g_raw"]))
                b_vals.append(float(row["b_raw"]))
            except Exception:
                continue

    if not rel_x:
        raise ValueError("No valid rows found in CSV")

    return (
        np.asarray(rel_x, dtype=np.float64),
        np.asarray(rel_y, dtype=np.float64),
        np.asarray(r_vals, dtype=np.float64),
        np.asarray(g_vals, dtype=np.float64),
        np.asarray(b_vals, dtype=np.float64),
    )


def _minmax_norm(values: np.ndarray) -> np.ndarray:
    vmin = float(np.min(values))
    vmax = float(np.max(values))
    if abs(vmax - vmin) < 1e-12:
        return np.zeros_like(values)
    return (values - vmin) / (vmax - vmin)


def main(argv: list[str]) -> int:
    csv_path = _resolve_csv_path(argv)
    rel_x, rel_y, r_raw, g_raw, b_raw = _load_rows(csv_path)

    rgb = np.column_stack([
        _minmax_norm(r_raw),
        _minmax_norm(g_raw),
        _minmax_norm(b_raw),
    ])

    fig, ax = plt.subplots(figsize=(8, 8))
    ax.scatter(rel_x, rel_y, c=rgb, s=26, edgecolors="none")
    ax.set_title(f"Colour Map (normalized RGB)\n{csv_path.name}")
    ax.set_xlabel("relative x (mm)")
    ax.set_ylabel("relative y (mm)")
    ax.set_aspect("equal", adjustable="box")
    ax.grid(alpha=0.25)
    plt.tight_layout()
    plt.show()
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
