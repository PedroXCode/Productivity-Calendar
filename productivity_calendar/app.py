from __future__ import annotations
import tkinter as tk
from tkinter import ttk, simpledialog
from datetime import date
import calendar

from .repo import Repo
from .themes import THEMES, CLICK_BG
from .utils import iso, start_of_week, end_of_week, start_of_year, end_of_year, clamp_int
from .heatmap import render_heatmap
from .charts import render_charts

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Productivity Calendar")
        self.geometry("980x720")
        self.minsize(900, 620)

        self.repo = Repo()

        self.visible_year = date.today().year
        self.visible_month = date.today().month
        self.selected_date = date.today()
        self.heat_year = date.today().year

        self.theme_name = self.repo.get_setting("theme") or "light"
        self.theme = THEMES["light"]

        self._build_ui()
        self.apply_theme()
        self.render_calendar()
        self.refresh_all()

        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.bind("<Configure>", self._on_resize)

    def on_close(self):
        self.repo.close()
        self.destroy()

    def apply_theme(self):
        self.theme = THEMES["dark"] if self.theme_name == "dark" else THEMES["light"]
        self.configure(bg=self.theme["bg"])

        style = ttk.Style(self)
        try:
            style.theme_use("vista")
        except:
            pass

        style.configure("TFrame", background=self.theme["bg"])
        style.configure("TLabel", background=self.theme["bg"], foreground=self.theme["fg"])
        style.configure("Muted.TLabel", background=self.theme["bg"], foreground=self.theme["muted"])
        style.configure("TNotebook", background=self.theme["bg"])
        style.configure("TNotebook.Tab", padding=[10, 6])

        if hasattr(self, "day_buttons"):
            for btn in self.day_buttons.values():
                try:
                    btn.configure(bg=self.theme["empty_cell"], fg=self.theme["fg"], activebackground=self.theme["hover"])
                except:
                    pass

        if hasattr(self, "heat_canvas"):
            self.heat_canvas.configure(bg=self.theme["bg"])
        if hasattr(self, "charts_canvas"):
            self.charts_canvas.configure(bg=self.theme["bg"])

        self.render_heatmap()
        self.render_charts()

    def toggle_theme(self):
        self.theme_name = self.var_theme.get()
        self.repo.set_setting("theme", self.theme_name)
        self.apply_theme()
        self.refresh_all()

    def _build_ui(self):
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

        self.tab_calendar = ttk.Frame(self.notebook)
        self.tab_year = ttk.Frame(self.notebook)
        self.tab_charts = ttk.Frame(self.notebook)
        self.tab_settings = ttk.Frame(self.notebook)

        self.notebook.add(self.tab_calendar, text="Calendario")
        self.notebook.add(self.tab_year, text="Heatmap anual")
        self.notebook.add(self.tab_charts, text="Gráficas")
        self.notebook.add(self.tab_settings, text="Ajustes")

        header = ttk.Frame(self.tab_calendar); header.pack(fill="x", padx=8, pady=(8, 6))
        ttk.Button(header, text="◀", command=self.prev_month).pack(side="left")
        self.lbl_month = ttk.Label(header, text="", font=("Segoe UI", 16, "bold")); self.lbl_month.pack(side="left", padx=12)
        ttk.Button(header, text="▶", command=self.next_month).pack(side="left")

        goals = ttk.Frame(self.tab_calendar); goals.pack(fill="x", padx=8, pady=(0, 6))
        self.lbl_goal_month = ttk.Label(goals, text="Meta del mes: —", font=("Segoe UI", 11, "bold"))
        self.lbl_goal_month.pack(side="left", padx=(0, 18))
        self.lbl_goal_week = ttk.Label(goals, text="Meta de la semana: —", font=("Segoe UI", 11, "bold"))
        self.lbl_goal_week.pack(side="left", padx=(0, 18))
        ttk.Button(goals, text="Cambiar metas", command=self.set_goals).pack(side="right")

        stats = ttk.Frame(self.tab_calendar); stats.pack(fill="x", padx=8, pady=(0, 10))
        self.stat_week = ttk.Label(stats, text="Semana (prom): —"); self.stat_week.pack(side="left", padx=(0, 18))
        self.stat_month = ttk.Label(stats, text="Mes (prom): —"); self.stat_month.pack(side="left", padx=(0, 18))
        self.stat_year = ttk.Label(stats, text="Año (prom): —"); self.stat_year.pack(side="left", padx=(0, 18))
        self.color_counts = ttk.Label(stats, text="Este mes: 🟢 0  🔴 0  🟠 0"); self.color_counts.pack(side="left", padx=(18, 0))

        container = ttk.Frame(self.tab_calendar); container.pack(fill="both", expand=True, padx=8, pady=6)
        dow = ttk.Frame(container); dow.pack(fill="x")
        for i, name in enumerate(["L","M","X","J","V","S","D"]):
            lbl = ttk.Label(dow, text=name, anchor="center", font=("Segoe UI", 10, "bold"))
            lbl.grid(row=0, column=i, sticky="nsew", padx=2, pady=2)
            dow.grid_columnconfigure(i, weight=1)

        self.grid_frame = ttk.Frame(container); self.grid_frame.pack(fill="both", expand=True)

        bottom = ttk.Frame(self.tab_calendar); bottom.pack(fill="x", padx=8, pady=10)
        self.lbl_selected = ttk.Label(bottom, text="", font=("Segoe UI", 11, "bold")); self.lbl_selected.pack(side="left")
        ttk.Button(bottom, text="Quitar %", command=self.clear_percent).pack(side="right")
        ttk.Button(bottom, text="Editar %", command=self.edit_percent).pack(side="right", padx=(0, 8))

        yhead = ttk.Frame(self.tab_year); yhead.pack(fill="x", padx=8, pady=(8, 6))
        ttk.Button(yhead, text="◀ Año", command=self.prev_heat_year).pack(side="left")
        self.lbl_heat_year = ttk.Label(yhead, text="", font=("Segoe UI", 14, "bold")); self.lbl_heat_year.pack(side="left", padx=12)
        ttk.Button(yhead, text="Año ▶", command=self.next_heat_year).pack(side="left")
        ttk.Label(yhead, text="0% rojo → 100% verde", style="Muted.TLabel").pack(side="right")

        self.heat_canvas = tk.Canvas(self.tab_year, highlightthickness=0)
        self.heat_canvas.pack(fill="both", expand=True, padx=8, pady=8)

        chead = ttk.Frame(self.tab_charts); chead.pack(fill="x", padx=8, pady=(8, 6))
        ttk.Label(chead, text="Gráficas (basadas en %)", font=("Segoe UI", 12, "bold")).pack(side="left")
        ttk.Button(chead, text="Refrescar", command=self.render_charts).pack(side="right")

        self.charts_canvas = tk.Canvas(self.tab_charts, highlightthickness=0)
        self.charts_canvas.pack(fill="both", expand=True, padx=8, pady=8)

        s = ttk.Frame(self.tab_settings); s.pack(fill="both", expand=True, padx=12, pady=12)
        ttk.Label(s, text="Ajustes", font=("Segoe UI", 14, "bold")).pack(anchor="w", pady=(0, 10))

        self.var_theme = tk.StringVar(value=self.theme_name)
        row = ttk.Frame(s); row.pack(fill="x", pady=6)
        ttk.Label(row, text="Modo:").pack(side="left")
        ttk.Radiobutton(row, text="☀️ Claro", variable=self.var_theme, value="light", command=self.toggle_theme).pack(side="left", padx=10)
        ttk.Radiobutton(row, text="🌙 Oscuro", variable=self.var_theme, value="dark", command=self.toggle_theme).pack(side="left", padx=10)

        ttk.Separator(s).pack(fill="x", pady=16)
        ttk.Button(s, text="Ir al mes actual", command=self.go_today).pack(anchor="w")

    # navigation
    def go_today(self):
        self.visible_year = date.today().year
        self.visible_month = date.today().month
        self.selected_date = date.today()
        self.render_calendar()
        self.refresh_all()

    def prev_month(self):
        if self.visible_month == 1:
            self.visible_month = 12; self.visible_year -= 1
        else:
            self.visible_month -= 1
        self.render_calendar(); self.refresh_all()

    def next_month(self):
        if self.visible_month == 12:
            self.visible_month = 1; self.visible_year += 1
        else:
            self.visible_month += 1
        self.render_calendar(); self.refresh_all()

    def prev_heat_year(self):
        self.heat_year -= 1; self.render_heatmap()

    def next_heat_year(self):
        self.heat_year += 1; self.render_heatmap()

    # interaction
    def set_selected(self, d: date):
        self.selected_date = d
        self.update_bottom()

    def next_color(self, state: int) -> int:
        return 1 if state == 0 else 2 if state == 1 else 3 if state == 2 else 0

    def edit_percent(self):
        st, pct = self.repo.get_day(self.selected_date)
        initial = pct if 0 <= pct <= 100 else 0
        val = simpledialog.askinteger("Productividad", "Ingresa porcentaje (0–100):",
                                      parent=self, minvalue=0, maxvalue=100, initialvalue=initial)
        if val is None:
            return
        self.repo.upsert_day(self.selected_date, st, int(val))
        self.render_calendar(); self.refresh_all()

    def clear_percent(self):
        st, _ = self.repo.get_day(self.selected_date)
        self.repo.upsert_day(self.selected_date, st, -1)
        self.render_calendar(); self.refresh_all()

    def day_click(self, d: date, btn: tk.Button):
        st, pct = self.repo.get_day(d)
        self.repo.upsert_day(d, self.next_color(st), pct)
        self.set_selected(d)
        self.paint_button(d, btn)
        self.refresh_all(keep_calendar=True)

    def day_double_click(self, d: date):
        self.set_selected(d)
        self.edit_percent()

    def paint_button(self, d: date, btn: tk.Button):
        st, pct = self.repo.get_day(d)
        bg = CLICK_BG.get(st)
        pct_txt = f"\n{pct}%" if 0 <= pct <= 100 else ""
        base_bg = self.theme["empty_cell"]
        show_bg = base_bg if bg is None else bg
        btn.configure(text=f"{d.day}{pct_txt}", bg=show_bg, fg=self.theme["fg"],
                      activebackground=self.theme["hover"], relief="solid",
                      bd=2 if d == self.selected_date else 1, highlightthickness=0)

    def render_calendar(self):
        for child in self.grid_frame.winfo_children():
            child.destroy()
        self.day_buttons = {}

        ym = date(self.visible_year, self.visible_month, 1)
        month_name = ym.strftime("%B %Y")
        self.lbl_month.config(text=month_name[:1].upper() + month_name[1:])

        cal = calendar.Calendar(firstweekday=0)
        weeks = cal.monthdatescalendar(self.visible_year, self.visible_month)

        for r in range(len(weeks)):
            self.grid_frame.grid_rowconfigure(r, weight=1)
        for c in range(7):
            self.grid_frame.grid_columnconfigure(c, weight=1)

        for r, week in enumerate(weeks):
            for c, d in enumerate(week):
                in_month = (d.month == self.visible_month)
                btn = tk.Button(self.grid_frame, text="",
                                font=("Segoe UI", 11, "bold"),
                                anchor="nw", justify="left",
                                bg=self.theme["empty_cell"],
                                fg=(self.theme["fg"] if in_month else self.theme["disabled_fg"]),
                                relief="solid", bd=1,
                                cursor="hand2" if in_month else "arrow",
                                activebackground=self.theme["hover"],
                                wraplength=110)
                btn.grid(row=r, column=c, sticky="nsew", padx=3, pady=3)

                if in_month:
                    btn.bind("<Button-1>", lambda e, dd=d, b=btn: self.day_click(dd, b))
                    btn.bind("<Double-Button-1>", lambda e, dd=d: self.day_double_click(dd))
                    btn.bind("<Button-3>", lambda e, dd=d: (self.set_selected(dd), None))
                    self.paint_button(d, btn)
                else:
                    btn.configure(state="disabled", disabledforeground=self.theme["disabled_fg"], text=str(d.day), bg=self.theme["bg"])

                self.day_buttons[(r, c)] = btn

        if self.selected_date.month != self.visible_month or self.selected_date.year != self.visible_year:
            self.selected_date = date(self.visible_year, self.visible_month, 1)
        self.update_bottom()

    # stats/goals
    def _avg_for_range(self, start: date, end: date):
        rows = self.repo.get_range(start, end)
        vals = [pct for _, _, pct in rows if 0 <= pct <= 100]
        return None if not vals else sum(vals) / len(vals)

    def _color_counts_for_month(self, year: int, month: int):
        start = date(year, month, 1)
        end = date(year, month, calendar.monthrange(year, month)[1])
        rows = self.repo.get_range(start, end)
        g = r = o = 0
        for _, cs, _ in rows:
            if cs == 1: g += 1
            elif cs == 2: r += 1
            elif cs == 3: o += 1
        return g, r, o

    def set_goals(self):
        mg = int(self.repo.get_setting("month_goal") or "80")
        wg = int(self.repo.get_setting("week_goal") or "80")
        new_mg = simpledialog.askinteger("Meta del mes", "Define la meta del mes (0–100):",
                                         minvalue=0, maxvalue=100, initialvalue=mg, parent=self)
        if new_mg is None:
            return
        new_wg = simpledialog.askinteger("Meta de la semana", "Define la meta de la semana (0–100):",
                                         minvalue=0, maxvalue=100, initialvalue=wg, parent=self)
        if new_wg is None:
            return
        self.repo.set_setting("month_goal", str(clamp_int(new_mg, 0, 100)))
        self.repo.set_setting("week_goal", str(clamp_int(new_wg, 0, 100)))
        self.refresh_all()

    def refresh_goals(self):
        today = date.today()
        w_start, w_end = start_of_week(today), end_of_week(today)
        m_start = date(today.year, today.month, 1)
        m_end = date(today.year, today.month, calendar.monthrange(today.year, today.month)[1])

        week_avg = self._avg_for_range(w_start, w_end)
        month_avg = self._avg_for_range(m_start, m_end)

        month_goal = clamp_int(int(self.repo.get_setting("month_goal") or 80), 0, 100)
        week_goal = clamp_int(int(self.repo.get_setting("week_goal") or 80), 0, 100)

        self.lbl_goal_month.config(text=f"Meta del mes: {month_goal}%  {'✔' if (month_avg is not None and month_avg >= month_goal) else '❌'}")
        self.lbl_goal_week.config(text=f"Meta de la semana: {week_goal}%  {'✔' if (week_avg is not None and week_avg >= week_goal) else '❌'}")

    def update_bottom(self):
        _, pct = self.repo.get_day(self.selected_date)
        pct_text = f"{pct}%" if 0 <= pct <= 100 else "—"
        self.lbl_selected.config(text=f"Seleccionado: {iso(self.selected_date)}  |  %: {pct_text}")

    def refresh_stats(self):
        today = date.today()
        w_start, w_end = start_of_week(today), end_of_week(today)
        m_start = date(today.year, today.month, 1)
        m_end = date(today.year, today.month, calendar.monthrange(today.year, today.month)[1])
        y_start, y_end = start_of_year(today), end_of_year(today)

        w = self._avg_for_range(w_start, w_end)
        m = self._avg_for_range(m_start, m_end)
        y = self._avg_for_range(y_start, y_end)

        self.stat_week.config(text=f"Semana (prom): {'—' if w is None else str(round(w))+'%'}")
        self.stat_month.config(text=f"Mes (prom): {'—' if m is None else str(round(m))+'%'}")
        self.stat_year.config(text=f"Año (prom): {'—' if y is None else str(round(y))+'%'}")

        g, r, o = self._color_counts_for_month(self.visible_year, self.visible_month)
        self.color_counts.config(text=f"Este mes: 🟢 {g}  🔴 {r}  🟠 {o}")

    def refresh_all(self, keep_calendar=False):
        self.refresh_stats()
        self.refresh_goals()
        self.render_heatmap()
        self.render_charts()
        if not keep_calendar:
            self.update_bottom()

    def render_heatmap(self):
        render_heatmap(self.heat_canvas, self.theme, self.repo, self.heat_year, self.lbl_heat_year)

    def render_charts(self):
        render_charts(self.charts_canvas, self.theme, self.repo, self.visible_year, self.visible_month, self._avg_for_range)

    def _on_resize(self, _e=None):
        self.render_heatmap()
        self.render_charts()

def main():
    App().mainloop()
