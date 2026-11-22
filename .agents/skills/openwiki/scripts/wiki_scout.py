#!/usr/bin/env python3
# Copyright (c) 2026 akatzmann (https://github.com/akatzmann) | Apache-2.0 License
"""Permission-safe OpenWiki OKF v0.2 frontmatter, link-graph, and scout CLI.

Zero-dependency Python 3 standard-library utility that traverses readable
OpenWiki Markdown subtrees while safely skipping unreadable paths, parses OKF v0.2
provenance and optional epistemic metadata, detects temporal/source staleness,
and resolves 1-hop graph neighborhoods.
"""

import argparse
import errno
import json
import os
import re
import sqlite3
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import unquote

EXCLUDED_FILES = frozenset({"INSTRUCTIONS.md", "log.md"})
VALID_STATUSES = frozenset({"draft", "stable", "deprecated"})
IGNORED_ERRNOS = frozenset({errno.EACCES, errno.ENOENT, errno.EPERM})

_FENCE_RE = re.compile(r"^\s*(`{3,}|~{3,})")
_INLINE_CODE_RE = re.compile(r"`[^`\n]+`")
_HEADING_RE = re.compile(r"^#\s+(.+)$", re.MULTILINE)
_MD_LINK_RE = re.compile(r"(?<!!)\[[^\]]*\]\(([^)\s]+)\)")
_EPI_BADGE_RE = re.compile(r"^-\s*\*\*Epistemic State:\*\*\s*(.+)$")
_EPI_P_RE = re.compile(r"\bp\s*=\s*(\d+(?:\.\d+)?)")
_EPI_OBS_RE = re.compile(r"\bobs:\s*(\d+)")
_EPI_EXC_RE = re.compile(r"\bexceptions:\s*(\d+)")
_FTS_TOKEN_RE = re.compile(r"[^\W_]+", re.UNICODE)


def _is_ignorable_oserror(exc: OSError) -> bool:
    return isinstance(exc, (PermissionError, FileNotFoundError)) or exc.errno in IGNORED_ERRNOS


def _resolve_project_root(abs_wiki_root: Path) -> Tuple[Path, bool]:
    """Determine (project_root, has_git) for resolving repo-relative paths and git history."""
    if (abs_wiki_root / ".git").exists() and abs_wiki_root.name != "openwiki":
        return abs_wiki_root, True
    parent = abs_wiki_root.parent
    if (parent / ".git").exists():
        return parent, True
    if abs_wiki_root.name == "openwiki":
        # Check upward for a real repo root, stopping before .tmp isolation folders
        cur = parent
        while cur != cur.parent and cur.name != ".tmp":
            if (cur / ".git").exists():
                return cur, True
            cur = cur.parent
        return parent, False
    cur = abs_wiki_root
    while cur != cur.parent and cur.name != ".tmp":
        if (cur / ".git").exists():
            return cur, True
        cur = cur.parent
    return abs_wiki_root, False


def to_id(abs_wiki_root: Path, abs_file: Path) -> str:
    """Compute OpenWiki node ID (root-relative POSIX path without .md extension)."""
    rel = abs_file.relative_to(abs_wiki_root).as_posix()
    return rel[:-3] if rel.endswith(".md") else rel


def collect_markdown_files(abs_wiki_root: Path) -> List[Path]:
    """Recursively collect readable .md files under abs_wiki_root."""
    collected: List[Path] = []

    def _walk(current_dir: Path) -> None:
        try:
            with os.scandir(current_dir) as it:
                entries = sorted(list(it), key=lambda e: e.name)
        except OSError as exc:
            if _is_ignorable_oserror(exc):
                return
            raise

        for entry in entries:
            if entry.name.startswith("."):
                continue
            try:
                candidate = Path(entry.path).resolve()
                if candidate != abs_wiki_root and not candidate.is_relative_to(abs_wiki_root):
                    continue
                if entry.is_dir(follow_symlinks=False):
                    _walk(candidate)
                elif (
                    entry.is_file(follow_symlinks=False)
                    and entry.name.endswith(".md")
                    and entry.name not in EXCLUDED_FILES
                ):
                    collected.append(candidate)
            except OSError as exc:
                if _is_ignorable_oserror(exc):
                    continue
                raise

    _walk(abs_wiki_root)
    collected.sort()
    return collected


def _strip_yaml_comment(line: str) -> str:
    in_single = False
    in_double = False
    escaped = False
    for idx, ch in enumerate(line):
        if escaped:
            escaped = False
            continue
        if ch == "\\" and in_double:
            escaped = True
            continue
        if ch == "'" and not in_double:
            in_single = not in_single
        elif ch == '"' and not in_single:
            in_double = not in_double
        elif ch == "#" and not in_single and not in_double:
            if idx == 0 or line[idx - 1].isspace():
                return line[:idx].rstrip()
    return line.rstrip()


