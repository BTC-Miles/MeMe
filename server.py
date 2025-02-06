from flask import Flask
from flask import request
from flask import make_response
from dotenv import load_dotenv
from get_addr_list import get_user_transactions
from redis_db import get_vip_info
import get_token_info
import aiohttp
import asyncio
import analytics
import jwt
import auth
import os

load_dotenv()
SECRECT_KEY = os.getenv("SECRECT_KEY")

app = Flask(__name__)

semaphore = asyncio.Semaphore(2)
# Generate a response dict
def generate_response(result, msg):
    return {'result': result, 'msg': msg},result

@app.route('/',methods=['GET'])
def hello():
    return 'hello world'

@app.route('/analytics/<address>',methods=['GET'])
async def analytics_addr(address):
        JWT = request.headers.get('Authorization')

        if JWT:

            if verify_jwt(JWT, "123") == 'Token expired. Get a new one.' or verify_jwt(JWT, "123") == 'Invalid token. Please log in again.':
                 return generate_response(401, 'Unauthorized')
        else :
            return generate_response(401, 'Unauthorized')
        code, result =await analytics.analytics_token(address)
        return generate_response(code, result)

@app.route('/gettokeninfo/<address>',methods=['GET'])
def get_token(address):
    JWT = request.headers.get('Authorization')
    if JWT:
            if verify_jwt(JWT, "123") == 'Token expired. Get a new one.' and verify_jwt(JWT, "123") == 'Invalid token. Please log in again.':
                 return generate_response(401, 'Unauthorized')
    else :
        return generate_response(401, 'Unauthorized')
    code,result=get_token_info.get_token_info(address)
    return  generate_response(code,result)
    
@app.route('/login',methods=['post'])
def login():
    wallet = request.form.get('wallet')
    code,vip_info = get_vip_info(wallet)
    vip_status = vip_info.get('vip_status')
    token =  auth.generate_jwt(wallet, vip_status, SECRECT_KEY)
    return generate_response(200, token)

def verify_jwt(token, SECRECT_KEY):
    try:
        payload = jwt.decode(token, SECRECT_KEY, algorithms=['HS256'])
        is_vip = payload.get('is_vip', False)

        if not is_vip:
            return 'VIP status required for this action.' 

        return payload

    except jwt.ExpiredSignatureError:
        return 'Token expired. Get a new one.'
    except jwt.InvalidTokenError:
        return 'Invalid token. Please log in again.'

@app.route('/verifytransferaccount/<address>',methods=['GET'])
async def verify_transfer_account(address):
    code,result = await get_user_transactions(address)
    return generate_response(code, result)

@app.route('/getvipstatus/<address>',methods=['GET'])
async def get_vip_status(address):
    code,vip_info = await get_vip_info(address)
    return generate_response(code, vip_info)

if __name__ == '__main__':
    # import uvicorn
    app.run(host="0.0.0.0", port=6006,debug=True)