# Mihir's Marketing Job Finder

A **read-only**, automated job discovery add-on for this GitHub account. This project does **not** change the portfolio website, apply to jobs, or send messages to recruiters.

## How it works

- Uses [JobSpy](https://github.com/speedyapply/JobSpy) to search Indeed and LinkedIn for marketing jobs around NYC and US remote roles.
- Uses Remotive's public remote-jobs API as a backup source.
- Searches for Digital Marketing Specialist, Social Media Specialist, Marketing Analyst, Growth Marketing Associate, Content Strategist, Marketing Operations, and Digital Marketing Intern.
- Applies keyword-based match scores, removes duplicates, and generates a Markdown report and CSV.
- Runs daily at **13:30 UTC** after this pull request is merged into the default branch. Scheduled GitHub Actions can be delayed or occasionally skipped.
- Lets you launch a search manually using **Actions → Marketing Job Finder → Run workflow**.
- Saves results as a GitHub Actions artifact called `marketing-jobs` for 30 days. Open the completed run and download it under **Artifacts**.

## How to activate

1. Review the pull request, especially the GitHub Actions workflow and external dependencies.
2. Merge it into `main` to enable the daily schedule.
3. In the GitHub **Actions** tab, enable workflows if prompted.
4. Open **Marketing Job Finder** → **Run workflow** to test.
5. Open the run and download **marketing-jobs**.
6. If the job returns no results, inspect the log: job board rate limiting or site changes can cause failed searches.

## Edit your preferences

Edit `SEARCHES` in `job_finder/search.py` to change titles or cities, then commit and rerun the workflow. Titles are currently filtered to marketing, social media, content, growth and analytics-oriented jobs. These are initial matches and still require your review.

## Limitations and safety

- **No automated job applications.** Review each listing and apply yourself.
- Listings may be expired, duplicated across sites, or geographically restricted. Verify the employer's actual application page.
- This tool cannot verify CPT, OPT, visa sponsorship, or whether the employer can hire an international student. Always check work authorization separately.
- Avoid excessive scraping. LinkedIn and Indeed may block or rate-limit bots; respect applicable terms and disable a source if necessary.
- No resume, personal contact details, credentials, or tokens are stored in the repository.
- The script uses JobSpy and Remotive, neither of which is officially affiliated with GitHub.
- Match scores are **simple keyword relevance scores**, not scientifically validated ATS rankings.
- Reports are uploaded as workflow artifacts, not published to the public website.

## Local execution

Requires Python 3.11+.

```bash
python -m pip install -r job_finder/requirements.txt
cd job_finder
python search.py
```

Reports: `job_finder/latest.md` and `job_finder/latest.csv`.

## Foundation

Search backend: [speedyapply/JobSpy](https://github.com/speedyapply/JobSpy) (MIT license). Optional public remote results from [Remotive](https://remotive.com/).
