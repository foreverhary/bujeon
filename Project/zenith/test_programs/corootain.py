import asyncio

from process_package.defined_variable_function import logger


async def make_americano():
     logger.debug("Americano Start")
     await asyncio.sleep(3)
     logger.debug("Americano End")
     return "Americano"

async def make_latte():
    logger.debug("Latte Start")
    await asyncio.sleep(5)
    logger.debug("Latte End")
    return "Latte"

async def main():
    coro1 = make_americano()
    coro2 = make_latte()
    result = await asyncio.gather(
                coro1,
                coro2
    )
    logger.debug(result)

logger.debug("Main Start")
asyncio.run(main())
logger.debug("Main End")