from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import redirect
from django.views.generic import FormView, ListView, DetailView, View
from .models import Hub, Post, EngineSettings#, TraceHub
from .settings import HUBS_MAIN_URL, FIRST_START, MAX_TASKS
import time
import asyncio
from .tasks import first_run
from .guts import Engine
from .forms import HabForm

engine = Engine()

def home(request):
    global FIRST_START
    global HUBS_MAIN_URL
    global MAX_TASKS
    global engine
    if request.method == 'GET':
        if FIRST_START:
            settings = EngineSettings.objects.all()
            if len(settings) == 0:
                print('First run! Initialization...')
                return render(request, 'engine/first_run.html')
            else:
                engine.run()
                return redirect('hub_list_url')
    elif request.method == 'POST':
        if FIRST_START:
            settings = EngineSettings.objects.all()
            if len(settings) == 0:
                print('Making settings...')
                t1 = time.time()
                first_run()
                t2 = time.time()
                print(f'Initialization complete. Total time: {t2-t1} seconds.')
                settings = EngineSettings()
                settings.first_run = False
                settings.hubs_main_url = HUBS_MAIN_URL
                settings.max_tasks = MAX_TASKS
                settings.save()
                FIRST_START = False
            else:
                settings[0].first_run = False
        engine.run()
    return redirect('hub_list_url')


class HubListView(ListView):
    model = Hub
    #template_name = 'engine/hub_list.html'
    context_object_name = 'hubs'

class HubSearchListView(View):
    model = Hub
    def get(self, request, *args, **kwargs):
        hub_id = request.get('pk')
        if hub_id is None:
            return Http404(f'Hub not found!')


class HubDetailView(View):
    def get(self, request, *args, **kwargs):
        # get request override
        hub_pk = self.kwargs['pk']

        hub = Hub.objects.get(pk__exact=hub_pk)
        if hub is None:
            return Http404(f'Not found: hub with id = {hub_pk}')

        context = dict()
        context['id'] = hub.id
        context['name'] = hub.name
        context['description'] = hub.description
        context['link'] = hub.link
        context['poll'] = hub.poll
        context['poll_interval'] = hub.poll_interval
        context['last_poll_date_time'] = hub.last_poll_date_time

        post_list = []
        post_qs = Post.objects.filter(hub__exact=hub)

        if len(post_qs):
            for post in post_qs:
                post_table_record = {
                    'id': post.id,
                    'date_time': post.date_time,
                    'title': post.title,
                    'author_name': post.author_name,
                    'author_link': post.author_link,
                    'link': post.link,
                    'body': post.body
                }
                post_list.append(post_table_record)

        context['posts'] = post_list

        return render(request, 'engine/hub_detail.html', context=context)


    def post(self, request, *args, **kwargs):
        # POST request processing
        global engine
        hub_pk = self.kwargs['pk']
        #context = dict()

        hub = Hub.objects.get(pk__exact=hub_pk)
        if hub is None:
            return Http404(f'Not found: hub with id = {hub_pk}')

        hub.poll_interval = int(request.POST.get('poll_interval'))
        new_poll = request.POST.get('poll')
        new_poll = True if new_poll == 'on' else False
        old_poll = hub.poll
        if new_poll != old_poll:
            hub.poll = new_poll
            if hub.poll == True:
                engine.start_tracking(hub.id, hub.link)
            elif hub.poll == False:
                engine.stop_tracking(hub.id)
        hub.save()

        return redirect('hub_list_url')
