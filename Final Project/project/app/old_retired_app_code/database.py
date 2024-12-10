import json
import os

def get_prices():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    prices_path = os.path.join(base_dir, "prices.json")  # Correct path to the prices.json file
    
    with open(prices_path, "r") as file:
        return json.load(file)
