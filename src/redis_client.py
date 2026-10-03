import time
import redis

redis_client = redis.Redis(
    host="redis",
    port=6379,
    decode_responses=True,
)


def record_transaction(customer_id: str):
    """
    Record a transaction and return the number
    of transactions from this customer in the
    previous 1 hour.
    """

    key = f"customer:{customer_id}:transactions"

    now = time.time()
    one_hour_ago = now - 3600

    redis_client.zadd(
        key,
        {str(now): now}
    )

    redis_client.zremrangebyscore(
        key,
        0,
        one_hour_ago,
    )

    count = redis_client.zcard(key)

    redis_client.expire(
        key,
        3600,
    )

    return count