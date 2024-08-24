


from faker import Faker
from datetime import date

class DateGenerator:
    def __init__(self):
        self.fake = Faker()

    def generate_random_date(self, start_date: str = "-30y", end_date: str = "today") -> date:
        """
        Generates a random date between the start_date and end_date.

        :param start_date: The start date range in Faker's relative date format (e.g., '-30y' for 30 years ago).
        :param end_date: The end date range in Faker's relative date format (e.g., 'today').
        :return: A random date between start_date and end_date.
        """
        return self.fake.date_between(start_date=start_date, end_date=end_date)
        
        
"""

# example_usage.py

from date_generator import DateGenerator

# Create an instance of DateGenerator
date_gen = DateGenerator()

# Generate a random date
random_date = date_gen.generate_random_date()
print(f"Random Date: {random_date}")

# Generate a random date within a specific range
custom_random_date = date_gen.generate_random_date(start_date="-10y", end_date="-5y")
print(f"Custom Random Date: {custom_random_date}")

"""