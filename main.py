import time

from parsers.data_parser import DataParser
from parsers.url_parser import URLParser


async def main():
    start_time = time.perf_counter()
    url_parser = URLParser()
    data_parser = DataParser()

    product_url_list = await url_parser.get_url_for_each_product_card()
    print(await data_parser.get_total_product_price(product_url_list))

    print(f'Elapsed time: {time.perf_counter() - start_time}')

    # OUT:
    # Стоимость всех товаров на площадке: 45067195 руб.
    # Elapsed time: 3.11463470000308


if __name__ == '__main__':
    import asyncio

    asyncio.run(main())
    main().close()
