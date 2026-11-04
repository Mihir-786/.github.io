"""Export public job leads to Career Ops; optionally import locally with approval.

This tool never connects to LinkedIn, sends messages, applies for jobs,
reads a resume, or uploads private data.
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import os
import re
import shutil
import tempfile
from pathlib import Path
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

ROOT = Path(__file__).resolve().parent
TRACKING_KEYS = {"trk", "trackingid", "refid", "lipi", "originalsubdomain"}


def normalized_url(value: str) -> str:
    """Keep meaningful ATS parameters; discard only common tracking parameters."""
    try:
        p = urlsplit(value.strip())
        if p.scheme.lower() not in {"http", "https"} or not p.netloc:
            return ""
        pairs = [(k, v) for k, v in parse_qsl(p.query, keep_blank_values=True)
                 if not k.lower().startswith("utm_") and k.lower() not in TRACKING_KEYS]
        return urlunsplit((p.scheme.lower(), p.netloc.lower(),
                           p.path.rstrip("/") or "/", urlencode(pairs), ""))
    except ValueError:
        return ""


def safe_field(value: str) -> str:
    return re.sub(r"\s+", " ", (value or "").replace("|", "/")).strip()[:110]


def export_candidates(csv_path: Path, output_path: Path, limit: int) -> int:
    with csv_path.open(newline="", encoding="utf-8-sig") as handle:
        rows = list(csv.DictReader(handle))
    candidates = []
    seen = set()
    for item in sorted(rows, key=lambda r: -float(r.get("score") or 0)):
        raw_url = (item.get("url") or "").strip()
        key = normalized_url(raw_url)
        if not key or key in seen:
            continue
        seen.add(key)
        company = safe_field(item.get("company") or "Unknown company")
        title = safe_field(item.get("title") or "Unknown role")
        location = safe_field(item.get("location") or "")
        candidates.append(f"- [ ] {raw_url} | {company} | {title} | {location}")
        if len(candidates) >= limit:
            break
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join([
        "# Career Ops candidate URLs (public job data only)",
        "",
        f"Exported: {stamp}. Selection: top {len(candidates)} keyword-ranked jobs.",
        "Scores are preliminary keyword matches, NOT resume-fit scores.",
        "Check the full JD, job availability, work authorization and location.",
        "This file contains no resume, contact details or outreach messages.",
        "",
        "## Pending",
        *candidates,
        "",
        "## Processed",
        "",
    ]), encoding="utf-8")
    print(f"Exported {len(candidates)} candidate URLs to {output_path}")
    return len(candidates)


def import_candidates(queue: Path, destination: Path, confirm: bool) -> int:
    """Append only unseen pending URLs to an existing *local* Career Ops inbox."""
    if not queue.is_file() or not destination.is_file():
        raise SystemExit("Queue and local Career Ops pipeline file must both exist.")
    old = destination.read_text(encoding="utf-8")
    match = re.search(r"(?m)^## Pending\s*$", old)
    if not match:
        raise SystemExit("Local pipeline has no '## Pending' heading; nothing changed.")
    queued = []
    for line in queue.read_text(encoding="utf-8").splitlines():
        if not line.startswith("- [ ] "):
            continue
        url = line[6:].split(" | ", 1)[0].strip()
        if normalized_url(url):
            queued.append(line)
    existing = {normalized_url(u) for u in
                re.findall(r"https?://[^\s|)<>\]]+", old)}
    additions = []
    for line in queued:
        url = line[6:].split(" | ", 1)[0].strip()
        key = normalized_url(url)
        if key not in existing:
            existing.add(key)
            additions.append(line)
    print(f"Local import preview: {len(additions)} new URLs "
          f"(of {len(queued)} exported). No applications or messages sent.")
    if not confirm:
        print("No files changed. Add --confirm to import after review.")
        return len(additions)
    if not additions:
        return 0
    following = re.search(r"(?m)^## ", old[match.end():])
    at = match.end() + following.start() if following else len(old)
    new_content = old[:at].rstrip("\n") + "\n" + "\n".join(additions) + \
                  "\n\n" + old[at:].lstrip("\n")
    backup = destination.with_name(destination.name + "." +
                dt.datetime.now().strftime("%Y%m%d-%H%M%S-%f") + ".bak")
    shutil.copy2(destination, backup)
    fd, temp_name = tempfile.mkstemp(dir=destination.parent, prefix=".career-ops-")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(new_content)
        os.replace(temp_name, destination)
    finally:
        if os.path.exists(temp_name):
            os.unlink(temp_name)
    print(f"Imported {len(additions)} new job URLs into {destination}")
    print(f"Backup saved locally to {backup}")
    return len(additions)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--csv", type=Path, default=ROOT / "latest.csv")
    parser.add_argument("--output", type=Path, default=ROOT / "career_ops_candidates.md")
    parser.add_argument("--limit", type=int, default=15)
    parser.add_argument("--queue", type=Path, help="Existing exported Markdown file")
    parser.add_argument("--import-to", type=Path, help="LOCAL Career Ops data/pipeline.md")
    parser.add_argument("--confirm", action="store_true",
                        help="Approve a local import (never messages/applications)")
    args = parser.parse_args()
    if args.import_to:
        import_candidates(args.queue or args.output, args.import_to, args.confirm)
        return
    if not 1 <= args.limit <= 100:
        parser.error("--limit must be between 1 and 100")
    export_candidates(args.csv, args.output, args.limit)


if __name__ == "__main__":
    main()
