# cv_analyser

Narzędzie, które pobiera oferty pracy i rankuje je względem Twojego CV.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Użycie

1. Pobierz oferty z Arbeitnow i zapisz je do `data/jobs.json`:

```bash
python scraper.py
```

2. Dopasuj oferty do CV albo listy umiejętności:

```bash
python analyser.py --cv sample_cv.txt
python analyser.py --skills "python, docker, sql"
```

## Co dalej

- parsowanie CV z PDF
- lepsze wyciąganie umiejętności (nie tylko słowa kluczowe)
- filtrowanie po remote / lokalizacji / typie umowy