def _split_top_level(text: str, sep: str = ",") -> List[str]:
    parts: List[str] = []
    buf: List[str] = []
    in_single = False
    in_double = False
    escaped = False
    depth = 0
    for ch in text:
        if escaped:
            buf.append(ch)
            escaped = False
            continue
        if ch == "\\" and in_double:
            buf.append(ch)
            escaped = True
            continue
        if ch == "'" and not in_double:
            in_single = not in_single
            buf.append(ch)
        elif ch == '"' and not in_single:
            in_double = not in_double
            buf.append(ch)
        elif not in_single and not in_double:
            if ch in "[{":
                depth += 1
                buf.append(ch)
            elif ch in "]}" and depth > 0:
                depth -= 1
                buf.append(ch)
            elif ch == sep and depth == 0:
                parts.append("".join(buf).strip())
                buf = []
            else:
                buf.append(ch)
        else:
            buf.append(ch)
    tail = "".join(buf).strip()
    if tail or parts:
        parts.append(tail)
    return [p for p in parts if p != ""]


def _unquote_scalar(token: str) -> Any:
    s = token.strip()
    if len(s) >= 2 and s[0] == '"' and s[-1] == '"':
        inner = s[1:-1]
        return inner.replace('\\"', '"').replace("\\\\", "\\")
    if len(s) >= 2 and s[0] == "'" and s[-1] == "'":
        return s[1:-1].replace("''", "'")
    low = s.lower()
    if low == "true":
        return True
    if low == "false":
        return False
    if low in ("null", "~", ""):
        return None
    if re.fullmatch(r"-?\d+", s):
        try:
            return int(s)
        except ValueError:
            return s
    if re.fullmatch(r"-?\d+\.\d+", s):
        try:
            return float(s)
        except ValueError:
            return s
    return s


def _partition_yaml_kv(text: str) -> Optional[Tuple[str, str]]:
    """Split 'key: value' on the first unquoted colon followed by whitespace or EOL."""
    in_single = False
    in_double = False
    escaped = False
    for idx, ch in enumerate(text):
        if escaped:
            escaped = False
            continue
        if ch == "\\" and in_double:
            escaped = True
            continue
        if ch == "'" and not in_double:
            in_single = not in_single
        elif ch == '"' and not in_single:
            in_double = not in_double
        elif ch == ":" and not in_single and not in_double:
            if idx + 1 == len(text) or text[idx + 1].isspace():
                raw_key = text[:idx].strip()
                if not raw_key:
                    return None
                key = str(_unquote_scalar(raw_key))
                val = text[idx + 1 :].strip()
                return key, val
    return None


def _parse_inline_value(raw: str) -> Any:
    s = raw.strip()
    if not s:
        return None
    if s.startswith("[") and s.endswith("]"):
        inner = s[1:-1].strip()
        if not inner:
            return []
        return [_parse_inline_value(item) for item in _split_top_level(inner, ",")]
    if s.startswith("{") and s.endswith("}"):
        inner = s[1:-1].strip()
        if not inner:
            return {}
        out: Dict[str, Any] = {}
        for item in _split_top_level(inner, ","):
            kv = _partition_yaml_kv(item)
            if kv is not None:
                out[kv[0]] = _parse_inline_value(kv[1])
        return out
    return _unquote_scalar(s)


