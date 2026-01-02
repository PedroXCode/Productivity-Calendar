from __future__ import annotations
import math
from datetime import date, timedelta
import tkinter as tk
from .utils import iso, pct_to_heat_color

def render_heatmap(canvas: tk.Canvas, theme: dict, repo, year: int, label_widget=None) -> None:
    canvas.delete("all")
    canvas.configure(bg=theme["bg"])
    if label_widget is not None:
        label_widget.config(text=f"Año {year}")

    start = date(year, 1, 1)
    end = date(year, 12, 31)
    rows = repo.get_range(start, end)
    pct_map = {d_iso: pct for d_iso, _, pct in rows}

    grid_start = start - timedelta(days=start.weekday())
    grid_end = end + timedelta(days=(6 - end.weekday()))
    total_days = (grid_end - grid_start).days + 1
    weeks = math.ceil(total_days / 7)

    W = max(1, canvas.winfo_width())
    padding = 16
    cell = max(10, min(18, (W - padding * 2) // (weeks + 2)))
    gap = 2

    labels = ["L", "M", "X", "J", "V", "S", "D"]
    for r, lab in enumerate(labels):
        canvas.create_text(padding, padding + r * (cell + gap) + cell/2,
                           text=lab, fill=theme["muted"], font=("Segoe UI", 9), anchor="w")

    d = grid_start
    for i in range(weeks):
        for r in range(7):
            x0 = padding + 22 + i * (cell + gap)
            y0 = padding + r * (cell + gap)
            x1 = x0 + cell
            y1 = y0 + cell

            in_year = (d.year == year)
            pct = pct_map.get(iso(d), -1)
            if (0 <= pct <= 100) and in_year:
                fill = pct_to_heat_color(pct)
            else:
                fill = theme["heatmap_empty"] if in_year else theme["bg"]

            rect = canvas.create_rectangle(x0, y0, x1, y1, outline=theme["grid_border"], width=1, fill=fill)

            dd = d
            pp = pct
            def on_enter(_e, dd=dd, pp=pp, x=x0, y=y0):
                if dd.year != year:
                    return
                txt = f"{iso(dd)}  |  {'—' if not (0<=pp<=100) else str(pp)+'%'}"
                canvas.delete("tooltip")
                canvas.create_text(x, y-10, text=txt, fill=theme["fg"], font=("Segoe UI", 9),
                                   anchor="sw", tags="tooltip")
            def on_leave(_e):
                canvas.delete("tooltip")
            canvas.tag_bind(rect, "<Enter>", on_enter)
            canvas.tag_bind(rect, "<Leave>", on_leave)

            d += timedelta(days=1)
