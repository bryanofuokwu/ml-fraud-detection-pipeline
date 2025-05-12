from kafka import KafkaProducer
import json, time, random

producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    value_serializer=lambda x: json.dumps(x).encode('utf-8')
)

user_ids = ['u1', 'u2', 'u3']
countries = ['US', 'GB', 'NG']

while True:
    txn = {
        'user_id': random.choice(user_ids),
        'amount': round(random.uniform(5, 500), 2),
        'timestamp': int(time.time() * 1000),
        'country': random.choice(countries),
        'card_present': random.choice([True, False])
    }
    producer.send('transactions', txn)
    print("Sent:", txn)
    time.sleep(1)
