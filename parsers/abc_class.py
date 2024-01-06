from abc import ABC
from typing import Any

import httpx
from httpx import AsyncClient


class Parser(ABC):
    @staticmethod
    async def get_response(target_url: str | list) -> str | Any:
        """
        Метод для отправки HTTP запроса на стартовый URL адрес.
        :return: Текстовое содержание HTML разметки.
        """

        async with AsyncClient() as client:
            try:
                response = await client.get(target_url, timeout=4)
                response.encoding = "utf8"
                return response.text

            except (httpx.ConnectTimeout, httpx.ReadTimeout) as error:
                return error
