"""Backlinks in fondo alla pagina (stile Obsidian «Menzioni nel documento»)."""

from __future__ import annotations

import re
from collections import defaultdict
from pathlib import Path

from mkdocs.utils import get_relative_url

WIKILINK_RE = re.compile(
    r"(?<!!)\[\[([^\]|#\]]+)(?:#[^\]|#\]]*)?(?:\|[^\]]*)?\]\]"
)

_BACKLINKS: dict[str, list[str]] = {}
_PAGES: dict[str, object] = {}
_TITLES: dict[str, str] = {}


def _norm(name: str) -> str:
    return name.strip().casefold()


def _page_title(src_path: str) -> str:
    if src_path in _TITLES:
        return _TITLES[src_path]
    # Come in Obsidian: titolo = nome del file (non il primo heading)
    title = Path(src_path).stem
    _TITLES[src_path] = title
    return title


def _index_pages(files) -> dict[str, list]:
    by_key: dict[str, list] = defaultdict(list)

    for file in files:
        if not file.is_documentation_page():
            continue
        _PAGES[file.src_path] = file
        rel = Path(file.src_path).as_posix()
        stem = Path(rel).stem
        for key in {_norm(stem), _norm(rel.removesuffix(".md"))}:
            if file not in by_key[key]:
                by_key[key].append(file)

    return by_key


def _resolve_target(target: str, by_key: dict[str, list]) -> list:
    raw = target.strip().replace("\\", "/")
    keys = [_norm(raw), _norm(Path(raw).stem)]
    seen: list = []
    for key in keys:
        for file in by_key.get(key, []):
            if file not in seen:
                seen.append(file)
    return seen


def on_files(files, config):
    """Scansiona i wikilink e costruisce l'indice pagina -> chi la cita."""
    global _BACKLINKS, _PAGES, _TITLES
    _BACKLINKS = defaultdict(list)
    _PAGES = {}
    _TITLES = {}

    by_key = _index_pages(files)
    docs_dir = Path(config.docs_dir)

    for file in files:
        if not file.is_documentation_page():
            continue
        src = docs_dir / file.src_path
        if not src.is_file():
            continue
        text = src.read_text(encoding="utf-8")
        for match in WIKILINK_RE.finditer(text):
            for dest in _resolve_target(match.group(1), by_key):
                if dest.src_path == file.src_path:
                    continue
                sources = _BACKLINKS[dest.src_path]
                if file.src_path not in sources:
                    sources.append(file.src_path)


def on_page_markdown(markdown, page, config, files, **kwargs):
    """Aggiunge la sezione Menzioni con link alle note che puntano qui."""
    heading = config.extra.get("backlinks", {}).get("heading", "Menzioni")
    if not config.extra.get("backlinks", {}).get("enabled", True):
        return markdown

    sources = _BACKLINKS.get(page.file.src_path)
    if not sources:
        return markdown

    lines = ["\n\n---\n", f"## {heading}\n"]
    for src_path in sorted(sources, key=lambda p: _page_title(p).casefold()):
        src_file = _PAGES.get(src_path)
        if not src_file:
            continue
        title = _page_title(src_path)
        # get_relative_url(dest, current_page)
        href = get_relative_url(src_file.url, page.url)
        lines.append(f"- [{title}]({href})\n")

    return markdown + "".join(lines)
