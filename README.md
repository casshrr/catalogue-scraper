# Catalogue Scraper

This is a portfolio adaptation of one of the Python/Selenium web-scraping scripts developed during my PwC internship. The original website and collected data have been excluded; this version runs against [Books to Scrape](https://books.toscrape.com/), a website intended for scraping practice.

It collects book titles, categories, displayed prices, URLs and capture timestamps.

The script retains a catalogue tab and a reusable product tab, skips URLs already recorded, and saves a CSV checkpoint after every product using a temporary file and atomic replacement. Restarting traverses the catalogue again but skips previously saved products.

## Open in PyCharm

1. Extract the ZIP, then open the `books-scraper` folder as a project.
2. Configure a Python 3.10+ interpreter and a project virtual environment.
3. Install the packages listed in `requirements.txt` into that environment.
4. Run `scraper.py`. Google Chrome must be installed.

The project includes `.gitignore` rules for virtual environments, PyCharm settings, generated CSV files and common environment files. Review the files selected for your first commit before sharing the project.

## Run

Requires Python 3.10+ and Google Chrome. ChromeDriver is managed by webdriver-manager; its first run may need an internet download.

```sh
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python scraper.py
```

Windows activation: `.venv\Scripts\activate`.

The default visits **two catalogue pages** (up to 40 books) and writes `books_checkpoint.csv` next to the script. Change `max_pages=2` in `main()` for a different limit, or use `None` for the full catalogue.

## Output and scope

The existing CSV column structure is preserved. `subcategory`, `group`, `company` and `country` remain empty because this source does not provide those fields. Prices remain displayed strings, not numeric values. A completed URL is skipped on later runs, so this is a capture/resume script rather than a price-update service.

This version retains the core extraction, deduplication and checkpoint-recovery approach. It is shared as a personal portfolio adaptation, without implying PwC endorsement. 

Checks performed: syntax, checkpoint save/load, two-page traversal, URL deduplication and restart behaviour using a simulated browser. A live Selenium run has not been performed in this environment.
