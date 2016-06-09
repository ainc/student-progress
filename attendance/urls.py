from django.conf.urls import url
from django.contrib import admin
from django.contrib.auth import views as auth_views

from . import views 

urlpatterns = [
    url(r'^$', views.home_page, name='home_page'),
    url(r'^roster/(?P<coach_id>\d+)/(?P<class_id>\d+)/$', views.class_roster, name='class_roster'),
    url(r'^attendance/(?P<coach_id>\d+)/(?P<class_id>\d+)/(?P<session_id>\d+)$', views.class_session, name='class_session'),
    url(r'^coach/(?P<coach_id>\d+)/classes/$', views.classes_for_coach, name='classes_for_coach'),
    url(r'^attendance/overview/(?P<coach_id>\d+)/(?P<class_id>\d+)/$', views.class_overview, name='class_overview'),
    url(r'^coach/(?P<coach_id>\d+)/enroll/(?P<class_id>\d+)/$', views.enroll, name='enroll_student'),
    url(r'^coach/(?P<coach_id>\d+)/create_session/(?P<class_id>\d+)/$', views.create_session, name='create_session'),
    url(r'^login/$', views.login, name='login'),
    url(r'^signup/$', views.signup, name='signup'),
    url(r'^signup/coaches/$', views.coach_signup, name='coach_signup'),
    url(r'^student/(?P<student_id>\d+)/$', views.student_profile, name='student_profile'),
    url(r'^student/(?P<student_id>\d+)/update/$', views.update_profile, name='update_profile'),
    url(r'^student/(?P<student_id>\d+)/notes/$', views.student_notes, name='student_notes'),
    url(r'^student/(?P<student_id>\d+)/notes/leave/$', views.leave_note, name='leave_note'),

 ]
