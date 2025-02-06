import requests
from dotenv import load_dotenv
import os

load_dotenv()
URL = os.getenv('SOLSCAN_API_URL')
API_KEY = os.getenv('API_KEY')
RAYID_URL = os.getenv('RAYID_URL')
GOPLUS_URL = os.getenv('GOPLUS_URL')
burnPercent=0

def get_token_info(address,internal=False):
    #TODO: 10min can get poolInfo from redium,so we consider if the address is pump address,we use 100% burnPercent.This is a temporary solution.
    if address.endswith("pump"):        
        burnPercent=100
        
    urlTokenInfo = URL + "token/meta?address=" + address
    urlRaymint=RAYID_URL+"mint?mint1="+address+"&poolType=all&poolSortField=default&sortType=desc&pageSize=1000&page=1"
    urlSol = URL + "token/markets?token[]="+address+"&page=1&page_size=10"    
    urlGoplus = GOPLUS_URL +address
    headersSol = {"token":API_KEY}
    headersRay = {"accept": "application/json"}
    try:
        responseTokenInfo = requests.get(urlTokenInfo, headers=headersSol)
        tokenInfo = responseTokenInfo.json()['data']
        tokenName = tokenInfo['symbol']
        decimals = tokenInfo['decimals']
        marketCap = tokenInfo['market_cap']
        holder = tokenInfo['holder']
      #  volume24h = tokenInfo['volume_24h']
        
    except Exception as e:
        print("token_info get error",e)
        return 500,"token_info get error"
    try:
        
        responseGoplus = requests.get(urlGoplus, headers=headersRay)
        tokenSupply = responseGoplus.json()['result'][address]
        totalSupply = tokenSupply["total_supply"]

    except Exception as e:
        print("totalSupply get error",e)
        return 500,"totalSupply get error"
    try:
        responseRay = requests.get(urlRaymint,headers=headersRay).json()
        if responseRay['data']==[]:
            response_sol = requests.get(urlSol, headers=headersSol).json()
            poolId = response_sol['data'][0]['pool_id']
            urlRayPoolInfo = RAYID_URL+"ids?ids="+poolId
            responseRay = requests.get(urlRayPoolInfo).json()
            burnPercent=responseRay['data'][0]['burnPercent']
        else:
            burnPercent=responseRay['data']['data'][0]['burnPercent'] # maybe not correct
            # print("burnPercent",burnPercent)
    except Exception as e:
        print("poolInfo get error",e)
        burnPercent=0
    
    isMintAuth=False
    if not tokenSupply['mintable']['authority']:
        isMintAuth=True
    if internal:
        result = {
            'totalSupply':int(float(totalSupply)),
            'isMintAuth':isMintAuth,
            'burnPercent':burnPercent,
            'tokenName':tokenName,
            'marketCap':marketCap,
            'holders':holder,
            'decimals':decimals
        }
    else:
        result = {
            'totalSupply':int(float(totalSupply)),
            'isMintAuth':isMintAuth,
            'burnPercent':burnPercent,
            'tokenName':tokenName,
            'tokenName':tokenName,
            'marketCap':marketCap,
            'holders':holder
        }
    return 200,result
