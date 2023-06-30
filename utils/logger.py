from datetime import datetime
from enum import Enum

from colorama import Fore, Style, init

init(autoreset=True)


class Status(Enum):
    WARNING = f"{Style.BRIGHT}{Fore.YELLOW}WARNING{Style.RESET_ALL}"
    INFO = f"{Style.BRIGHT}{Fore.CYAN}INFO{Style.RESET_ALL}"
    SUCCESS = f"{Style.BRIGHT}{Fore.GREEN}SUCCESS{Style.RESET_ALL}"
    FAILURE = f"{Style.BRIGHT}{Fore.RED}FAILURE{Style.RESET_ALL}"


class Log:

    def __init__(self) -> None:
        raise NotImplementedError(f"Cannot create instance of {type(self)} class")

    # "Движок" логгера
    def display(status: Status):
        """
            Декоратор, ставящий перед возвращаемым функции текстом
            временную отметку и статус "`status`", после выводя в `stdout`
        """
        def display(function):
            def wrapper(text: str) -> str:
                timestamp = datetime.now().strftime("%Y-%m-%d %X")
                timestamp_string = f"{Style.BRIGHT}{Fore.BLACK}{timestamp}"
                status_string = f"{timestamp_string} {status.value}\t"
                print(status_string + function(text), flush=True)
            return wrapper
        return display

    # Методы для логгера
    @display(Status.WARNING)
    def warning(text: str) -> str:
        return text

    @display(Status.INFO)
    def info(text: str) -> str:
        return text

    @display(Status.SUCCESS)
    def success(text: str) -> str:
        return text

    @display(Status.FAILURE)
    def failure(text: str) -> str:
        return text
