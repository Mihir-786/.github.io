# Connect GitHub Job Finder to Resume Matcher

This integration connects your **GitHub job discovery results** to the open-source **[Resume Matcher](https://github.com/srbhr/Resume-Matcher)** tailoring queue, **on your own computer**.

## What it does

- Daily GitHub Job Finder still gathers NYC and US remote marketing openings.
- Alongside `latest.csv` and `latest.md`, the `marketing-jobs` workflow artifact includes `resume_matcher_jobs.json` with job title, company, original job link, and any usable job-description text the source returned.
- A local importer lets you review all entries and select up to 10 at a time for Resume Matcher's queue.
- Resume Matcher uses your **private master resume**, which stays in its local database, to draft job-specific PDFs and internal ATS-match reports.
- You review every tailored resume before sending an application.

**No resumes, email addresses, application data, API keys, or personal profile details are uploaded to GitHub.**

## Initial installation — Resume Matcher on your computer

Follow Resume Matcher's **[official setup guide](https://github.com/srbhr/Resume-Matcher/blob/main/SETUP.md)**. You can use its Docker Compose option if you have Docker installed, or its Python/Node development setup. Its setup guide currently lists Python 3.13+, Node 24+, and an AI provider configuration.

Important: this is a **local, single-user application without login protection**. Keep it bound to `localhost` (127.0.0.1), **never expose port 8000 or 3000 directly to the public internet**.

1. Start Resume Matcher and open **http://localhost:3000**.
2. Add your master resume (PDF or DOCX), check it for accuracy, and mark it as the master.
3. Configure an AI model in Resume Matcher settings. Model/API usage may carry costs.
4. Ensure both the UI and backend are running.

Your GitHub account itself does *not* run the Resume Matcher application; GitHub Actions only exports public job posting data.

## Export listings from GitHub

1. After this integration PR is merged, open **Actions → Marketing Job Finder → Run workflow** (or let the daily run complete).
2. Open the completed run; download **Artifacts → marketing-jobs**.
3. Unzip it; it contains `latest.csv`, `latest.md`, and `resume_matcher_jobs.json`.
4. Download `job_finder/import_to_resume_matcher.py` from this repository. This uses Python standard library only.

Some job boards return only a title and URL, so the exporter marks those entries as having **no usable full job description**. For those, open the original link and paste the complete JD manually into Resume Matcher.

## Preview the matches before queuing

In a terminal in the directory containing the importer and JSON:

```bash
python import_to_resume_matcher.py resume_matcher_jobs.json
```

This prints numbered job listings without contacting Resume Matcher or generating AI output.

To preview your selection (still no writes):

```bash
python import_to_resume_matcher.py resume_matcher_jobs.json --ids 1 3 5
```

To explicitly queue selected jobs **into your local Resume Matcher**:

```bash
python import_to_resume_matcher.py resume_matcher_jobs.json --ids 1 3 5 --confirm
```

The importer calls the local `/api/v1/resumes/list` endpoint to find your ready master resume, then the local `/api/v1/jobs/queue` endpoint. It refuses non-loopback API URLs and does not upload any application or resume details.

Then open **http://localhost:3000/queue** to see the queue. The queued process can invoke your configured AI provider and consume its quota or incur charges. **The importer requires `--confirm` to authorize that.**

You may choose a specific master by adding `--master-id YOUR_LOCAL_RESUME_ID`, or use `--base-url http://localhost:8000/api/v1` if needed.

## Important limitations

- These are **candidate postings**, not verified openings. Confirm the original URL, hiring status, work location and salary.
- Automated searches are subject to source availability, job board terms, and rate limits.
- Source descriptions may be truncated. Always compare against the full, current job listing.
- There is **no fully unattended resume creation in GitHub Actions**. Your master resume and AI access stay outside the public repository; you explicitly select and approve jobs locally.
- Resume Matcher's 0–100 score is its own relevance/parseability measure, **not an employer's official ATS score or a probability of getting an interview**.
- Avoid unsupported credentials, invented work experience, or claims of sponsorship/OPT/CPT eligibility. Check work authorization separately.
- This is a lightweight integration via Resume Matcher's documented queue endpoint, **not a fork, installation, or hosted instance of Resume Matcher**.

## Project links

- [Job Finder workflow](https://github.com/Mihir-786/.github.io/actions/workflows/marketing-job-finder.yml)
- [Resume Matcher installation instructions](https://github.com/srbhr/Resume-Matcher/blob/main/SETUP.md)
- [Resume Matcher open-source repository](https://github.com/srbhr/Resume-Matcher)
