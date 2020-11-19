import asyncio
from .models import Hub, Post
from .workers import init_fetch_hubs, fetch_all_hub_posts
from django.utils import timezone
#from asgiref.sync import async_to_sync, sync_to_async


from .settings import HUBS_MAIN_URL


def first_run():
    """
    Database initialization during the first run
    :return:
    """
    hubs = asyncio.run(init_fetch_hubs(HUBS_MAIN_URL))
    hubs = hubs[0]
    print(f"Initialization: found and fetched {len(hubs)} hubs in '{HUBS_MAIN_URL}'")

    for hub in hubs:
        new_hub = Hub()
        new_hub.id = hub
        new_hub.name = hubs[hub]['name']
        new_hub.description = hubs[hub]['descriptor']
        new_hub.link = hubs[hub]['link']
        new_hub.last_poll_date_time = timezone.now() # datetime.datetime.now()
        new_hub.poll_interval = 0
        new_hub.save()

        # commented because first start with posts fetching takes several minutes (up to 15).
        # async def fetch_posts():
        #     async with aiohttp.ClientSession() as session:
        #         tasks = [
        #             asyncio.create_task(fetch_all_hub_posts(new_hub.link, session, paginated_fetch=False)),
        #         ]
        #         posts_list = await asyncio.gather(*tasks)
        #         return posts_list
        # hubs = asyncio.run(init_fetch_hubs(HUBS_MAIN_URL))

        # posts = asyncio.run(fetch_all_hub_posts(new_hub.link, aiohttp.ClientSession(), paginated_fetch=False))
        # posts = posts[0]
        #
        # print(f"Initialization: found and fetched {len(posts)} posts in hub '{new_hub.name}' main page")
        #
        # for post in posts:
        #     new_post = Post()
        #     new_post.id = post
        #     new_post.hub = new_hub
        #     new_post.date_time = posts[post]['datetime']
        #     new_post.author_link = posts[post]['author_link']
        #     new_post.author_name = posts[post]['author_nickname']
        #     new_post.title = posts[post]['title']
        #     new_post.link = posts[post]['post_link']
        #     new_post.body = posts[post]['body']
        #     new_post.hash = posts[post]['hash']
        #     # post_dump = [
        #     # new_post.id,
        #     # new_post.hub,
        #     # new_post.date_time,
        #     # new_post.author_link,
        #     # new_post.author_name,
        #     # new_post.title,
        #     # new_post.link,
        #     # new_post.body,
        #     # new_post.hash
        #     #     ]
        #     # for i in post_dump:
        #     #     print(type(i))
        #     #     print(i)
        #     new_post.save()


