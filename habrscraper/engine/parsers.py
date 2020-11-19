import re
import hashlib
import dateparser
from bs4 import BeautifulSoup


id_parser_template = re.compile(r".+_(?P<id>[0-9]+)$")
author_nick_parser = re.compile(r".+/(?P<nickname>\w+)/?$")
page_num_parser = re.compile(r".+/page(?P<page>[0-9]+)/?$")
hub_name_parser = re.compile(r".+/hub/(?P<hub_name>[_\-\w]+)/?$")

"""
Possible datetime formats:
"13 октября 2017 в 14:44"
"сегодня в 14:38"
"вчера в 17:24"
datetime_parsing_template = re.compile(r"(?P<date>.+) в (?P<hours>\d\d):(?P<minutes>\d\d)$")
Ну его в баню. беру готовую библиотеку dateparser ^:)
datetime.datetime(2020, 11, 13, 14, 44)
"""


class UrlParseException(Exception):
    pass

class PaginationParseException(Exception):
    pass


def get_pagination_range(html_text):
    """
    Finds firs an last page from pagination
    :param html_text:
    :return:
    """
    html_parser = BeautifulSoup(html_text, 'html.parser')

    pagination_list = html_parser.find_all('li', {'class': "toggle-menu__item toggle-menu__item_pagination"})
    if pagination_list is None:
        raise PaginationParseException('Pagination parse error!')

    first_li = pagination_list[0].find('span').text
    # page_num_href = last_li.find('a', {"class":"toggle-menu__item-link toggle-menu__item-link_pagination toggle-menu__item-link_bordered"})['href']
    # page_num_group = page_num_parser.search(page_num_href)
    page_num = first_li  # int(page_num_group.group('page'))
    first_page = int(page_num)

    last_li = pagination_list[-1]
    page_num_href = last_li.find('a', {
        "class": "toggle-menu__item-link toggle-menu__item-link_pagination toggle-menu__item-link_bordered"})['href']
    page_num_group = page_num_parser.search(page_num_href)
    page_num = int(page_num_group.group('page'))
    last_page = int(page_num)

    return first_page, last_page


async def get_post_content(post_url, session):
    """
    Parses post content
    :param post_url:
    :param session:
    :return:
    """
    async with session.get(post_url) as response:
        html_body = await response.read()
        html_text = html_body.decode()
        post_soup = BeautifulSoup(html_text, 'html.parser')
        post_body = post_soup.find('div', {'class': "post__body post__body_full"})
        return str(post_body)


async def parse_posts(hub_html_content, session):
    """
    Parses posts from hub page, posts content including
    :param hub_html_content:
    :param session:
    :return: list of dicts with posts info
    """
    html_parser = BeautifulSoup(hub_html_content, 'html.parser')
    posts = dict()
    posts_list = html_parser.find_all('li', class_='content-list__item content-list__item_post shortcuts_item')
    # posts_list = parser.find_all('article', {'class': 'post post_preview'})
    #print(f'Found {len(posts_list)} posts')

    for item in posts_list:
        try:
            post_id_str = item.get('id')
            if post_id_str is None:
                # print(f"Can't parse post id string {item}")
                continue
            # print(f'Post id = {post_id}')
            search = id_parser_template.search(post_id_str)
            if search:
                group_search = search.group('id')
                if group_search:
                    post_id = int(group_search)
                else:
                    print('Cannot parse post id')
                    continue
            else:
                print('Cannot parse post id')
                continue

            #post content fenching and parsing
            post_author_link = item.find('a', class_='post__user-info user-info')['href']
            post_author_nickname = item.find('span',
                                             {'class': 'user-info__nickname user-info__nickname_small'}).text
            # search_nickname = author_nick_parser.search(post_author_link)
            # if search_nickname:
            #     post_author_nickname = search_nickname.group('nickname')
            # else:
            #     print("Can't parse user name!")
            #     continue
            post_date = item.find('span', class_='post__time').text
            post_title = item.find('a', class_='post__title_link').text
            post_link = str(item.find('a', class_='post__title_link')['href'])
            post_body = await get_post_content(post_link, session)  # switche off to fasten the procesing
            post_hash = str(hashlib.sha1(post_body.encode('utf-8')).hexdigest())  # switch off to fasten the procesing
            posts[post_id] = {
                'datetime': dateparser.parse(post_date),
                'title': post_title,
                'author_link': post_author_link,
                'author_nickname': post_author_nickname,
                'post_link': post_link,
                'body': post_body,
                'hash': post_hash
            }
            # print(posts)

        except Exception as ex:
            print(f'There is an exception {ex}')
    return posts


def parse_hubs(html_content):
    """
    Parses hub list page
    :param html_content:
    :return: list of hub dicts
    """
    html_parser = BeautifulSoup(html_content, 'html.parser')
    hubs_container = html_parser.find('ul', {'class': 'content-list content-list_hubs'})
    hubs_list = hubs_container.find_all('li', {'class': "content-list__item content-list__item_hubs table-grid js-subscribe_item"})
    #print(f'Found {len(hubs_list)} hubs')

    hubs = dict()
    for hub in hubs_list:
        try:
            hub_id_str = hub['id']
            # print(f'hub-id = {hub_id}')
            search = id_parser_template.search(hub_id_str)
            if search:
                group_search = search.group('id')
                if group_search:
                    hub_id = int(group_search)
                else:
                    print('Cannot parse hub id')
                    continue
            else:
                print('cannot parse hub id!')
                continue
            hub_name = hub.find('a', {'class': "list-snippet__title-link"}).text
            hub_description = hub.find('div', {'class': "list-snippet__desc"}).text
            hub_link = hub.find('a', {'class': "list-snippet__title-link"})['href']
            hubs[hub_id] = {
                'name': hub_name,
                'descriptor': hub_description,
                'link': hub_link
            }
        except Exception as ex:
            print(f'There is an exception in parsing hubs page: {ex}')

    return hubs