def parse_frontmatter(raw_content: str) -> Tuple[Dict[str, Any], str]:
    """Parse OKF v0.2 YAML frontmatter and return (metadata_dict, markdown_body)."""
    if not raw_content.startswith("---"):
        return {}, raw_content
    lines = raw_content.splitlines(keepends=True)
    if not lines or lines[0].strip() != "---":
        return {}, raw_content

    end_idx: Optional[int] = None
    for idx in range(1, len(lines)):
        if lines[idx].strip() == "---":
            end_idx = idx
            break
    if end_idx is None:
        return {}, raw_content

    fm_lines = lines[1:end_idx]
    body = "".join(lines[end_idx + 1 :])
    meta: Dict[str, Any] = {}

    cleaned: List[Tuple[int, str]] = []
    for raw_line in fm_lines:
        stripped_comment = _strip_yaml_comment(raw_line.rstrip("\r\n"))
        if not stripped_comment.strip():
            continue
        indent = len(stripped_comment) - len(stripped_comment.lstrip(" "))
        cleaned.append((indent, stripped_comment.lstrip(" ")))

    i = 0
    n = len(cleaned)
    while i < n:
        indent, content = cleaned[i]
        kv = _partition_yaml_kv(content)
        if kv is None:
            i += 1
            continue
        key, inline_val = kv
        i += 1

        if inline_val in (">", ">-", "|", "|-"):
            fold_parts: List[str] = []
            while i < n and cleaned[i][0] > indent:
                fold_parts.append(cleaned[i][1])
                i += 1
            joiner = "\n" if inline_val.startswith("|") else " "
            meta[key] = joiner.join(fold_parts).strip()
            continue

        if inline_val:
            meta[key] = _parse_inline_value(inline_val)
            continue

        # Collect indented block children for this key
        children: List[Tuple[int, str]] = []
        while i < n and cleaned[i][0] > indent:
            children.append(cleaned[i])
            i += 1

        if not children:
            meta[key] = None
            continue

        if children[0][1] == "-" or children[0][1].startswith("- "):
            seq: List[Any] = []
            j = 0
            m = len(children)
            while j < m:
                c_indent, c_text = children[j]
                if not (c_text == "-" or c_text.startswith("- ")):
                    j += 1
                    continue
                rem = c_text[1:].strip()
                j += 1
                if not rem:
                    item_map: Dict[str, Any] = {}
                    while j < m and children[j][0] > c_indent:
                        sub_kv = _partition_yaml_kv(children[j][1])
                        if sub_kv is not None:
                            item_map[sub_kv[0]] = _parse_inline_value(sub_kv[1])
                        j += 1
                    seq.append(item_map)
                elif rem.startswith("{") and rem.endswith("}"):
                    seq.append(_parse_inline_value(rem))
                else:
                    rem_kv = _partition_yaml_kv(rem)
                    if rem_kv is not None:
                        item_map = {rem_kv[0]: _parse_inline_value(rem_kv[1])}
                        while j < m and children[j][0] > c_indent:
                            sub_kv = _partition_yaml_kv(children[j][1])
                            if sub_kv is not None:
                                item_map[sub_kv[0]] = _parse_inline_value(sub_kv[1])
                            j += 1
                        seq.append(item_map)
                    else:
                        seq.append(_parse_inline_value(rem))
            meta[key] = seq
        else:
            mapping: Dict[str, Any] = {}
            for _, c_text in children:
                sub_kv = _partition_yaml_kv(c_text)
                if sub_kv is not None:
                    mapping[sub_kv[0]] = _parse_inline_value(sub_kv[1])
            meta[key] = mapping

    return meta, body


def _parse_iso_utc(raw_ts: Any) -> Optional[datetime]:
    if not isinstance(raw_ts, str):
        return None
    val = raw_ts.strip()
    if not val:
        return None
    if val.endswith("Z") or val.endswith("z"):
        val = val[:-1] + "+00:00"
    try:
        dt = datetime.fromisoformat(val)
    except ValueError:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def _normalize_verified(raw_verified: Any) -> Optional[Dict[str, str]]:
    """Extract {by, at} from mapping or list of mappings, selecting latest UTC 'at'."""
    candidates: List[Dict[str, str]] = []
    items = raw_verified if isinstance(raw_verified, list) else [raw_verified]
    for entry in items:
        if not isinstance(entry, dict):
            continue
        by_val = entry.get("by")
        at_val = entry.get("at")
        if isinstance(at_val, str) and at_val.strip():
            candidates.append(
                {
                    "by": str(by_val).strip() if by_val is not None else "",
                    "at": at_val.strip(),
                }
            )
    if not candidates:
        return None

    best = candidates[0]
    best_dt = _parse_iso_utc(best["at"])
    for cand in candidates[1:]:
        cand_dt = _parse_iso_utc(cand["at"])
        if cand_dt is not None and (best_dt is None or cand_dt >= best_dt):
            best = cand
            best_dt = cand_dt
    return best


def _normalize_sources(raw_sources: Any) -> List[Dict[str, str]]:
    if not isinstance(raw_sources, list):
        return []
    out: List[Dict[str, str]] = []
    for item in raw_sources:
        if isinstance(item, dict):
            res = item.get("resource")
            if isinstance(res, str) and res.strip():
                out.append({"resource": res.strip()})
        elif isinstance(item, str) and item.strip():
            out.append({"resource": item.strip()})
    return out


def _strip_fenced_blocks(body: str) -> str:
    kept: List[str] = []
    active_fence_char = ""
    active_fence_len = 0
    for line in body.splitlines(keepends=True):
        m = _FENCE_RE.match(line)
        if m:
            marker = m.group(1)
            if not active_fence_char:
                active_fence_char = marker[0]
                active_fence_len = len(marker)
                continue
            if marker[0] == active_fence_char and len(marker) >= active_fence_len:
                active_fence_char = ""
                active_fence_len = 0
                continue
        if not active_fence_char:
            kept.append(line)
    return "".join(kept)


