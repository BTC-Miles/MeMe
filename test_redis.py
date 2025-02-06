import redis

# 连接到本地的 Redis 实例
r = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)

# 获取所有的键
keys = r.keys('*')

# 遍历所有的键并打印对应的值
for key in keys:
    value = r.get(key)
    print(f"Key: {key}, Value: {value}")
