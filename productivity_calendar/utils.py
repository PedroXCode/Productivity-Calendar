from __future__ import annotations
from datetime import date, timedelta

def iso(d: date) -> str:
    return d.strftime("%Y-%m-%d")

def start_of_week(d: date) -> date:
    return d - timedelta(days=d.weekday())

def end_of_week(d: date) -> date:
    return start_of_week(d) + timedelta(days=6)

def start_of_year(d: date) -> date:
    return date(d.year, 1, 1)

def end_of_year(d: date) -> date:
    return date(d.year, 12, 31)

def clamp_int(v: int, lo: int, hi: int) -> int:
    return max(lo, min(hi, int(v)))

def pct_to_heat_color(pct: int) -> str:
    """Map 0..100 -> red..green gradient."""
    pct = clamp_int(pct, 0, 100)
    r1, g1, b1 = (220, 53, 69)
    r2, g2, b2 = (25, 135, 84)
    t = pct / 100.0
    r = round(r1 + (r2 - r1) * t)
    g = round(g1 + (g2 - g1) * t)
    b = round(b1 + (b2 - b1) * t)
    return f"#{r:02x}{g:02x}{b:02x}"
