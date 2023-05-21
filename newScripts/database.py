import asyncpg
import asyncio
from queries import Query


class Database:
    def __init__(self) -> None:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.init_tables())

    async def init_tables(self) -> None:
        """Создаёт pool соединений и все нужные таблицы, если они не существуют"""
        self.pool = await asyncpg.create_pool()
        async with self.pool.acquire() as conn:
            await conn.execute(Query.CREATE_ALL.value)

    async def close(self) -> None:
        """Метод, закрывающий подключение к бд. Вызывать перед закрытием скрипта"""
        await asyncio.wait_for(self.pool.close(), timeout=5)
