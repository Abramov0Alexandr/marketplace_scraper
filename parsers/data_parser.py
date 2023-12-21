import asyncio

from bs4 import BeautifulSoup
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
            item_quantity_tag = soup.find('span', id='in_stock')
            item_price_tag = soup.find('span', id='price')

            item_quantity: list[int] = [int(quantity.text.split(': ')[1]) for quantity in item_quantity_tag]
            item_price: list[int] = [int(price.text.split(' ')[0]) for price in item_price_tag]

            return sum([x * y for x, y in zip(item_quantity, item_price)])

        tasks = [fetch_total_price_for_each_product(current_url) for current_url in products_url]
        total_price = sum(await asyncio.gather(*tasks))

        return f"Стоимость всех товаров на площадке: {total_price} руб."
