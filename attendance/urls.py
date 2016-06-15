from django.conf.urls import url
from django.contrib import admin
from django.contrib.auth import views as auth_views

from . import views 

urlpatterns = [
    url(r'^$', views.home_page, name='home_page'),
    url(r'^coach/(?P<coach_id>\d+)/roster/(?P<class_id>\d+)/$', views.class_roster, name='class_roster'),
    url(r'^coach/(?P<coach_id>\d+)/attendance/(?P<class_id>\d+)/session/(?P<session_id>\d+)$', views.class_session, name='class_session'),
    url(r'^coach/(?P<coach_id>\d+)/classes/$', views.classes_for_coach, name='classes_for_coach'),
    url(r'^coach/(?P<coach_id>\d+)/class/(?P<class_id>\d+)/$', views.class_overview, name='class_overview'),
    url(r'^coach/(?P<coach_id>\d+)/enroll/(?P<class_id>\d+)/$', views.enroll, name='enroll_student'),
    url(r'^coach/(?P<coach_id>\d+)/create_session/(?P<class_id>\d+)/$', views.create_session, name='create_session'),
    url(r'^login/$', views.login, name='login'),
    url(r'^signup/$', views.signup, name='signup'),
    url(r'^signup/coaches/$', views.coach_signup, name='coach_signup'),
    url(r'^student/(?P<student_id>\d+)/$', views.student_profile, name='student_profile'),
    url(r'^student/(?P<student_id>\d+)/update/$', views.update_profile, name='update_profile'),
    url(r'^student/(?P<student_id>\d+)/notes/$', views.student_notes, name='student_notes'),
    url(r'^student/(?P<student_id>\d+)/notes/leave/$', views.leave_note, name='leave_note'),
    url(r'^student/(?P<student_id>\d+)/goals/$', views.student_goals, name='student_goals'),
    url(r'^student/(?P<student_id>\d+)/goals/set/$', views.set_goal, name='set_goal'),
    url(r'^student/(?P<student_id>\d+)/goals/mark/(?P<goal_id>\d+)/$', views.mark_goal, name='mark_goal'),
    url(r'^student/(?P<student_id>\d+)/skills/$', views.student_skills, name='student_skills'),
    url(r'^student/(?P<student_id>\d+)/skill/(?P<skill_id>\d+)/subskills/$', views.skill_overview, name='skill_overview'),


 ]
