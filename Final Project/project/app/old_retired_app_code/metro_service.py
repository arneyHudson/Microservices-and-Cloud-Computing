from bs4 import BeautifulSoup
import urllib.parse
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import undetected_chromedriver as uc

def fetch_page_source(url, wait_time=5, wait_selector=None):
    """
    Opens the given URL using Selenium and returns the rendered page source.
    """
    driver = uc.Chrome()
    try:
        driver.get(url)
        WebDriverWait(driver, wait_time).until(EC.presence_of_element_located((By.CSS_SELECTOR, wait_selector)))
        page_source = driver.page_source
    finally:
        driver.quit()
    return page_source


def parse_products(soup):
    """
    Parses the product details from the BeautifulSoup object.
    Returns a list of product dictionaries with 'name' and 'price' keys.
    """
    search_items_found = soup.find_all(attrs={"data-testid": lambda x: x and "product-card-" in x})
    products = []

    for element in search_items_found:
        try:
            name_element = element['aria-label']

            price_container = element.find(attrs={"data-testid": lambda x: x and "cart-page-item-unit-price" in x})
            price_element = price_container['value'] if price_container else None

            sizing_container = element.find(attrs={"data-testid": lambda x: x and "cart-page-item-sizing" in x})
            sizing_element = sizing_container.get_text(strip=True) if sizing_container else None

            if name_element and price_element:
                name = name_element
                if sizing_element:
                    name += f" {sizing_element}"
                name = name.encode('ascii', 'ignore').decode('ascii')  # Remove non-ASCII characters
                price = float(price_element)

                products.append({
                    "name": name,
                    "price": price
                })
        except Exception as e:
            print(f"Error parsing element: {e}")
    return products


def remove_duplicates(products):
    """
    Removes duplicate products based on the 'name' field while keeping the first occurrence.
    Returns a list of unique products.
    """
    seen_names = set()
    unique_products = []

    for product in products:
        if product['name'] not in seen_names:
            unique_products.append(product)
            seen_names.add(product['name'])

    return unique_products


def search_metro_market(search_term):
    """
    Searches Metro Market for the given term, scrapes product details, and removes duplicates.
    Returns a list of unique products.
    """
    encoded_term = urllib.parse.quote(search_term)
    search_url = f"https://www.metromarket.net/search?query={encoded_term}&searchType=default_search"
    wait_time = 5
    wait_selector = "div[data-testid='product-grid-container']"

    try:
        # Fetch and parse the page source
        page_source = fetch_page_source(search_url, wait_time, wait_selector)
        soup = BeautifulSoup(page_source, 'html.parser')

        # Extract and process products
        products = parse_products(soup)
        if products:
            products = remove_duplicates(products)

        return products
    except Exception as e:
        print(f"Error during scraping Metro Market: {e}")
        return []