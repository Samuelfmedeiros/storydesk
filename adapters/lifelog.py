"""Adapter LifeLog — Astro + MDX (posts PT em posts/, EN em posts/en/).

Segue o padrão do LifeLog: bilíngue, frontmatter com project/tags/icon/cover,
capa em public/covers/, build com `npx astro build`.
"""
import os
import re
import subprocess
from pathlib import Path

from storydesk.adapter import ContentAdapter


class LifelogAdapter(ContentAdapter):
    name = "lifelog"

    def __init__(self, repo_path: str = ""):
        self.repo = Path(repo_path or os.environ.get("LIFELOG_REPO", ""))
        self.posts_dir = self.repo / "src/content/posts"
        self.en_dir = self.posts_dir / "en"
        self.covers_dir = self.repo / "public/covers"

    def init(self, repo_path: str) -> bool:
        self.repo = Path(repo_path)
        self.posts_dir = self.repo / "src/content/posts"
        self.en_dir = self.posts_dir / "en"
        self.covers_dir = self.repo / "public/covers"
        return (self.posts_dir.exists() and self.en_dir.exists())

    def draft_path(self, slug: str, lang: str) -> str:
        if lang == "en":
            return str(self.en_dir / f"{slug}.mdx")
        return str(self.posts_dir / f"{slug}.mdx")

    def write_draft(self, slug: str, lang: str, content: str) -> str:
        path = Path(self.draft_path(slug, lang))
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return str(path)

    def list_slugs(self) -> list[str]:
        slugs = set()
        for d in [self.posts_dir, self.en_dir]:
            if not d.exists():
                continue
            for f in d.glob("*.mdx"):
                slugs.add(f.stem)
        return sorted(slugs)

    def recent_slugs(self, n: int = 3) -> list[str]:
        """Slugs mais recentes por mtime (ignora EN duplicado)."""
        files = []
        seen = set()
        for d in [self.posts_dir, self.en_dir]:
            if not d.exists():
                continue
            for f in d.glob("*.mdx"):
                if f.stem in seen:
                    continue
                seen.add(f.stem)
                files.append(f)
        files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
        return [f.stem for f in files[:n]]

    def build(self) -> bool:
        r = subprocess.run(["npx", "astro", "build"], cwd=self.repo,
                           capture_output=True, text=True, timeout=420)
        return r.returncode == 0

    def publish(self, slug: str) -> bool:
        """Commit+push dos arquivos do slug (PT+EN+capa)."""
        files = []
        pt = self.posts_dir / f"{slug}.mdx"
        en = self.en_dir / f"{slug}.mdx"
        cover = self.covers_dir / f"{slug}.webp"
        for f in [pt, en, cover]:
            if f.exists():
                files.append(str(f.relative_to(self.repo)))
        if not files:
            return False
        r = subprocess.run(
            ["git", "add"] + files, cwd=self.repo, capture_output=True, text=True)
        if r.returncode != 0:
            return False
        r = subprocess.run(
            ["git", "commit", "-m", f"feat(post): {slug} [storydesk]"],
            cwd=self.repo, capture_output=True, text=True)
        if r.returncode != 0:
            return False
        r = subprocess.run(["git", "push", "origin", "main"], cwd=self.repo,
                           capture_output=True, text=True, timeout=90)
        return r.returncode == 0

    # ── helpers ─────────────────────────────────────────────
    def frontmatter(self, slug: str, lang: str) -> dict:
        path = Path(self.draft_path(slug, lang))
        if not path.exists():
            return {}
        content = path.read_text(encoding="utf-8")
        m = re.search(r"^---\n(.*?)\n---", content, re.S)
        if not m:
            return {}
        fm = {}
        for line in m.group(1).splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                fm[k.strip()] = v.strip().strip("\"'")
        return fm