def _extract_epistemic(raw_epi: Any, clean_body: str) -> Optional[Dict[str, Any]]:
    fm_part: Dict[str, Any] = {}
    if isinstance(raw_epi, dict):
        if "p" in raw_epi and isinstance(raw_epi["p"], (int, float)) and not isinstance(raw_epi["p"], bool):
            fm_part["p"] = float(raw_epi["p"])
        if "obs" in raw_epi and isinstance(raw_epi["obs"], int) and not isinstance(raw_epi["obs"], bool):
            fm_part["obs"] = int(raw_epi["obs"])
        if (
            "exceptions" in raw_epi
            and isinstance(raw_epi["exceptions"], int)
            and not isinstance(raw_epi["exceptions"], bool)
        ):
            fm_part["exceptions"] = int(raw_epi["exceptions"])

    p_vals: List[float] = []
    total_obs = 0
    total_exc = 0
    body_count = 0
    for raw_line in clean_body.splitlines():
        m = _EPI_BADGE_RE.match(raw_line.strip())
        if not m:
            continue
        body_count += 1
        badge = m.group(1)
        mp = _EPI_P_RE.search(badge)
        if mp:
            p_vals.append(float(mp.group(1)))
        mo = _EPI_OBS_RE.search(badge)
        if mo:
            total_obs += int(mo.group(1))
        me = _EPI_EXC_RE.search(badge)
        if me:
            total_exc += int(me.group(1))

    if not fm_part and body_count == 0:
        return None

    result = dict(fm_part)
    if body_count > 0:
        result["body_count"] = body_count
        result["total_exceptions"] = total_exc
        result["total_obs"] = total_obs
        if p_vals:
            min_p = min(p_vals)
            max_p = max(p_vals)
            result["min_p"] = min_p
            result["max_p"] = max_p
            result["summary"] = (
                f"{body_count} hypotheses (p={min_p:.2f}..{max_p:.2f}, exceptions={total_exc})"
            )
        else:
            result["summary"] = f"{body_count} hypotheses (exceptions={total_exc})"
    return result


def _extract_raw_md_links(clean_body: str) -> List[str]:
    prose = _INLINE_CODE_RE.sub("", clean_body)
    links: List[str] = []
    for match in _MD_LINK_RE.finditer(prose):
        raw_target = match.group(1).strip()
        target = raw_target.split("#", 1)[0].split("?", 1)[0].strip()
        if not target or ":" in target or not target.endswith(".md"):
            continue
        links.append(unquote(target))
    return links


def _git_last_commit_utc(
    project_root: Path, rel_resource: str, cache: Dict[str, Optional[datetime]]
) -> Optional[datetime]:
    if rel_resource in cache:
        return cache[rel_resource]
    env = {
        **os.environ,
        "GIT_CEILING_DIRECTORIES": str(project_root.parent),
    }
    try:
        proc = subprocess.run(
            ["git", "-C", str(project_root), "log", "-1", "--format=%cI", "--", rel_resource],
            capture_output=True,
            text=True,
            env=env,
            timeout=5,
        )
    except (OSError, subprocess.SubprocessError):
        cache[rel_resource] = None
        return None

    if proc.returncode != 0:
        cache[rel_resource] = None
        return None
    iso_str = proc.stdout.strip()
    dt = _parse_iso_utc(iso_str) if iso_str else None
    cache[rel_resource] = dt
    return dt


def _evaluate_staleness(
    status: str,
    superseded_by: Optional[str],
    stale_after: Optional[str],
    verified: Optional[Dict[str, str]],
    sources: List[Dict[str, str]],
    page_mtime: float,
    project_root: Path,
    has_git: bool,
    now_utc: datetime,
    git_cache: Dict[str, Optional[datetime]],
) -> Tuple[bool, Optional[str]]:
    reasons: List[str] = []

    if status == "deprecated":
        if superseded_by:
            reasons.append(f"deprecated (superseded by {superseded_by})")
        else:
            reasons.append("deprecated")

    if stale_after:
        sa_dt = _parse_iso_utc(stale_after)
        if sa_dt is not None and now_utc > sa_dt:
            reasons.append(f"stale_after expired ({stale_after})")

    verified_dt = _parse_iso_utc(verified["at"]) if verified else None
    if verified_dt is not None and sources:
        verified_epoch = verified_dt.timestamp()
        for src in sources:
            raw_res = src.get("resource", "")
            if not raw_res or "://" in raw_res or raw_res.startswith("mailto:"):
                continue
            try:
                res_abs = (project_root / raw_res).resolve()
                if not res_abs.is_relative_to(project_root) or not res_abs.is_file():
                    continue
                rel_res = res_abs.relative_to(project_root).as_posix()
                res_mtime = res_abs.stat().st_mtime
            except OSError as exc:
                if _is_ignorable_oserror(exc):
                    continue
                raise

            git_dt = _git_last_commit_utc(project_root, rel_res, git_cache) if has_git else None
            if git_dt is not None:
                if git_dt > verified_dt:
                    reasons.append(f"source modified after verified.at: {rel_res}")
            elif res_mtime > verified_epoch and res_mtime > page_mtime + 60.0:
                reasons.append(f"source modified after verified.at: {rel_res}")

    if not reasons:
        return False, None
    return True, "; ".join(reasons)


