import os
import json
import time
import random
from datetime import datetime
from faker import Faker
from dotenv import load_dotenv
from google.cloud import pubsub_v1

# 1. Load configuration
load_dotenv()
fake = Faker()

# 2. Configuration
PROJECT_ID = os.getenv('GOOGLE_CLOUD_PROJECT')
TOPIC_ID = "globalpay-transactions"

# 3. Initialize Publisher
publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path(PROJECT_ID, TOPIC_ID)

# 4. Mock Data Lists
PSPS = ['Stripe', 'stripe', 'Adyen', 'ADYEN', 'PayPal', 'paypal', 'Square']
PAYMENT_TYPES = ['credit_card', 'debit_card', 'digital_wallet', None] 

# NEW: Merchant List for your Gold Layer analysis
MERCHANTS = [
    ('Starbucks', 'Food & Beverage'),
    ('Amazon', 'E-commerce'),
    ('Apple Store', 'Electronics'),
    ('Shell', 'Gas Station'),
    ('Walmart', 'Retail'),
    ('Steam', 'Gaming'),
    ('Uber', 'Transportation')
]

def generate_transaction():
    """
    Creates a single mock transaction with merchant and geo data.
    """
    # Select a random merchant tuple
    merchant = random.choice(MERCHANTS)
    
    transaction = {
        "transaction_id": fake.uuid4(),
        "timestamp": datetime.utcnow().isoformat(),
        "customer_id": f"CUST-{random.randint(1000, 9999)}",
        "amount": round(random.uniform(10.00, 15000.00), 2), # Increased range to hit your 13k threshold
        "currency": random.choice(['USD', 'EUR', 'GBP']),
        "latitude": float(fake.latitude()),
        "longitude": float(fake.longitude()),
        "psp": random.choice(PSPS),
        "payment_type": random.choice(PAYMENT_TYPES),
        "merchant_name": merchant[0],
        "merchant_category": merchant[1],
        "country": fake.country_code(),
    }
    return transaction

if __name__ == "__main__":
    print(f"Starting stream to {topic_path}...")
    
    while True:
        data = generate_transaction()
        message_bytes = json.dumps(data).encode("utf-8")
        
        try:
            future = publisher.publish(topic_path, message_bytes)
            print(f"Published message ID: {future.result()}")
        except Exception as e:
            print(f"Error publishing: {e}")
        
        # Wait 1 second before sending the next one
        time.sleep(1)