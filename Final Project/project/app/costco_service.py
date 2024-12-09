from bs4 import BeautifulSoup
import urllib.parse
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import undetected_chromedriver as uc

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


def parse_costco_products(body):
    """
    Parses product details from the BeautifulSoup body object for Costco's website.
    Returns a list of product dictionaries with 'name' and 'price' keys.
    """
    search_items_found = body.find_all(attrs={"data-testid": lambda x: x and "Grid" in x})
    products = []

    for element in search_items_found:
        try:
            # Search through all descendant elements for the name and price
            name_elements = element.find_all(attrs={"data-testid": lambda value: value and "Text_ProductTile_" in value})
            price_elements = element.find_all(attrs={"data-testid": lambda x: x and "Text_Price" in x})
            
            # Extract name and price details
            name = name_elements[0].get_text(strip=True) if name_elements else None
            price_text = price_elements[0].get_text(strip=True).replace("$", "") if price_elements else None
            
            # Convert the price to a float
            price = float(price_text) if price_text else None

            if name and price:
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


def search_costco(search_term):
    """
    Searches Costco for the given term, scrapes product details, and removes duplicates.
    Returns a list of unique products.
    """
    encoded_term = urllib.parse.quote(search_term)
    search_url = f"https://www.costco.com/s?dept=All&keyword={encoded_term}"
    wait_time = 5
    wait_selector = "div.MuiGrid2-root.MuiGrid2-direction-xs-row.MuiGrid2-grid-xs-3.mui-1cbigla"

    try:
        # Fetch and parse the page source
        page_source = fetch_page_source(search_url, wait_time, wait_selector)
        soup = BeautifulSoup(page_source, 'html.parser')
        body = soup.find('body')

        # Optional: Save the body content for debugging
        #if body:
            #with open("body_content_2.txt", "w", encoding="utf-8") as file:
                #file.write(body.prettify())

        # Extract and process products
        products = parse_costco_products(body)
        if products:
            products = remove_duplicates(products)

        return products
    except Exception as e:
        print(f"Error during scraping Costco: {e}")
        return []