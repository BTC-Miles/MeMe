import time
from dotenv import load_dotenv
import os
import requests
import asyncio
import aiohttp

load_dotenv()
URL = os.getenv('SOLSCAN_API_URL')
API_KEY = os.getenv('API_KEY')
TOP_ADDR = os.getenv('TOP_ADDR')
URL = os.getenv('SOLSCAN_API_URL')
QUCIK_URL = os.getenv('QUCIK_URL')
MIST_URL = os.getenv('MIST_URL')
CONCURRENT_REQUESTS_LIMIT = 100
MAX_RETRIES = os.getenv('MAX_RETRIES')

def get_addr_label(address):
    url=f"{MIST_URL}{address}"
    try:
        response = requests.get(url)
        data = response.json()
        print("data : ",data)
        return data['data']['label_type']
    except Exception as e:
        print(f"Error fetching address: {address} label: {e}")
        return 'unknown'

async def find_sol_track(address,addrInfo,owner_to_from_map,session,semaphore): 
    if address == 'Raydium Authority V4':
        return 
    url = URL+"account/transfer/export?address="+address+"&amount[]=0.000001&token=So11111111111111111111111111111111111111111&flow=in"    
    
    headers = {"token": API_KEY}
    # response = requests.get(url, headers=headers)
 
    async with session.get(url, headers=headers) as response:
            retries = 0
            while retries < int(MAX_RETRIES) :
                if response.status != 200:
                    print(f"Failed to fetch data for {address}, status code: {response.status}")
                    retries += 1
                    await asyncio.sleep(1)
                else:
                    break
            try:
                # get the last transaction
                lines = await response.text() 
                lines = lines.strip().split("\n")
                if len(lines) < 2:
                    
                    owner_to_from_map[address] = set()
                    return owner_to_from_map
                lines = lines[1:2] # only get the last transaction

                fields = lines[0].split(",")  
                #  print("fields : ",fields)
                from_address = fields[3]  
                # Update the map with the 'from' address for this 'owner'
                if address not in owner_to_from_map:
                    owner_to_from_map[address] = set()
                owner_to_from_map[address].add(from_address)

            except Exception as e:
                print(f"Error fetching data for {address}: {e}")
                return owner_to_from_map

async def find_link(addrInfo):
    owner_to_from_map = {}
    try:
        async with aiohttp.ClientSession() as session:
            semaphore = asyncio.Semaphore(CONCURRENT_REQUESTS_LIMIT)
            tasks = []
            
            for addr in addrInfo:
                owner = addr['owner']
                tasks.append(find_sol_track(owner, addrInfo, owner_to_from_map, session,semaphore))
                
            await asyncio.gather(*tasks)
    except Exception as e :
        print('find_sol_track error',e)
        return 500,'find_sol_track error'
    try:
        from_to_owners_map = {}
        for owner, from_addresses in owner_to_from_map.items():
            for from_address in from_addresses:
                if from_address not in from_to_owners_map:
                    from_to_owners_map[from_address] = set()
                from_to_owners_map[from_address].add(owner)
    
        from_address_symbol_map = {}
        symbol_counter = 1  # To assign unique symbol IDs
        for from_address, owners in from_to_owners_map.items():
            if len(owners) > 1:  # More than one owner sharing this 'from' address
                from_address_symbol_map[from_address] = symbol_counter
                symbol_counter += 1

        # Now we add 'from' address and 'symbol' to addrInfo
        for addr in addrInfo:
            owner = addr['owner']
            # Get the 'from' address for the current owner
            from_address = next(iter(owner_to_from_map.get(owner, [])), None)
            addr['from'] = from_address
            # If the 'from' address is shared, add the symbol
            addr['symbol'] = from_address_symbol_map.get(from_address, 0)  # Default to 0 if no symbol is assigned
    except Exception as e :
        print("trace link eccor :",e)
        return 500,'trace link eccor'

    return 200,addrInfo