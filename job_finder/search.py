"""Daily marketing job discovery. No applications or messages are sent."""
from __future__ import annotations

import csv
import datetime as dt
import html
import json
import os
import re
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent
NYC = "New York, NY"
SEARCHES = [
    ("Digital Marketing Specialist", NYC, False),
    ("Social Media Specialist", NYC, False),
    ("Marketing Analyst", NYC, False),
    ("Growth Marketing Associate", NYC, False),
    ("Content Strategist", "United States", True),
    ("Marketing Operations", "United States", True),
    ("Digital Marketing Intern", NYC, False),
]
TITLE_KEYWORDS = (
    "marketing", "social media", "content strategist", "content creator",
    "growth", "seo", "brand specialist", "account coordinator",
)
EXCLUDE_TITLE = (
    "director", "vice president", "chief ", "principal ", "head of ",
    "door-to-door", "sales representative", "brand ambassador",
)
SCORE_TERMS = {
    "social media": 5, "digital marketing": 6, "content strategist": 6,
    "marketing analyst": 7, "marketing operations": 7, "growth marketing": 7,
    "paid social": 3, "ga4": 3, "google analytics": 3, "sql": 4,
    "seo": 3, "campaign": 2, "analytics": 2, "agency": 2,
    "coordinator": 2, "specialist": 2, "associate": 2, "intern": 2,
}

def clean(text):
    return re.sub(r"\s+", " ", html.unescape(str(text or ""))).strip()

def key_for(url):
    parts = urllib.parse.urlsplit(url)
    return urllib.parse.urlunsplit((parts.scheme, parts.netloc.lower(), parts.path.rstrip("/"), "", ""))

def relevance(item):
    title = clean(item["title"]).lower()
    desc = clean(item.get("description", "")).lower()
    if not any(x in title for x in TITLE_KEYWORDS):
        return -1
    if any(x in title for x in EXCLUDE_TITLE):
        return -1
    total = sum(weight for term, weight in SCORE_TERMS.items() if term in title) * 2
    total += sum(weight for term, weight in SCORE_TERMS.items() if term in desc)
    if "new york" in clean(item.get("location", "")).lower():
        total += 4
    if item.get("remote"):
        total += 3
    return total

def add(items, item):
    for field in ("title", "company", "location", "url", "source"):
        item[field] = clean(item.get(field))
    if not item["title"] or not item["url"]:
        return
    item["score"] = relevance(item)
    if item["score"] < 5:
        return
    item["key"] = key_for(item["url"])
    if item["key"] in items and items[item["key"]]["score"] >= item["score"]:
        return
    items[item["key"]] = item

def get_json(url):
    req = urllib.request.Request(url, headers={"User-Agent": "MihirMarketingJobFinder/1.0 (personal job search)"})
    with urllib.request.urlopen(req, timeout=24) as response:
        return json.load(response)

def collect_jobspy(items, errors):
    if os.getenv("USE_JOBSPY", "true").lower() != "true":
        return
    try:
        from jobspy import scrape_jobs
    except ImportError as exc:
        errors.append("JobSpy unavailable: " + str(exc))
        return
    for term, location, remote in SEARCHES:
        try:
            rows = scrape_jobs(
                site_name=["indeed", "linkedin"],
                search_term=term,
                location=location,
                country_indeed="USA",
                is_remote=remote,
                results_wanted=10,
                hours_old=72,
                verbose=0,
            )
            if rows is None:
                continue
            for _, row in rows.iterrows():
                d = row.to_dict()
                add(items, {
                    "title": d.get("title"), "company": d.get("company"),
                    "location": d.get("location") or location,
                    "url": d.get("job_url"), "source": d.get("site") or "JobSpy",
                    "description": d.get("description") or "",
                    "remote": remote,
                })
        except Exception as exc:
            errors.append("JobSpy / " + term + ": " + str(exc)[:180])
        time.sleep(1)

def collect_remotive(items, errors):
    try:
        data = get_json("https://remotive.com/api/remote-jobs?limit=200")
        for job in data.get("jobs", []):
            location = clean(job.get("candidate_required_location"))
            # Only explicitly US / North America / worldwide remote eligibility;
            # employers still need to confirm the applicant's state and authorization.
            if not any(s in location.lower() for s in (
                "united states", "usa", "u.s.", "north america", "worldwide", "anywhere"
            )):
                continue
            add(items, {
                "title": job.get("title"), "company": job.get("company_name"),
                "location": location or "Remote (verify US eligibility)",
                "url": job.get("url"), "source": "Remotive",
                "description": re.sub("<[^>]+>", " ", job.get("description") or ""),
                "remote": True,
            })
    except Exception as exc:
        errors.append("Remotive: " + str(exc)[:180])

def markdown(items, errors):
    now = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    ranked = sorted(items.values(), key=lambda item: -item["score"])[:45]
    lines = [
        "# Marketing job matches — " + now, "",
        "Search: NYC on-site/hybrid and US-eligible remote roles; marketing, content, "
        "social media, analytics, growth, and internships.", "",
        "These are leads, not verified open vacancies. Check each job's availability, "
        "location restrictions, requirements and work authorization before applying.", "",
        "Matches collected: **" + str(len(items)) + "**. Showing top **" + str(len(ranked)) + "**.", "",
        "| Role | Company | Location | Source | Match | Apply |",
        "|---|---|---|---|---:|---|",
    ]
    for job in ranked:
        def safe(value):
            return clean(value).replace("|", "\\|")[:110]
        url = job["url"].replace(")", "%29")
        lines.append("| " + " | ".join([
            safe(job["title"]), safe(job["company"]), safe(job["location"]),
            safe(job["source"]), str(job["score"]),
            "[View listing](" + url + ")",
        ]) + " |")
    if not ranked:
        lines += ["", "No matching jobs were returned on this run. Review the workflow logs "
                  "and try a manual rerun; some job boards rate-limit automated requests."]
    if errors:
        lines += ["", "## Source warnings", ""]
        lines += ["- " + clean(e) for e in errors]
    lines += ["", "This automation **never applies for jobs or sends recruiter messages**.", ""]
    (ROOT / "latest.md").write_text("\n".join(lines), encoding="utf-8")
    with (ROOT / "latest.csv").open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=["title", "company", "location", "source", "url", "score", "remote"])
        writer.writeheader()
        for job in ranked:
            writer.writerow({k: job.get(k, "") for k in writer.fieldnames})
    print("Collected", len(items), "matching jobs; warnings:", len(errors))
    return len(ranked)

if __name__ == "__main__":
    found, warnings = {}, []
    collect_jobspy(found, warnings)
    collect_remotive(found, warnings)
    markdown(found, warnings)
