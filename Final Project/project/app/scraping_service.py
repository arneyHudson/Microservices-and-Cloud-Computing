from bs4 import BeautifulSoup
import urllib.parse
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import undetected_chromedriver as uc
from selenium import webdriver
import re

def create_webdriver():
    options = webdriver.ChromeOptions()
    # Ensure remote Selenium service is used
    driver = webdriver.Remote(
        command_executor="http://selenium:4444/wd/hub",
        options=options
    )
    return driver

def fetch_page_source(url, wait_time=5, wait_selector=None):
    """
    Opens the given URL using Selenium with specified window size and returns the rendered page source.
    """
    driver = uc.Chrome()
    try:
        driver.get(url)
        WebDriverWait(driver, wait_time).until(EC.presence_of_element_located((By.CSS_SELECTOR, wait_selector)))
        page_source = driver.page_source
    finally:
        driver.quit()
    return page_source


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


############################################################################################
#                            Costco Scraping Service                                       #
############################################################################################

def parse_costco_products(body):
    """
    Parses product details from the BeautifulSoup body object for Costco's website.
    Returns a list of product dictionaries with 'name' and 'price' keys.
    """
    search_items_found = body.find_all(attrs={"data-testid": lambda x: x and "Grid" in x})
    products = []

    for element in search_items_found:
        try:
            name_elements = element.find_all(attrs={"data-testid": lambda value: value and "Text_ProductTile_" in value})
            price_elements = element.find_all(attrs={"data-testid": lambda x: x and "Text_Price" in x})
            
            name = name_elements[0].get_text(strip=True) if name_elements else None
            name = name.replace("|", "")
            name = name.encode('ascii', 'ignore').decode('ascii')  # Remove non-ASCII characters
            price_text = price_elements[0].get_text(strip=True).replace("$", "") if price_elements else None
            
            price = float(price_text) if price_text else None

            if name and price:
                products.append({
                    "name": name,
                    "price": price
                })
        except Exception as e:
            print(f"Error parsing element: {e}")
    return products


def search_costco(search_term):
    """
    Searches Costco for the given term, scrapes product details, and removes duplicates.
    """
    encoded_term = urllib.parse.quote(search_term)
    search_url = f"https://www.costco.com/s?dept=All&keyword={encoded_term}"
    wait_time = 5
    wait_selector = "div.MuiGrid2-root.MuiGrid2-direction-xs-row.MuiGrid2-grid-xs-3.mui-1cbigla" 

    try:
        page_source = fetch_page_source(search_url, wait_time, wait_selector)
        soup = BeautifulSoup(page_source, 'html.parser')
        body = soup.find('body')

        products = parse_costco_products(body)
        if products:
            products = remove_duplicates(products)

        return products
    except Exception as e:
        print(f"Error during scraping Costco: {e}")
        return []
    
    
    
############################################################################################
#                            Walmart Scraping Service                                      #
############################################################################################

def parse_walmart_price(price_text):
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
            price = parse_walmart_price(price_container.get_text(strip=True)) if price_container else None

            if name and price:
                # Encode name to ASCII to avoid special characters
                name = name.replace("|", "")
                name = name.encode('ascii', 'ignore').decode('ascii')
                products.append({"name": name, "price": price})
        except Exception as e:
            print(f"Error parsing product: {e}")

    return products


def search_walmart(search_term):
    """
    Searches Walmart for the given term and returns a list of unique products with names and prices.
    """
    encoded_term = urllib.parse.quote(search_term)
    search_url = f"https://www.walmart.com/search?q={encoded_term}"
    wait_selector = "div[data-testid='item-stack']"
    wait_time = 5

    try:
        # Fetch the rendered page source
        page_source = fetch_page_source(search_url, wait_time, wait_selector)
        soup = BeautifulSoup(page_source, 'html.parser')

        # Parse product details
        products = parse_walmart_products(soup)
        if products:
            products = remove_duplicates(products)

        return products
    except Exception as e:
        print(f"Error during Walmart scraping: {e}")
        return []



############################################################################################
#                            Metro Market Scraping Service                                 #
############################################################################################

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
                name = name.replace("|", "")
                name = name.encode('ascii', 'ignore').decode('ascii')  # Remove non-ASCII characters
                price = float(price_element)

                products.append({
                    "name": name,
                    "price": price
                })
        except Exception as e:
            print(f"Error parsing element: {e}")
    return products


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


############################################################################################
#                            Aldi Scraping Service                                         #
############################################################################################