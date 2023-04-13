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

set_role_query = """
    UPDATE general
    SET role_to_ping = ?
    WHERE guild_id = ?
"""


db: sqlite3.Connection = sqlite3.connect(DB_PATH)
db.cursor().execute(create_query)
db.commit()


def set_role(guildId: int, roleId: int) -> None:
    db.cursor().execute(set_role_query, (roleId, guildId))
    db.commit()


def set_channel(guildId: int, channelId: int) -> None:
    db.cursor().execute(set_channel_query, (channelId, guildId))
    db.commit()
