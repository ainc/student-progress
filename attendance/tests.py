from django.test import TestCase, Client, RequestFactory
from django.contrib.auth.models import User, Group
import datetime
from . import views

#Basic attendance testing

from .models import Coach, Student, StudentProfile, StudentGuardian, Relationship, Enrollment, CoachNote, StudentGoal, Class, ClassSession, AttendanceRecord, Team, TeamMember, Skill, Subskill

from django.contrib.sessions.middleware import SessionMiddleware

def add_session_to_request(request):
    """Annotate a request object with a session"""
    middleware = SessionMiddleware()
    middleware.process_request(request)
    request.session.save()

class StudentProgress(TestCase):

	def setUp(self):
		self.factory = RequestFactory(enforce_csrf_checks=True)
		self.user = User.objects.create_user(username='jacob', email='jacob@…', password='top_secret')
		self.profile = StudentProfile.objects.create(user=self.user, bio='hello world')
		self.student = Student.objects.create(profile=self.profile, first_name='jacob', last_name='miller')
		self.c = Client()
		self.skill = Skill.objects.create(title='django')
		self.subskill = Subskill.objects.create(skill=self.skill, description='Learn automated testing')

		self.coach_user = User.objects.create_user(username='jon', email='jon@…', password='top_secret')
		
		group = Group.objects.create(name='coaches')
		self.coach_user.groups.add(group)
		self.coach = Coach.objects.create(user=self.coach_user, first_name='Jon', last_name='Hzovanic')

		self.new_class = Class.objects.create(class_name='Test')

    #Tests that don't require an authenticated user
	def test_get_home(self):
		response = self.c.get('/', {})
		self.assertEqual(response.status_code, 200)

	def test_get_login(self):
		response = self.c.get('/login/', {})
		self.assertEqual(response.status_code, 200)
	
	def test_get_signup(self):
		response = self.c.get('/signup/', {})
		self.assertEqual(response.status_code, 200)

	def test_get_coaches_signup(self):
		response = self.c.get('/signup/coaches/', {})
		self.assertEqual(response.status_code, 200)

	#Tests that require a logged in user

	def test_student_login(self):
		request = self.factory.get('/student/' + str(self.student.student_id))

		# Recall that middleware are not supported. You can simulate a
		# logged-in user by setting request.user manually.
		request.user = self.user

		# Test my_view() as if it were deployed at /customer/details
		response = views.student_profile(request, self.student.student_id)
		self.assertEqual(response.status_code, 200)

	def test_coach_login(self):
		request = self.factory.get('/coach/' + str(self.coach.coach_id))

		# Recall that middleware are not supported. You can simulate a
		# logged-in user by setting request.user manually.
		request.user = self.coach_user

		# Test my_view() as if it were deployed at /customer/details
		response = views.classes_for_coach(request, self.coach.coach_id)
		self.assertEqual(response.status_code, 200)

	def test_coach_dashboard(self):
		request = self.factory.get('/coach/dashboard/')

		# Recall that middleware are not supported. You can simulate a
		# logged-in user by setting request.user manually.
		request.user = self.coach_user

		# Test my_view() as if it were deployed at /customer/details
		response = views.coach_dashboard(request)
		self.assertEqual(response.status_code, 200)

	def test_post_login(self):

		request = self.factory.post('/login/', {'username': 'jacob', 'password': 'top_secret'})
		add_session_to_request(request)

		response = views.login(request)
		self.assertEqual(response.status_code, 302)

		request = self.factory.post('/login/', {'username': 'jon', 'password': 'top_secret'})
		add_session_to_request(request)

		response = views.login(request)
		self.assertEqual(response.status_code, 302)

	def test_leave_note(self):
		request = self.factory.post('/student/' + str(self.student.student_id) + '/notes/leave', {'note': '12345'})
		request.user = self.coach_user
		add_session_to_request(request)

		response = views.leave_note(request, self.student.student_id)
		note = CoachNote.objects.get(pk=1)
		self.assertEqual('12345', note.note)
		self.assertEqual(response.status_code, 302)


	def test_set_goal(self):
		request = self.factory.post('/student/' + str(self.student.student_id) + '/goals/set', {'goal': '12345'})
		request.user = self.user
		add_session_to_request(request)

		response = views.set_goal(request, self.student.student_id)
		goal = StudentGoal.objects.get(pk=1)
		self.assertEqual('12345', goal.description)
		self.assertEqual(response.status_code, 302)

	def test_enroll_student(self):
		request = self.factory.post('/coach/' + str(self.coach.coach_id) + '/enroll/' + str(self.new_class.class_id) + '/', {'student': [self.student.student_id]})
		request.user = self.coach_user
		add_session_to_request(request)

		response = views.enroll(request, self.coach.coach_id, self.new_class.class_id)
		enroll = Enrollment.objects.get(student=self.student)
		self.assertEqual(self.student, enroll.student)
		self.assertEqual(response.status_code, 302)




