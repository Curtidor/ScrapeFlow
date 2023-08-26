import asyncio

from scraping.data_parser import DataParser
from events.event_dispatcher import EventDispatcher
from loaders.config_loader import ConfigLoader
from loaders.response_loader import ResponseLoader
from scraping.data_saver import DataSaver
from scraping.data_scraper import DataScraper
from factories.config_element_factory import ConfigElementFactory


async def main():
    print("STARTING..")

    event_dispatcher = EventDispatcher(debug_mode=True)
    event_dispatcher.start()

    config = ConfigLoader('configs/scrap_this_site.com/Oscar_Winning_Films_AJAX_and_Javascript.json')

    elements = ConfigElementFactory.create_elements(config.get_raw_target_elements(), config.get_data_order())

    data_saver = DataSaver(config.get_saving_data(), config.get_data_order())
    data_saver.setup(clear=True)
    data_scraper = DataScraper(config, elements, event_dispatcher)
    data_parser = DataParser(config, event_dispatcher, data_saver)

    ResponseLoader.setup(event_dispatcher=event_dispatcher)

    for url, crawler in config.get_setup_information():
        print("RUNNING CRAWLER")
        crawler.start()
        await crawler.exit()

    await ResponseLoader.close()
    print("END...")

if __name__ == "__main__":
    asyncio.run(main())
