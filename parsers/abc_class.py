from abc import ABC
from typing import Any

import httpx
from httpx import AsyncClient


class Parser(ABC):
    def __init__(self):
        self.__starting_url = "https://parsinger.ru/html/index1_page_1.html"
        self.__base_shop_url = "https://parsinger.ru/html/"
        self.__available_categories = [
            "watch",
            "mobile",
            "mouse",
            "hdd",
            "headphones",
        ]

        self.__all_card_headers = [
            "Наименование",
            "Артикул",
            "Бренд",
            "Модель",
            "Тип",
            "Технология экрана",
            "Материал корпуса",
            "Материал браслета",
            "Размер",
            "Сайт производителя",
            "Наличие",
            "Цена",
            "Старая цена",
            "Ссылка на карточку с товаром",
        ]

        self.__specific_card_headers = [
            "Наименование",
            "Артикул",
            "Бренд",
            "Модель",
            "Наличие",
            "Цена",
            "Старая цена",
            "Ссылка на карточку с товаром",
        ]

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

    @property
    def starting_url(self):
        return self.__starting_url

    @property
    def base_shop_url(self):
        return self.__base_shop_url

    @property
    def available_categories(self):
        return self.__available_categories

    @property
    def all_card_headers(self):
        return self.__all_card_headers

    @property
    def specific_card_headers(self):
        return self.__specific_card_headers
