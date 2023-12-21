import asyncio

from bs4 import BeautifulSoup

from parsers.abc_class import Parser


class URLParser(Parser):
    """
    Класс, отвечающий для получения следующих списков URL адресов:
    - URL адреса каждой категории товара.
    - URL адреса всех страниц с товарами со всех категорий.
    - URL адреса каждого товара каждой категории.
    """

    def __init__(self):
        self.__starting_url = 'https://parsinger.ru/html/index1_page_1.html'
        self.__base_shop_url = 'https://parsinger.ru/html/'

    async def get_category_urls(self) -> list[str]:
        """
        Метод для получения URL адресов на каждую категорию товара.
        :return: Список, содержащий URL адреса категорий товаров.
        """

        soup = BeautifulSoup(await self.get_response(self.starting_url), 'lxml')
        category_urls_tags = soup.find('div', class_='nav_menu').find_all('a')
        return [self.base_shop_url + tags['href'] for tags in category_urls_tags]

    async def get_url_for_each_category_page(self) -> list[str]:
        """
        Метод для получения списка URL адресов каждой страницы каждой категорий.
        :return: Список URL адресов.
        """

        category_urls = await self.get_category_urls()

        async def fetch_category_page_urls(category_url: str) -> list:
            """
            Вложенная функция для обработки URL адресов каждой категории товаров.
            :param category_url: URL адрес категории товаров.
            :return: Функция возвращает списки, содержащие URL адреса на каждую страницу товаров каждой категории.
            """

            category_pages_html = await self.get_response(category_url)
            soup = BeautifulSoup(category_pages_html, 'lxml')
            category_urls_tags = soup.find('div', class_='pagen').find_all('a')
            return [self.base_shop_url + category_url['href'] for category_url in category_urls_tags]

        tasks = [fetch_category_page_urls(each_category_url) for each_category_url in category_urls]
        all_category_list_url = await asyncio.gather(*tasks)

        return [url for sublist in all_category_list_url for url in sublist]

    async def get_url_for_each_product_card(self) -> list[str]:
        """
        Метод для получения списка URL адресов каждого товара каждой категории.
        :return: Список URL адресов.
        """

        product_list_urls = await self.get_url_for_each_category_page()

        async def fetch_products_page_urls(product_url: str) -> list:
            """
            Вложенная функция для обработки каждой страницы каждой категории товара.
            :param product_url: URL адрес каждой страницы всех категорий.
            :return: Список, содержащий URL адреса на каждый товар.
            """

            product_pages_html = await self.get_response(product_url)
            soup = BeautifulSoup(product_pages_html, 'lxml')
            product_url_tags = soup.find_all('div', class_='sale_button')
            return [self.base_shop_url + product_url.find_all('a')[0]['href'] for product_url in product_url_tags]

        tasks = [fetch_products_page_urls(each_product_urls) for each_product_urls in product_list_urls]
        all_products_list_url = await asyncio.gather(*tasks)
        return [url for sublist in all_products_list_url for url in sublist]

    def __str__(self):
        return f"{self.__class__.__name__} for collection URLs from {self.base_shop_url}"

    def __repr__(self):
        return self.__class__

    @property
    def starting_url(self):
        return self.__starting_url

    @property
    def base_shop_url(self):
        return self.__base_shop_url
