from django.urls import path, re_path
from . import views
from .views import EventView

urlpatterns = [

    path("", views.EventView, name="eventView"),
]