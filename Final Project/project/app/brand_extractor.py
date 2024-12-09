import difflib
import re
from collections import Counter

class BrandExtractor:
    def __init__(self):
        
        self._default_brands = {'Roundy', 'Kroger', 'Simple Truth Organic', # Metro/Kroger/Pick n Save
                               'Great Value', # Walmart
                               'Kirkland Signature', # Costco
                               'Trader Joe', # Trader Joe's
                               'Good & Gather', # Target
                               'Simply Nature' # Aldi
        }
        
        
        # Predefined list of known brands (this would be much more extensive in a real implementation)
        self._known_brands = {
            # Fresh Produce Brands
            'Dole', 'Chiquita', 'Driscoll\'s',  # Known fresh fruit and vegetable brands

            # Condiments and Sauces
            'Heinz', 'Hunt\'s', 'Kraft Heinz', 'Campbell\'s', 'Prego', 'Ragu', 'Barilla', 'Taco Bell',  # Sauces, ketchup, and condiments

            # Frozen Food
            'Stouffer\'s', 'Amy\'s', 'Lean Cuisine',  # Popular frozen food brands

            # Chips and Snacks
            'Lay\'s', 'Doritos', 'Pringles', 'Frito-Lay', 'Ritz', 'Triscuit', 'Wheat Thins', 'Nilla',  # Chips, crackers, and snacks

            # Dairy and Dairy Alternatives
            'Organic Valley', 'Horizon', 'Breyers', 'Ben & Jerry\'s', 'Sargento', 'Tillamook', 'Almond Breeze', 'fairlife',
            'Lactaid', 'Oatsome', 'TruMoo', 'Silk', 'So Delicious', 'Califia Farms', 'Ripple', 'Elmhurst', 'Mooala', # Dairy and plant-based options

            # Cereals and Breakfast Foods
            'Quaker', 'General Mills', 'Nature Valley', 'Pillsbury', 'Kellogg\'s', 'Post', 'Cheerios', 'Cinnamon Toast Crunch', 
            'Lucky Charms', 'Nature\'s Path', 'Bob\'s Red Mill', 'Belvita',  # Breakfast cereals and granola bars

            # Beverages (Non-Energy)
            'Coca-Cola', 'Pepsi', 'Nestle', 'Unilever', 'Tropicana', 'Minute Maid', 'Snapple', 'V8', 'Pure Leaf', 
            'Capri Sun', 'Sprite', 'Mountain Dew', 'Fanta', 'Mello Yello', 'Barq\'s', 'Sunkist', 'Canada Dry', 'Schweppes', 
            'Seagram\'s', 'Smartwater', 'Dasani', 'Evian', 'Perrier', 'San Pellegrino', 'Fiji', 'Voss', 'Core', 'Essentia', 
            'Deer Park', 'Poland Spring', 'Crystal Geyser', 'Nestle Pure Life',  # Popular sodas, waters, and juices

            # Energy Drinks
            'Red Bull', 'Gatorade', 'Ghost Hydration', 'Bang', 'Monster', 'Rockstar', 'Celsius', 'Guru', 'Xyience', 'NOS', 
            'Full Throttle', 'Vitamin Water', 'Propel', 'Powerade', 'BodyArmor',  # Well-known energy drink brands

            # Meat and Protein Products
            'Smithfield', 'Oscar Mayer', 'Tyson', 'Hormel', 'Blue Diamond', 'Blue Sky Farms', 'Great Day Farms', 'Phil\'s Free Range', 
            'Eggland\'s Best', 'Happy Egg Co.', 'Just Crack an Egg', 'Herb\'s Pickled Eggs', 'Kemps Select', 'Patrick\'s Best Garden', 
            'Amish Wedding', 'Mott\'s',  # Known brands for meat, eggs, and protein-rich foods

            # Snacks and Candy
            'Oreo', 'Chips Ahoy', 'Skittles', 'Starburst', 'M&M\'s', 'Twix', 'Snickers', 'Milky Way', '3 Musketeers', 'Dove', 
            'Galaxy', 'Bounty', 'Lindt', 'Ghirardelli', 'Godiva', 'Ferrero', 'Kinder', 'Tic Tac', 'Breath Savers', 'Altoids', 
            'Life Savers', 'Creme Savers', 'Big League Chew', 'Ice Breakers', 'Juicy Fruit', 'Doublemint', 'Hubba Bubba',  # Cookies, candy, and chewing gum

            # Household Products
            'Clorox', 'Scott', 'Tide', 'Arm & Hammer', 'Johnson & Johnson', 'OxiClean', 'Lysol', 'Colgate', 'Gillette',  # Common cleaning and hygiene products

            # Health and Nutrition
            'Pure Protein', 'Premier Protein', 'Muscle Milk', 'Orgain', 'Ensure', 'Boost', 'Glucerna', 'SlimFast', 'Atkins', 'Quest', 
            'Clif', 'Luna', 'Kind', 'RXBAR', 'Larabar',  # Protein and meal replacement brands

            # Ready-to-Eat Meals and Packaged Foods
            'Roundy\'s', 'Simple Truth', 'Great Value', 'Kraft', 'Bimbo', 'Breyers', 'Jif', 'Skippy', 'Pillsbury', 'Tropicana', 
            'Minute Maid', 'Smithfield', 'Oscar Mayer', 'Tyson', 'Hormel', 'Blue Diamond', 'Nature Valley', 'Bob\'s Red Mill', 'Sweet Baby Ray\'s', # Packaged foods and ready meals

            # Water and Hydration
            'Glaceau', 'Smartwater', 'Dasani', 'Evian', 'Perrier', 'San Pellegrino', 'Fiji', 'Voss', 'Core', 'Essentia', 'Deer Park',
            'Poland Spring', 'Nestle Pure Life',  # Bottled water brands

            # Eggs
            'Vital Farms', 'Pete and Gerry\'s', 'Chino Valley Ranchers', 'Nellie\'s Free Range', 'Dutch Farms'  # Egg brands
            
            # Miscellaneous
            'Frito-Lay', 'Taco Bell', 'Prego', 'Ragu', 'Barilla',  # Various miscellaneous snack or fast food-related brands
        }
        
                  

        # Generic terms to filter out during brand extraction
        self._generic_terms = set([
            # Size and quantity
            'large', 'small', 'medium', 'extra', 'jumbo', 'count', 'ct', 'pack', 
            
            # Quality descriptors
            'organic', 'natural', 'free', 'cage', 'pasture', 'raised', 
            'classic', 'premium', 'select', 'choice', 'best', 'quality', 'grade', 
            
            # Food characteristics
            'brown', 'white', 'fresh', 'frozen', 'whole', 'low', 'fat', 
            'gluten', 'vegan', 'vegetarian', 
            
            # Processing terms
            'boiled', 'dried', 'pickled', 'canned', 'sliced', 'chopped',
            
            # Nutritional and dietary terms
            'keto', 'paleo', 'low-carb', 'sugar-free', 'no-salt', 'low-sodium'
        ])
    
    def _is_known_brand(self, potential_brand):
        """Check if the potential brand is in our known brands list"""
        return any(
            difflib.SequenceMatcher(None, potential_brand.lower(), known.lower()).ratio() > 0.8
            for known in self._known_brands
        )
    
    def _statistical_brand_detection(self, product_names):
        """
        Use statistical analysis to identify potential brands
        Looks at the frequency of initial words across multiple product names
        """
        # Extract first words from product names
        first_words = [name.split()[0] for name in product_names]
        
        # Count frequency of first words
        word_counts = Counter(first_words)
        
        # Filter out known generic terms and single letter words
        potential_brands = {
            word for word, count in word_counts.items() 
            if word.istitle() and 
               word.lower() not in self._generic_terms and 
               len(word) > 1
        }
        
        return potential_brands
    
    def extract_brand(self, product_name, context_brands=None):
        """
        Multi-step brand extraction
        1. Check against known brands
        2. Use statistical context if available
        3. Use intelligent word selection
        """
        # Normalize the product name
        product_name = product_name.strip()
        
        # First, check for exact matches with known brands
        for known_brand in self._known_brands:
            if known_brand.lower() in product_name.lower():
                return known_brand
        
        # Split the product name into words
        words = product_name.split()
        
        # Check the first few words (1-3) for potential brand names
        for i in range(1, min(4, len(words) + 1)):
            potential_brand = ' '.join(words[:i])
            
            # Criteria for a potential brand:
            # 1. All words are capitalized
            # 2. Not just a generic term
            # 3. Not too long
            if (not any(generic in potential_brand.lower() for generic in self._generic_terms) and
                len(potential_brand) < len(product_name) / 2):
                
                # If context brands are provided, use them for additional validation
                if context_brands:
                    # Check similarity with context brands
                    if any(difflib.SequenceMatcher(None, potential_brand.lower(), ctx.lower()).ratio() > 0.7
                           for ctx in context_brands):
                        return potential_brand
                else:
                    return potential_brand
        
        # If no brand found, return None
        return "No Brand"
    
    def extract_brands_from_dataset(self, product_names):
        """
        Extract brands from a larger dataset of product names
        """
        # Use statistical analysis to identify potential brands
        statistical_brands = self._statistical_brand_detection(product_names)
        
        # Extract brands for each product
        brands = {}
        for product in product_names:
            brand = self.extract_brand(product, context_brands=statistical_brands)
            if brand:
                brands[product] = brand
        
        return brands

"""# Example usage
extractor = BrandExtractor()

# Test with multiple product lists
metro_products = [item['name'] for item in metro_results]
walmart_products = [item['name'] for item in walmart_results]

# Extract brands from both datasets
metro_brands = extractor.extract_brands_from_dataset(metro_products)
walmart_brands = extractor.extract_brands_from_dataset(walmart_products)

# Print results
print("Metro Brands:")
for product, brand in metro_brands.items():
    print(f"{product} with Brand\t: {brand}")

print("\nWalmart Brands:")
for product, brand in walmart_brands.items():
    print(f"{product} with Brand\t: {brand}")"""