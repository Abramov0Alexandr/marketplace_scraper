import asyncio
import csv
import itertools
from re import compile
from re import Pattern

import httpx
import requests
from bs4 import BeautifulSoup
from httpx import Response

from parsers.abc_class import Parser


class DataParser(Parser):
    """
    Класс для работы с данными, полученными в ходе анализа HTML страниц товаров.
    """

    def __init__(self):
        pass

    async def get_total_product_price(self, products_url: list[str]) -> str:
        """
        Метод для получения суммы общей стоимости товаров, размещенной на площадке.
        :param products_url: Список URL адресов на все товары.
        :return: Информация об общей стоимости товаров.
        """

        async def fetch_total_price_for_each_product(product_url: str) -> int:
            """
            Вложенная функция для обхода всех URL адресов, сбора информации о количестве товаров и их стоимости.
            :param product_url: URL адрес товара.
            :return: После получения информации о количестве и стоимости товаров,
            функция возвращает итоговую стоимость всех товаров.
            """

            each_item_html_page = await self.get_response(product_url)
            soup = BeautifulSoup(each_item_html_page, "lxml")
            item_quantity_tag = soup.find("span", id="in_stock")
            item_price_tag = soup.find("span", id="price")

            item_quantity: list[int] = [
                int(quantity.text.split(": ")[1]) for quantity in item_quantity_tag
            ]
            item_price: list[int] = [
                int(price.text.split(" ")[0]) for price in item_price_tag
            ]

            return sum([x * y for x, y in zip(item_quantity, item_price)])

        tasks = [
            fetch_total_price_for_each_product(current_url)
            for current_url in products_url
        ]
        total_price = sum(await asyncio.gather(*tasks))

        return f"Total price of items placed in the marketplace is: {total_price} rub."

    async def write_csv(
        self,
        products_url: list[str],
        table_filename: str = "result_table",
        write_headers: bool = True,
    ) -> None:
        """
        Метод для записи данных в формат csv.
        :param table_filename: Название итогового файла.
        :param products_url: Список URL адресов на страницу товара.
        :param write_headers: Если флаг True, то в csv файле будут записаны заголовки таблицы.
        :return: None.
        """

        if await self.__is_product_card_url(products_url, self.available_categories):

            # Получаем данные для записи в CSV.
            (
                title_list,
                article_list,
                description_list,
                stock_list,
                current_price_list,
                old_price_list,
                items_url,
            ) = await self.__get_data_from_item_card(products_url)

            if write_headers:

                # Создаем CSV файл и записываем заголовки
                await self.__write_headers(
                    await self.__generate_card_headers(products_url),
                    filename=table_filename,
                )

                # получаем данные и дополняем созданный CSV файл.
                await self.__card_data_writer(
                    title_list,
                    article_list,
                    description_list,
                    stock_list,
                    current_price_list,
                    old_price_list,
                    items_url,
                    filename=table_filename,
                    mode="a",
                )

            else:
                await self.__card_data_writer(
                    title_list,
                    article_list,
                    description_list,
                    stock_list,
                    current_price_list,
                    old_price_list,
                    items_url,
                    filename=table_filename,
                )

        else:
            (
                title_list,
                description_list,
                price_list,
            ) = await self.__get_data_from_page(products_url)

            await self.__page_data_writer(
                title_list, description_list, price_list, filename=table_filename
            )

    async def __get_data_from_item_card(
        self, products_url: list[str]
    ) -> tuple[
        list[str],
        list[str],
        list[list[str]],
        list[str],
        list[str],
        list[str],
        list[str],
    ]:
        """
        Метод для получения внутренней информации с карточки товара (раздел "Подробнее").
        :param products_url: Список с URL адресами товаров.
        :return: Кортеж из списков, содержащих информацию о каждом товаре.
        """

        title_list: list[str] = []
        article_list: list[str] = []
        description_list: list[list[str]] = []
        stock_list: list[str] = []
        current_price_list: list[str] = []
        old_price_list: list[str] = []
        items_url: list[str] = [page for page in products_url]

        with requests.Session() as session:
            for page in products_url:
                response = session.get(page)
                response.encoding = "utf8"

                items_title = await self.__get_soup_data(response, "p", id="p_header")
                items_article = await self.__get_soup_data(
                    response, "p", class_="article"
                )
                items_description = await self.__get_soup_data(
                    response, "ul", id="description"
                )
                items_in_stock = await self.__get_soup_data(
                    response, "span", id="in_stock"
                )
                items_current_price = await self.__get_soup_data(
                    response, "span", id="price"
                )
                items_old_price = await self.__get_soup_data(
                    response, "span", id="old_price"
                )

                title_list.extend([item for item in items_title])
                article_list.extend(
                    [article.split(": ")[1].strip() for article in items_article]
                )
                description_list.extend(
                    [item.split("\n") for item in items_description]
                )
                stock_list.extend([item.split(": ")[1] for item in items_in_stock])
                current_price_list.extend([item for item in items_current_price])
                old_price_list.extend([item for item in items_old_price])

        return (
            title_list,
            article_list,
            description_list,
            stock_list,
            current_price_list,
            old_price_list,
            items_url,
        )

    async def __get_data_from_page(
        self, products_page_url: list[str]
    ) -> tuple[list[str], list[list[str]], list[str]]:
        """
        Метод для получения информации о товаре со страницы с карточками товаров.
        :param products_page_url: Список с URL адресами товаров.
        :return: Кортеж из списков, содержащих информацию о каждом товаре.
        """

        title_list: list[str] = []
        description_list: list[list[str]] = []
        price_list: list[str] = []

        with requests.Session() as session:
            for page in products_page_url:
                response = session.get(page)
                response.encoding = "utf8"

                items_title = await self.__get_soup_data(
                    response, "a", class_="name_item"
                )
                items_description = await self.__get_soup_data(
                    response, "div", class_="description"
                )
                items_price = await self.__get_soup_data(response, "p", class_="price")

                title_list.extend([item.strip() for item in items_title])
                description_list.extend(
                    [item.split("\n") for item in items_description]
                )
                price_list.extend([item for item in items_price])

        return (
            title_list,
            description_list,
            price_list,
        )

    @staticmethod
    async def __generate_card_headers(item_card_url: list[str]) -> list[str]:
        """
        Метод для генерации заголовков csv таблицы.
        :param item_card_url: Список URL адресов с карточками товаров.
        :return: Список заголовков.
        """

        card_url = httpx.get(item_card_url[1])
        card_url.encoding = "utf-8"

        soup = BeautifulSoup(card_url, "lxml")
        description = soup.find("ul", id="description")
        description_list = [i.text.split(": ")[0].strip() for i in description]

        headers_list = [header for header in description_list if header]

        return [
            "Наименование",
            "Артикул",
            *headers_list,
            "Наличие",
            "Цена",
            "Старая цена",
            "Ссылка на карточку с товаром",
        ]

    @staticmethod
    async def __write_headers(
        table_headers: list,
        filename: str,
    ) -> None:
        """
        Метод для первоначального создания CSV файла и записи в него заголовков таблицы.
        :param table_headers: Заголовки для их записи в таблицу.
        :param filename: Название файла, по умолчанию "result_table.csv"
        :return: None.
        """

        with open(f"{filename}.csv", "w", encoding="utf-8-sig", newline="") as file:
            writer = csv.writer(file, delimiter=";")
            writer.writerow(table_headers)

    @staticmethod
    async def __card_data_writer(
        *args: list[str] | list[list[str]],
        filename: str,
        mode: str = "w",
    ) -> None:
        """
        Метод для записи переданных данных в файл формата CSV.
        :param args: Списки, содержащие информацию о товарах.
        :param filename: Название файла, по умолчанию "result_table.csv".
        :param mode: Режима обработки файла.
        :return: None.
        """

        with open(
            f"{filename}.csv", mode=mode, encoding="utf-8-sig", newline=""
        ) as file:
            writer = csv.writer(file, delimiter=";")
            for (
                title,
                article,
                descr,
                stock,
                current_price,
                old_price,
                url,
            ) in itertools.zip_longest(*args):
                flatten = (
                    title,
                    article,
                    *[x.split(":")[1].strip() for x in descr if x],
                    stock,
                    current_price,
                    old_price,
                    url,
                )

                writer.writerow(flatten)
        print(f"Таблица '{filename}.csv' записана")

    @staticmethod
    async def __page_data_writer(
        *args: list[str] | list[list[str]],
        filename: str,
        mode: str = "w",
    ) -> None:
        """
        Метод для записи переданных данных в файл формата CSV.
        :param args: Списки, содержащие информацию о товарах.
        :param filename: Название файла, по умолчанию "result_table.csv".
        :param mode: Режима обработки файла.
        :return: None.
        """

        with open(
            f"{filename}.csv", mode=mode, encoding="utf-8-sig", newline=""
        ) as file:
            writer = csv.writer(file, delimiter=";")
            for title, description, price in itertools.zip_longest(*args):
                flatten = (
                    title,
                    *[x.split(":")[1].strip() for x in description if x],
                    price,
                )

                writer.writerow(flatten)
        print(f"The table named '{filename}.csv' has been recorded")

    @staticmethod
    async def __get_soup_data(item_url: Response, *args, **kwargs) -> list[str]:
        """
        Метод для создания объекта BeautifulSoup и поиск элементов по указанным тегам и атрибутам.
        :param item_url: URL адрес на товар.
        :param args: HTML тег для поиска элемента.
        :param kwargs: HTML аттрибуты для поиска элемента.
        :return: Список найденных значений.
        """

        soup = BeautifulSoup(item_url.text, "lxml")
        searched_tag = soup.find_all(args, kwargs)

        if kwargs.get("class_"):
            kwargs["class"] = kwargs.get("class_")
            kwargs.pop("class_")
            searched_tag = soup.find_all(args, attrs=kwargs)
            return [item_data.text for item_data in searched_tag]

        return [item_data.text for item_data in searched_tag]

    @staticmethod
    async def __is_product_card_url(
        checked_urls: list[str], checked_categories: list[str]
    ) -> bool:
        """
        Метод для проверки какие именно URL адреса находятся в передаваемом списке.
        В случае, если список адресов содержит ссылки на внутреннюю карточку товара, то возвращается True.
        Иначе, список содержит адреса на страницы с категориями товаров.
        :param checked_urls: Список URL адресов, которые будут проверены.
        :param checked_categories: Список категорий, которые будут искаться, как фрагмент URL адреса карточки товара.
        :return: Boolean.
        """

        pattern: Pattern[str] = compile(r"/html/(\w+)/")
        categories = set(
            [
                pattern.search(url).group(1)
                for url in checked_urls
                if pattern.search(url)
            ]
        )
        return bool(categories.intersection(set(checked_categories)))

    def __str__(self):
        return f"Class {self.__class__.__name__} for processing the data received during parsing"

    def __repr__(self):
        return f"{self.__class__.__name__}()"
