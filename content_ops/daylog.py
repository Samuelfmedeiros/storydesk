"""Daylog — registra o dia a dia (matéria-prima das histórias)."""
from datetime import datetime

from .state import get_daylog, save_daylog


def add_note(text: str, when: str | None = None):
    day = (when or datetime.now().strftime("%Y-%m-%d"))
    hour = datetime.now().strftime("%H:%M")
    dl = get_daylog()
    dl["days"].setdefault(day, [])
    dl["days"][day].append({"time": hour, "text": text})
    save_daylog(dl)
    return day


def show(day: str | None = None):
    dl = get_daylog()
    day = day or datetime.now().strftime("%Y-%m-%d")
    notes = dl["days"].get(day, [])
    return notes


def recent(days: int = 3):
    """Últimos N dias com notas — usado pela curadoria/plan."""
    dl = get_daylog()
    ordered = sorted(dl["days"].keys(), reverse=True)
    out = {}
    for d in ordered[:days]:
        out[d] = dl["days"][d]
    return out