def _section_title(abs_file: Path, abs_wiki_root: Path) -> str:
    parent = abs_file.parent.resolve()
    name = "Home" if parent == abs_wiki_root else parent.name
    return name[:1].upper() + name[1:] if name else "Home"


def _load_nodes(
    wiki_root: Path | str, now: Optional[datetime] = None
) -> Tuple[Path, Path, List[Dict[str, Any]]]:
    abs_wiki_root = Path(wiki_root).resolve()
    project_root, has_git = _resolve_project_root(abs_wiki_root)
    now_utc = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
    git_cache: Dict[str, Optional[datetime]] = {}

    if not abs_wiki_root.exists():
        return abs_wiki_root, project_root, []

    md_files = collect_markdown_files(abs_wiki_root)
    nodes: List[Dict[str, Any]] = []

    for abs_file in md_files:
        try:
            raw_text = abs_file.read_text(encoding="utf-8", errors="replace")
            page_mtime = abs_file.stat().st_mtime
        except OSError as exc:
            if _is_ignorable_oserror(exc):
                continue
            raise

        meta, body = parse_frontmatter(raw_text)
        body_start_line = len(raw_text[: len(raw_text) - len(body)].splitlines()) + 1
        clean_body = _strip_fenced_blocks(body)
        is_index = abs_file.name == "index.md"
        node_id = to_id(abs_wiki_root, abs_file)
        rel_path = (
            abs_file.relative_to(project_root).as_posix()
            if abs_file.is_relative_to(project_root)
            else abs_file.relative_to(abs_wiki_root).as_posix()
        )

        raw_type = meta.get("type")
        page_type = (
            raw_type.strip()
            if isinstance(raw_type, str) and raw_type.strip()
            else ("Section" if is_index else "Reference")
        )

        raw_title = meta.get("title")
        if isinstance(raw_title, str) and raw_title.strip():
            title = raw_title.strip()
        elif is_index:
            title = _section_title(abs_file, abs_wiki_root)
        else:
            m_head = _HEADING_RE.search(clean_body)
            title = m_head.group(1).strip() if m_head else abs_file.stem

        raw_desc = meta.get("description")
        description = raw_desc.strip() if isinstance(raw_desc, str) else ""

        raw_tags = meta.get("tags")
        tags = (
            [str(t).strip() for t in raw_tags if t is not None and str(t).strip()]
            if isinstance(raw_tags, list)
            else []
        )

        raw_status = meta.get("status")
        status_norm = raw_status.strip().lower() if isinstance(raw_status, str) else "stable"
        status = status_norm if status_norm in VALID_STATUSES else "stable"

        verified = _normalize_verified(meta.get("verified"))
        raw_stale_after = meta.get("stale_after")
        stale_after = (
            raw_stale_after.strip()
            if isinstance(raw_stale_after, str) and raw_stale_after.strip()
            else None
        )
        sources = _normalize_sources(meta.get("sources"))

        raw_applies = meta.get("applies_to")
        applies_to: Optional[Any] = None
        if isinstance(raw_applies, str) and raw_applies.strip():
            applies_to = raw_applies.strip()
        elif isinstance(raw_applies, list):
            applies_to = [str(x).strip() for x in raw_applies if x is not None and str(x).strip()]

        raw_sup = meta.get("superseded_by")
        superseded_by = raw_sup.strip() if isinstance(raw_sup, str) and raw_sup.strip() else None

        epistemic = _extract_epistemic(meta.get("epistemic"), clean_body)
        stale, stale_reason = _evaluate_staleness(
            status=status,
            superseded_by=superseded_by,
            stale_after=stale_after,
            verified=verified,
            sources=sources,
            page_mtime=page_mtime,
            project_root=project_root,
            has_git=has_git,
            now_utc=now_utc,
            git_cache=git_cache,
        )

        nodes.append(
            {
                "id": node_id,
                "path": rel_path,
                "type": page_type,
                "title": title,
                "description": description,
                "tags": tags,
                "status": status,
                "verified": verified,
                "verified_by": verified["by"] if verified else None,
                "verified_at": verified["at"] if verified else None,
                "stale_after": stale_after,
                "sources": sources,
                "applies_to": applies_to,
                "superseded_by": superseded_by,
                "epistemic": epistemic,
                "stale": stale,
                "stale_reason": stale_reason,
                "_abs_file": abs_file,
                "_body": body,
                "_body_start_line": body_start_line,
                "_raw_links": _extract_raw_md_links(clean_body),
                "_out_ids": [],
                "_in_ids": [],
            }
        )

    nodes_by_id = {n["id"]: n for n in nodes}
    for node in nodes:
        seen_targets = set()
        file_dir = node["_abs_file"].parent
        for raw_link in node["_raw_links"]:
            try:
                target_abs = (file_dir / raw_link).resolve()
            except OSError:
                continue
            if not target_abs.is_relative_to(abs_wiki_root):
                continue
            target_id = to_id(abs_wiki_root, target_abs)
            if target_id == node["id"] or target_id in seen_targets or target_id not in nodes_by_id:
                continue
            seen_targets.add(target_id)
            node["_out_ids"].append(target_id)
            nodes_by_id[target_id]["_in_ids"].append(node["id"])

    for node in nodes:
        out_paths = [nodes_by_id[tid]["path"] for tid in node["_out_ids"]]
        node["out_links"] = out_paths
        node["out_links_count"] = len(out_paths)

    return abs_wiki_root, project_root, nodes


