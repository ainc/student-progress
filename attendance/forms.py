from django.forms import ModelForm

from django import forms

from .models import Class, ClassSession, Coach, Student, AttendanceRecord, StudentProfile

class ClassSessionForm(ModelForm):
	class Meta:
		model = ClassSession
		fields = ['coach']


class SignupForm(forms.Form):
	first_name = forms.CharField(max_length=30, label='First name')
	last_name = forms.CharField(max_length=30, label='Last name')
	email = forms.CharField(max_length=90, label='Email')
	number = forms.CharField(max_length=11, label='Phone')

	def signup(self, request, user):
		user.first_name = self.cleaned_data['first_name']
		user.last_name = self.cleaned_data['last_name']
		user.save()



