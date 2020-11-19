import asyncio
import aiohttp
import datetime
import threading


from .models import Hub, Post
from .workers import fetch_all_hub_posts, main_posts
from .settings import MAX_TASKS



class HubPollTask:
    #  Hub posts tracker \ fetches new posts
    def __init__(self, hub_id, hub_url, poll_interval):
        self._hub_id = hub_id
        self._hub_url = hub_url
        self._poll_interval = poll_interval
        #self._session = session #aiohttp.ClientSession()  #  one session for each_hub
        self._posts_id_cash = []
        self._active = False
        #print(f'Poll task created for hub {self._hub_id} {self._hub_url}...')

    def __del__(self):
        self._active = False

    def run(self):
        self._active = True

    def stop(self):
        self._active = False
        #if not self._active:
            #self._posts_id_cash = [] #  cash flush.

    async def reset(self, session, sem):
        hub_posts = await fetch_all_hub_posts(self._hub_url, session, sem)  # only first page of the hub!
        self._posts_id_cash.extend(list(hub_posts.keys()))  # cash for posts id, init

    async def step(self, session, sem, queue):

        while True:
            if self._active:
                print(f'Poll cycle for hub {self._hub_id} {self._hub_url}...')
                hub_posts = await fetch_all_hub_posts(self._hub_url, session, sem) #  need option 'skip content'
                posts_id_cash = set(hub_posts.keys())
                new_posts = set(self._posts_id_cash) ^ posts_id_cash
                msg = dict()

                if new_posts:
                    print(f'new posts in {self._hub_id} {self._hub_url}:')
                    for post in new_posts:
                        print(f'new post in{self._hub_id} {self._hub_url} : {post}')

                        #  might be wrapped on JSON....
                        msg[self._hub_id] = {'posts': hub_posts[post], 'date_time': datetime.datetime.now()}
                        await queue.put(msg)
                else:
                    msg[self._hub_id] = {'posts': None, 'date_time': datetime.datetime.now()} #last poll time need to be updated in DB
                    await queue.put(msg)

                #await self._queue.put(None) #  finished with the queue
            await queue.put(None)  # finished with the queue
            await asyncio.sleep(self._poll_interval)


class HubDbUpdater:
    #  reads queue and pushes new posts into DB if Hub is tracked
    def __init__(self):
        self._hubs_id_cash = []
        self._active = False

    def __del__(self):
        self._active = False

    def run(self):
        self._active = True

    def stop(self):
        self._active = False

    async def loop(self, queue):
        while True:
            if self._active:
                msg = await queue.get()
                if msg:
                    print(f'Updater got msg: {msg}')
                    hub_id = msg.keys()[0]
                    hub = Hub.objects.get(id=hub_id)
                    hub.last_poll_date_time = msg['date_time']
                    posts = msg['posts']

                    if posts is not None:
                        for post in posts:
                            new_post = Post()
                            new_post.id = post
                            new_post.hub = hub
                            new_post.date_time = posts[post]['datetime']
                            new_post.author_link = posts[post]['author_link']
                            new_post.author_name = posts[post]['author_nickname']
                            new_post.title = posts[post]['title']
                            new_post.link = posts[post]['post_link']
                            new_post.body = posts[post]['body']
                            new_post.hash = posts[post]['hash']
                            # post_dump = [
                            # new_post.id,
                            # new_post.hub,
                            # new_post.date_time,
                            # new_post.author_link,
                            # new_post.author_name,
                            # new_post.title,
                            # new_post.link,
                            # new_post.body,
                            # new_post.hash
                            #     ]
                            # for i in post_dump:
                            #     print(type(i))
                            #     print(i)
                            new_post.save()
                        hub.save()
            await asyncio.sleep(0.01)


class TaskManager:
    _hub_tasks = dict()

    def __init__(self):
        hub_qs = Hub.objects.all()

        for hub in hub_qs:
            task = HubPollTask(hub.id,
                               hub.link,
                               hub.poll_interval)
            TaskManager._hub_tasks[hub.id] = task

    def add_task(self, hub_id, hub_url):
        print(f'Adding poll task for hub {hub_id} {hub_url}')
        if hub_id in TaskManager._hub_tasks.keys():
            TaskManager._hub_tasks[hub_id].run()  #  task reactivation is not tested (seems not working)!!!

    def del_task(self, hub_id):
        print(f'Removing poll task for hub {hub_id} ')
        if hub_id in TaskManager._hub_tasks.keys():
            TaskManager._hub_tasks[hub_id].stop()

    async def loop(self, queue):
        session = aiohttp.ClientSession()
        sem = asyncio.Semaphore(MAX_TASKS)
        for _, task in TaskManager._hub_tasks.items():  # first poll task run: reset new posts
            await task.reset(session, sem)

        while True:  # main polling loop
            for _, task in TaskManager._hub_tasks.items():
                await task.step(session, sem)


class Engine:
    #  singleton

    _engine_count = 0

    def __init__(self):
        if Engine._engine_count > 0:
            raise Exception("Only one Engine instance may exists!")
        self._engine_count += 1
        self._task_manager = TaskManager()
        self._hub_db_updater = HubDbUpdater()

    def start_tracking(self, hub_id, hub_url):
        self._task_manager.add_task(hub_id, hub_url)

    def stop_tracking(self, hub_id):
        self._task_manager.del_task(hub_id)

    def engine_main(self):
        coros = []
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        queue = asyncio.Queue(loop=loop)

        self._hub_db_updater.run()
        coros.append(self._hub_db_updater.loop(queue))
        coros.append(self._task_manager.loop(queue))

        loop.run_until_complete(asyncio.gather(*coros))
        loop.close()

    def run(self):
        thread = threading.Thread(target=self.run)
        thread.start()
