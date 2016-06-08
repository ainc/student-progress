from django.shortcuts import get_object_or_404, render, redirect
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from .models import Enrollment, Coach, Student, ClassSession, AttendanceRecord, Class, StudentProfile
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User 
from django.contrib.auth import login as login_user
from django.db import IntegrityError
# Create your views here.

def home_page(request):
	return render(request, 'attendance/home_page.html', {})


#View to render the roster for a coach and a class
@login_required
def class_roster(request, coach_id, class_id):
	coach = get_object_or_404(Coach, pk=coach_id)
	clas = get_object_or_404(Class, pk=class_id)
	query_set = Enrollment.objects.filter(coach=coach, _class=clas)

	return render(request, 'attendance/roster.html', {'roster': query_set, 'coach': coach, 'class': clas})

#View to render the roster and the edit attendance for a coach, a class, and a class session
@login_required
def class_session(request, coach_id, class_id, session_id):
	coach = get_object_or_404(Coach, pk=coach_id)
	clas = get_object_or_404(Class, pk=class_id)
	session = get_object_or_404(ClassSession, pk=session_id)
	query_set = Enrollment.objects.filter(coach=coach, _class=clas)

	#Get all of the students in alphabetical order for this particular session 
	student_records = AttendanceRecord.objects.filter(coach=coach, _class=clas, session=session).order_by('student__last_name')

	#For posts we'll update the data or create a new attendance record 
	if request.method == 'POST':

		#For all the enrollment objects in the query set
		for record in query_set:
			attended = False
			note = str(request.POST.get('note-' + str(record.student.student_id) ))
			if str(record.student.student_id) in request.POST.getlist('attended'):
				attended = True

			#Either update the existing record or create a new one
			try:
				#Get the old record and update it
				rec = AttendanceRecord.objects.get(coach=coach, session=session, student=record.student, _class=clas)
				rec.attended = attended
				if note != '':
					rec.note = note
				rec.save()
			except AttendanceRecord.DoesNotExist:
				#Create a new record then
				AttendanceRecord.objects.create(coach=coach, session=session, student=record.student, _class=clas, attended=attended, note=note)
		
		return HttpResponseRedirect(reverse('attendance:class_overview', args=(coach.coach_id, clas.class_id)))
	#Get requests will render a table full of attendance elements 
	else:
		isUpdate = False
		#If there are no previous attendance records, we'll notify the view that we shouldn't prepopulate the table 
		if len(student_records) != 0:
			isUpdate = True

		#Render the session template
		return render(request, 'attendance/session.html', {'roster': query_set, 'coach': coach, 'class': clas, 'session': session, 'isUpdate': isUpdate, 'old_records': student_records})


@login_required
def classes_for_coach(request, coach_id):
	coach = get_object_or_404(Coach, pk=coach_id)
	#This query will return a dictionary of all the unique classes this coach teaches
	classDicts = ClassSession.objects.filter(coach=coach).values('_class').distinct()
	classes = []
	#For all those dicts, we'll extract and lookup the actual class
	for value in classDicts:
		entryDict = {}
		entryDict["class"] = Class.objects.get(pk=value['_class'])
		entryDict["class_id"] = value['_class']
		classes.append(entryDict)

	return render(request, 'attendance/class_list.html', {'classes': classes, 'coach': coach})


#View to show an attendance overview for each student--showing how often they have come to the class
@login_required
def class_overview(request, class_id, coach_id):
	#Get the coach, class, and students
	coach = get_object_or_404(Coach, pk=coach_id)
	clas = get_object_or_404(Class, pk=class_id)
	sessions = ClassSession.objects.filter(coach=coach, _class=clas).order_by('class_date')
	enrollments = Enrollment.objects.filter(coach=coach, _class=clas).order_by('student__last_name')

	students_in_class = []
	student_attendance_records = []

	#Parse the students in the class
	for record in enrollments:
		students_in_class.append(record.student)
	
	#For each session, find the attendance record 
	for session in sessions:

		#A session dict will look like {'session': ClassSession, 'records': [{'note': 'Missed', 'attended': '-'}, {'note': '', 'attended': 'x'}, {'note': 'Hodor', 'attended': '-'}'}
		sessionDict = {}

		sessionDict['session'] = session
		students_records = []
		for student in students_in_class:
			student_record_dict = {}
			ar = AttendanceRecord.objects.filter(coach=coach, _class=clas, student=student, session=session)
			#If there is no record, then we'll populate the dictionary with a temporary value
			if len(ar) == 0:
				student_record_dict['attended'] = '/'
				student_record_dict['note'] = ''
			else:
				#Otherwise, store the attended/note from the AttendanceRecord
				if ar[0].attended:
					student_record_dict['attended'] = 'x'
				else:
					student_record_dict['attended'] = '-'
				student_record_dict['note'] = ar[0].note
			students_records.append(student_record_dict)

		#Records will be an array 
		sessionDict['records'] = students_records
		student_attendance_records.append(sessionDict)

	return render(request, 'attendance/overview.html', {'coach': coach, 'class': clas,  'sessions':sessions, 'records': student_attendance_records, 'students': students_in_class})


