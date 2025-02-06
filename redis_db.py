import redis
import os
import logging
from dotenv import load_dotenv
from datetime import datetime, timedelta

load_dotenv(override=True)
REDIS_URL = os.getenv("REDIS_URL")
REDIS_PORT = os.getenv("REDIS_PORT")

client = redis.StrictRedis(
    host = REDIS_URL,
    port = REDIS_PORT,
    decode_responses = True
)

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    filename='app.log',
                    filemode='a')

def check_and_extend_vip(address, update_time):
    current_time = datetime.utcnow() + timedelta(hours=8)  # 转换为 UTC+8
    try:
        expiry_str = client.get(address)
    except KeyError:  
        expiry_str = None 
    except Exception as e: 
        logging.error(f"An error occurred: {e}")
        expiry_str = None

    if expiry_str:
        try:
            expiry_time = datetime.fromisoformat(expiry_str) + timedelta(hours=8)  # 转换为 UTC+8
        except ValueError:  
            logging.error(f"Invalid expiry format for address {address}: {expiry_str}")
            expiry_time = current_time  

        if current_time > expiry_time: 
            new_expiry_time = current_time + timedelta(days=update_time)  
        else:
            new_expiry_time = expiry_time + timedelta(days=update_time)  
    else:  
        new_expiry_time = current_time + timedelta(days=update_time)  

    return new_expiry_time

# update vip time
async def write_vip(address, update_time, transaction):
    if not address:
        raise ValueError("Address cannot be empty.")
    
    try:
        transaction_status = client.get(transaction)
        print("transaction_status1:", transaction_status)
    except Exception as e: 
        logging.error(f"An error occurred: {e}")
        transaction_status = None
        print("transaction_status2:", transaction_status)

    if transaction_status == '1':
        print("transaction_status3:", transaction_status)
        return False, "Transfer already exists"
    
    else:
        print("transaction_status4:", transaction_status)
        client.set(transaction, '1')
        new_expiry_time = check_and_extend_vip(address, update_time)
        new_expiry_str = new_expiry_time.isoformat()
        client.set(address, new_expiry_str)
        logging.info(f"VIP expiry time for {address} updated to {new_expiry_str}.")
        return True, f"VIP expiry time for {address} updated to {new_expiry_str}."

async def get_vip_info(address):
    current_time = datetime.utcnow() + timedelta(hours=8)  # 转换为 UTC+8
    vip_status = False
    try:
        expiry_str = client.get(address)
        print('expiry_str:', expiry_str)
    except KeyError:  
        expiry_str = None
        vip_status = False
        vip_info = {
            'vip_status': vip_status,
            'vip_time': None
        }
        return 200, vip_info 
    except Exception as e: 
        logging.error(f"An error occurred: {e}")
        expiry_str = None

    if expiry_str:  
        try:
            expiry_time = datetime.fromisoformat(expiry_str) + timedelta(hours=8)  # 转换为 UTC+8
        except ValueError:  
            logging.error(f"Invalid expiry format for address {address}: {expiry_str}")
            expiry_time = current_time

        if current_time > expiry_time: 
            vip_status = False
            vip_info = {
                'vip_status': vip_status,
                'vip_time': expiry_time
            }
            return 200, vip_info
        if current_time <= expiry_time: 
            vip_status = True
            vip_info = {
                'vip_status': vip_status,
                'vip_time': expiry_time
            }
            return 200, vip_info
    
    vip_info = {
        'vip_status': vip_status,
        'vip_time': None
    }
    print("accdascsad")
    return 200, vip_info
