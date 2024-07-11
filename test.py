import redis

# Connect to Redis
r = redis.Redis(host='memory', port=6379)

# Sample JSON data
item = {
    "id": 1,
    "name": "Item1",
    "description": "A sample item",
    "price": 10.99
}

# Store the JSON data
r.json().set('item:1', '.', item)

# Set expiration time (in seconds)
r.expire('item:1', 3600)  # Expires in 1 hour

# Retrieve JSON data
retrieved_item = r.json().get('item:1')
print(retrieved_item)
