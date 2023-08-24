from django.urls import path

from . import views

urlpatterns = [
    path("feed/", views.feed, name="feed"),
    path("fetch/", views.fetch, name="fetch"),
    path("manage/", views.manage, name="manage"),
    path("loading/", views.loading, name="loading"),
    path("start_parsing/", views.start_parsing, name="start_parsing"),

]