#For a signup request
def signup(request):

	#If it's a post then we'll authenticate and store the data entered
	if request.method == 'POST':
		username = request.POST['username']
		email = request.POST['email']
		password = request.POST['password']
		first_name = request.POST['first_name']
		last_name = request.POST['last_name']

		try:

			#Create a user object for these fields
			user = User.objects.create_user(username, email, password)
			user.first_name = first_name
			user.last_name = last_name
			user.save()
			user = authenticate(username=username, password=password)
			login_user(request, user)
		except IntegrityError as e:
			return render(request, 'attendance/signup.html', {'duplicate_key': True, 'first_name': first_name, 'last_name':last_name, 'email': email, 
				'username': '' })

		#Now we need to know which type of user we are registering
		type_of_user = request.POST['type']

		#For students we will need to create a profile 
		if type_of_user == 'Student':
			profile = StudentProfile.objects.create(email=email, user=user)
			student = Student.objects.create(first_name=first_name, last_name=last_name, profile=profile)
			
			return redirect('attendance:student_profile', student_id=student.student_id)
			#return render(request, 'attendance/student_profile.html', {'student': student, 'profile': profile, 'can_edit': True, 'should_update': True})
		#For parents we have to make sure they approved to view their student's information
		elif type_of_user == 'Parent':
			return render(request, 'attendance/guardian_reg.html', {'first_name': first_name, 'last_name': last_name, 'email': email})

	#Get requests will return the signup html page
	else:
		return render(request, 'attendance/signup.html', {'duplicate_key': False, 'first_name': 
			'', 'last_name':'', 'email': '', 
				'username': '' })


#View for a standard login page
def login(request):

	#post will authenticate a user 
	if request.method == 'POST':
		username = request.POST['username']
		password = request.POST['password']
		user = authenticate(username=username, password=password)
		#If the user was authenticated, then we'll log them in
		if user is not None:
			if user.is_active:
				login_user(request, user)
				#Take them to their profile if they have one (aka a student, not a parent)
				if user.studentprofile:
					student = Student.objects.get(profile=user.studentprofile)

					return redirect('attendance:student_profile', student_id=student.student_id)
				else:
					return redirect('attendance:home_page.html')
			else:
				print('not active')
				return render(request, 'attendance/login.html', {'error': True})
		else:
			print('none')
			return render(request, 'attendance/login.html', {'not_found': True})

	else:
		return render(request, 'attendance/login.html')

@login_required
#View to show a student profile. This will have two views--depending on if the user is authenticated or not
def student_profile(request, student_id):
	#Users have to be logged in to see this page
	if request.user.is_authenticated():
		student = get_object_or_404(Student, pk=student_id)
		profile = student.profile
		return render(request, 'attendance/student_profile.html', {'student': student, 'profile': profile})

	else:
		return render(request, 'attendance/login.html')
	
#View for editing a student profile 
@login_required
def update_profile(request, student_id):

	#First authenticate the user to see if they can edit this profile 
	if request.user.is_authenticated():
		#Then grab the current user's information 
		student = get_object_or_404(Student, pk=student_id)
		profile = student.profile
		#If the current user's profile matches the one they are trying to edit, then they are authorized 
		if request.user.studentprofile == profile:
			print('Okay for update')
			#Dissect a post request 
			if request.method == 'POST':
				#Get all fields that could be updated 
				email = request.POST['email']
				bio = request.POST['bio']
				phone = request.POST['phone']
				github_username = request.POST['github_username']
				first_name = request.POST['first_name']
				last_name = request.POST['last_name']

				#Update the fields
				profile.bio = bio
				profile.email = email
				profile.github_user_name = github_username
				profile.phone = phone
				student.first_name = first_name
				student.last_name = last_name

				#Save the objects again
				profile.save()
				student.save()

				#Return the user to their updated profile page
				return HttpResponseRedirect(reverse('attendance:student_profile', args=(student.student_id,)))

			#GET requests should show the update page 
			else:
				return render(request, 'attendance/update_profile.html', {'student': student, 'profile': profile})

		#If not the user, show them an unauthorized message. Filthy trickses, nasty hobbitses
		else:
			return HttpResponse('Unauthorized')
	#No precious, they musnt access this page 
	else:
		return HttpResponse('Unauthorized')



	

