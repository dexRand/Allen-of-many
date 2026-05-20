"""Converte wikilink Obsidian e embed immagini in Markdown per MkDocs."""

from __future__ import annotations

import os
import re
from collections import defaultdict
from pathlib import Path

from mkdocs.utils import get_relative_url

EMBED_RE = re.compile(r"!\[\[([^\]|#]+)(?:\|(\d+))?\]\]")
WIKILINK_RE = re.compile(
    r"(?<!!)\[\[([^\]|#]+)(?:#([^\]|]+))?(?:\|([^\]]+))?\]\]"
)

_IMAGE_EXT = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg", ".bmp"}

_ASSETS: dict[str, list[str]] = {}
_MD_PAGES: dict[str, object] = {}


def _norm(name: str) -> str:
    return re.sub(r"[\s_\-]", "", name.casefold()).replace(".md", "")


def _asset_keys(name: str) -> set[str]:
    raw = name.strip()
    p = Path(raw)
    return {_norm(raw), _norm(p.stem), _norm(p.name)}


def on_files(files, config):
    """Indice di tutti i file in docs_dir (note + allegati)."""
    global _ASSETS, _MD_PAGES
    _ASSETS = defaultdict(list)
    _MD_PAGES = {}

    docs_dir = Path(config.docs_dir)
    if not docs_dir.is_dir():
        return

    for root, _, names in os.walk(docs_dir, followlinks=True):
        for name in names:
            rel = Path(root, name).relative_to(docs_dir).as_posix()
            for key in _asset_keys(name):
                if rel not in _ASSETS[key]:
                    _ASSETS[key].append(rel)

    for file in files:
        if file.is_documentation_page():
            _MD_PAGES[file.src_path.replace("\\", "/")] = file


def _pick_asset(keys: set[str]) -> str | None:
    for key in keys:
        matches = _ASSETS.get(key)
        if not matches:
            continue
        # Preferisci note .md rispetto ad allegati omonimi
        for rel in matches:
            if rel.endswith(".md"):
                return rel
        return matches[0]
    return None


def _pick_md_page(target: str) -> str | None:
    """Risolve [[Nota]] usando l'indice pagine MkDocs."""
    for key in _asset_keys(target):
        for src_path in _MD_PAGES:
            if _norm(Path(src_path).stem) == key:
                return src_path
    return None


def _rel_href(page_src: str, asset_rel: str, docs_dir: Path) -> str:
    from_dir = (docs_dir / page_src).parent
    rel = os.path.relpath(docs_dir / asset_rel, from_dir).replace("\\", "/")
    return rel


def _replace_embed(match: re.Match, page, docs_dir: Path) -> str:
    name = match.group(1).strip()
    width = match.group(2)
    asset = _pick_asset(_asset_keys(name))
    if not asset:
        return match.group(0)

    href = _rel_href(page.file.src_path, asset, docs_dir)
    alt = Path(name).stem
    if width:
        return f'![{alt}]({href}){{ width="{width}px" }}'
    return f"![{alt}]({href})"


def _replace_wikilink(match: re.Match, page, docs_dir: Path) -> str:
    target = match.group(1).strip()
    anchor = match.group(2) or ""
    alias = match.group(3)

    # Tag Obsidian ([[+canon]]): solo testo, mai link
    if target.startswith("+"):
        return alias or target

    ext = Path(target).suffix.lower()
    if ext in _IMAGE_EXT:
        asset = _pick_asset(_asset_keys(target))
        if asset:
            href = _rel_href(page.file.src_path, asset, docs_dir)
            label = alias or Path(target).stem
            return f"![{label}]({href})"
        return match.group(0)

    md_path = _pick_md_page(target)
    if md_path:
        src_file = _MD_PAGES.get(md_path)
        if src_file:
            href = get_relative_url(src_file.url, page.url)
        else:
            href = _rel_href(page.file.src_path, md_path, docs_dir)
        if anchor:
            href += "#" + re.sub(
                r"[^\w\u4e00-\u9fff\- ]", "", anchor.strip().lower()
            ).replace(" ", "-")
        label = alias or Path(target).stem
        return f"[{label}]({href})"

    return match.group(0)


def on_page_markdown(markdown, page, config, files, **kwargs):
    docs_dir = Path(config.docs_dir)
    markdown = EMBED_RE.sub(lambda m: _replace_embed(m, page, docs_dir), markdown)
    markdown = WIKILINK_RE.sub(
        lambda m: _replace_wikilink(m, page, docs_dir), markdown
    )
    return markdown
