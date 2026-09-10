"""Memória editorial — o que já foi publicado/coberto, anti-repetição na curadoria."""
from .state import get_state, save_state


def mark_published(slug: str, title: str, project: str, blog: str = "lifelog"):
    st = get_state()
    st["published"].append({"slug": slug, "title": title, "project": project,
                            "date": __import__("datetime").datetime.now().isoformat(),
                            "blog": blog})
    st["covered_projects"].setdefault(project, [])
    if slug not in st["covered_projects"][project]:
        st["covered_projects"][project].append(slug)
    save_state(st)


def mark_draft(slug: str, project: str, status: str = "ready"):
    st = get_state()
    st["drafts"].append({"slug": slug, "project": project, "status": status})
    save_state(st)


def is_covered(slug: str, project: str | None = None) -> bool:
    st = get_state()
    for p in st["published"]:
        if p["slug"] == slug:
            return True
    if project and slug in st["covered_projects"].get(project, []):
        return True
    return False


def published_slugs() -> list[str]:
    return [p["slug"] for p in get_state()["published"]]


def covered_projects() -> dict:
    return get_state()["covered_projects"]


def summary() -> dict:
    st = get_state()
    return {
        "published_count": len(st["published"]),
        "draft_count": len(st["drafts"]),
        "covered_projects": st["covered_projects"],
        "last_published": st["published"][-1] if st["published"] else None,
    }
