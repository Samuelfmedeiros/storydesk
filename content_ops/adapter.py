"""Adaptador genérico de conteúdo — interface para blogs/sites.

LifeLog (Astro/MDX) é o adapter de referência; outros blogs implementam
a mesma interface (ghost, wordpress, astro genérico, etc).
"""
from abc import ABC, abstractmethod


class ContentAdapter(ABC):
    """Interface mínima que todo blog/site precisa expor."""

    name: str = "generic"

    @abstractmethod
    def init(self, repo_path: str) -> bool:
        """Vincula o content-ops ao repo/blog. Retorna True se ok."""

    @abstractmethod
    def draft_path(self, slug: str, lang: str) -> str:
        """Caminho do arquivo de rascunho para slug+lang (ex: 'pt'/'en')."""

    @abstractmethod
    def write_draft(self, slug: str, lang: str, content: str) -> str:
        """Escreve o rascunho e retorna o caminho."""

    @abstractmethod
    def list_slugs(self) -> list[str]:
        """Slugs já publicados no blog (para memória/anti-repetição)."""

    @abstractmethod
    def build(self) -> bool:
        """Roda o build do blog. Retorna True se passou."""

    @abstractmethod
    def publish(self, slug: str) -> bool:
        """Commit+push (publica). Sempre chamado após aprovação humana."""

    def verify_live(self, url: str, slug: str) -> bool:
        """Verifica se o post está no ar (URL + slug no HTML)."""
        import urllib.request

        try:
            req = urllib.request.Request(url, headers={"User-Agent": "content-ops/0.1"})
            with urllib.request.urlopen(req, timeout=15) as resp:
                html = resp.read().decode("utf-8", errors="replace")
            return slug in html
        except Exception:
            return False
