import redis
from rq import Queue

rd= redis.Redis(host='127.0.0.1', port=6379)
ocr_queue= Queue('ocr', connection=rd)