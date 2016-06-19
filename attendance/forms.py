from django.forms import ModelForm

from django import forms

from .models import Class, ClassSession, Coach, Student, AttendanceRecord, StudentProfile

from django.conf import settings

# class SignupForm(forms.Form):
# 	first_name = forms.CharField(max_length=30, label='First name')
# 	last_name = forms.CharField(max_length=30, label='Last name')
# 	email = forms.CharField(max_length=90, label='Email')
# 	number = forms.CharField(max_length=11, label='Phone')
# 	type_of_user = forms.ChoiceField(choices=(('student', 'student'), ('parent', 'parent'),))

# 	def signup(self, request, user):
# 		user.first_name = self.cleaned_data['first_name']
# 		user.last_name = self.cleaned_data['last_name']
# 		user.save()


# from allauth.account.forms import LoginForm as AllauthLoginForm

# class LoginForm(forms.Form):
    
#     def login(self, request, redirect_url=None):
        
#         response = super(LoginForm, self).login(request, redirect_url)
#         if request.user.is_authenticated():
#             redirect = settings.LOGIN_REDIRECT_URL.format(
#                 username=self.user.username)
#         else:
#             redirect = "/"
#         return HttpResponseRedirect(redirect)




