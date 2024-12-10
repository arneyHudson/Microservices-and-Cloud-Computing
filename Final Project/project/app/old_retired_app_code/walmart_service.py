from bs4 import BeautifulSoup
import urllib.parse
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import undetected_chromedriver as uc
import re


def fetch_page_source(url, wait_selector, wait_time=5):
    """
    Fetches the rendered page source using Selenium with the given wait conditions.
    """
    driver = uc.Chrome()

    try:
        driver.get(url)
        WebDriverWait(driver, wait_time).until(EC.presence_of_element_located((By.CSS_SELECTOR, wait_selector)))
        return driver.page_source
    finally:
        driver.quit()


def parse_price(price_text):
    """
    Parses and formats a price string into a float value.
    Handles cases with commas and invalid characters.
    """
    # Remove everything except digits, commas, and periods
    price_text = re.sub(r"[^\d.,]", "", price_text.replace("$", ""))
    # Retain commas in thousand separators and fix misplaced commas/periods
    price_text = re.sub(r"(?<=\d),(?=\d{3}\b)", "", price_text)
    # Handle formatting for decimal placement
    if len(price_text) > 2:
        price_text = price_text[:-2] + '.' + price_text[-2:]
    elif len(price_text) == 2:
        price_text = '0.' + price_text
    else:
        price_text = '0.0'

    try:
        return float(price_text)
    except ValueError:
        return None


def parse_walmart_products(soup):
    """
    Extracts product details (name and price) from the BeautifulSoup object.
    """
    search_items = soup.find_all(
        attrs={"class": lambda x: x and "mb0 ph0-xl pt0-xl bb b--near-white w-25 pb3-m ph1" in x}
    )
    products = []

    for element in search_items:
        try:
            # Extract the product name
            name_element = element.find(attrs={"data-automation-id": lambda x: x and "product-title" in x})
            name = name_element.get_text(strip=True) if name_element else None

            # Extract and parse the product price
            price_container = element.find(attrs={"class": lambda x: x and "mr1 mr2-xl b black lh-solid f5 f4-l" in x})
            price = parse_price(price_container.get_text(strip=True)) if price_container else None

            if name and price:
                # Encode name to ASCII to avoid special characters
                name = name.encode('ascii', 'ignore').decode('ascii')
                products.append({"name": name, "price": price})
        except Exception as e:
            print(f"Error parsing product: {e}")

    return products


def remove_duplicates(products):
    """
    Removes duplicate products based on the 'name' field while keeping the first occurrence.
    """
    seen_names = set()
    unique_products = []

    for product in products:
        if product['name'] not in seen_names:
            unique_products.append(product)
            seen_names.add(product['name'])

    return unique_products


def search_walmart(search_term):
    """
    Searches Walmart for the given term and returns a list of unique products with names and prices.
    """
    encoded_term = urllib.parse.quote(search_term)
    search_url = f"https://www.walmart.com/search?q={encoded_term}"
    wait_selector = "div[data-testid='item-stack']"

    try:
        # Fetch the rendered page source
        page_source = fetch_page_source(search_url, wait_selector)
        soup = BeautifulSoup(page_source, 'html.parser')

        # Parse product details
        products = parse_walmart_products(soup)
        if products:
            products = remove_duplicates(products)

        return products
    except Exception as e:
        print(f"Error during Walmart scraping: {e}")
        return []
