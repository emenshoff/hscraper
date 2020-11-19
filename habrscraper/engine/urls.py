
from django.contrib import admin
from django.urls import path
from django.urls import include

from .views import HubListView, home, HubSearchListView,  HubDetailView

urlpatterns = [
    path('', home, name='home_url'),
    path('hubs/', HubListView.as_view(), name='hub_list_url'),
    path('hub/<int:pk>/', HubDetailView.as_view(), name='hub_detail_url'),
    #path('hubs/<int:pk>', HubSearchListView.as_view(), name='hub_search_url'),
    #path('posts/', PostListView.as_view(), 'post_list_url'),

]
