# Career Ops + Marketing Job Finder: safe, manual-first setup

## What this integration does

The existing GitHub Job Finder searches and scores public job listings. This bridge adds an optional `career_ops_candidates.md` export to the same GitHub Actions artifact. The export contains the 15 highest keyword-scored public job listings in the `## Pending` format Career Ops understands. This is only a preliminary ranking, not a CV-fit analysis.

**Nothing here sends recruiter messages, sends applications, logs into LinkedIn, or publishes your CV.** Your existing daily schedule and main scraper remain unchanged.

## Step 1 — Run the job finder

From the public GitHub repository choose **Actions → Marketing Job Finder → Run workflow** (or use its daily scheduled run). Download the `marketing-jobs` artifact ZIP. After this change is merged, that ZIP contains `latest.csv`, `latest.md`, and `career_ops_candidates.md`.

## Step 2 — Set up Career Ops privately

Install Node.js 22.13+ and Git. On your own computer, in a separate local folder, run:

    npx @santifer/career-ops init

Then start a supported AI coding CLI (such as Codex or Claude Code) inside your newly initialized `career-ops` folder. Follow Career Ops' own first-run instructions to enter a *private* master CV, target marketing roles, and location preferences. See https://github.com/career-ops-hq/career-ops/blob/main/docs/SETUP.md .

Do **not** put a master CV, LinkedIn connections export, recruiter lists, API keys, or the Career Ops `data/` directory in this public repository. If using a Git repository for Career Ops, make it private and inspect its ignore rules.

## Step 3 — Import shortlisted URLs locally

**Simplest:** Open the downloaded `career_ops_candidates.md`. Copy its `- [ ]` job lines into the `## Pending` section of the private `career-ops/data/pipeline.md` file, avoiding duplicates.

**Optional one-command local merge:** If you also have this Job Finder repo checked out locally, run the following from its root folder. Use the paths on your computer:

    python job_finder/career_ops_bridge.py --queue /path/to/downloaded/career_ops_candidates.md --import-to /path/to/career-ops/data/pipeline.md

This first prints how many jobs would be added; it does **not** write. After checking the preview, rerun with `--confirm` at the end. The import preserves existing tracker rows and creates a timestamped backup of your local pipeline file. It sends nothing to the Internet.

## Step 4 — Career Ops research and outreach

1. Ask your Career Ops AI coding assistant: **Run career-ops pipeline mode for data/pipeline.md. Evaluate the first five jobs against my real CV and show gaps before creating any PDF.**
2. For jobs you choose, ask: **Run career-ops contacto mode for this company and role. Find a publicly verifiable recruiter or hiring manager, show the evidence and profile link, and draft a LinkedIn note under 300 characters. Do not send it.**
3. Review names, roles, links, and draft wording yourself. Send LinkedIn connection requests and messages manually. Do not automate mass invites or DMs.
4. When you **actually apply**, record it in Career Ops tracker. Ask for **followup** after the appropriate interval. Drafts are not marked sent until you confirm.

Career Ops commands and privacy controls: https://github.com/career-ops-hq/career-ops

## Notes and limitations

- LinkedIn and other boards can include outdated or reposted listings; check the actual employer posting.
- Job Finder's `score` is a keyword heuristic, not a validated ATS percentage or hiring probability.
- Career Ops is a separate local application, not a GitHub Actions extension. Installation, first-run setup, and your AI CLI account are separate.
- A specific recruiter is not guaranteed to be discoverable; never invent contact details.
- Verify employer work-authorization, CPT/OPT, hybrid/on-site requirements, and compensation before applying.

## Customize export

Run locally, after your daily scraper has created `job_finder/latest.csv`:

    python job_finder/career_ops_bridge.py --csv job_finder/latest.csv --limit 20

This writes `job_finder/career_ops_candidates.md` without modifying Career Ops.
