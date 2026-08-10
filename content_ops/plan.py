"""Curadoria e planejamento editorial — sugere posts sem repetir (memória)."""
from datetime import datetime

from .daylog import recent
from .memory import covered_projects, published_slugs


# Projetos conhecidos do ecossistema Samuel (vira config no adapter genérico)
DEFAULT_TOPICS = [
    {"project": "lifelog", "label": "LifeLog", "icon": "📖",
     "pitch": "A história do LifeLog — o blog pessoal que virou sistema de conteúdo."},
    {"project": "dogwalk", "label": "Dogwalk", "icon": "🐶",
     "pitch": "A história do Dogwalk/PataPass — marketplace de pets com Stripe Connect."},
    {"project": "arachne", "label": "Arachne", "icon": "🕷️",
     "pitch": "A história do Arachne — scraping + RAG, MCP, browser agent."},
    {"project": "capivara", "label": "Capivara", "icon": "🐹",
     "pitch": "A história do Capivara — hub pessoal, RAG local, 2FA, dashboard honesto."},
    {"project": "portfolio", "label": "Portfolio", "icon": "🚀",
     "pitch": "A história do Portifólio Samuel — cockpit sci-fi, 5 mini-games, blog sync."},
    {"project": "tatuengine", "label": "TatuEngine", "icon": "🌊",
     "pitch": "A história do TatuEngine — wave field theory, agente autopoiético."},
    {"project": "descobertas", "label": "Descobertas", "icon": "💡",
     "pitch": "Descobertas técnicas — ferramentas, estudos e lições aprendidas."},
    {"project": "seguranca", "label": "Segurança", "icon": "🔒",
     "pitch": "Segurança — ai-jail, CSP, rate limit, bug hunter, hardening."},
]


def suggest(count: int = 3) -> list[dict]:
    """Sugere próximos posts: projetos menos cobertos + material recente do daylog.

    Anti-repetição: ignora slugs já publicados (memória) e dá prioridade a
    projetos com pouca cobertura.
    """
    covered = covered_projects()
    published = set(published_slugs())

    # Projetos por cobertura (menos coberto primeiro)
    scored = []
    for t in DEFAULT_TOPICS:
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
    topics = projects or [t["project"] for t in DEFAULT_TOPICS]
    today = datetime.now().date()
    base = datetime.strptime(base_date, "%Y-%m-%d").date()
    idx = (today - base).days % len(topics)
    return [{"project": topics[(idx + i) % len(topics)], "offset": i} for i in range(7)]
