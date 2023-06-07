from enum import Enum


class Query(Enum):
    """Класс-хранилище всех запросов"""

    CREATE_STREAMERS = """
        CREATE TABLE IF NOT EXISTS streamers (
            streamer_id INT PRIMARY KEY,
            streamer_login VARCHAR(32) UNIQUE NOT NULL,
            is_online BOOLEAN DEFAULT FALSE NOT NULL
        );
    """

    CREATE_GUILDS = """
        CREATE TABLE IF NOT EXISTS guilds (
            guild_id BIGINT PRIMARY KEY,
            channel_id BIGINT NULL,
            linked_count SMALLINT NOT NULL CHECK (linked_count >= 0) DEFAULT 0
        );
    """

    CREATE_ROLES = """
        CREATE TABLE IF NOT EXISTS roles (
            id BIGSERIAL PRIMARY KEY,
            role_id BIGINT NOT NULL UNIQUE,
            belongs_to BIGINT NOT NULL,
            FOREIGN KEY (belongs_to) REFERENCES guilds(guild_id) ON DELETE CASCADE
        );
    """

    CREATE_STREAMER_TO_ROLES = """
        CREATE TABLE IF NOT EXISTS role_to_streamer (
            id BIGSERIAL PRIMARY KEY,
            streamer_id INT NOT NULL,
            role_id BIGINT UNIQUE NOT NULL,
            FOREIGN KEY (streamer_id) REFERENCES streamers(streamer_id),
            FOREIGN KEY (role_id) REFERENCES roles(role_id) ON DELETE CASCADE ON UPDATE CASCADE
        );
    """

    CREATE_ALL = "\n".join((CREATE_STREAMERS, CREATE_GUILDS,
                            CREATE_ROLES, CREATE_STREAMER_TO_ROLES))

    GUILD_ADD = "INSERT INTO guilds(guild_id, channel_id) VALUES ($1, $2)"
    GUILD_REMOVE = "DELETE FROM guilds WHERE guild_id = $1"
    ADD_ROLE = [
        "INSERT INTO roles (role_id, belongs_to) VALUES ($1, $2)",
        "INSERT INTO streamers (streamer_id, streamer_login) VALUES ($1, $2) ON CONFLICT DO NOTHING",
        "INSERT INTO role_to_streamer (streamer_id, role_id) VALUES ($1, $2)"
    ]

    GET_GUILD_ROLE_FROM_STREAMER = """
        SELECT role_id
        FROM role_to_streamer
        WHERE streamer_id = (
            SELECT streamer_id
            FROM streamers
            WHERE streamer_login = $2
        ) AND role_id IN (
            SELECT role_id
            FROM roles
            WHERE belongs_to = $1
        )
    """

    CHECK_IF_LINKED = """
        SELECT belongs_to
        FROM roles WHERE
         belongs_to = $1 AND
         role_id IN (
            SELECT role_id
            FROM role_to_streamer
            WHERE streamer_id = $2
         )
    """

    GET_ALL_ROLES = """
        SELECT role_id
        FROM roles
        WHERE belongs_to = $1
    """

    GET_LINKED_STREAMERS = f"""
        SELECT streamer_login
        FROM streamers
        WHERE streamer_id IN (
            SELECT streamer_id
            FROM role_to_streamer
            WHERE role_id IN (
                {GET_ALL_ROLES}
            )
        )
    """

    GET_STREAMER_AMOUNT = "SELECT COUNT(*) as amount FROM streamers"
    INCREMENT_LINKED_DATA = """
        UPDATE guilds SET linked_count = linked_count + $2
        WHERE guild_id = $1
    """
    GET_LINKED_DATA = "SELECT linked_count FROM guilds WHERE guild_id = $1"
    GET_COMMAND_CHANNEL = "SELECT channel_id FROM guilds WHERE guild_id = $1 LIMIT 1"
    UPDATE_COMMAND_CHANNEL = "UPDATE guilds SET channel_id = $2 WHERE guild_id = $1"
    DELETE_ROLE_FROM_ROLES = "DELETE FROM roles WHERE role_id = $1"
