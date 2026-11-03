"""Review and optionally queue Job Finder listings in locally running Resume Matcher.

Default behavior is read-only. Requires --confirm for any queued AI work.
Never sends your resume or personal data to GitHub.
"""
from __future__ import annotations
import argparse
import json
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path


def load_jobs(filename):
    payload = json.loads(Path(filename).read_text(encoding="utf-8"))
    if payload.get("format") != "marketing-job-finder/v1":
        raise ValueError("Unexpected job export format")
    return payload["jobs"]


def request_json(method, url, payload=None):
    body = json.dumps(payload).encode("utf-8") if payload is not None else None
    headers = {"Content-Type": "application/json"} if body is not None else {}
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    with urllib.request.urlopen(req, timeout=20) as response:
        return json.load(response)


def pick_master(api, explicit_id):
    if explicit_id:
        return explicit_id
    result = request_json("GET", api + "/resumes/list?include_master=true")
    masters = [r for r in result.get("data", []) if r.get("is_master") and r.get("processing_status") == "ready"]
    if not masters:
        raise RuntimeError("No ready master resume found. Upload one in Resume Matcher first.")
    chosen = next((m for m in masters if m.get("is_default_master")), masters[0])
    return chosen["resume_id"]


def main():
    p = argparse.ArgumentParser(description="Review or queue public jobs in local Resume Matcher")
    p.add_argument("input", help="resume_matcher_jobs.json from marketing-jobs artifact")
    p.add_argument("--ids", nargs="+", type=int, help="1-based job numbers to queue; at most 10")
    p.add_argument("--confirm", action="store_true", help="Authorize queue writes and possible AI charges")
    p.add_argument("--master-id", help="Optional Resume Matcher master resume ID")
    p.add_argument("--base-url", default="http://127.0.0.1:8000/api/v1",
                   help="Local Resume Matcher backend, default http://127.0.0.1:8000/api/v1")
    args = p.parse_args()
    url = urllib.parse.urlsplit(args.base_url)
    if url.scheme != "http" or url.hostname not in {"localhost", "127.0.0.1", "::1"}:
        p.error("--base-url must be plain HTTP on localhost; do not expose Resume Matcher publicly")
    api = args.base_url.rstrip("/")
    jobs = load_jobs(args.input)
    print(f"{len(jobs)} job listings. Descriptions available for "
          f"{sum(bool(j.get('description')) for j in jobs)}.")
    for i, job in enumerate(jobs, 1):
        quality = "JD ready" if job.get("description") else "open link for full JD"
        print(f"{i:>2}. {job.get('title', '')} | {job.get('company', '')} "
              f"| {job.get('location', '')} | {quality}")
    if not args.ids:
        print("\nPreview only. To queue specific listings, add --ids 1 3 --confirm.")
        return 0
    ids = list(dict.fromkeys(args.ids))
    if any(n < 1 or n > len(jobs) for n in ids) or len(ids) > 10:
        p.error("Choose 1–10 valid job indices, each between 1 and the displayed listing count.")
    chosen = [jobs[n - 1] for n in ids]
    missing = [j["title"] for j in chosen if not j.get("description")]
    if missing:
        p.error("Some selected jobs have no usable description: " + ", ".join(missing)
                + ". Open their links and paste the full JD into Resume Matcher manually.")
    if not args.confirm:
        print("\nNOT QUEUED. Add --confirm to approve starting local AI tailoring work.")
        return 0
    master = pick_master(api, args.master_id)
    print("\nUsing master resume ID:", master)
    for job in chosen:
        description = (
            f"Job Title: {job.get('title', '')}\n"
            f"Company: {job.get('company', '')}\n"
            f"Location: {job.get('location', '')}\n"
            f"Original posting: {job.get('url', '')}\n\n"
            f"{job['description']}"
        )
        result = request_json("POST", api + "/jobs/queue", {
            "resume_id": master,
            "job_description": description,
            "role": job.get("title", ""),
            "company": job.get("company", ""),
            "rate_limit_seconds": 5,
            "prompt_id": "keywords",
        })
        print("Queued:", job.get("title"), "|", job.get("company"),
              "| item", result.get("item_id", "unknown"))
    print("\nOpen http://localhost:3000/queue to review tailored resumes.")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (ValueError, OSError, urllib.error.URLError, RuntimeError) as exc:
        print("Error:", exc, file=sys.stderr)
        sys.exit(1)
