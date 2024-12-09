# Unit conversion factors to grams
CONVERSION_FACTORS = {
    "gram": 1,
    "g": 1,
    "kilogram": 1000,
    "kg": 1000,
    "milligram": 0.001,
    "mg": 0.001,
    "ounce": 28.3495,
    "oz": 28.3495,
    "pound": 453.592,
    "lb": 453.592,
    "liter": 1000,  # Assume water density (1L = 1kg)
    "litre": 1000,
    "milliliter": 1,  # Assume water density
    "ml": 1
}

def parse_measurements(product_name):
    """Extract the unit, count, and compute the total weight in grams."""
    words = product_name.lower().split()
    total_weight_grams = 0
    count = 1

    # Check for count/pack
    for i, word in enumerate(words):
        if word in ["count", "pack"]:
            try:
                count = int(words[i - 1])  # Assume the number precedes "count" or "pack"
            except (ValueError, IndexError):
                pass

    # Check for unit and size
    for unit, factor in CONVERSION_FACTORS.items():
        if unit in product_name.lower():
            try:
                # Get the numeric value preceding the unit
                size_index = words.index(unit)
                size = float(words[size_index - 1])  # Get the number before the unit
                total_weight_grams = size * factor * count
                break
            except (ValueError, IndexError):
                pass

    return total_weight_grams or None  # Return None if no valid measurement found

def compare_prices(prices_data, product_id):
    """
    Compare prices for a given product_id across different stores.

    :param prices_data: A dictionary with store names as keys and price lists as values.
    :param product_id: The product ID to search for and compare prices.
    :return: A dictionary with comparison results.
    """
    # Combine all product lists into one unified list
    all_products = []
    for store, products in prices_data.items():
        for product in products:
            all_products.append({
                **product,  # Add all the product fields from each store
                'store': store  # Add a field for the store name
            })

    # Find the product by ID in the combined list
    product = next((p for p in all_products if str(p["product_id"]) == str(product_id)), None)
    if not product:
        return {"error": "Product not found"}

    # Get the product name and weight (if possible)
    total_weight_grams = parse_measurements(product["name"])
    if not total_weight_grams:
        return {
            "error": f"Unable to determine total weight for product '{product['name']}'"
        }

    # Calculate the price per gram for each store
    price_per_gram = {}
    for store in prices_data:
        store_price = product.get(f"{store.lower()}_price")
        if store_price:
            price_per_gram[store] = store_price / total_weight_grams

    # Determine the cheapest store
    cheapest_store = min(price_per_gram, key=price_per_gram.get)

    # Prepare the result with the calculations
    result = {
        "product": product["name"],
        "total_weight_grams": round(total_weight_grams, 2),
        "prices_per_gram": {store: round(price, 4) for store, price in price_per_gram.items()},
        "cheaper_store": cheapest_store
    }

    return result