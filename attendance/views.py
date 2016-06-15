from django.shortcuts import get_object_or_404, render, redirect
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from .models import Enrollment, Coach, Student, ClassSession, AttendanceRecord, Class, StudentProfile, StudentGoal, CoachNote, Skill, Subskill, StudentProgress
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User, Group
from django.contrib.auth import login as login_user
from django.db import IntegrityError
# Create your views here.
from datetime import datetime

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
				if hasattr(user, 'studentprofile'):
					student = Student.objects.get(profile=user.studentprofile)

					return redirect('attendance:student_profile', student_id=student.student_id)
				elif hasattr(user, 'coach'):
					return redirect('attendance:classes_for_coach', coach_id=user.coach.coach_id)
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
		enrollments = Enrollment.objects.filter(student=student).values_list('_class', 'coach_id')
		upcoming_sessions = []
		for clas in enrollments:
			dic = {}
			dic['class'] = get_object_or_404(Class, pk=clas[0])
			dic['coach'] = get_object_or_404(Coach, pk=clas[1])
			dic['sessions'] = ClassSession.objects.filter(coach=clas[1], _class=clas[0], class_date__gte=datetime.now()).order_by('class_date')
			upcoming_sessions.append(dic)
		
		goals_met = StudentGoal.objects.filter(student=student, met=True)
		goals_set = StudentGoal.objects.filter(student=student)

		notes = CoachNote.objects.filter(student=student)

		skills = Subskill.objects.all()
		skills_met = StudentProgress.objects.filter(student=student, achieved=True)
		return render(request, 'attendance/student_profile.html', {'student': student, 'profile': profile, 'upcoming': upcoming_sessions, 'goals_met': len(goals_met), 'goals_set': len(goals_set), 'notes': len(notes), 'skills': len(skills), 'skills_met': len(skills_met)})

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

#View for viewing student notes
@login_required
def student_notes(request, student_id):

	#First authenticate the user to see if they can edit this profile 
	if request.user.is_authenticated():
		#Then grab the current user's information 
		student = get_object_or_404(Student, pk=student_id)
		#Dissect a post request 
		if request.method == 'POST':
			#Get all fields that could be updated 
			
			#Return the user to their updated profile page
			return HttpResponseRedirect(reverse('attendance:student_profile', args=(student.student_id,)))

		#GET requests should show the update page 
		else:
			notes = CoachNote.objects.filter(student=student)
			return render(request, 'attendance/notes.html', {'student': student, 'notes': notes})
	#No precious, they musnt access this page 
	else:
		return HttpResponse('Unauthorized')


#Have a view for coaches to signup
def coach_signup(request):
	#If it's a post then we'll authenticate and store the data entered
	if request.method == 'POST':

		username = request.POST['username']
		email = request.POST['email']
		password = request.POST['password']
		first_name = request.POST['first_name']
		last_name = request.POST['last_name']
			
		if request.POST['coach_phrase'] == 'rule #22':
			print('pass correct')
			try:

				#Create a user object for these fields
				user = User.objects.create_user(username, email, password)
				user.first_name = first_name
				user.last_name = last_name
				user.is_staff = True
				#Add the coach to the coaches group
				group = Group.objects.get(name='coaches')
				user.groups.add(group)
				#Associate this coach with this user
				coach = Coach.objects.create(first_name=first_name, last_name=last_name, user=user)
				user.save()
				user = authenticate(username=username, password=password)
				login_user(request, user)

				return HttpResponseRedirect(reverse('attendance:classes_for_coach', args=(coach.coach_id,)))
			except IntegrityError as e:
				print(e)
				#Take them back to the page to correct errors
				return render(request, 'attendance/coach_portal.html', {'duplicate_key': True, 'first_name': first_name, 'last_name':last_name, 'email': email, 
					'username': '' })
		#Wrong pass phrases return
		else:
			#Take them back to the page to correct errors
			return render(request, 'attendance/coach_portal.html', {'duplicate_key': False, 'first_name': first_name, 'last_name':last_name, 'email': email, 
				'username': username, 'wrong_phrase': True })

	#Get requests will return the signup html page
	else:
		return render(request, 'attendance/coach_portal.html', {'duplicate_key': False, 'first_name': 
			'', 'last_name':'', 'email': '', 
				'username': '' })

