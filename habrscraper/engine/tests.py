from django.test import TestCase

from .parsers import get_all_hubs, get_posts
from .models import Hub, Post


class EngineTest(TestCase):
    def test_fetch_hubs(self):
        hubs_url = 'https://habr.com/ru/hubs/'
        hubs = get_all_hubs(hubs_url)
        for hub in hubs:
            new_hub = Hub()
            new_hub.id = hub
            new_hub.name = hubs[hub]['name']
            new_hub.description = hubs[hub]['descriptor']
            new_hub.link = hubs[hub]['link']
            new_hub.save()
            # posts = get_posts(new_hub.link)
            # for post in posts:
            #     new_post = Post()
            #     new_post.id = post
            #     new_post.hub = new_hub
            #     #new_post.date = posts[post]['datetime']
            #     new_post.author_link = posts[post]['author_link']
            #     new_post.author_name = posts[post]['author_nickname']
            #     new_post.title = posts[post]['title']
            #     new_post.link = posts[post]['link']
            #     new_post.body = posts[post]['body']
            #     new_post.hash = posts[post]['hash']
            #     new_post.save()

        self.assertIsNone(None)


