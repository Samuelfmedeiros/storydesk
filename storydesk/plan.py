"""Curadoria e planejamento editorial — sugere posts sem repetir (memória)."""
from datetime import datetime

from .daylog import recent
from .memory import covered_projects, published_slugs
from .state import get_config


# Tópicos padrão (neutros). Personalize com seus projetos em
# ~/.storydesk/config.json -> {"topics": [{"project", "label", "icon", "pitch"}]}
DEFAULT_TOPICS = [
    {"project": "devlog", "label": "Devlog", "icon": "🛠️",
     "pitch": "O que estou construindo agora — decisões, betes e progresso."},
    {"project": "descobertas", "label": "Descobertas", "icon": "💡",
     "pitch": "Ferramentas, estudos e lições aprendidas."},
    {"project": "automacao", "label": "Automação", "icon": "🤖",
     "pitch": "Automação, agentes e integrações que economizam horas."},
    {"project": "seguranca", "label": "Segurança", "icon": "🔒",
     "pitch": "Hardening, rate limit, CSP e lições de defesa."},
]


def get_topics() -> list[dict]:
    """Tópicos do usuário (config.json) ou os padrões neutros."""
    topics = get_config().get("topics")
    if isinstance(topics, list) and topics:
        return topics
    return DEFAULT_TOPICS


def suggest(count: int = 3) -> list[dict]:
    """Sugere próximos posts: projetos menos cobertos + material recente do daylog.

    Anti-repetição: ignora slugs já publicados (memória) e dá prioridade a
    projetos com pouca cobertura.
    """
    covered = covered_projects()
    published = set(published_slugs())

    # Projetos por cobertura (menos coberto primeiro)
    scored = []
    for t in get_topics():
        n = len(covered.get(t["project"], []))
        scored.append((n, t))
    scored.sort(key=lambda x: x[0])

    suggestions = []
    for _, topic in scored[:count]:
        # Material recente do daylog que menciona o projeto
        hints = []
        for day, notes in recent(2).items():
            for n in notes:
                low = n["text"].lower()
                if topic["project"].lower() in low or topic["label"].lower() in low:
                    hints.append(f"{day} {n['time']}: {n['text'][:80]}")
        suggestions.append({
            "project": topic["project"],
            "label": topic["label"],
            "icon": topic["icon"],
            "pitch": topic["pitch"],
            "covered": len(covered.get(topic["project"], [])),
            "daylog_hints": hints[:2],
        })
    return suggestions


def weekly_grid(base_date: str = "2026-07-24", projects=None) -> list[dict]:
    """Grade cíclica semanal: índice do dia = (hoje - base).days % len(projetos)."""
    topics = projects or [t["project"] for t in get_topics()]
    today = datetime.now().date()
    base = datetime.strptime(base_date, "%Y-%m-%d").date()
    idx = (today - base).days % len(topics)
    return [{"project": topics[(idx + i) % len(topics)], "offset": i} for i in range(7)]
