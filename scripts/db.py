import sqlite3
import os

DB_PATH = os.path.join("db", "db.db")
create_query = """
    CREATE TABLE IF NOT EXISTS general (
        guild_id                BIGINT PRIMARY KEY
                                    UNIQUE
                                    NOT NULL,
        announcement_channel_id BIGINT,
        role_to_ping            BIGINT
    );
"""

set_channel_query = """
    UPDATE general
    SET announcement_channel_id = ?
    WHERE guild_id = ?
"""

delete_channel_query = """
    UPDATE general
    SET announcement_channel_id = Null
    WHERE guild_id = ?
"""

set_role_query = """
    UPDATE general
    SET role_to_ping = ?
    WHERE guild_id = ?
"""

delete_role_query = """
    UPDATE general
    SET role_to_ping = Null
    WHERE guild_id = ?
"""

get_server_data = """
    SELECT *
    FROM general
    WHERE guild_id == ?
"""

class Database:
    @staticmethod
    def postQuery(query: str, commit=True):
        """
            Decorator for functions who make queries and don't want to get back response
            First, the function gets executed and only then db gets the query call
            `Function arguments` == `query params`, so order matters.
        """
        def external(f):
            def internal(self, *args, **kwargs):
                f(self, *args, **kwargs)
                self.db.cursor().execute(query, args)
                if commit:
                    print(f"Committed to: {self.db=}")
                    self.db.commit()
            return internal
        return external

    @staticmethod
    def getQuery(query: str, fetchAmount=None):
        def external(f):
            def internal(self, *args, **kwargs):
                f(self, *args, **kwargs)
                methodName = None
                if fetchAmount is None:
                    methodName = "fetchall"

                cursor = self.db.cursor().execute(query, args)
                if methodName == "fetchall":
                    return cursor.fetchall()

                data = cursor.fetchmany(fetchAmount)
                return data[0] if fetchAmount == 1 else data
            return internal
        return external

    @postQuery(create_query)
    def __init__(self):
        self.db: sqlite3.Connection = sqlite3.connect(DB_PATH)

    @postQuery(delete_channel_query)
    def remove_channel(self, guildId: int) -> None: ...

    @postQuery(delete_role_query)
    def remove_role(self, guildId: int) -> None: ...

    @postQuery(set_role_query)
    def set_role(self, roleId: int, guildId: int) -> None: ...

    @postQuery(set_channel_query)
    def set_channel(self, channelId: int, guildId: int) -> None: ...

    @getQuery(get_server_data, fetchAmount=1)
    def get_guild_data(self, guildId: int) -> list: ...

    def __del__(self):
        self.db.close()
