from enum import Enum


class Query(Enum):
    """Класс-хранилище всех запросов"""

    CREATE_STREAMERS = """
        CREATE TABLE IF NOT EXISTS streamers (
            streamer_id INT PRIMARY KEY
        );
    """

    CREATE_GUILDS = """
        CREATE TABLE IF NOT EXISTS guilds (
            guild_id BIGINT PRIMARY KEY,
            channel_id BIGINT
        );
    """

    CREATE_ROLES = """
        CREATE TABLE IF NOT EXISTS roles (
            role_id BIGINT PRIMARY KEY,
            belongs_to BIGINT,
            FOREIGN KEY (belongs_to) REFERENCES guilds(guild_id)
        );
    """

    CREATE_STREAMER_TO_ROLES = """
        CREATE TABLE IF NOT EXISTS role_to_streamer (
            id BIGSERIAL PRIMARY KEY,
            streamer_id INT,
            role_id BIGINT,
            FOREIGN KEY (streamer_id) REFERENCES streamers(streamer_id),
            FOREIGN KEY (role_id) REFERENCES roles(role_id)
        );
    """

    CREATE_ALL = "\n".join((CREATE_STREAMERS, CREATE_GUILDS,
                            CREATE_ROLES, CREATE_STREAMER_TO_ROLES))