def _public_page_dict(node: Dict[str, Any]) -> Dict[str, Any]:
    return {k: v for k, v in node.items() if not k.startswith("_")}


def _neighbor_summary(node: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "id": node["id"],
        "path": node["path"],
        "title": node["title"],
        "type": node["type"],
        "status": node["status"],
        "stale": node["stale"],
    }


def _matches_section(node_id: str, section: Optional[str], root_name: str = "") -> bool:
    if not section:
        return True
    norm = section.strip().strip("/").removesuffix(".md")
    if root_name and norm.startswith(root_name + "/"):
        norm = norm[len(root_name) + 1 :]
    if not norm:
        return True
    return node_id == norm or node_id.startswith(norm + "/")


def build_catalog(
    wiki_root: Path | str,
    section: Optional[str] = None,
    stale_only: bool = False,
    now: Optional[datetime] = None,
) -> Dict[str, Any]:
    """Build permission-safe OpenWiki page catalog with frontmatter, epistemic, and staleness flags."""
    abs_wiki_root, _, nodes = _load_nodes(wiki_root, now=now)
    filtered = [
        _public_page_dict(n)
        for n in nodes
        if _matches_section(n["id"], section, abs_wiki_root.name) and (not stale_only or n["stale"])
    ]
    return {
        "root": abs_wiki_root.name,
        "total": len(filtered),
        "stale_count": sum(1 for p in filtered if p["stale"]),
        "pages": filtered,
    }


def _resolve_target_node(
    target: str, abs_wiki_root: Path, project_root: Path, nodes: List[Dict[str, Any]]
) -> Optional[Dict[str, Any]]:
    by_id = {n["id"]: n for n in nodes}
    by_path = {n["path"]: n for n in nodes}

    clean = target.strip()
    if clean in by_id:
        return by_id[clean]
    if clean in by_path:
        return by_path[clean]
    if clean.endswith(".md") and clean[:-3] in by_id:
        return by_id[clean[:-3]]

    for base in (Path.cwd(), project_root, abs_wiki_root):
        try:
            cand = (base / clean).resolve()
        except OSError:
            continue
        if cand.is_relative_to(abs_wiki_root):
            cid = to_id(abs_wiki_root, cand)
            if cid in by_id:
                return by_id[cid]
    return None


def get_neighbors(
    wiki_root: Path | str, target: str, now: Optional[datetime] = None
) -> Dict[str, Any]:
    """Return 1-hop outgoing links and incoming backlinks for an accessible page."""
    abs_wiki_root, project_root, nodes = _load_nodes(wiki_root, now=now)
    node = _resolve_target_node(target, abs_wiki_root, project_root, nodes)
    if node is None:
        raise LookupError(f"Page not found or inaccessible: {target}")

    by_id = {n["id"]: n for n in nodes}
    outgoing = [_neighbor_summary(by_id[tid]) for tid in node["_out_ids"] if tid in by_id]
    incoming = [_neighbor_summary(by_id[sid]) for sid in sorted(node["_in_ids"]) if sid in by_id]
    return {
        "target": {
            **_neighbor_summary(node),
            "stale_reason": node["stale_reason"],
        },
        "outgoing": outgoing,
        "incoming": incoming,
    }


def sanitize_fts_tokens(query: str) -> List[str]:
    """Extract safe alphanumeric Unicode tokens from arbitrary natural-language/code queries."""
    seen: set[str] = set()
    tokens: List[str] = []
    for raw_tok in _FTS_TOKEN_RE.findall(query or ""):
        low = raw_tok.lower()
        if low not in seen:
            seen.add(low)
            tokens.append(raw_tok)
    return tokens


