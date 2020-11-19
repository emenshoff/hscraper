from bs4 import BeautifulSoup
import asyncio
import aiohttp
#import aiofiles
from time import time
from .parsers import parse_posts, hub_name_parser, parse_hubs, get_pagination_range

from .settings import MAX_TASKS


async def fetch_hub_posts(hub_url, session):
    """
    Fetchs hub posts from one page
    :param hub_url: one page
    :param session:
    :return: list of dicts with posts info
    """
    async with session.get(hub_url) as response:
        html_body = await response.read()
        html_text = html_body.decode()
        posts = await parse_posts(html_text, session)
        return posts


async def fetch_all_hub_posts(hub_url,
                              session,
                              sem,
                              paginated_fetch=False):
    """
    Optional pagination for all hub posts fetching.
    :param hub_url:
    :param session:
    :param paginated_fetch:
    :return: list of dicts with posts info
    """
    #print(hub_url)
    hub_name_search = hub_name_parser.search(hub_url)
    hub_name_group = hub_name_search.group('hub_name')
    hub_name = hub_name_group[0]
    async with sem:
        async with session.get(hub_url) as response:
            html_body = await response.read()
            html_text = html_body.decode()
            hub_posts = dict()
            #await asyncio.sleep(0.0001)

            if paginated_fetch:
                first_page, last_page = get_pagination_range(html_text)

                for page in range(first_page, last_page + 1):
                    hub_page_url = f"{hub_url}/page{page}/"
                    posts = await fetch_hub_posts(hub_page_url, session)
                    hub_posts.update(posts)
            else:
                posts = await fetch_hub_posts(hub_url, session)
                hub_posts.update(posts)
            return hub_posts


async def fetch_hubs(hub_url, session):
    async with session.get(hub_url) as response:
        html_body = await response.read()
        html_text = html_body.decode()
        return parse_hubs(html_text)


async def fetch_all_hubs(hubs_url,
                         session,
                         paginated_fetch=False):
    """
    Fetchs all hubs info with pagination option
    :param hubs_url:
    :param session:
    :param paginated_fetch:
    :return: матрешка описнаия хабов
    """
    async with session.get(hubs_url) as response:
        html_body = await response.read()
        html_text = html_body.decode()

        all_hubs = dict()

        if paginated_fetch:
            first_page, last_page = get_pagination_range(html_text)
            for page in range(first_page, last_page + 1):
                page_url = f"https://habr.com/ru/hubs/page{page}/"
                hubs = await fetch_hubs(page_url, session)
                all_hubs.update(hubs)
        else:
            hubs = parse_hubs(html_text)
            all_hubs.update(hubs)

        return all_hubs


async def init_fetch_hubs(hubs_url):
    """
    Fetches all hubs info in first start ot the program.
    :return:
    """
    #sem = asyncio.Semaphore(MAX_TASKS)
    async with aiohttp.ClientSession() as session:
        hubs_list = None
        tasks = [
            asyncio.create_task(fetch_all_hubs(hubs_url, session, paginated_fetch=True)),
            #asyncio.create_task(),
            #asyncio.create_task(),
        ]
        time1 = time()
        hubs_list = await asyncio.gather(*tasks)
        time2 = time()
        print(f"function {init_fetch_hubs.__name__} execution time is {time2 - time1:.2f} seconds...")
        return hubs_list


async def main_posts(hub_url):
    sem = asyncio.Semaphore(MAX_TASKS)
    async with aiohttp.ClientSession() as session:
        hubs_list = None
        tasks = [
            asyncio.create_task(fetch_all_hub_posts(hub_url, session, sem, paginated_fetch=False)),
            #asyncio.create_task(),
            #asyncio.create_task(),
        ]
        time1 = time()
        hubs_list = await asyncio.gather(*tasks)
        time2 = time()
        print(f"function {main_posts.__name__} execution time is {time2 - time1:.2f} seconds...")
        return hubs_list





