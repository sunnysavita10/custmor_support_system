import csv
import time
import re
import os
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup

os.makedirs("data", exist_ok=True)

def get_top_reviews(product_url, count=2):
    options = uc.ChromeOptions()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-blink-features=AutomationControlled")
    driver = uc.Chrome(options=options)

    if not product_url.startswith("http"):
        return "No reviews found"

    try:
        driver.get(product_url)
        time.sleep(4)
        try:
            driver.find_element(By.XPATH, "//button[contains(text(), '✕')]").click()
            time.sleep(1)
        except:
            pass

        for _ in range(4):
            ActionChains(driver).send_keys(Keys.END).perform()
            time.sleep(1.5)

        soup = BeautifulSoup(driver.page_source, "html.parser")
        review_blocks = soup.select("div._27M-vq, div.col.EPCmJX, div._6K-7Co")
        seen = set()
        reviews = []

        for block in review_blocks:
            text = block.get_text(separator=" ", strip=True)
            if text and text not in seen:
                reviews.append(text)
                seen.add(text)
            if len(reviews) >= count:
                break
    except Exception:
        reviews = []

    driver.quit()
    return " || ".join(reviews) if reviews else "No reviews found"

def scrape_flipkart_products(query, max_products=1, review_count=2):
    options = uc.ChromeOptions()
    driver = uc.Chrome(options=options)
    search_url = f"https://www.flipkart.com/search?q={query.replace(' ', '+')}"
    driver.get(search_url)
    time.sleep(4)

    try:
        driver.find_element(By.XPATH, "//button[contains(text(), '✕')]").click()
    except:
        pass

    time.sleep(2)
    products = []

    items = driver.find_elements(By.CSS_SELECTOR, "div[data-id]")[:max_products]
    for item in items:
        try:
            title = item.find_element(By.CSS_SELECTOR, "div.KzDlHZ").text.strip()
            price = item.find_element(By.CSS_SELECTOR, "div.Nx9bqj").text.strip()
            rating = item.find_element(By.CSS_SELECTOR, "div.XQDdHH").text.strip()
            reviews_text = item.find_element(By.CSS_SELECTOR, "span.Wphh3N").text.strip()
            match = re.search(r"\d+(,\d+)?(?=\s+Reviews)", reviews_text)
            total_reviews = match.group(0) if match else "N/A"

            link_el = item.find_element(By.CSS_SELECTOR, "a[href*='/p/']")
            href = link_el.get_attribute("href")
            product_link = href if href.startswith("http") else "https://www.flipkart.com" + href
            match = re.findall(r"/p/(itm[0-9A-Za-z]+)", href)
            product_id = match[0] if match else "N/A"
        except:
            continue

        top_reviews = get_top_reviews(product_link, count=review_count) if "flipkart.com" in product_link else "Invalid product URL"
        products.append([product_id, title, rating, total_reviews, price, top_reviews])

    driver.quit()
    return products

def save_to_csv(data, filename="data/product_reviews.csv"):
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["product_id", "product_title", "rating", "total_reviews", "price", "top_reviews"])
        writer.writerows(data)
