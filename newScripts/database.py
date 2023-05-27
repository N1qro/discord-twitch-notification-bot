import asyncpg
import asyncio
import sys
import asyncio.exceptions
from accessify import private
from logger import Log
from queries import Query


class Database:
    @private
    def __init__(self, pool) -> None:
        self.pool = pool

    @classmethod
    async def connect(cls):
        if await cls.check_connection():
            pool = await asyncpg.create_pool()
            return cls(pool)

    @staticmethod
    async def check_connection():
        """Проверяет возможность подключения к базе данных.
           Оканчивает скрипт в случае невозможности подключения"""
        try:
            Log.info("Cheking the PostgreSQL connection possibility...")
            conn = await asyncpg.connect(timeout=5)
            await conn.close()
        except asyncio.exceptions.TimeoutError:
            Log.failure("Check your PostgreSQL connection, timeout error")
            sys.exit(2)
        except ConnectionRefusedError:
            Log.failure("Is your PostgreSQL port correct? Connection refused")
            sys.exit(3)
        except asyncpg.exceptions.InvalidAuthorizationSpecificationError as e:
            Log.failure(str(e))
            sys.exit(4)
        except Exception as e:
            Log.failure(str(e))
            sys.exit(-1)
        else:
            Log.success("Connection possible. Can proceed further!")
            return True

    async def init_tables(self) -> None:
        """Создаёт pool соединений и все нужные таблицы, если они не существуют"""
        async with self.pool.acquire() as conn:
            await conn.execute(Query.CREATE_ALL.value)

    async def test_query(self) -> None:
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                return await conn.fetch("SELECT * FROM person LIMIT 5")
