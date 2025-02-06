import get_addr_list
import get_token_info
import time
import find_link

# Generate an error message
def error_message(msg, error = None):
    if error:
        error = f' {error}'
    else:
        error = ''
    return 'Error: ' + msg + error


async def analytics_token(address):

    #get contract base information,ex:totalSupply
    code,tokenInfo=get_token_info.get_token_info(address,True)
    if code != 200:
        return code,tokenInfo
    #tokenInfo['totalSupply']=tokenInfo['totalSupply']*()
    #get information on Top 100 address 
    code,addrInfo=await get_addr_list.get_addr_list(address)
    if code != 200:
        return code,addrInfo

    #Get the correlation information for 100 addresses.
    code,addrInfo=await find_link.find_link(addrInfo)
    if code != 200:
        return code,addrInfo
    
    try:

        top100Amonut = 0
        symbolAmountList = {}
        record = []
        for i in range(100):
            #calculate the total amount of the top 100 addresses
            top100Amonut = addrInfo[i]['amount']+top100Amonut
            addrInfo[i]['amount'] = addrInfo[i]['amount']/(10**tokenInfo['decimals'])
            #calculate the ratio of the amount of the top 100 addresses to the total amount 
            addrInfo[i]['amountRatio'] = round(float(addrInfo[i]['amount']/tokenInfo['totalSupply'])*100,2)
            if addrInfo[i]['symbol'] == 0:
                continue
            
            #set symbol
            if addrInfo[i]['symbol'] not in symbolAmountList:
                # Record the location of each associated address
                record.append(i) 
                symbolAmountList[addrInfo[i]['symbol']] = addrInfo[i]['amount']
            else:
                record.append(i)
                # calculate the total amount of the associated address
                symbolAmountList[addrInfo[i]['symbol']] = addrInfo[i]['amount']+symbolAmountList[addrInfo[i]['symbol']]
        #calculate the ratio of the amount of the associated address to the total amount
        for i in symbolAmountList:
            symbolAmountList[i] = symbolAmountList[i]/tokenInfo['totalSupply']*100

        for i in record:
            
            addrInfo[i]['symbol'] = {
                'serial':addrInfo[i]['symbol'],
                'ratio': round(float(symbolAmountList[addrInfo[i]['symbol']]),2),
            } 
    except Exception as e:
         print('Get some info error :',e)
         return 500,error_message('Get some info error')
    
    result = {
        'addrInfo':addrInfo,
    }
    
    return 200,result