import sqlite3
from scripts.enums import GuildData
import os


class Database:
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

    @staticmethod
    def postQuery(query: str, commit=True):
        """
            Decorator for functions who make queries and don't want to get back response
            First, the function gets executed and only then db gets the query call
            `Function *args` == `query params`, so order matters.
        """
        def external(f):
            def internal(self, *args, **kwargs):
                f(self, *args, **kwargs)
                self.db.cursor().execute(query, args)
                if commit:
                    self.db.commit()
            return internal
        return external

    @staticmethod
    def getQuery(query: str, fetchAmount=None):
        """
            Decorator for functions which make queries and want to get back response
            First, the function gets executed and only then db gets the query call
            `Function *args` == `query params`, so order matters. 
        """
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

    @staticmethod
    def convertTo(cls):
        def external(f):
            def internal(self, *args, **kwargs):
                data = f(self, *args, **kwargs)
                if isinstance(data[0], list):
                    return list(map(cls, *data))
                return cls(*data)
            return internal
        return external

    @postQuery(create_query)
    def __init__(self):
        self.db: sqlite3.Connection = sqlite3.connect(self.DB_PATH)

    @postQuery("UPDATE general SET announcement_channel_id = Null WHERE guild_id = ?")
    def reset_channel(self, guildId: int) -> None: ...

    @postQuery("UPDATE general SET role_to_ping = Null WHERE guild_id = ?")
    def reset_role(self, guildId: int) -> None: ...

    @postQuery("UPDATE general SET role_to_ping = ? WHERE guild_id = ?")
    def set_role(self, roleId: int, guildId: int) -> None: ...

    @postQuery("UPDATE general SET announcement_channel_id = ? WHERE guild_id = ?")
    def set_channel(self, channelId: int, guildId: int) -> None: ...

    @convertTo(GuildData)
    @getQuery("SELECT * FROM general WHERE guild_id == ?", fetchAmount=1)
    def get_guild_data(self, guildId: int) -> GuildData: ...

    def __del__(self):
        self.db.close()
