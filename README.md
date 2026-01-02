# Productivity Calendar (Windows) — ZALDRION Style ⚡

Una app de escritorio (Windows) para **seguimiento de productividad** usando:
- 📅 Calendario mensual con clics de color (cíclico: none → 🟢 → 🔴 → 🟠 → none)
- 📊 % por día (0–100)
- 🎯 Metas semanal/mensual con ✔ / ❌
- 🔥 Heatmap anual estilo GitHub (por %)
- 📈 Gráficas: línea diaria (mes visible) y barras por mes (año actual)
- 🌙 Modo claro/oscuro

> Los datos se guardan localmente en SQLite (archivo `productivity_calendar.db`).

---

## Requisitos
- Windows 10/11
- Python 3.10+ (recomendado 3.11/3.12)

---

## 🖥️ Compatibilidad

Este proyecto es **multiplataforma** y funciona en los siguientes sistemas:

### Sistemas Operativos
- ✅ **Windows 10 / 11**
- ✅ **Linux** (Ubuntu, Debian, Kali Linux, Fedora, Arch)
- ⚠️ **macOS** (funciona, pero no probado oficialmente)

### Notas
- En Linux puede ser necesario instalar Tkinter manualmente:
  ```bash
  sudo apt install python3-tk

---

## Ejecutar (rápido)
### Opción A: con script
- Doble clic: `scripts/run.bat`

### Opción B: desde terminal
```bash
python -m productivity_calendar
```

---

## Estructura del proyecto
```text
ProductivityCalendar/
  productivity_calendar/
    __init__.py
    __main__.py
    app.py
    repo.py
    themes.py
    utils.py
    heatmap.py
    charts.py
  scripts/
    run.bat
    run.ps1
  docs/
    screenshots/
  tests/
  .github/workflows/
    ci.yml
  .gitignore
  LICENSE
  requirements.txt
  pyproject.toml
```

---

## Persistencia
En el mismo folder donde corres la app se crea `productivity_calendar.db`.
Puedes copiar ese archivo como backup.

---

## Construir .EXE (opcional)
```bash
pip install -r requirements.txt
pip install pyinstaller
pyinstaller --onefile --windowed -n ProductivityCalendar productivity_calendar/__main__.py
```
El `.exe` queda en `dist/`.
