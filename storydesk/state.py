"""Estado e config do storydesk — ~/.storydesk/ (JSON, sem secrets)."""
import json
import os
from pathlib import Path

CONFIG_DIR = Path(os.environ.get("STORYDESK_HOME", Path.home() / ".storydesk"))
CONFIG_FILE = CONFIG_DIR / "config.json"
STATE_FILE = CONFIG_DIR / "state.json"
DAYLOG_FILE = CONFIG_DIR / "daylog.json"

# Diretório legado (content-ops <= 0.1) — migrado uma única vez
LEGACY_DIR = Path.home() / ".content-ops"


def _migrate_legacy_home():
    """Copia o estado do content-ops (~/.content-ops) na 1a execução, se existir."""
    if not LEGACY_DIR.exists() or CONFIG_DIR.exists():
        return
    import shutil

    shutil.copytree(LEGACY_DIR, CONFIG_DIR)


def ensure_dirs():
    _migrate_legacy_home()
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)


def load_json(path: Path, default):
    ensure_dirs()  # garante migração do legado também no caminho de leitura
    if not path.exists():
        return default
    try:
        with open(path) as f:
            return json.load(f)
    except Exception:
        return default


def save_json(path: Path, data):
    ensure_dirs()
    tmp = path.with_suffix(".tmp")
    with open(tmp, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    tmp.replace(path)


def get_config() -> dict:
    cfg = load_json(CONFIG_FILE, {})
    cfg.setdefault("blogs", [])  # [{name, adapter, repo_path, url}]
    cfg.setdefault("default_blog", None)
    return cfg


def save_config(cfg: dict):
    save_json(CONFIG_FILE, cfg)


def get_state() -> dict:
    st = load_json(STATE_FILE, {})
    st.setdefault("published", [])   # [{slug, title, project, date, blog}]
    st.setdefault("covered_projects", {})  # {project: [slugs]}
    st.setdefault("drafts", [])       # [{slug, status: draft|ready|published}]
    return st


def save_state(st: dict):
    save_json(STATE_FILE, st)


def get_daylog() -> dict:
    dl = load_json(DAYLOG_FILE, {})
    dl.setdefault("days", {})  # {"2026-08-09": ["nota 1", "nota 2"]}
    return dl


def save_daylog(dl: dict):
    save_json(DAYLOG_FILE, dl)
