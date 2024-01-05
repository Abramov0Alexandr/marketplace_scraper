import asyncio
import csv

import requests
from bs4 import BeautifulSoup
from httpx import Response

from parsers.abc_class import Parser


class DataParser(Parser):
    """
    Класс для работы с данными, полученными в ходе анализа HTML страниц товаров.
    """

    async def get_total_product_price(self, products_url: list[str]) -> str:
        """
        Метод для получения суммы общей стоимости товаров, размещенной на площадке.
        :param products_url: Список URL адресов на все товары.
        :return: Информация об общей стоимости товаров.
        """

        async def fetch_total_price_for_each_product(product_url: str):
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

        return f"Стоимость всех товаров на площадке: {total_price} руб."

    async def write_csv(self, products_url: list[str]):
        """
        Метод для записи данных в формат csv.
        :param products_url: Список URL адресов на страницу товара.
        :return: None.
        """

        with open("res.csv", "w", encoding="utf-8-sig", newline="") as file:
            writer = csv.writer(file, delimiter=";")
            writer.writerow(
                [
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
            )

        title_list: list = []
        article_list: list = []
        description_list: list = []
        stock_list: list = []
        current_price_list: list = []
        old_price_list: list = []
        items_url = [page for page in products_url]

        with requests.Session() as session:
            for page in products_url:
                response = session.get(page)
                response.encoding = "utf8"

                items_title = self.get_soup_data(response, "p", id="p_header")
                items_article = self.get_soup_data(response, "p", class_="article")
                items_description = self.get_soup_data(response, "ul", id="description")
                items_in_stock = self.get_soup_data(response, "span", id="in_stock")
                items_current_price = self.get_soup_data(response, "span", id="price")
                items_old_price = self.get_soup_data(response, "span", id="old_price")

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

        with open("res.csv", "a", encoding="utf-8-sig", newline="") as file:
            writer = csv.writer(file, delimiter=";")
            for title, article, descr, stock, cprice, oprice, url in zip(
                title_list,
                article_list,
                description_list,
                stock_list,
                current_price_list,
                old_price_list,
                items_url,
            ):
                # Формируем строку для записи
                flatten = (
                    title,
                    article,
                    *[x.split(":")[1].strip() for x in descr if x],
                    stock,
                    cprice,
                    oprice,
                    url,
                )

                writer.writerow(flatten)

        print("Таблица записана")

    @staticmethod
    def get_soup_data(item_url: Response, *args, **kwargs) -> list:
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
