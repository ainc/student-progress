from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.account.adapter import DefaultAccountAdapter
from django.conf import settings
from .models import Student, StudentProfile 

class SocialAccountAdapter(DefaultSocialAccountAdapter):
	def save_user(self, request, sociallogin, form=None):
		user = super(SocialAccountAdapter, self).save_user(request, sociallogin, form)
		print(form)
		#Create our student here
		profile = StudentProfile.objects.create(email=user.email, user=user, github_user_name=user.username, bio=sociallogin.account.extra_data['bio'], profile_img_url=sociallogin.account.extra_data['avatar_url'])
		Student.objects.create(first_name=user.first_name, last_name='', profile=profile)
		
		return user

	#This is where we extract more information from the github signup
	def populate_user(self, request, sociallogin, data):
		user = sociallogin.user
		user.username = data['username']
		user.first_name = data['name']
		user.email = data['email']

		return user

	def get_connect_redirect_url(self, request, socialaccount):

		return settings.LOGIN_REDIRECT_URL.format(student_id=socialaccount.user.studentprofile.student.student_id)


class MyAccountAdapter(DefaultAccountAdapter):

	def get_login_redirect_url(self, request):
		if hasattr(request.user, 'studentprofile'):
			path = "/student/{student_id}/"
			return path.format(student_id=request.user.studentprofile.student.student_id)