def search_pages(
    wiki_root: Path | str,
    query: str,
    section: Optional[str] = None,
    limit: int = 8,
    now: Optional[datetime] = None,
) -> Dict[str, Any]:
    """Run ephemeral :memory: SQLite FTS5 weighted BM25 search over readable pages."""
    abs_wiki_root, _, nodes = _load_nodes(wiki_root, now=now)
    tokens = sanitize_fts_tokens(query)
    if not tokens or limit <= 0:
        return {
            "root": abs_wiki_root.name,
            "query": query,
            "tokens": tokens,
            "match_mode": "NONE",
            "total": 0,
            "results": [],
        }

    candidates = [n for n in nodes if _matches_section(n["id"], section, abs_wiki_root.name)]
    if not candidates:
        return {
            "root": abs_wiki_root.name,
            "query": query,
            "tokens": tokens,
            "match_mode": "NONE",
            "total": 0,
            "results": [],
        }

    by_path = {n["path"]: n for n in candidates}
    quoted = [f'"{tok.replace(chr(34), chr(34) * 2)}"' for tok in tokens]
    and_expr = " AND ".join(quoted)
    or_expr = " OR ".join(quoted)

    sql_query = (
        "SELECT "
        "path, "
        "bm25(pages_fts, 0.0, 10.0, 5.0, 5.0, 1.0) AS raw_bm25, "
        "snippet(pages_fts, 4, '[', ']', '...', 24) AS snip, "
        "highlight(pages_fts, 4, char(1), char(2)) AS hl_body "
        "FROM pages_fts "
        "WHERE pages_fts MATCH ? "
        "ORDER BY raw_bm25 ASC, rowid ASC "
        "LIMIT ?"
    )

    conn = sqlite3.connect(":memory:")
    try:
        conn.execute(
            "CREATE VIRTUAL TABLE pages_fts USING fts5("
            "path UNINDEXED, title, tags, description, body, tokenize='porter unicode61'"
            ")"
        )
        conn.executemany(
            "INSERT INTO pages_fts (path, title, tags, description, body) VALUES (?, ?, ?, ?, ?)",
            [
                (
                    n["path"],
                    n["title"],
                    " ".join(n["tags"]),
                    n["description"],
                    n["_body"],
                )
                for n in candidates
            ],
        )
        rows = conn.execute(sql_query, (and_expr, int(limit))).fetchall()
        match_mode = "AND" if rows else "NONE"
        if not rows and len(quoted) > 1:
            rows = conn.execute(sql_query, (or_expr, int(limit))).fetchall()
            if rows:
                match_mode = "OR"
    finally:
        conn.close()

    results: List[Dict[str, Any]] = []
    for row_path, raw_bm25, raw_snip, hl_body in rows:
        node = by_path.get(row_path)
        if node is None:
            continue
        hl_str = hl_body or ""
        body_hit = "\x01" in hl_str
        body_start = node["_body_start_line"]
        match_lines = (
            [body_start + idx for idx, ln in enumerate(hl_str.splitlines()) if "\x01" in ln]
            if body_hit
            else []
        )
        clean_snip = " ".join((raw_snip or "").split())
        if body_hit and clean_snip:
            snippet_out = clean_snip
        elif node["description"]:
            snippet_out = node["description"]
        else:
            snippet_out = clean_snip

        score = round(max(0.0, -float(raw_bm25)), 10)
        results.append(
            {
                "score": score,
                "id": node["id"],
                "path": node["path"],
                "type": node["type"],
                "title": node["title"],
                "description": node["description"],
                "tags": node["tags"],
                "status": node["status"],
                "verified_at": node["verified_at"],
                "stale": node["stale"],
                "stale_reason": node["stale_reason"],
                "applies_to": node["applies_to"],
                "epistemic": node["epistemic"],
                "out_links": node["out_links"],
                "out_links_count": node["out_links_count"],
                "match_lines": match_lines,
                "snippet": snippet_out,
            }
        )

    return {
        "root": abs_wiki_root.name,
        "query": query,
        "tokens": tokens,
        "match_mode": match_mode,
        "total": len(results),
        "results": results,
    }


def _format_overview_text(catalog: Dict[str, Any]) -> str:
    lines = [
        f"OpenWiki Overview ({catalog['root']}): {catalog['total']} pages "
        f"({catalog['stale_count']} stale)"
    ]
    for p in catalog["pages"]:
        flag = "STALE" if p["stale"] else p["status"]
        epi_str = ""
        epi = p.get("epistemic")
        if isinstance(epi, dict):
            if "p" in epi:
                epi_str = f" [p={epi['p']:.2f}]"
            elif "summary" in epi:
                epi_str = f" [{epi['summary']}]"
        ver_str = f" verified={p['verified_at']}" if p.get("verified_at") else ""
        reason_str = f" -> {p['stale_reason']}" if p.get("stale_reason") else ""
        lines.append(
            f"- [{flag}] {p['path']} ({p['type']}): {p['title']}"
            f"{ver_str}{epi_str} (links={p['out_links_count']}){reason_str}"
        )
    return "\n".join(lines)


