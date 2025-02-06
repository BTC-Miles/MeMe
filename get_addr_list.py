import asyncio
import requests
import json
import logging
import heapq
import time
import os
import aiohttp
from dotenv import load_dotenv
from solders.pubkey import Pubkey
from solana.rpc.async_api import AsyncClient
from solana.rpc.api import Client
from redis_db import write_vip

load_dotenv(override=True)
URL = os.getenv('SOLSCAN_API_URL')
API_KEY = os.getenv('API_KEY')
TOP_ADDR = os.getenv('TOP_ADDR')
SOL_URL = os.getenv('SOL_URL')
MAX_RETRIES = os.getenv('MAX_RETRIES')
RECEIVE_ADDRESS = os.getenv('RECEIVE_ADDRESS')
VIP_M = os.getenv("VIP_M")
VIP_S = os.getenv("VIP_S")
VIP_Y = os.getenv("VIP_Y")
BALANCE_CONSTANT = os.getenv("BALANCE_CONSTANT")
print('SOL_URL',SOL_URL)

logging.basicConfig(level=logging.ERROR,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    filename='app.log',
                    filemode='a')

# addrInfo =  []
async def get_addr_list(address):
    tasks=[]
    retries=0
    getProgramAccountsPayload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getProgramAccounts",
        "params": [
            "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA", 
            {
                "encoding": "jsonParsed",
                "filters": [
                    {"dataSize": 165},
                    {
                        "memcmp": {
                            "offset": 0,
                            "bytes": address
                        }
                    }
                ]
            }
        ]
    }
    getProgramAccountsPayload2022 = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getProgramAccounts",
        "params": [
            "TokenzQdBNbLqP5VEhdkAS6EPFLC1PHnBqCXEpPxuEb",
            {
                "encoding": "jsonParsed",
                "filters": [
                    {"dataSize": 165},
                    {
                        "memcmp": {
                            "offset": 0,
                            "bytes": address
                        }
                    }
                ]
            }
        ]
    }
    headers = {
        "Content-Type": "application/json"
    }
    try:
        while retries < int(MAX_RETRIES) :
            response = requests.post(SOL_URL, headers=headers, data=json.dumps(getProgramAccountsPayload))
            if response.status_code != 200:
                print(f"Error fetching address list1: {response.status_code}")
                retries += 1
                time.sleep(1)
            elif response.json().get('result')!=[]:
                break
            response = requests.post(SOL_URL, headers=headers, data=json.dumps(getProgramAccountsPayload2022))
            if response.status_code != 200:
                    print(f"Error fetching address list2: {response.status_code}")
                    retries += 1
                    time.sleep(1)        
            else:
                break
        # if response.status != 200:
        tokenHolder = response.json().get('result')
       
        
        holder_list = []
        
        for i in range(len(tokenHolder)):
        
            balance = tokenHolder[i]["account"]['data']["parsed"]['info']['tokenAmount']['amount']
            owner = tokenHolder[i]["account"]['data']["parsed"]['info']['owner']
            
            if balance:
                holder_list.append((int(balance), tokenHolder[i]['pubkey'],owner)) 
        
        top_100 = heapq.nlargest(100, holder_list)

    except Exception as e:
        print(f"Error fetching address  {e}")
        return 500, f"Error fetching address list"    
    addrInfo,caculation = await get_balance(top_100,address)
    msg = {
        'caculation':f'{caculation}',
        'addrInfo':f'{addrInfo}'
    }
        
    return 200,msg

async def get_balance(addrList,tokenAddr):
        addrInfo = []
        key = []
        tasks = []
        totalbuy = 0
        totalsell = 0
        try:
            client = AsyncClient(SOL_URL)
            
            for balance,address,owner in addrList:
                key.append(Pubkey.from_string(owner))
    
            balance_sol=await client.get_multiple_accounts(key)

            for address_info,account in zip(addrList,balance_sol.value):
             
                if owner == '5Q544fKrFoe6tsEbD7S8EmxGTJYAKtTVhAW5Q5pge4j1':
                    addr_info = {
                        'address': 'Raydium Authority V4',
                        'owner' : 'Raydium Authority V4',
                        'solAmount': account.lamports,
                        'amount': address_info[0],
                        'symbol' : 0
                    }
                elif account is None:
                    addr_info = {
                    'address': address_info[1],
                    'owner': address_info[2],
                    'solAmount': 0,
                    'amount': address_info[0],
                    }
                else:
                    addr_info = {
                        'address': address_info[1],
                        'owner': address_info[2],
                        'solAmount': round(int(float(account.lamports))/(10**9),3),
                        'amount': address_info[0],
                    }
                tasks.append(buy_or_sell(tokenAddr, address_info[2], addr_info,totalbuy,totalsell))
                
               
                addrInfo.append(addr_info)
            caculation = get_caculate_result(totalbuy,totalsell)
            await asyncio.gather(*tasks)
            return addrInfo,caculation
        except Exception as e:
            print(f"Error fetching balance for {address}: {e}")
            return 500, f"Error fetching balance "

