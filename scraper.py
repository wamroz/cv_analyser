import json
from pathlib import Path

import requests

API_URL = "https://arbeitnow.com/api/job-board-api"
DATA_DIR = Path("data")
JOBS_PATH = DATA_DIR / "jobs.json"
HEADERS = {"User-Agent": "cv-analyser/0.1"}


def fetch_jobs():
    print("Retrieving job offers...")
    response = requests.get(API_URL, headers=HEADERS, timeout=30)
    response.raise_for_status()

    payload = response.json()
    jobs = payload.get("data", [])
    print(f"Downloaded {len(jobs)} offers.")
    return jobs


def save_jobs(jobs, path=JOBS_PATH):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(jobs, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Saved jobs to {path}")


def preview_jobs(jobs, limit=5):
    print("-" * 40)
    for i, job in enumerate(jobs[:limit], 1):
        tags = ", ".join(job.get("tags") or []) or "n/a"
        print(f"{i}. {job.get('title')}")
        print(f"   Company: {job.get('company_name')}")
        print(f"   Location: {job.get('location')} | Remote: {job.get('remote')}")
        print(f"   Tags: {tags}")
        print(f"   Link: {job.get('url')}")
        print("-" * 40)


def download_data():
    try:
        jobs = fetch_jobs()
    except requests.RequestException as exc:
        print(f"Error downloading jobs: {exc}")
        return []

    save_jobs(jobs)
    preview_jobs(jobs)
    return jobs


if __name__ == "__main__":
    download_data()
