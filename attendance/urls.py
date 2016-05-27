from django.conf.urls import url
from django.contrib import admin

from . import views 

urlpatterns = [
    url(r'^$', views.home_page, name='home_page'),
    url(r'^roster/(?P<coach_id>\d+)/(?P<class_id>\d+)/$', views.class_roster, name='class_roster'),
]
