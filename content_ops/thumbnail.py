"""Thumbnail — gera capa via Cloudflare FLUX (Worker) com fallback PIL.

Pipeline (documentado no LifeLog):
  1. Cloudflare Worker (FLUX.1 Schnell) — scripts/generate-cover.py do projeto
  2. Fallback PIL — lifelog-cover-gen.py (~/.hermes/scripts)
  3. Sem capa → aviso (não bloqueia)
"""
import os
import subprocess
from pathlib import Path

from .state import get_config


def generate(slug: str, project: str, repo_path: str, force: bool = False) -> str:
    """Gera a capa. Retorna caminho do arquivo ou "" se falhou (fallback avisado)."""
    covers_dir = Path(repo_path) / "public/covers"
    target = covers_dir / f"{slug}.webp"
    if target.exists() and not force:
        return str(target)

    # 1) Cloudflare Worker via script do projeto
    gen_script = Path(repo_path) / "scripts/generate-cover.py"
    if gen_script.exists():
        try:
            cmd = ["python3", str(gen_script), slug]
            if force:
                # força removendo antes (script não tem --force p/ slug único)
                if target.exists():
                    target.unlink()
            r = subprocess.run(cmd, cwd=repo_path, capture_output=True,
                               text=True, timeout=180)
            if r.returncode == 0 and target.exists():
                return str(target)
        except Exception:
            pass

    # 2) Fallback PIL (~/.hermes/scripts/lifelog-cover-gen.py)
    pil_script = Path.home() / ".hermes/scripts/lifelog-cover-gen.py"
    if pil_script.exists():
        try:
            r = subprocess.run(["python3", str(pil_script)], capture_output=True,
                               text=True, timeout=120)
            if r.returncode == 0 and target.exists():
                return str(target)
        except Exception:
            pass

    return ""  # sem capa → aviso (não bloqueia publicação)
