from django.shortcuts import render
from django.http import HttpResponse
from .models import Enrollment, Coach, Student, ClassSession, AttendanceRecord, Class

# Create your views here.

def home_page(request):
	return render(request, 'attendance/home_page.html', {})

def class_roster(request, coach_id, class_id):
	coach = Coach.objects.get(pk=coach_id)
	clas = Class.objects.get(pk=class_id)
	query_set = Enrollment.objects.filter(coach=coach, _class=clas)

	return render(request, 'attendance/roster.html', {'roster': query_set, 'coach': coach, 'class': clas})