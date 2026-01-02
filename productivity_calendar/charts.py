from __future__ import annotations
import calendar
from datetime import date
import tkinter as tk
from .utils import iso, pct_to_heat_color

def _draw_box_title(cv: tk.Canvas, theme: dict, box, title: str):
    x0, y0, x1, y1 = box
    cv.create_rectangle(x0, y0, x1, y1, outline=theme["grid_border"], width=1, fill=theme["card"])
    cv.create_text(x0 + 10, y0 + 14, text=title, fill=theme["fg"], anchor="w", font=("Segoe UI", 11, "bold"))

def draw_line_daily_month(cv: tk.Canvas, theme: dict, repo, year: int, month: int, box):
    x0, y0, x1, y1 = box
    plot_pad = 40
    px0, py0, px1, py1 = x0 + 10, y0 + plot_pad, x1 - 10, y1 - 14

    days = calendar.monthrange(year, month)[1]
    start = date(year, month, 1)
    end = date(year, month, days)
    rows = repo.get_range(start, end)
    pct_map = {d_iso: pct for d_iso, _, pct in rows}

    points = [(d, pct_map.get(iso(date(year, month, d)), -1)) for d in range(1, days+1)]
    points = [(d, pct) for d, pct in points if 0 <= pct <= 100]

    cv.create_line(px0, py1, px1, py1, fill=theme["muted"])
    cv.create_line(px0, py0, px0, py1, fill=theme["muted"])
    cv.create_text(px0, py0-10, text="100%", fill=theme["muted"], anchor="w", font=("Segoe UI", 9))
    cv.create_text(px0, py1+10, text="0%", fill=theme["muted"], anchor="w", font=("Segoe UI", 9))

    if len(points) < 2:
        cv.create_text((px0+px1)/2, (py0+py1)/2, text="No hay suficientes datos (mínimo 2 días con %).",
                       fill=theme["muted"], font=("Segoe UI", 10))
        return

    def sx(day):
        return px0 + (day-1) * (px1-px0) / max(1, (days-1))
    def sy(pct):
        return py1 - (pct) * (py1-py0) / 100.0

    coords = []
    for d, pct in points:
        coords.extend([sx(d), sy(pct)])
    cv.create_line(*coords, fill=theme["fg"], width=2, smooth=True)

    for d, pct in points:
        x, y = sx(d), sy(pct)
        cv.create_oval(x-3, y-3, x+3, y+3, fill=theme["fg"], outline="")

def draw_bar_monthly_year(cv: tk.Canvas, theme: dict, repo, year: int, box, avg_for_range):
    x0, y0, x1, y1 = box
    plot_pad = 40
    px0, py0, px1, py1 = x0 + 10, y0 + plot_pad, x1 - 10, y1 - 14

    avgs = []
    for m in range(1, 13):
        s = date(year, m, 1)
        e = date(year, m, calendar.monthrange(year, m)[1])
        avgs.append(avg_for_range(s, e))

    cv.create_line(px0, py1, px1, py1, fill=theme["muted"])
    cv.create_line(px0, py0, px0, py1, fill=theme["muted"])
    cv.create_text(px0, py0-10, text="100%", fill=theme["muted"], anchor="w", font=("Segoe UI", 9))
    cv.create_text(px0, py1+10, text="0%", fill=theme["muted"], anchor="w", font=("Segoe UI", 9))

    bar_w = (px1 - px0) / 12.0
    for i, avg in enumerate(avgs):
        m = i + 1
        x_left = px0 + i * bar_w + 4
        x_right = px0 + (i+1) * bar_w - 4
        if avg is None:
            height = 0
            fill = theme["heatmap_empty"]
        else:
            height = (avg/100.0) * (py1 - py0)
            fill = pct_to_heat_color(int(round(avg)))

        y_top = py1 - height
        cv.create_rectangle(x_left, y_top, x_right, py1, outline=theme["grid_border"], width=1, fill=fill)
        cv.create_text((x_left+x_right)/2, py1+14, text=str(m), fill=theme["muted"], font=("Segoe UI", 8))
        if avg is not None:
            cv.create_text((x_left+x_right)/2, y_top-10, text=f"{round(avg)}%", fill=theme["fg"], font=("Segoe UI", 8))

def render_charts(canvas: tk.Canvas, theme: dict, repo, visible_year: int, visible_month: int, avg_for_range):
    canvas.delete("all")
    canvas.configure(bg=theme["bg"])
    W = max(1, canvas.winfo_width())
    H = max(1, canvas.winfo_height())
    pad = 30
    top_h = (H - pad*3)//2
    box1 = (pad, pad, W - pad, pad + top_h)
    box2 = (pad, pad*2 + top_h, W - pad, H - pad)

    _draw_box_title(canvas, theme, box1, "Línea diaria (mes visible)")
    draw_line_daily_month(canvas, theme, repo, visible_year, visible_month, box1)

    year = date.today().year
    _draw_box_title(canvas, theme, box2, f"Barras por mes (año {year})")
    draw_bar_monthly_year(canvas, theme, repo, year, box2, avg_for_range)
