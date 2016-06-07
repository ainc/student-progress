from django.forms import ModelForm

from .models import Class, ClassSession, Coach, Student, AttendanceRecord, StudentProfile

class ClassSessionForm(ModelForm):
	class Meta:
		model = ClassSession
		fields = ['coach']