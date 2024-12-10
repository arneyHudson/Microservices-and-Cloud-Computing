import re
import difflib
from brand_extractor import BrandExtractor

class ProductComparator:
    
    
    # Consolidated list of default/parent brands
    DEFAULT_BRANDS = {
        'Roundy': ['Roundy', 'Metro'],
        'Kroger': ['Kroger', 'Ralph\'s', 'Fred Meyer'],
        'Great Value': ['Great Value', 'Walmart'],
        'Simple Truth': ['Simple Truth', 'Kroger'],
        'Kirkland Signature': ['Kirkland Signature', 'Costco'],
        'Trader Joe': ['Trader Joe', 'Trader Joe\'s'],
        'Good & Gather': ['Good & Gather', 'Target'],
        'Simply Nature': ['Simply Nature', 'Aldi']
    }

    # Expanded unit conversion dictionary
    UNIT_CONVERSIONS = {
        'gallon': {
            'gallon': 1,
            'gallons': 1,
            'gal': 1,
            'gal.': 1,
            '1 gallon': 1,
            'half gallon': 0.5,
            '1/2 gallon': 0.5,
            '1/2 gal': 0.5,
            'quart': 4,
            'qts': 4,
            'pt': 8,
            'pint': 8,
            'oz': 128,
            'ounce': 128,
            'oz.': 128,
            'ounces': 128,
            'fl oz': 128,
            'fluid ounce': 128,
            'fluid ounces': 128,
            'liter': 3.78541,
            '1/2 liter': 7.57082,
        }, 
        '1/2 gallon': {
            'gallon': 0.5,
            'gallons': 0.5,
            'gal': 0.5,
            'gal.': 0.5,
            '1 gallon': 0.5,
            'half gallon': 1,
            '1/2 gallon': 1,
            '1/2 gal': 1,
            'quart': 2,
            'qts': 2,
            'pt': 4,
            'pint': 4,
            'oz': 64,
            'fl oz': 64,
            'fluid ounce': 64,
            'fluid ounces': 64,
            'liter': 1.89271,
            '1/2 liter': 3.78541,
        },
        'liter': {
            'liter': 1,
            'liters': 1,
            'l': 1,
            '1 liter': 1,
            'half liter': 0.5,
            '1/2 liter': 0.5,
            'milliliter': 1000,
            'ml': 1000,
            'centiliter': 100,
            'cl': 100,
            'deciliter': 10,
            'dl': 10
        },
        'pound': {
            'pound': 1,
            'lbs': 1,
            'lb': 1,
            'kilogram': 2.20462,  # 1 kg = 2.20462 pounds
            'kg': 2.20462,
            'ounce': 16,
            'oz': 16,
            'ounces': 16
        }
    }

    @classmethod
    def convert_unit(cls, quantity, from_unit, to_unit):
        """
        Convert a given quantity from one unit to another (e.g., gallon to pint).
        
        Args:
            quantity (float): The quantity to convert
            from_unit (str): The unit to convert from
            to_unit (str): The unit to convert to
        
        Returns:
            float: The converted quantity
        """
        # Normalize the units (lowercase and without spaces)
        from_unit = from_unit.lower().strip()
        to_unit = to_unit.lower().strip()

        # Search for base units (gallon, liter, etc.) in the conversion dictionary
        for base_unit, conversions in cls.UNIT_CONVERSIONS.items():
            if from_unit in conversions and to_unit in conversions:
                conversion_factor = conversions[to_unit] / conversions[from_unit]
                return quantity * conversion_factor
        return quantity  # Return the original quantity if no conversion found
    
    @staticmethod
    def extract_unit_and_quantity(product_name):
        """
        Extract the quantity and unit from the product name, supporting multiple variations of units.
        """
        unit_patterns = '|'.join([r'1/2 gallon', r'half gallon',  # Explicit fractional patterns
                                  r'gallon', r'gallons', r'gal', r'gal\.','quart', r'qt', 
                                  r'pt', r'pint', r'oz', r'fluid ounce', r'fluid ounces', 
                                  r'fl oz', r'liter', r'liters', r'l', r'milliliter', 
                                  r'ml', r'centiliter', r'cl', r'deciliter', r'dl', 
                                  r'pound', r'lb', r'lbs', r'kilogram', r'kg', r'ounce'])

        # Regex for quantities, prioritizing fractional patterns
        match = re.search(r'((?:\d+/\d+)|(?:\d+\.?\d*))\s*(' + unit_patterns + r')', product_name, re.IGNORECASE)
        if match:
            quantity = match.group(1)
            unit = match.group(2).lower()

            # Convert fractional quantities like '1/2' to decimal
            if '/' in quantity:
                numerator, denominator = map(float, quantity.split('/'))
                quantity = numerator / denominator
            else:
                quantity = float(quantity)

            return quantity, unit
        return None, None

    @classmethod
    def normalize_brand(cls, brand):
        """
        Find the primary brand name for a given brand.
        
        Args:
            brand (str): The brand to normalize
        
        Returns:
            str: The primary brand name or the original brand if not found
        """
        for primary_brand, variants in cls.DEFAULT_BRANDS.items():
            if any(variant.lower() in brand.lower() for variant in variants):
                return primary_brand
        return brand

    @staticmethod
    def extract_count(product_name):
        """
        Extract product count from the name.
        
        Args:
            product_name (str): Name of the product
        
        Returns:
            int: Number of items, or None if not found
        """
        match = re.search(r'(\d+)\s*(?:ct|count|bottles|cans|quantity|pack)', product_name, re.IGNORECASE)
        return int(match.group(1)) if match else 1

    @classmethod
    def calculate_price_per_count_with_conversion(cls, price, quantity, unit, target_unit='gallon', count=None):
        """
        Calculate the price per count, considering unit conversion if necessary.

        Args:
            price (float): Price of the product.
            quantity (float): Quantity of the product.
            unit (str): Unit of the product.
            target_unit (str): Target unit for price per count calculation (default is 'gallon').

        Returns:
            float: Adjusted price per count in the target unit.
        """
        # Convert the quantity to the target unit if necessary
        if unit != target_unit:
            converted_quantity = cls.convert_unit(quantity, unit, target_unit)
            if converted_quantity:  # Only update if conversion is valid
                quantity = converted_quantity
        
        if count:
            quantity *= count

        price_per_count = price / quantity if quantity else float('inf')  # Prevent division by zero
        return price_per_count

    @classmethod
    def calculate_product_similarity(cls, metro, walmart):
        """
        Calculate similarity between two products.

        Args:
            metro (dict): First product details
            walmart (dict): Second product details

        Returns:
            dict: Comparison details including similarity, prices, brands, etc.,
                or None if products cannot be compared.
        """
        # Normalize brands
        brand_extractor = BrandExtractor()
        metro_brand = brand_extractor.extract_brand(metro['name'])
        walmart_brand = brand_extractor.extract_brand(walmart['name'])
        metro_brand = cls.normalize_brand(metro_brand)
        walmart_brand = cls.normalize_brand(walmart_brand)
        
        is_metro_organic = 'organic' in metro['name'].lower()
        is_walmart_organic = 'organic' in walmart['name'].lower()

        # Ensure both products are organic or neither are
        if is_metro_organic != is_walmart_organic:
            return None
        
        # Ensure both are "Chocolate Milk" products or neither are
        if (("Chocolate" in metro['name'] and "Milk" in metro['name']) and 
            not ("Chocolate" in walmart['name'] and "Milk" in walmart['name'])) or \
        (not ("Chocolate" in metro['name'] and "Milk" in metro['name']) and 
            ("Chocolate" in walmart['name'] and "Milk" in walmart['name'])):
            return None
        
        # Extract quantities and units from both products
        
        
        metro_quantity, metro_unit = cls.extract_unit_and_quantity(metro['name'])
        walmart_quantity, walmart_unit = cls.extract_unit_and_quantity(walmart['name'])
        
        
        # Convert the units if necessary
        #if metro_quantity and walmart_quantity:
            #if metro_unit != walmart_unit:
                #metro_quantity = cls.convert_unit(metro_quantity, metro_unit, walmart_unit)

        # Check if both brands are default or non-default
        is_default_metro = metro_brand in cls.DEFAULT_BRANDS
        is_default_walmart = walmart_brand in cls.DEFAULT_BRANDS
        
        # Ensure "No Brand" items are only compared with other "No Brand" items
        if metro_brand == "No Brand" or walmart_brand == "No Brand":
            if metro_brand != walmart_brand:  # Skip comparison if one is "No Brand" and the other is not
                return None
            

        if is_default_metro != is_default_walmart:  # Ensure both are default or both are non-default
            return None  # Skip comparison if one is default and the other is not

        # Remove brand names from product names if both are default brands
        metro_product_name = metro['name']
        walmart_product_name = walmart['name']
        if is_default_metro and is_default_walmart:
            for brand_variant in cls.DEFAULT_BRANDS[metro_brand]:
                metro_product_name = re.sub(re.escape(brand_variant), '', metro_product_name, flags=re.IGNORECASE).strip()
            for brand_variant in cls.DEFAULT_BRANDS[walmart_brand]:
                walmart_product_name = re.sub(re.escape(brand_variant), '', walmart_product_name, flags=re.IGNORECASE).strip()

        # Check brand similarity
        if not (is_default_metro and is_default_walmart):
            brand_similarity = difflib.SequenceMatcher(None, metro_brand, walmart_brand).ratio()
            if brand_similarity < 0.8:  # Skip comparison if brand similarity is below 0.8
                return None
        
        # Extract counts
        count_metro = cls.extract_count(metro_product_name)
        count_walmart = cls.extract_count(walmart_product_name)

        # Calculate price per count
        def calculate_price_per_count(price, count, price_per_gallon=None):
            if count >= 1 and price_per_gallon is not None:
                return price_per_gallon
            if count:  # First check if count is available
                return price / count
            elif price_per_gallon is not None:  # Then check if price per gallon is available
                return price_per_gallon
            else:  # Fallback to the original price
                return price
        
        #print(f"\nMetro Price per Gallon: {price_per_gallon_metro}, metro_quantity: {metro_quantity}, metro_unit: {metro_unit}, metro_price: {metro['price']}")
        #print(f"Walmart Price per Gallon: {price_per_gallon_walmart}, walmart_quantity: {walmart_quantity}, walmart_unit: {walmart_unit}, walmart_price: {walmart['price']}")

        price_per_gallon_metro = cls.calculate_price_per_count_with_conversion(
            metro['price'], metro_quantity, metro_unit, count=count_metro, target_unit='gallon'
        ) if metro_quantity and metro_unit else None

        price_per_gallon_walmart = cls.calculate_price_per_count_with_conversion(
            walmart['price'], walmart_quantity, walmart_unit, count=count_walmart, target_unit='gallon'
        ) if walmart_quantity and walmart_unit else None
        
        price_per_count_metro = calculate_price_per_count(metro['price'], count_metro, price_per_gallon_metro)
        price_per_count_walmart = calculate_price_per_count(walmart['price'], count_walmart, price_per_gallon_walmart)
        
        metro['price_per_count'] = price_per_count_metro
        walmart['price_per_count'] = price_per_count_walmart
        

        # Calculate string similarity (without brand names for default brands)
        name_similarity = difflib.SequenceMatcher(None, metro_product_name, walmart_product_name).ratio()
        brand_similarity = difflib.SequenceMatcher(None, metro_brand, walmart_brand).ratio()

        # Combine similarities
        overall_similarity = (name_similarity + brand_similarity) / 2

        # Adjust similarity based on count
        if count_metro and count_walmart:
            count_similarity = 1 - abs(count_metro - count_walmart) / max(count_metro, count_walmart)
            overall_similarity *= count_similarity

        return {
            'metro': metro,
            'walmart': walmart,
            'similarity': overall_similarity,
            'price_metro': metro['price'],
            'price_walmart': walmart['price'],
            'price_per_count_metro': price_per_count_metro,
            'price_per_count_walmart': price_per_count_walmart,
            'price_difference': abs(metro['price'] - walmart['price']),
            'price_per_count_difference': abs(price_per_count_metro - price_per_count_walmart),
            'metro_brand': metro_brand,
            'walmart_brand': walmart_brand
        }

    @classmethod
    def find_best_matches(cls, metro_results, walmart_results):
        """
        Find the best matches between two sets of products.

        Args:
            metro_results (list): Products from first store
            walmart_results (list): Products from second store

        Returns:
            dict: Best matches for each product
        """
        best_comparison = {}

        for metro_product in metro_results:
            best_match = None
            highest_similarity = 0

            for walmart_product in walmart_results:
                comparison = cls.calculate_product_similarity(metro_product, walmart_product)

                if comparison and comparison['similarity'] > highest_similarity:
                    highest_similarity = comparison['similarity']
                    best_match = comparison

            if best_match:
                best_comparison[metro_product['name']] = best_match

        return best_comparison

    @classmethod
    def print_comparisons(cls, comparisons):
        """
        Print the comparison results in a readable format.
        
        Args:
            comparisons (dict): Best product matches
        """
        for product_name, comparison in comparisons.items():
            print(f"Metro: {comparison['metro']['name']} - ${comparison['metro']['price']}")
            print(f"Walmart: {comparison['walmart']['name']} - ${comparison['walmart']['price']}")
            print(f"Metro Brand: {comparison['metro_brand']}")
            print(f"Walmart Brand: {comparison['walmart_brand']}")
            print(f"Similarity: {comparison['similarity']:.2f}")
            print(f"Price Difference: ${comparison['price_difference']:.2f}")
            print(f"Price per Count Difference: ${comparison['price_per_count_difference']:.2f}")
            print(f"Price per Count Metro: ${comparison['price_per_count_metro']:.2f}")
            print(f"Price per Count Walmart: ${comparison['price_per_count_walmart']:.2f}\n")

