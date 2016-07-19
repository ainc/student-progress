from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.account.adapter import DefaultAccountAdapter
from django.conf import settings
from .models import Student, StudentProfile, Coach
from django.contrib.auth.models import User, Group

class SocialAccountAdapter(DefaultSocialAccountAdapter):
	def save_user(self, request, sociallogin, form=None):
		
		user = super(SocialAccountAdapter, self).save_user(request, sociallogin, form)

		first = 'New'
		last = 'User'

		if user.last_name:
			last = user.last_name

		if user.first_name:
			first = user.first_name

		profile_img_url = sociallogin.account.extra_data['avatar_url']

		#If this is a coach signing up then we'll create a coach account for them 
		if 'coach_signup' in request.session.keys():
			Coach.objects.create(first_name=first, last_name=last, user=user, profile_img_url=profile_img_url)

			#Add the coach to the coaches group
			group = Group.objects.get(name='coaches')
			user.groups.add(group)
			user.save()
			return user
		#Create our student here
		bio = ''
		if sociallogin.account.extra_data['bio']:
			bio = sociallogin.account.extra_data['bio']
		else:
			bio = 'Bio'
		profile = StudentProfile.objects.create(email=user.email, user=user, github_user_name=user.username, bio=bio, profile_img_url=profile_img_url)
		Student.objects.create(first_name=first, last_name=last, profile=profile)
		
		return user

	#This is where we extract more information from the github signup
	def populate_user(self, request, sociallogin, data):
		user = sociallogin.user
		user.username = data['username']

		if data['name']:
			names = data['name'].split()

			if len(names) == 1:
				user.first_name = names[0]
			elif len(names) == 2:
				user.first_name = names[0]
				user.last_name = names[1]

			elif len(names) > 2:
				user.first_name = names[0]
				user.last_name = names[len(names) -1]
			else:
				user.first_name = 'New'
				user.last_name = 'User'
		else:
			user.first_name = 'New'
			user.last_name = 'User'

		if data['name']:
			user.email = data['email']
		else:
			user.email = 'email@example.com'

		return user

	def get_connect_redirect_url(self, request, socialaccount):

		if hasattr(request.user, 'studentprofile'):
			path = '/student/{student_id}/'
			return path.format(student_id=request.user.studentprofile.student.student_id)

		#Coaches should see another view 
		elif hasattr(request.user, 'coach'):
			path = '/coach/dashboard/'

		else:
			path = '/'


class MyAccountAdapter(DefaultAccountAdapter):

	def save_user(self, request, user, form, commit=True):

		user = super(MyAccountAdapter, self).save_user(request, user, form)

		data = form.cleaned_data

		if data.get('type_of_user') == 'student':
			profile = StudentProfile.objects.create(email=user.email, user=user)
			Student.objects.create(first_name=user.first_name, last_name=user.last_name, profile=profile)



	def get_login_redirect_url(self, request):
		if hasattr(request.user, 'studentprofile'):
			path = "/student/{student_id}/"
			return path.format(student_id=request.user.studentprofile.student.student_id)

		#Coaches should see another view 
		if hasattr(request.user, 'coach'):
			path = "/coach/dashboard/"
			return path

		return "/"