import time
import os
from urllib.parse import urljoin
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime
from pathlib import Path


BASE_URL = "https://books.toscrape.com/"
CATALOG_URL = BASE_URL


def save_checkpoint(data, output_path):
    temp_path = output_path + ".tmp"
    pd.DataFrame(data).to_csv(temp_path, index=False, encoding="utf-8-sig")
    os.replace(temp_path, output_path)


def load_checkpoint(output_path):
    if not os.path.exists(output_path):
        return []

    try:
        checkpoint = pd.read_csv(output_path)
        checkpoint = checkpoint.astype(object).where(pd.notna(checkpoint), None)
        print(f"Checkpoint loaded: {len(checkpoint)} products already scraped")
        return checkpoint.to_dict("records")
    except Exception as error:
        print(f"Could not load checkpoint: {error}")
        return []

def init_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")

    prefs = {
        "profile.default_content_setting_values.notifications": 2,
        "profile.default_content_setting_values.geolocation": 2
    }
    options.add_experimental_option("prefs", prefs)

    return webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )


def wait_for_product_page(driver):
    WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, ".product_main h1"))
    )


def safe_text(driver, by, selector):
    try:
        return driver.find_element(by, selector).text.strip()
    except NoSuchElementException:
        return None


def get_price(driver):
    return safe_text(driver, By.CSS_SELECTOR, ".product_main .price_color")


def get_categories(driver):
    # Books to Scrape exposes one genre in the breadcrumb, not three category levels.
    category = safe_text(driver, By.CSS_SELECTOR, "ul.breadcrumb li:nth-child(3) a")
    return category, None, None


def scrape(driver, output_path, data=None, max_pages=None):
    # wait for initial products
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, "article.product_pod h3 a")
        )
    )

    catalog_window = driver.current_window_handle
    driver.execute_script("window.open('about:blank');")
    product_window = driver.window_handles[-1]


    data = data or []
    product_links = {
        item["url"] for item in data
        if item.get("url")
    }
    pages_loaded = 1

    while True:
        # collect product links currently loaded
        cards = driver.find_elements(By.CSS_SELECTOR, "article.product_pod h3 a")

        current_links = set()
        for a in cards:
            href = a.get_attribute("href")
            if not href:
                continue
            current_links.add(urljoin(driver.current_url, href))

        new_links = current_links - product_links
        print(f"Page {pages_loaded}: {len(new_links)} new products found")


        driver.switch_to.window(product_window)

        for idx, link in enumerate(new_links, 1):
            print(f"  [{idx}/{len(new_links)}] Scraping {link}")
            driver.get(link)

            wait_for_product_page(driver)

            cat1, cat2, cat3 = get_categories(driver)

            product = {
                "category": cat1,
                "subcategory": cat2,
                "group": cat3,
                "name": safe_text(driver, By.CSS_SELECTOR, ".product_main h1"),
                "company": None,  # Not supplied by this practice website.
                "country": None,  # Not supplied by this practice website.
                "price": get_price(driver),
                "url": link,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }

            data.append(product)
            save_checkpoint(data, output_path)
            product_links.add(link)
            print(f"  Checkpoint saved: {len(data)} products")

        driver.switch_to.window(catalog_window)
        product_links.update(new_links)


        # stop if reached page limit
        if max_pages is not None and pages_loaded >= max_pages:
            print("Reached max_pages limit")
            break

        # Books to Scrape uses a next-page link.
        next_pages = driver.find_elements(By.CSS_SELECTOR, "li.next a")
        if not next_pages:
            print("No more pages to load")
            break
        next_url = urljoin(driver.current_url, next_pages[0].get_attribute("href"))
        driver.get(next_url)
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "article.product_pod h3 a"))
        )
        pages_loaded += 1
        time.sleep(2)

    print(f"Total product links collected: {len(product_links)}")


    return data


def main():
    output_path = str(Path(__file__).resolve().parent / "books_checkpoint.csv")
    products = load_checkpoint(output_path)
    driver = None

    try:
        driver = init_driver()
        driver.get(CATALOG_URL)

        products = scrape(driver, output_path, products, max_pages=2)
        save_checkpoint(products, output_path)
        print(f"Saved {output_path}")
    finally:
        if driver is not None:
            driver.quit()

if __name__ == "__main__":
    main()