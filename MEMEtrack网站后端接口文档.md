## **MEMEtrack网站后端接口文档**

主要接口有三个一个是查询代币的基本信息一个是查询追踪的信息

1）gettokeninfo

```
URL：https://3.0.175.221:6006/gettokeninfo/<address>
```

类型：

```
GET
```

参数：

```
address:string
```

返回值：

```
{
	result:200
	msg:{
    "burnPercent": 100,				//烧池子
    "holders": 612,						//持有者总量
    "isMintAuth": true,				//Mint丢弃
    "marketCap": 109716.59577493522,		//总市值
    "tokenName": "granny",				//代币名称
    "totalSupply": 999990838000000		//总供应量（最好转换成亿为单位）
		
	}
}
```

2) analytics

```
URL：https://3.0.175.221:6006/analytics/<address>
```

类型：

```
GET
```

参数：

```
address:string
```

返回值：

```
{
	result:200,
	msg:{
	  caculation:'1'										//'1'庄家拉盘中,'2'庄家出货中,'3'庄家洗盘中,'4'庄家控盘
	  																	//中,'5'庄家吸筹中
		addrInfo:[{
        "amountRatio": float,					//持有比例
        "from": string,								//sol来源地址
        "owner": string,							//持有人
        "solAmount": int,							//钱包余额
        "buy":int,										//买
        "sell":int,										//卖
        "symbol": {										//来源地址查重检查
          "Ratio": float,							//集群占总量的比例
          "serial": int								//所属集群
        }

		}]
	}
	
}
```



3）login

```
URL：https://3.0.175.221:6006/login
```

类型：

```
POST
```

参数：

```
wallet：sting
```

返回值：

```
{
	result:200,
	msg:JWT
	}
```

错误处理

result：错误码

msg：错误信息

ex：

```
{
	result:500    //内部查询错误
	msg：EOORO			//具体错误内容
}
```



4）verifytransferaccount

```
URL:https://3.0.175.221:6006/verifytransferaccount/<address>
```

类型：

```
GET
```

参数：

```
address:string
```

返回值：

```
{
result:200,
msg:{
	status:True/False,//账户状态
	info:"Transfer already exists"//错误信息
	}
}
```

错误信息:

```
info:"Transfer already exists"//该转账已存在
info:"sol amount error, update fail"//sol转账数量有误
info:"Error, update fail"//失败
```

正确信息:
```
info:"VIP expiry time for {address} updated to {new_expiry_str}""//成功更新某个地址的VIP到期时间
```



5）getvipstatus

```
URL:https://3.0.175.221:6006/getvipstatus/<address>
```

类型:

```
GET
```

参数:

```
address:string
```

返回值:
```
result:200,
vip_info:{
                'vip_status' : vip_status,//vip的状态，True或False
                'vip_time' : expiry_time//vip到期时间，格式为，Mon, 24 Feb 2025 03:53:01 GMT，后续会改为UTC +8
            }
```