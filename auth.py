import jwt
import datetime
import redis
import re

# initialize redis
def initialize_redis(wallet,redis_client):
    try:
        if not redis_client.exists(wallet):
            redis_client.set(wallet, "valid")
            print(f"Wallet {wallet} added to Redis.")
    except Exception as e:
        print(f"Error initializing Redis: {e}")

# Read wallet info
def readDB(wallet,redis_client):
    try:
        return redis_client.exists(wallet)
    except Exception as e:
        print(f"Error reading from Redis: {e}")
        return False
    
# Write wallet addr into Redis
def write_to_redis(wallet,redis_client,status="valid"):
    try:
        redis_client.set(wallet, status)
        print(f"Wallet {wallet} written to Redis with status: {status}")
    except Exception as e:
        print(f"Error writing to Redis: {e}")

# search if Wallet in database
def verify_address(wallet,redis_client):
    if not readDB(wallet,redis_client):
        raise ValueError("Wallet address not found in the database")

# generate JWT
def generate_jwt(wallet, is_vip, secret_key):
    try:
        verify_address(wallet)
        payload = {
            'user_id': wallet,
            'is_vip' : is_vip,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1),
            'iat': datetime.datetime.utcnow()
        }
        token = jwt.encode(payload, secret_key, algorithm='HS256')
        print("Generated JWT:", token)
        return token
    except Exception as e:
        print(f"Error generating JWT: {e}")
        return None