import asyncio
import time

from parsers.data_parser import DataParser
from parsers.url_parser import URLParser


async def main():
    start_time = time.perf_counter()
    url_parser = URLParser()
    data_parser = DataParser()

    watches_url = await url_parser.get_url_for_each_product_card(specific="watch")
    await data_parser.write_csv(watches_url)
    print(f"Elapsed time: {time.perf_counter() - start_time}")


if __name__ == "__main__":
    try:
        asyncio.run(main())
        main().close()

    except Exception as e:
        print(e)
        main().close()
