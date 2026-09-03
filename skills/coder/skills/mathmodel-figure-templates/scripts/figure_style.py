#!/usr/bin/env python3
"""Reusable Matplotlib style profiles for mathematical-modeling figures."""

from __future__ import annotations

from pathlib import Path
from typing import NamedTuple


class FigureProfile(NamedTuple):
    name: str
    single_column_width_mm: float
    double_column_width_mm: float
    body_size_pt: float
    panel_label_size_pt: float
    palette: tuple[str, ...]
    rcparams: dict[str, object]


BASE = {
    "font.family": "sans-serif",
    "font.sans-serif": ["Helvetica", "Arial", "DejaVu Sans", "Liberation Sans"],
    "svg.fonttype": "none",
    "pdf.fonttype": 42,
    "ps.fonttype": 42,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "legend.frameon": False,
    "savefig.bbox": "tight",
    "savefig.pad_inches": 0.03,
    "figure.facecolor": "white",
    "axes.facecolor": "white",
}


def with_base(**updates: object) -> dict[str, object]:
    values = dict(BASE)
    values.update(updates)
    return values


PROFILES = {
    "nature": FigureProfile(
        "nature", 89.0, 180.0, 6.0, 8.0,
        ("#3F4A6B", "#6E7793", "#A7ADBF", "#B33A29", "#D77257", "#6B7280"),
        with_base(**{
            "font.size": 6.0, "axes.labelsize": 7.0, "xtick.labelsize": 6.0,
            "ytick.labelsize": 6.0, "legend.fontsize": 6.0, "axes.linewidth": 0.7,
            "xtick.direction": "out", "ytick.direction": "out", "axes.edgecolor": "#1A1A1A",
            "text.color": "#1A1A1A", "axes.labelcolor": "#1A1A1A",
        }),
    ),
    "science": FigureProfile(
        "science", 89.0, 180.0, 7.0, 8.0,
        ("#355C7D", "#6C8EAD", "#C06C5B", "#7A9E7E", "#6B7280"),
        with_base(**{"font.size": 7.0, "axes.labelsize": 7.5, "xtick.labelsize": 6.5,
                     "ytick.labelsize": 6.5, "legend.fontsize": 6.5, "axes.linewidth": 0.75}),
    ),
    "ieee": FigureProfile(
        "ieee", 88.9, 184.0, 8.0, 9.0,
        ("#000000", "#3B6EA8", "#A65E2E", "#5B8C5A", "#707070"),
        with_base(**{"font.size": 8.0, "axes.labelsize": 8.0, "xtick.labelsize": 7.0,
                     "ytick.labelsize": 7.0, "legend.fontsize": 7.0, "axes.linewidth": 0.8}),
    ),
    "mcm": FigureProfile(
        "mcm", 82.0, 170.0, 8.5, 9.5,
        ("#2F5D7C", "#4F8A8B", "#C47F3A", "#7B6D8D", "#6B7280"),
        with_base(**{"font.size": 8.5, "axes.labelsize": 9.0, "xtick.labelsize": 8.0,
                     "ytick.labelsize": 8.0, "legend.fontsize": 8.0, "axes.linewidth": 0.8}),
    ),
    "cumcm": FigureProfile(
        "cumcm", 82.0, 170.0, 9.0, 10.0,
        ("#315B7D", "#4D8178", "#B7783C", "#756682", "#666666"),
        with_base(**{"font.sans-serif": ["Noto Sans CJK SC", "Source Han Sans SC", "Microsoft YaHei", "SimHei", "DejaVu Sans"],
                     "axes.unicode_minus": False, "font.size": 9.0, "axes.labelsize": 9.0,
                     "xtick.labelsize": 8.0, "ytick.labelsize": 8.0, "legend.fontsize": 8.0,
                     "axes.linewidth": 0.8}),
    ),
}


def get_profile(name: str) -> FigureProfile:
    key = name.strip().lower().replace("/", "-")
    aliases = {"nature-nmi": "nature", "nmi": "nature", "mcm-icm": "mcm", "icm": "mcm"}
    key = aliases.get(key, key)
    if key not in PROFILES:
        raise ValueError(f"unknown profile {name!r}; choose from {', '.join(sorted(PROFILES))}")
    return PROFILES[key]


def apply_profile(name: str) -> FigureProfile:
    import matplotlib as mpl

    profile = get_profile(name)
    mpl.rcParams.update(profile.rcparams)
    mpl.rcParams["axes.prop_cycle"] = mpl.cycler(color=profile.palette)
    return profile


def figure_size(name: str, columns: int = 1, aspect: float = 0.68) -> tuple[float, float]:
    profile = get_profile(name)
    width_mm = profile.single_column_width_mm if columns == 1 else profile.double_column_width_mm
    width_in = width_mm / 25.4
    return width_in, width_in * aspect


def add_panel_label(axis, label: str, profile: str = "nature") -> None:
    values = get_profile(profile)
    axis.text(-0.12, 1.04, label.lower(), transform=axis.transAxes,
              fontsize=values.panel_label_size_pt, fontweight="bold",
              fontstyle="normal", va="bottom", ha="left")


def save_figure(figure, output_stem: str | Path, dpi: int = 450) -> list[Path]:
    stem = Path(output_stem)
    stem.parent.mkdir(parents=True, exist_ok=True)
    outputs = [stem.with_suffix(suffix) for suffix in (".pdf", ".svg", ".png")]
    figure.savefig(outputs[0], bbox_inches="tight")
    figure.savefig(outputs[1], bbox_inches="tight")
    figure.savefig(outputs[2], dpi=dpi, bbox_inches="tight")
    return outputs
