from abc import ABC
from abc import abstractmethod
from typing import Any

from httpx import AsyncClient
from httpx import ConnectTimeout
from httpx import ReadTimeout
from httpx import Response


class Parser(ABC):
    @abstractmethod
    def __init__(self) -> None:
        self.__starting_url: str = ""
        self.__base_shop_url: str = ""

    @property
    def available_categories(self) -> list[str]:
        return [
            "watch",
            "mobile",
            "mouse",
            "hdd",
            "headphones",
        ]

    @staticmethod
    async def get_response(target_url: str) -> Any:
        """
        Метод для отправки HTTP запроса на стартовый URL адрес.
        :return: Текстовое содержание HTML разметки.
        """

        async with AsyncClient() as client:
            try:
                response: Response = await client.get(target_url, timeout=4)
                response.encoding = "utf8"
                return response.text

            except (ConnectTimeout, ReadTimeout) as error:
                return error
