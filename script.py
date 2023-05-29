import redis

r = redis.StrictRedis(host='localhost', port=6379, db=0)
r.lpush("chat", 'admin: 123')
# r.ltrim("chat", 0, 9)
messages = r.lrange("chat", 0, -1)[::-1]
print([message.decode("utf-8") for message in messages])