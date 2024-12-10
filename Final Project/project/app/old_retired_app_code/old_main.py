from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import os
from costco_service import search_costco
from metro_service import search_metro_market
from project.app.old_retired_code.aldi_service import search_aldi
from walmart_service import search_walmart
from project.app.unit_conversion import compare_prices

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
    costco_results = search_costco(search_term)
    metro_results = search_metro_market(search_term)
    aldi_results = search_aldi(search_term)
    #walmart_results = search_walmart(search_term)

    # Combine the results into a dictionary
    return {
        'costco': costco_results,
        'metro': metro_results,
        'aldi': aldi_results,
        #'walmart': walmart_results
    }

@app.route('/fetch-prices/costco', methods=['GET'])
def costco_prices():
    search_term = request.args.get("search", "").lower()
    results = search_costco(search_term)
    print(f"\nCostco Results:\n{results}")
    return jsonify(results)

@app.route('/fetch-prices/metro', methods=['GET'])
def metro_prices():
    search_term = request.args.get("search", "").lower()
    results = search_metro_market(search_term)
    print(f"\nMetro Results:\n{results}")
    return jsonify(results)

"""@app.route('/fetch-prices/aldi', methods=['GET'])
def aldi_prices():
    search_term = request.args.get("search", "").lower()
    results = search_aldi(search_term)
    print(f"\nAldi Results:\n{results}")
    return jsonify(results)"""

@app.route('/fetch-prices/walmart', methods=['GET'])
def walmart_prices():
    search_term = request.args.get("search", "").lower()
    results = search_walmart(search_term)
    print(f"\nWalmart Results: {results}")
    return jsonify(results)

@app.route('/compare', methods=['GET'])
def compare():
    product_id = request.args.get('product_id')
    if not product_id:
        return jsonify({"error": "Product ID is required"}), 400

    search_term = request.args.get('search', "").lower()  # You can pass search term directly if needed

    # Get the prices from all stores
    prices_data = get_prices_from_stores(search_term)
    
    # Now, pass the fetched data to your comparison service
    result = compare_prices(prices_data, product_id)
    
    if "error" in result:
        return jsonify(result), 404
    
    return jsonify(result)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
