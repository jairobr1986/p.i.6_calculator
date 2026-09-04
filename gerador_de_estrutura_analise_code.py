#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gerador de estrutura do projeto (árvore + amostra de conteúdo)
- Seguro para repositórios grandes
- Opções de linha de comando (argparse)
- Limites de profundidade, linhas e bytes por arquivo
- Lista de ignorados extensível em runtime
- Redação automática de possíveis segredos (password, token, secret, api_key, azure_key)
- Modo --ai: gera também um contexto_*.txt (SO, Python, pip, git, amostra de settings.json)

Exemplos:
  python gerador_de_estrutura_analise_code.py --tree-only --max-depth 4
  python gerador_de_estrutura_analise_code.py --max-depth 3 --max-lines 200 --max-bytes 262144
  python gerador_de_estrutura_analise_code.py --ignore-dirs backups_ui,logs,data/output,data/errors
  python gerador_de_estrutura_analise_code.py --ai

Saída padrão:
  docs/estrutura_completa_YYYY-MM-DD_HH-MM-SS.txt
  (se --ai for usado, também: docs/contexto_YYYY-MM-DD_HH-MM-SS.txt)
"""

import os
import sys
import argparse
import datetime
import platform
import subprocess
import re
from pathlib import Path

# ---------- Defaults ----------
DEFAULT_IGNORE_DIRS = {
    ".git", "__pycache__", ".venv", "venv",
    "node_modules", "dist", "build", ".idea", ".vscode",
    # Operacionais comuns no projeto
    "backups_ui", "logs",
}
DEFAULT_IGNORE_FILES = {
    ".env", ".env.local", ".DS_Store", "Thumbs.db"
}
DEFAULT_IGNORE_EXT = {
    ".pyc", ".log", ".tmp", ".map", ".exe", ".dll",
    ".zip", ".7z", ".rar", ".tar", ".gz", ".xz",
    ".pdf", ".png", ".jpg", ".jpeg", ".gif", ".bmp", ".ico",
    ".mp4", ".avi", ".mkv", ".mov",
}

# Padrões para redigir segredos nas amostras
REDACTIONS = [
    re.compile(r"(password\s*=\s*)(.+)", re.I),
    re.compile(r"(secret(_key)?\s*=\s*)(.+)", re.I),
    re.compile(r"(token\s*=\s*)(.+)", re.I),
    re.compile(r"(api(_key)?\s*=\s*)(.+)", re.I),
    re.compile(r"(azure_?key\s*=\s*)(.+)", re.I),
]

# ---------- Helpers ----------
def parse_set(value: str | None, default: set[str]) -> set[str]:
    if not value:
        return set(default)
    items = [x.strip() for x in value.split(",") if x.strip()]
    return set(default).union(items)

def is_binary_by_ext(name: str, extra_bin_ext: set[str]) -> bool:
    _, ext = os.path.splitext(name.lower())
    return ext in extra_bin_ext

def is_binary_by_bytes(path: str, sample: int = 1024) -> bool:
    try:
        with open(path, "rb") as f:
            chunk = f.read(sample)
            # Heurística simples
            if b"\0" in chunk:
                return True
            text_ratio = sum(32 <= b <= 126 or b in (9, 10, 13) for b in chunk) / max(1, len(chunk))
            return text_ratio < 0.6
    except Exception:
        # Se não dá para ler, trata como binário para não travar
        return True

def should_ignore(base_dir: str, name: str, path: str,
                  ignore_dirs: set[str], ignore_files: set[str],
                  ignore_ext: set[str]) -> bool:
    if os.path.isdir(path):
        if name in ignore_dirs:
            return True
        # Ignorar subpaths específicos (evita despejar dados operacionais)
        sub = os.path.relpath(path, base_dir).replace("\\", "/")
        if sub.startswith("data/output") or sub.startswith("data/errors"):
            return True
    else:
        if name in ignore_files:
            return True
        _, ext = os.path.splitext(name)
        if ext.lower() in ignore_ext:
            return True
    return False

def redact_line(line: str) -> str:
    out = line
    for rx in REDACTIONS:
        out = rx.sub(r"\1***redacted***", out)
    return out

def safe_read_text(path: str, max_bytes: int) -> tuple[str, bool]:
    """
    Lê até max_bytes do arquivo tentando utf-8 e latin-1; se falhar, usa replace.
    Retorna (texto, truncado_bool).
    """
    size = os.path.getsize(path)
    to_read = min(size, max_bytes)
    with open(path, "rb") as f:
        data = f.read(to_read)
    truncated = size > to_read

    for enc in ("utf-8", "latin-1"):
        try:
            return data.decode(enc), truncated
        except Exception:
            continue
    return data.decode("utf-8", errors="replace"), truncated

def write_file_preview(path: str, fh, indent: str, max_lines: int, max_bytes: int, extra_bin_ext: set[str]):
    name = os.path.basename(path)
    # heurísticas de binário:
    if is_binary_by_ext(name, extra_bin_ext) or is_binary_by_bytes(path):
        fh.write(indent + "[ARQUIVO BINÁRIO]\n\n")
        return

    try:
        text, truncated = safe_read_text(path, max_bytes)
        lines = text.splitlines()
        if not lines:
            fh.write(indent + "[ARQUIVO VAZIO]\n\n")
            return

        fh.write(indent + "----- CONTEÚDO (amostra) -----\n")
        cut = lines[:max_lines]
        for ln in cut:
            fh.write(indent + redact_line(ln) + "\n")
        if truncated or len(lines) > max_lines:
            fh.write(indent + "[... conteúdo truncado ...]\n")
        fh.write(indent + "------------------------------\n\n")
    except Exception as e:
        fh.write(indent + f"[ERRO AO LER ARQUIVO: {e}]\n\n")

def list_tree(base_dir: str,
              current: str,
              fh,
              prefix: str,
              max_depth: int | None,
              depth: int,
              ignore_dirs: set[str],
              ignore_files: set[str],
              ignore_ext: set[str],
              tree_only: bool,
              max_lines: int,
              max_bytes: int):
    try:
        entries = sorted(os.listdir(current))
    except (PermissionError, FileNotFoundError):
        return

    # Filtra ignorados
    visible = []
    for item in entries:
        p = os.path.join(current, item)
        if should_ignore(base_dir, item, p, ignore_dirs, ignore_files, ignore_ext):
            continue
        visible.append(item)

    for idx, item in enumerate(visible):
        p = os.path.join(current, item)
        is_dir = os.path.isdir(p)
        connector = "├── " if idx < len(visible) - 1 else "└── "
        line = prefix + connector + item
        fh.write(line + "\n")

        if is_dir:
            if max_depth is None or depth < max_depth:
                new_prefix = prefix + ("│   " if idx < len(visible) - 1 else "    ")
                list_tree(base_dir, p, fh, new_prefix, max_depth, depth + 1,
                          ignore_dirs, ignore_files, ignore_ext, tree_only,
                          max_lines, max_bytes)
        else:
            if not tree_only:
                indent = prefix + ("│   " if idx < len(visible) - 1 else "    ")
                write_file_preview(p, fh, indent, max_lines, max_bytes, ignore_ext)

def gather_context(base: Path) -> str:
    lines = []
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    lines.append("# Contexto do Projeto")
    lines.append(f"- Data/Hora: {now}")
    lines.append(f"- SO: {platform.system()} {platform.release()} ({platform.version()})")
    lines.append(f"- Python: {platform.python_version()}")
    lines.append(f"- App: Logistics Bot (V2 Enterprise)")

    # pip freeze (top 30)
    try:
        out = subprocess.check_output([sys.executable, "-m", "pip", "freeze"], text=True, timeout=10)
        pkgs = [ln.strip() for ln in out.splitlines() if ln.strip()]
        lines.append("- Pip (top 30):")
        for ln in pkgs[:30]:
            lines.append(f"  - {ln}")
    except Exception:
        lines.append("- Pip: (indisponível)")

    # git branch/commit
    try:
        branch = subprocess.check_output(["git", "rev-parse", "--abbrev-ref", "HEAD"], text=True, timeout=5).strip()
        commit = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], text=True, timeout=5).strip()
        lines.append(f"- Git: branch `{branch}`, commit `{commit}`")
    except Exception:
        lines.append("- Git: (indisponível)")

    # settings.json (amostra redigida)
    settings = base / "config" / "settings.json"
    if settings.exists():
        try:
            txt, _ = safe_read_text(str(settings), 64 * 1024)
            preview = "\n".join(redact_line(ln) for ln in txt.splitlines()[:80])
            lines.append("\n## config/settings.json (amostra redigida)")
            lines.append("```json")
            lines.append(preview)
            lines.append("```")
        except Exception:
            pass

    return "\n".join(lines) + "\n"

def main():
    ap = argparse.ArgumentParser(description="Gera a árvore do projeto com amostra de conteúdo.")
    ap.add_argument("--root", default=".", help="Diretório raiz a inspecionar (default=.)")
    ap.add_argument("--out", default="docs", help="Pasta onde salvar os arquivos (default=docs)")
    ap.add_argument("--max-depth", type=int, default=None, help="Profundidade máxima da árvore (default: ilimitada)")
    ap.add_argument("--tree-only", action="store_true", help="Não ler conteúdo dos arquivos (só a árvore)")
    ap.add_argument("--max-lines", type=int, default=300, help="Máximo de linhas por arquivo (default=300)")
    ap.add_argument("--max-bytes", type=int, default=512*1024, help="Máximo de bytes lidos por arquivo (default=524288)")
    ap.add_argument("--ignore-dirs", default="", help="Pastas extras para ignorar, separadas por vírgula")
    ap.add_argument("--ignore-files", default="", help="Arquivos extras para ignorar, separados por vírgula")
    ap.add_argument("--ignore-ext", default="", help="Extensões extras para ignorar, separadas por vírgula (inclua o ponto)")
    ap.add_argument("--ai", action="store_true", help="Gera também um contexto_*.txt com ambiente e resumo")

    args = ap.parse_args()

    base = Path(args.root).resolve()
    out_dir = Path(args.out).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    ignore_dirs  = parse_set(args.ignore_dirs, DEFAULT_IGNORE_DIRS)
    ignore_files = parse_set(args.ignore_files, DEFAULT_IGNORE_FILES)
    ignore_ext   = parse_set(args.ignore_ext,   DEFAULT_IGNORE_EXT)

    ts = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    root_name = base.name

    # Arquivo de árvore
    out_tree = out_dir / f"estrutura_completa_{ts}.txt"
    with open(out_tree, "w", encoding="utf-8") as fh:
        fh.write(f"{root_name}/\n")
        list_tree(str(base), str(base), fh, prefix="", max_depth=args.max_depth, depth=1,
                  ignore_dirs=ignore_dirs, ignore_files=ignore_files, ignore_ext=ignore_ext,
                  tree_only=args.tree_only, max_lines=args.max_lines, max_bytes=args.max_bytes)

    print(f"Estrutura completa do projeto salva em '{out_tree}'")

    # Arquivo de contexto (modo IA)
    if args.ai:
        out_ctx = out_dir / f"contexto_{ts}.txt"
        with open(out_ctx, "w", encoding="utf-8") as fh:
            fh.write(gather_context(base))
        print(f"Contexto do projeto salvo em '{out_ctx}'")

if __name__ == "__main__":
    main()