#Decorator method to help us check if the user is a coach
def group_check(user):
    return user.groups.filter(name__in=['coaches'])

#For the leave note view we make the user has coach permissions
@user_passes_test(group_check)
def leave_note(request, student_id):
	if request.user.is_authenticated():

		student = get_object_or_404(Student, pk=student_id)
		#Then we create a new coach note object 
		if request.method == 'POST':
			note = request.POST['note']
			CoachNote.objects.create(coach=request.user.coach, note=note, student=student)
			return HttpResponseRedirect(reverse('attendance:student_notes', args=(student_id)))
		else:
			return render(request, 'attendance/leave_note.html', {'student': student})

	else: 
		return HttpResponse('Unauthorized')



#View for editing a student profile 
@login_required
def set_goal(request, student_id):

	#First authenticate the user to see if they can edit this profile 
	if request.user.is_authenticated():
		#Then grab the current user's information 
		student = get_object_or_404(Student, pk=student_id)
		profile = student.profile
		#If the current user's profile matches the one they are trying to edit, then they are authorized 
		if request.user.studentprofile == profile:
			#Dissect a post request 
			if request.method == 'POST':
				#Get all fields that could be updated 
				goal = request.POST['goal']
				StudentGoal.objects.create(description=goal, student=student)

				#Return the user to their updated profile page
				return HttpResponseRedirect(reverse('attendance:student_goals', args=(student.student_id,)))

			#GET requests should show the update page 
			else:
				return render(request, 'attendance/set_goal.html', {'student': student})

		#If not the user, show them an unauthorized message. Filthy trickses, nasty hobbitses
		else:
			return HttpResponse('Unauthorized')
	#No precious, they musnt access this page 
	else:
		return HttpResponse('Unauthorized')

#View for editing a student profile 
@login_required
def mark_goal(request, student_id, goal_id):

	#First authenticate the user to see if they can edit this profile 
	if request.user.is_authenticated():
		#Then grab the current user's information 
		student = get_object_or_404(Student, pk=student_id)
		profile = student.profile
		#If the current user's profile matches the one they are trying to edit, then they are authorized 
		if request.user.studentprofile == profile:
			#Dissect a post request 
			if request.method == 'POST':
				goal = get_object_or_404(StudentGoal, pk=goal_id)
				goal.met = True
				goal.save()

				#Return the user to their updated profile page
				return HttpResponseRedirect(reverse('attendance:student_goals', args=(student.student_id,)))

			#GET requests should show the update page 
			else:
				return render(request, 'attendance/set_goal.html', {'student': student})

		#If not the user, show them an unauthorized message. Filthy trickses, nasty hobbitses
		else:
			return HttpResponse('Unauthorized')
	#No precious, they musnt access this page 
	else:
		return HttpResponse('Unauthorized')


#For the enrollment view we will grab the coach and the class, then show a list of all students that can be enrolled
@user_passes_test(group_check)
def enroll(request, coach_id, class_id):
	coach = get_object_or_404(Coach, pk=coach_id)
	clas = get_object_or_404(Class, pk=class_id)

	if request.method == 'POST':
		students = request.POST.getlist('student')
		#For each student id in the post request, we're going to create an enrollment record for them 
		for id_num in students:
			student = get_object_or_404(Student, pk=id_num)
			Enrollment.objects.create(student=student, coach=coach, _class=clas)
		return HttpResponseRedirect(reverse('attendance:class_roster', args=(coach.coach_id, clas.class_id,)))
	else:

		#This my friends, is probably the sexiest code I've written this summer 

		#Using set subtraction we'll grab only unenrolled students. Thank you Aaron Cote
		all_students = Student.objects.all().values_list('student_id', flat=True)
		enrolled_students = Enrollment.objects.filter(coach=coach, _class=clas).values_list('student__student_id', flat=True)
		unenrolled_student_ids = list(set(all_students)-set(enrolled_students))
		#Get the list of unenrolled student objects
		unenrolled_student_objects = [Student.objects.get(pk=id) for id in unenrolled_student_ids]
		return render(request, 'attendance/enroll.html', {'coach':coach, 'students':unenrolled_student_objects, 'class':clas})

