"""
    Этот модуль считывает переменные из .env файла и записывает их в среду.
    В случае если возникает ошибка с Docker и приложение не запускается,
    Можно дополнительно указать `DOCKER=TRUE` и указать их в докер-файле
    Чтобы этот скрипт прекратил своё выполнение.

    VALIDATE | Отвечает за наличие всех переменных

    DOCKER | Если `True`, модуль прекратит выполнение
"""


def load_env():
    import os
    if os.getenv("DOCKER") in (False, None):
        from dotenv import load_dotenv
        assert load_dotenv(), "No .env is configured!"

        assert os.getenv("VALIDATE"), "(VALIDATE) variable is not set"
        if os.getenv("VALIDATE").lower() in ("true", "t", "1", "yes", "y"):
            assert os.getenv("PGHOST"), "PostgreSQL host is not set"
            assert os.getenv("PGUSER"), "PostgreSQL user is not set"
            assert os.getenv("PGPASSWORD"), "PostgreSQL password is not set"
            assert os.getenv("PGDATABASE"), "PostgreSQL database is not set"
            assert os.getenv("BOT_PREFIX"), "Discord bot command prefix isn't set"
            assert os.getenv("BOT_TOKEN"), "Discord bot token isn't set"

        del load_dotenv
    del os
