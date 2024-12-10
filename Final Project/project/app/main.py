from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from functools import wraps
import os
import uuid
from datetime import datetime, timedelta
from scraping_service import search_metro_market, search_walmart
from product_comparator import ProductComparator

app = Flask(__name__)
CORS(app)

# Simple API key management with more lenient defaults
class APIKeyManager:
    def __init__(self):
        self.api_keys = {
            'default_key': {
                'name': 'Default User',
                'created_at': datetime.now(),
                'expires_at': datetime.now() + timedelta(days=365),
                'request_count': 0
            }
        }
    
    def validate_key(self, api_key):
        """
        Validate and track API key usage
        
        Args:
            api_key (str): API key to validate
        
        Returns:
            bool: Whether the key is valid
        """
        if api_key not in self.api_keys:
            return False
        
        key_info = self.api_keys[api_key]
        
        # Check expiration
        if datetime.now() > key_info['expires_at']:
            return False
        
        # Increment request count
        key_info['request_count'] += 1
        
        return True
    
    def generate_key(self, name='User', days_valid=365):
        """
        Generate a new API key
        
        Args:
            name (str): Name associated with the key
            days_valid (int): Number of days the key is valid
        
        Returns:
            str: Generated API key
        """
        new_key = str(uuid.uuid4())
        self.api_keys[new_key] = {
            'name': name,
            'created_at': datetime.now(),
            'expires_at': datetime.now() + timedelta(days=days_valid),
            'request_count': 0
        }
        return new_key

# Initialize API key manager
api_key_manager = APIKeyManager()

def require_api_key(func):
    """
    Decorator to require and validate API key
    """
    @wraps(func)
    def decorated_function(*args, **kwargs):
        # Try getting API key from header, query param, or use default
        api_key = (
            request.headers.get('X-API-Key') or 
            request.args.get('api_key') or 
            'default_key'
        )
        
        if not api_key_manager.validate_key(api_key):
            return jsonify({
                'error': 'Invalid or expired API key',
                'message': 'Please provide a valid API key'
            }), 401
        
        return func(*args, **kwargs)
    return decorated_function

# Serve frontend HTML file
@app.route('/')
def index():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'frontend.html')

def get_prices_from_stores(search_term):
    """
    Fetch prices from Metro Market and Walmart
    
    Args:
        search_term (str): Product to search
    
    Returns:
        tuple: Metro and Walmart search results
    """
    metro_results = None
    walmart_results = None
    
    try:
        metro_results = search_metro_market(search_term)
        if metro_results is None:
            raise ValueError(f"No results found for Metro Market for '{search_term}'")
    except Exception as e:
        app.logger.error(f"Metro Market search failed for '{search_term}': {e}")
    
    try:
        walmart_results = search_walmart(search_term)
        if walmart_results is None:
            raise ValueError(f"No results found for Walmart for '{search_term}'")
    except Exception as e:
        app.logger.error(f"Walmart search failed for '{search_term}': {e}")
        walmart_results = None  # Handle failure and return None or fallback data
        
    return metro_results, walmart_results

@app.route('/compare', methods=['GET'])
@require_api_key
def compare():
    """
    Compare prices between Metro Market and Walmart
    
    Returns:
        JSON: Comparison results
    """
    USAGE_STATS['total_requests'] += 1
    search_term = request.args.get('search', "").lower()
    
    # Validate search term
    if not search_term:
        return jsonify({
            'error': 'Missing search term',
            'message': 'Please provide a search term'
        }), 400
    
    metro_results, walmart_results = get_prices_from_stores(search_term)
    
    if metro_results is None:
        return jsonify({
            'error': 'No results found for metro market for the search term ' + search_term,
            'message': 'No results found for metro market for the search term ' + search_term
        }), 404
        
    if walmart_results is None:
        return jsonify({
            'error': 'No results found for walmart for the search term ' + search_term,
            'message': 'No results found for walmart for the search term ' + search_term
        }), 404
        
    comparisons = ProductComparator.find_best_matches(metro_results, walmart_results)
    
    return jsonify(comparisons)

@app.route('/generate-key', methods=['GET'])
def generate_api_key():
    """
    Generate a new API key
    
    Returns:
        JSON: Generated API key details
    """
    name = request.args.get('name', 'User')
    days = int(request.args.get('days', 365))
    
    new_key = api_key_manager.generate_key(name, days)
    
    return jsonify({
        'api_key': new_key,
        'name': name,
        'valid_days': days
    })


# Simple usage tracking
USAGE_STATS = {
    'total_requests': 0,
    'endpoints': {
        '/admin/usage': {'count': 0}
    }
}

@app.route('/admin/usage')
def get_usage_stats():
    USAGE_STATS['total_requests'] += 1
    USAGE_STATS['endpoints']['/admin/usage']['count'] += 1
    return jsonify(USAGE_STATS)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)