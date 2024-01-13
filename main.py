import asyncio
import time

from parsers.data_parser import DataParser
from parsers.url_parser import URLParser


async def main():
    start_time = time.perf_counter()
    data_parser = DataParser()
    url_parser = URLParser()

    urls = await url_parser.get_url_for_each_product_card(specific="mouse")
    print(await data_parser.write_csv(urls, table_filename="mouse_data_table"))

    print(f"Elapsed time: {time.perf_counter() - start_time}")


if __name__ == "__main__":
    try:
        asyncio.run(main())
        main().close()

    except Exception as e:
        print(e)
        main().close()
