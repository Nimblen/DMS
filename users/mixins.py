from redis.asyncio import Redis
from asgiref.sync import async_to_sync

class RedisStatusMixin:
    redis_key = "connected_users"

    @staticmethod
    async def get_redis_connection():
        """
        Возвращает асинхронное соединение с Redis.
        """
        return Redis(host="127.0.0.1", port=6379, db=0)

    @staticmethod
    async def is_user_online(user_id):
        """
        Проверяет, находится ли пользователь онлайн через Redis.
        """
        try:
            redis_conn = await RedisStatusMixin.get_redis_connection()
            is_online = await redis_conn.sismember(RedisStatusMixin.redis_key, user_id)
            await redis_conn.close()
            return is_online
        except Exception as e:
            # Логируем ошибку, если требуется
            print(f"Ошибка Redis: {e}")
            return False

    def is_online(self, user_id):
        """
        Синхронная обёртка для проверки статуса пользователя.
        """
        return async_to_sync(self.is_user_online)(user_id)
