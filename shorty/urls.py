from django.urls import path
from django.conf import settings
from . import views

urlpatterns = [
    path('', views.all_links, name='all_links'),
    # path('create/', views.create_link, name='create_link'),
    # path('done/', views.create_done, name='create_done'),
]