import asyncio
import time


async def main():
    start_time = time.perf_counter()

    print(f"Elapsed time: {time.perf_counter() - start_time}")


if __name__ == "__main__":
    try:
        asyncio.run(main())
        main().close()

    except Exception as e:
        print(e)
        main().close()