@user_passes_test(group_check)
def create_session(request, coach_id, class_id):
	coach = get_object_or_404(Coach, pk=coach_id)
	clas = get_object_or_404(Class, pk=class_id)

	if request.method == 'POST':
		date = request.POST['date']
		time = request.POST['time']

		formatted_date = datetime.strptime(str(date) + ' ' + str(time), '%m/%d/%Y %I:%M%p')

		#Create a new class session from this 
		new_session = ClassSession.objects.create(coach=coach, _class=clas, class_date=formatted_date)
		#Now take them to the actual attendance for this date
		return HttpResponseRedirect(reverse('attendance:class_session', args=(coach_id, class_id, new_session.session_id)))
	else:
		all_students = Student.objects.all().order_by('last_name')
		return render(request, 'attendance/create_session.html', {'coach':coach, 'students':all_students, 'class':clas})


@login_required
def student_goals(request, student_id):

	student = get_object_or_404(Student, pk=student_id)
	goals = StudentGoal.objects.filter(student=student)

	return render(request, 'attendance/goals.html', {'student':student, 'goals': goals})


@login_required
def skill_list(request, student_id):
	student = get_object_or_404(Student, pk=student_id)
	skills = Skill.objects.all()

	return render(request, 'attendance/skills.html', {'student':student, 'skills': skills})


@login_required
def skill_overview(request, student_id, skill_id):
	student = get_object_or_404(Student, pk=student_id)
	skill = get_object_or_404(Skill, pk=skill_id)

	#Grab all the subskills and all the ones the student has met
	subskills = Subskill.objects.filter(skill=skill)
	student_met = StudentProgress.objects.filter(student=student, achieved=True)

	subskill_list = []
	#Go through all the subskills 
	for subskill in subskills:
		#Create a dict that holds the subskill and if it was achieved
		subskill_dict = {}
		if subskill in student_met:
			subskill_dict['achieved'] = True
		else:
			subskill_dict['achieved'] = False

		subskill_dict['subskill'] = subskill

		#Append that dict to the list of subskills
		subskill_list.append(subskill_dict)

	print(subskill_list)
	return render(request, 'attendance/skill_overview.html', {'student':student, 'skill': skill, 'subskills': subskill_list})

@login_required
def student_skills(request, student_id):

	student = get_object_or_404(Student, pk=student_id)
	skills = Skill.objects.all()

	skill_list = []

	#Go through each skill 
	for skill in skills:
		#Create a dict to hold these values 
		skill_dict = {}
		skill_dict['skill'] = skill
		
		#Grab all the subskills and all the ones the student has met
		subskills = Subskill.objects.filter(skill=skill)
		student_met = StudentProgress.objects.filter(student=student, achieved=True)
		
		subskill_list = []
		#Go through all the subskills 
		for subskill in subskills:
			#Create a dict that holds the subskill and if it was achieved
			subskill_dict = {}
			if subskill in student_met:
				subskill_dict['achieved'] = True
			else:
				subskill_dict['achieved'] = False

			subskill_dict['subskill'] = subskill

			#Append that dict to the list of subskills
			subskill_list.append(subskill_dict)

		#Add that subskill list to the skill dict as subskills 
		skill_dict['subskills'] = subskill_list
		#Add them to the final list 
		skill_list.append(skill_dict)

	return render(request, 'attendance/skills.html', {'student': student, 'skills': skill_list})
