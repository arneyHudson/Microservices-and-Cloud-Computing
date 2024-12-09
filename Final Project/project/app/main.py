from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import os
from scraping_service import search_costco, search_metro_market, search_walmart, create_webdriver # ,search_aldi
from product_comparator import ProductComparator

app = Flask(__name__)
CORS(app)

# Serve frontend HTML file
@app.route('/')
def index():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'frontend.html')

def get_prices_from_stores(search_term):
    """
    Helper function to fetch prices from all stores and return the results.
    """
    # Fetch price data from each store's service
    #costco_results = search_costco(search_term)
    metro_results = search_metro_market(search_term)
    print(f"\nMetro Results:\n{metro_results}")
    
    #aldi_results = search_aldi(search_term)
    walmart_results = search_walmart(search_term)
    print(f"\nWalmart Results:\n{walmart_results}")

    # Combine the results into a dictionary
    return metro_results, walmart_results

@app.route('/compare', methods=['GET'])
def compare():
    
    search_term = request.args.get('search', "").lower()  # You can pass search term directly if needed
    
    # Get the prices from all stores
    metro_results, walmart_results = get_prices_from_stores(search_term)
    
    # Now, pass the fetched data to your comparison service
    comparisons = ProductComparator.find_best_matches(metro_results, walmart_results)
    
    return comparisons

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