"""metro_results = [{'name': 'Horizon Organic Shelf-Stable 1% Low Fat Milk Box - Vanilla 8 fl oz', 'price': 1.79}, {'name': 'Lactaid Lactose Free Whole Milk Half Gallon 1/2 gallon', 'price': 5.29}, {'name': 'Simple Truth Organic 2% Reduced Fat Milk Half Gallon 1/2 gal ', 'price': 4.19}, {'name': 'Simple Truth Organic Vitamin D Whole Milk Half Gallon 1/2 gal ', 'price': 4.19}, {'name': 'Lactaid Lactose Free Chocolate Whole Milk Half Gallon 64 oz', 'price': 5.29}, {'name': 'Kroger Lactose Free 2% Reduced Fat Milk Half Gallon 1/2 gal', 'price': 3.99}, {'name': "Roundy's Select 2% Reduced Fat Milk 1 Gallon", 'price': 2.99}, {'name': "Roundy's Select 2% Reduced Fat Milk 1/2 Gallon", 'price': 1.99}, {'name': 'fairlife Ultra-Filtered Milk, Lactose Free, High Protein, 2% Reduced Fat Milk 52 fl oz', 'price': 5.79}, {'name': 'Kroger CARBmaster Ultra Filtered Skim Vanilla Milk 59 fl oz', 'price': 4.99}, {'name': 'Simple Truth Organic Lactose Free 2% Reduced Fat Milk Half Gallon 1/2 gal', 'price': 4.19}, {'name': 'Horizon Organic Lactose Free 2% Reduced Fat Milk Half Gallon 1/2 gal', 'price': 5.99}, {'name': 'Lactaid Lactose Free Whole Milk 96 fl oz', 'price': 7.29}, {'name': 'Horizon Organic Lowfat Chocolate Milk 12 ct / 8 fl oz', 'price': 15.99}, {'name': 'Horizon Organic Lowfat Chocolate Milk 6 ct / 8 fl oz', 'price': 8.49}, {'name': 'Horizon Organic 1% Lowfat Strawberry Milk 12 ct / 8 fl oz', 'price': 15.99}, {'name': 'fairlife Ultra-Filtered Milk, Lactose Free, High Protein, Whole Milk 52 fl oz', 'price': 5.79}, {'name': 'Horizon Organic DHA Omega-3 Lowfat Chocolate Milk 6 ct / 8 fl oz', 'price': 9.29}, {'name': 'Horizon Organic 1% Lowfat Vanilla Milk 6 ct / 8 fl oz', 'price': 8.49}, {'name': 'Simple Truth Organic 1% Lowfat Chocolate Milk 12 bottles / 8 fl oz', 'price': 10.99}, {'name': 'fairlife Ultra-Filtered Milk, Lactose Free, High Protein, Fat Free Milk 52 fl oz', 'price': 5.79}, {'name': 'Horizon Organic Shelf-Stable 1% Low Fat Milk Box - Chocolate 8 fl oz', 'price': 1.79}, {'name': 'Horizon Organic Shelf-Stable 1% Low Fat Milk Box - Strawberry 8 fl oz', 'price': 1.79}, {'name': 'Horizon Organic Shelf-Stable 1% Low Fat Milk Box - Vanilla 8 fl oz', 'price': 1.79}, {'name': 'Simple Truth Organic Skim Fat Free Milk Half Gallon 1/2 gal ', 'price': 4.19}, {'name': 'Horizon Organic 2% Reduced Fat Milk Half Gallon 1/2 gal', 'price': 5.99}, {'name': 'Organic Valley 2% Reduced Fat Milk Half Gallon 1/2 gal', 'price': 5.79}, {'name': 'Simple Truth Organic 100% Grassfed 2% Reduced Fat Milk Half Gallon 1/2 gal', 'price': 6.29}, {'name': 'Simple Truth Organic 2% Reduced Fat Milk with DHA Omega-3 Half Gallon 1/2 gal', 'price': 4.19}]

walmart_results = [{'name': "Horizon Organic Shelf-Stable Whole Milk Boxes, 8 fl oz, 12 Pack", 'price': 13.98}, {'name': 'Great Value Whole Vitamin D Milk, Gallon, Plastic, Jug, 128 Fl Oz', 'price': 2.66}, {'name': 'Great Value, 2% Reduced Fat Milk, Gallon, Refrigerated', 'price': 2.66}, {'name': 'Great Value Milk Whole Vitamin D, Half Gallon, Plastic, Jug, 64oz', 'price': 1.86}, {'name': 'Great Value Milk, 2% Reduced Fat, Half Gallon, 64 fl oz Jug', 'price': 1.68}, {'name': 'Great Value 1% Low-Fat Milk, 1 Gallon Jug', 'price': 2.66}, {'name': 'Great Value 1% Low-fat Chocolate Milk Gallon, Plastic, Jug, 128 Fl Oz', 'price': 2.66}, {'name': 'Great Value Fat-Free Milk Gallon, Plastic, Jug, 128 Fl Oz', 'price': 2.66}, {'name': 'Great Value Milk 1% Lowfat Half Gallon Plastic Jug', 'price': 1.62}, {'name': 'Kemps Select Whole Milk with Vitamin D - 16 fl oz', 'price': 1.28}, {'name': 'Kemps Select 1% Reduced Fat Milk - Gallon', 'price': 4.12}, {'name': 'Kemps Select 2% Reduced Fat Milk - Gallon', 'price': 4.13}, {'name': 'Kemps Select Whole Milk - Gallon', 'price': 4.53}, {'name': 'Kemps Select Whole Milk with Vitamin D - 32 fl oz', 'price': 2.18}, {'name': 'fairlife Lactose Free 2% Reduced Fat Ultra Filtered Milk, 52 fl oz', 'price': 4.97}, {'name': 'Kemps Select 2% Reduced Fat Milk - 16 fl oz', 'price': 1.28}, {'name': 'Great Value Lactose Free 2% Reduced Fat Milk, Half Gallon, 64 fl oz', 'price': 3.38}, {'name': 'fairlife Lactose Free Fat Free Ultra Filtered Milk, 52 fl oz', 'price': 4.97}, {'name': 'fairlife Lactose Free Ultra Filtered Whole Milk, 52 fl oz', 'price': 4.97}, {'name': 'Great Value Lactose Free Whole Vitamin D Milk, Half Gallon, 64 fl oz', 'price': 3.38}, {'name': 'Kemps Select Fat Free Skim Milk - Gallon', 'price': 3.74}, {'name': 'Great Value Milk, Fat Free, Unflavored, Half Gallon, 64 oz Jug', 'price': 1.62}, {'name': 'Kemps Select Whole Milk with Vitamin D - 64 fl oz', 'price': 2.47}, {'name': 'Great Value 1% Low-fat Chocolate Milk Half Gallon, Plastic, Jug, 64 Fl Oz', 'price': 1.67}, {'name': 'TruMoo Chocolate Whole Milk Half Gallon', 'price': 3.56}, {'name': 'Great Value Organic Whole Vitamin D Milk, Gallon, 128 fl oz', 'price': 6.98}, {'name': 'Kemps Select 1% Lowfat Milk - 64 fl oz', 'price': 2.26}, {'name': 'Oatsome Organic Oat Milk, 1-Liter Carton, 33.8 Fl Oz (Pack of 1)', 'price': 3.67}, {'name': 'Kemps Select Fat Free Skim Milk - 64 fl oz', 'price': 2.0}, {'name': 'Almond Breeze Unsweetened Vanilla Almond Milk, 96 fl oz', 'price': 4.56}, {'name': 'Great Value Organic 2% Reduced Fat Milk, Half Gallon, 64 fl oz', 'price': 3.98}, {'name': 'Great Value Organic Whole Vitamin D Milk, Half Gallon, 64 fl oz', 'price': 3.98}, {'name': 'Almond Breeze Unsweetened Original Almond Milk, 64 oz, Dairy Free, Refrigerated, Cardboard Box', 'price': 3.38}, {'name': 'Lactaid Whole Milk, 96 oz', 'price': 6.38}, {'name': 'Organic Valley, Organic Whole Milk, Grassfed, Half Gallon Carton, 64 oz', 'price': 5.84}]

comparisons = ProductComparator.find_best_matches(metro_results, walmart_results)
ProductComparator.print_comparisons(comparisons)"""
