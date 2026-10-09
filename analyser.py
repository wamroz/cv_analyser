import argparse
import json
import re
from html.parser import HTMLParser
from pathlib import Path

from scraper import JOBS_PATH

STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "for", "from", "in",
    "is", "it", "of", "on", "or", "that", "the", "to", "with", "you", "your",
    "we", "our", "this", "will", "have", "has", "was", "were", "not", "but",
}


class HtmlTextExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts = []

    def handle_data(self, data):
        text = data.strip()
        if text:
            self.parts.append(text)

    def get_text(self):
        return " ".join(self.parts)


def strip_html(html):
    parser = HtmlTextExtractor()
    parser.feed(html or "")
    return parser.get_text()


def tokenize(text):
    words = re.findall(r"[a-zA-Z+#.]{2,}", text.lower())
    return {word.strip(".") for word in words if word not in STOPWORDS}


def load_jobs(path=JOBS_PATH):
    if not path.exists():
        raise FileNotFoundError(
            f"No jobs file at {path}. Run `python scraper.py` first."
        )
    return json.loads(path.read_text(encoding="utf-8"))


def load_cv_text(cv_path=None, skills=None):
    if cv_path:
        return Path(cv_path).read_text(encoding="utf-8")
    if skills:
        return skills.replace(",", " ")
    raise ValueError("Provide --cv or --skills")


def score_job(job, cv_tokens):
    title_tokens = tokenize(job.get("title") or "")
    tag_tokens = tokenize(" ".join(job.get("tags") or []))
    description_tokens = tokenize(strip_html(job.get("description") or ""))

    title_hits = cv_tokens & title_tokens
    tag_hits = cv_tokens & tag_tokens
    description_hits = cv_tokens & description_tokens

    score = (len(title_hits) * 3) + (len(tag_hits) * 2) + len(description_hits)
    matched = sorted(title_hits | tag_hits | description_hits)
    return score, matched


def rank_jobs(jobs, cv_text, limit=10):
    cv_tokens = tokenize(cv_text)
    ranked = []
    for job in jobs:
        score, matched = score_job(job, cv_tokens)
        if score > 0:
            ranked.append((score, matched, job))
    ranked.sort(key=lambda item: item[0], reverse=True)
    return cv_tokens, ranked[:limit]


def print_matches(cv_tokens, ranked):
    print(f"CV keywords: {len(cv_tokens)}")
    print("-" * 40)
    if not ranked:
        print("No matching offers. Try broader skills or refresh jobs.")
        return

    for i, (score, matched, job) in enumerate(ranked, 1):
        print(f"{i}. {job.get('title')}  (score: {score})")
        print(f"   Company: {job.get('company_name')}")
        print(f"   Location: {job.get('location')} | Remote: {job.get('remote')}")
        print(f"   Matched: {', '.join(matched[:12])}")
        print(f"   Link: {job.get('url')}")
        print("-" * 40)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Rank saved job offers against a CV or skill list."
    )
    parser.add_argument("--cv", help="Path to a .txt CV")
    parser.add_argument("--skills", help="Comma-separated skills, e.g. python,docker,sql")
    parser.add_argument("--limit", type=int, default=10, help="How many matches to show")
    return parser.parse_args()


def main():
    args = parse_args()
    jobs = load_jobs()
    cv_text = load_cv_text(args.cv, args.skills)
    cv_tokens, ranked = rank_jobs(jobs, cv_text, limit=args.limit)
    print_matches(cv_tokens, ranked)


if __name__ == "__main__":
    main()
