from flask import request
from database import get_prices
import requests
from bs4 import BeautifulSoup
import urllib.parse
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import undetected_chromedriver as uc

def search_aldi(search_term):
    encoded_term = urllib.parse.quote(search_term)
    
    # Metro Market search URL
    search_url = f"https://new.aldi.us/results?q={encoded_term}"
    
    # Set up Selenium WebDriver with Chrome options
    options = Options()
    options.headless = True  # Run in headless mode (no GUI)
    
    # Start the Chrome driver
    driver = uc.Chrome()
    
    try:
        # Open the Metro Market page using Selenium
        driver.get(search_url)
        try:
            close_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.ID, "onetrust-accept-btn-handler"))
            )
            close_button.click()
            print("Cookie popup dismissed.")
        except Exception as e:
            print(f"No cookie popup appeared or failed to close it: {e}")
        
        # Wait until the search results container is loaded (adjust this if necessary)
        WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div[data-testid='product-listing-viewer__product-area']")))
        # Get the page source after JavaScript has been rendered
        page_source = driver.page_source
        
        # Parse the page with BeautifulSoup
        soup = BeautifulSoup(page_source, 'html.parser')
        
        # Find price elements using the data-testid that contains 'cart-page-item-unit-price'
        search_items_found = soup.find_all(attrs={"id": lambda x: x and "product-tile-000" in x})
        # Prepare the result
        products = []
        for elements in search_items_found:
            print("Element: ", elements)
            # Extract the name from the `aria-label`
            name_element = ""
            
            brand_name_container = elements.find(attrs={"class": lambda x: x and "product-tile__brandname" in x}) 
            if brand_name_container:
                brand_name_element = brand_name_container.get_text(strip=True)
                name_element += brand_name_element + " "
                
            product_name_container = elements.find(attrs={"class": lambda x: x and "product-tile__name" in x}) 
            if product_name_container:
                product_name_element = product_name_container.get_text(strip=True)
                name_element += product_name_element
            
            
            price_container = elements.find(attrs={"data-testid": lambda x: x and "base-price__regular" in x}) 
            if price_container:
                price_element = price_container.get_text(strip=True).replace("$", "")
            
            if name_element and price_element:
                # Clean and extract the name and price
                name = name_element
                name = name.encode('ascii', 'ignore').decode('ascii')
                price = float(price_element)
                
                # Append to the result list
                products.append({
                    "name": name,
                    "price": price
                })
        # Close the browser after scraping
        driver.quit()

        return products
    
    except Exception as e:
        print(f"\nError during scraping Aldi: {e}")
        driver.quit()  # Ensure the driver is closed in case of an error
        return []