async def buy_or_sell(address,owner,addr_info,totalbuy,totalsell):
    buy=0
    sell=0
   # TODO: change the url to the node url
    url= f'{URL}token/defi/activities?address={owner}&from={owner}&activity_type[]=ACTIVITY_TOKEN_SWAP&token={address}'
    headers = {"token": API_KEY}
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            if response.status == 200:
                try:
                    data = await response.json()
                 
                    if not data['data']:
                        return 
                    for tokenData in data['data']:
                      
                        if tokenData['routers']['token1'] == 'So11111111111111111111111111111111111111112':
                            buy +=1
                        else:
                            sell +=1
                    addr_info['buy']=buy
                    addr_info['sell']=sell
                    totalbuy =+ buy
                    totalsell =+ sell
                except Exception as e:
                    print(f"Failed to get trade  for {address}: {e}")
            else:
                print(f"Failed to get trade  for {address}, status code: {response.status}")

async def get_caculate_result(totalbuy,totalsell):
    if totalbuy>1.5*totalsell:
        return 1
    if 2*totalbuy<totalsell:
        return 2
    if totalsell>totalbuy and totalbuy>0.5*totalsell:
        return 3
    if totalbuy>totalsell:
        return 4
    if totalbuy>2*totalsell:
        return 5

async def get_user_transactions(address):
    url = f"{URL}account/transactions?address={address}&limit=40"
    headers = {"token": API_KEY}
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            if response.status == 200:
                try:
                    raw_text = await response.text()
                    data = await response.json()
                    if not isinstance(data.get("data"), list) or not data["data"]:
                        return 200, "no data found"
                    for signer in data["data"]:
                        if isinstance(signer.get("signer"), list) and address in signer["signer"]:
                            status, message = await judge_transaction_details(address, signer["tx_hash"])
                            return status, message
                    return 200, "No matching transactions"
                except aiohttp.ContentTypeError as e:
                    logging.error(f"Response is not JSON: {e}")
                    return 500, "Response is not valid JSON"
                except Exception as e:
                    logging.error(f"An error occurred while parsing data: {e}")
                    return 500, "Error fetching user transactions data"
            else:
                logging.error(f"Failed to fetch transactions: {response.status}")
                return response.status, "Error from server"
    return 500, "Unexpected error"

async def judge_transaction_details(singer_address, tx_hash):
    url = f"{URL}transaction/detail?tx={tx_hash}"    
    headers = {"token": API_KEY}
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            if response.status == 200:
                try:
                    # 打印原始响应内容
                    raw_text = await response.text()
                    
                    # 解析 JSON 数据
                    raw_data = await response.json()
                    if "data" not in raw_data or not raw_data["data"]:
                        return 200, "no data found"
                    
                    data = raw_data.get("data", {})
                    sol_bal_change = data.get("sol_bal_change", [])
                    print(f"sol_bal_change: {sol_bal_change}")
                    print(f"RECEIVE_ADDRESS: {RECEIVE_ADDRESS}")

                    for entry in data.get("sol_bal_change", []):
                        #print(f"Checking entry: {entry}")
                        if entry.get("address") == RECEIVE_ADDRESS:
                            receive_balance = float(entry.get("change_amount"))
                            print(f"Match found: {receive_balance}")
                            receive_amount = receive_balance / 1000000000
                            print(f"Calculated receive_amount: {receive_amount}")
                            if receive_amount == float(VIP_M):
                                status,mssage = await write_vip(singer_address, 31,tx_hash)
                                logging.info(f"{singer_address} input value {receive_amount}, update a month")
                                msg = {
                                    'status':status,
                                    'info':mssage
                                }
                                return 200,msg
                            elif receive_amount == float(VIP_S,):
                                status,mssage = await write_vip(singer_address, 93,tx_hash)
                                logging.info(f"{singer_address} input value {receive_amount}, update a season")
                                msg = {
                                    'status':status,
                                    'info':mssage
                                }
                                return 200,msg
                            elif receive_amount == float(VIP_Y):
                                status,mssage = await write_vip(singer_address, 365,tx_hash)
                                logging.info(f"{singer_address} input value {receive_amount}, update a year")
                                msg = {
                                    'status':status,
                                    'info':mssage
                                }
                                return 200,msg
                            else:
                                logging.info(f"{singer_address} input value {receive_amount}, update Fail")
                                msg = {
                                    'status':False,
                                    'info':"sol amount error, update fail"
                                }
                                return 500, msg
                except Exception as e:
                    raw_text = await response.text()
                    logging.error(f"Failed to update VIP time: {e}, Response: {raw_text}")
                    msg = {
                            'status':False,
                            'info':"sol amount error, update fail"
                                }
                    return 500, msg
            else:
                logging.error(f"Failed to fetch transaction details: {response.status}")
                msg = {
                        'status':False,
                        'info':"sol amount error, update fail"
                        }
                return response.status, msg
    msg = {
            'status':False,
            'info':"Unexpected error"
            }       
    return 500, msg