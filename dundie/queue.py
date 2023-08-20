from redis import Redis
from rq import Queue

from dundie.config import settings

redis = Redis(
    host=settings.redis.host,
    port=settings.redis.port,
)

queue = Queue(connection=redis)
