from locust import HttpUser, task, between
import random

class PriceComparisonUser(HttpUser):
    # Wait time between tasks (simulates realistic user behavior)
    wait_time = between(1, 3)

    # List of sample search terms to simulate realistic queries
    search_terms = [
        'milk', 'bread', 'eggs', 'cheese', 'chicken', 
        'apple', 'banana', 'toilet paper', 'water', 
        'coffee', 'pasta', 'rice', 'cereal'
    ]

    @task
    def compare_prices(self):
        """
        Simulate price comparison requests
        """
        search_term = random.choice(self.search_terms)
        
        # Simulate API key usage
        self.client.get(
            f"/compare", 
            params={
                'search': search_term, 
                'api_key': 'default_key'
            },
            name="/compare"  # Aggregate similar requests in reports
        )

    @task(1)  # Lower weight for admin endpoint
    def check_usage_stats(self):
        """
        Periodically check usage statistics
        """
        self.client.get(
            "/admin/usage", 
            params={'api_key': 'default_key'},
            name="/admin/usage"
        )