def _format_neighbors_text(data: Dict[str, Any]) -> str:
    tgt = data["target"]
    flag = "STALE" if tgt["stale"] else tgt["status"]
    lines = [f"Target: [{flag}] {tgt['path']} ({tgt['type']}) — {tgt['title']}"]
    lines.append(f"Outgoing ({len(data['outgoing'])}):")
    if data["outgoing"]:
        for n in data["outgoing"]:
            n_flag = "STALE" if n["stale"] else n["status"]
            lines.append(f"  -> [{n_flag}] {n['path']} ({n['type']}): {n['title']}")
    else:
        lines.append("  (none)")
    lines.append(f"Incoming ({len(data['incoming'])}):")
    if data["incoming"]:
        for n in data["incoming"]:
            n_flag = "STALE" if n["stale"] else n["status"]
            lines.append(f"  <- [{n_flag}] {n['path']} ({n['type']}): {n['title']}")
    else:
        lines.append("  (none)")
    return "\n".join(lines)


def _format_search_text(data: Dict[str, Any]) -> str:
    lines = [
        f"OpenWiki Search ({data['root']}): query={data['query']!r} "
        f"mode={data['match_mode']} hits={data['total']}"
    ]
    for idx, r in enumerate(data["results"], start=1):
        flag = "STALE" if r["stale"] else r["status"]
        epi_str = ""
        epi = r.get("epistemic")
        if isinstance(epi, dict):
            if "p" in epi:
                epi_str = f" [p={epi['p']:.2f}]"
            elif "summary" in epi:
                epi_str = f" [{epi['summary']}]"
        out_cnt = r.get("out_links_count")
        if out_cnt is None:
            out_cnt = len(r.get("out_links") or [])
        links_str = f" links={out_cnt}" if out_cnt else ""
        m_lines = r.get("match_lines") or []
        if len(m_lines) > 8:
            head = ", ".join(str(n) for n in m_lines[:8])
            lines_str = f" lines=[{head}, +{len(m_lines) - 8} more]"
        elif m_lines:
            lines_str = f" lines={m_lines}"
        else:
            lines_str = ""
        reason_str = f" ({r['stale_reason']})" if r.get("stale_reason") else ""
        lines.append(
            f"{idx}. [{flag}]{reason_str} {r['path']} ({r['type']}) — {r['title']} "
            f"[score={r['score']:.4g}]{epi_str}{links_str}{lines_str}"
        )
        if r.get("snippet"):
            lines.append(f"   {r['snippet']}")
    return "\n".join(lines)


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Permission-safe OpenWiki OKF v0.2 frontmatter, link-graph, and scout CLI."
    )
    parser.add_argument("--root", default="openwiki", help="OpenWiki root directory (default: openwiki)")
    subparsers = parser.add_subparsers(dest="command", required=True)

    ov = subparsers.add_parser("overview", help="Catalog accessible OpenWiki pages and staleness")
    ov.add_argument("--root", default=argparse.SUPPRESS, help="OpenWiki root directory")
    ov.add_argument("--section", default=None, help="Filter to a subdirectory section (e.g. caveats)")
    ov.add_argument("--stale-only", action="store_true", help="Only emit stale or deprecated pages")
    ov.add_argument("--json", action="store_true", help="Emit structured JSON output")

    sr = subparsers.add_parser("search", help="Weighted BM25 search via ephemeral :memory: SQLite FTS5")
    sr.add_argument("query", nargs="+", help="Natural-language or keyword search query")
    sr.add_argument("--root", default=argparse.SUPPRESS, help="OpenWiki root directory")
    sr.add_argument("--section", default=None, help="Filter to a subdirectory section (e.g. caveats)")
    sr.add_argument("--limit", type=int, default=8, help="Maximum ranked results to return (default: 8)")
    sr.add_argument("--json", action="store_true", help="Emit structured JSON output")

    nb = subparsers.add_parser("neighbors", help="Inspect 1-hop outgoing links and incoming backlinks")
    nb.add_argument("target", help="Target page path or OpenWiki node ID")
    nb.add_argument("--root", default=argparse.SUPPRESS, help="OpenWiki root directory")
    nb.add_argument("--json", action="store_true", help="Emit structured JSON output")

    return parser


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_arg_parser()
    args = parser.parse_args(argv)

    if args.command == "overview":
        catalog = build_catalog(
            wiki_root=args.root,
            section=args.section,
            stale_only=args.stale_only,
        )
        if args.json:
            print(json.dumps(catalog, indent=2))
        else:
            print(_format_overview_text(catalog))
        return 0

    if args.command == "search":
        query_str = " ".join(args.query)
        data = search_pages(
            wiki_root=args.root,
            query=query_str,
            section=args.section,
            limit=args.limit,
        )
        if args.json:
            print(json.dumps(data, indent=2))
        else:
            print(_format_search_text(data))
        return 0

    if args.command == "neighbors":
        try:
            data = get_neighbors(wiki_root=args.root, target=args.target)
        except LookupError as exc:
            print(str(exc), file=sys.stderr)
            return 1
        if args.json:
            print(json.dumps(data, indent=2))
        else:
            print(_format_neighbors_text(data))
        return 0

    return 1


if __name__ == "__main__":
    sys.exit(main())
