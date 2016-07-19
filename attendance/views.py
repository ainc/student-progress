from django.shortcuts import get_object_or_404, render, redirect
from django.core.urlresolvers import reverse, resolve
from django.http import HttpResponse, HttpResponseRedirect
from .models import Enrollment, Coach, Student, ClassSession, AttendanceRecord, Class, StudentProfile, StudentGoal, CoachNote, Skill, Subskill, StudentProgress, Relationship, StudentGuardian, Team, TeamMember, PassPhrase
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User, Group
from django.contrib.auth import login as login_user
from django.db import IntegrityError
from allauth.socialaccount.models import SocialToken
import collections
from decimal import Decimal

# Create your views here.
from datetime import datetime

from gitstat.git import git_zen

'''
	Decorators 

	group_check -- for now, any coach will have the ability to edit/add information to any coach's classes
'''

#Decorator method to help us check if the user is a coach
def group_check(user):
    return user.groups.filter(name__in=['coaches'])

#Helper function to let us know if this current user has the authorization to access this page 
def has_access(request, coach_id, class_id):
	if hasattr(request.user, 'coach'):
		can_access = False

		coach = Coach.objects.get(pk=coach_id)
		clas = Class.objects.get(pk=class_id)
		if request.user.coach == coach:
			can_access = True

		if request.user.coach.coach_id in TeamMember.objects.filter(team__head_coach=coach, team___class=clas).values_list('assistant_coach', flat=True):
			can_access = True

		return can_access
	else:
		return False

def home_page(request):
	return render(request, 'attendance/home_page.html', {})

''' 
Coaches methods 

'''

#View to render the roster for a coach and a class
@user_passes_test(group_check)
def class_roster(request, coach_id, class_id):
	if not has_access(request, coach_id, class_id):
		return render(request, 'attendance/unauthorized.html', {})

	coach = get_object_or_404(Coach, pk=coach_id)
	clas = get_object_or_404(Class, pk=class_id)
	query_set = Enrollment.objects.filter(coach=coach, _class=clas)

	return render(request, 'attendance/roster.html', {'roster': query_set, 'coach': coach, 'class': clas})

#View to render the roster and the edit attendance for a coach, a class, and a class session
@user_passes_test(group_check)
def class_session(request, coach_id, class_id, session_id):
	if not has_access(request, coach_id, class_id):
		return render(request, 'attendance/unauthorized.html', {})

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


@user_passes_test(group_check)
def classes_for_coach(request, coach_id):
	coach = get_object_or_404(Coach, pk=coach_id)
	#This query will return a dictionary of all the unique classes this coach teaches
	classDicts = ClassSession.objects.filter(coach=coach).values('_class').distinct()
	teams = Team.objects.filter(head_coach=coach)
	classes = []
	for entry in teams:
		classes.append({'head_coach': entry.head_coach, 'class': entry._class})

	#For all the classes where our coach is an assistant, we'll go through and store those values too
	assistant_classes = []
	for entry in TeamMember.objects.filter(assistant_coach=coach):
		assist_dict = {}
		assist_dict['class'] = entry.team._class
		assist_dict['head_coach'] = entry.team.head_coach
		assistant_classes.append(assist_dict)


	return render(request, 'attendance/class_list.html', {'classes': classes, 'coach': coach, 'assistant_classes': assistant_classes})


#View to show an attendance overview for each student--showing how often they have come to the class
@user_passes_test(group_check)
def class_overview(request, class_id, coach_id):
	if not has_access(request, coach_id, class_id):
		return render(request, 'attendance/unauthorized.html', {})
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



''' user auth '''

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
			#Create a new guardian object here
			guardian = StudentGuardian.objects.create(name=first_name + ' ' + last_name, user=user)
			return redirect('attendance:add_relation', guardian_id=guardian.guardian_id)

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
				elif hasattr(user, 'studentguardian'):
					return redirect('attendance:parent_home', guardian_id=user.studentguardian.guardian_id)
				else:
					return redirect('attendance:home_page')
			else:
				print('not active')
				return render(request, 'attendance/login.html', {'error': True})
		else:
			print('recorded none')
			return render(request, 'attendance/login.html', {'not_found': True})

	else:
		return render(request, 'attendance/login.html')


''' student profiles ''' 

@login_required
#View to show a student profile. This will have two views--depending on if the user is authenticated or not
def student_profile(request, student_id):
	#Users have to be logged in to see this page
	if request.user.is_authenticated():

		#Make sure only approved parents can access this page
		user = request.user


		tokens = SocialToken.objects.filter(account__user=user, account__provider='github')
		

		github_username = 'ainc'

		student = get_object_or_404(Student, pk=student_id)

		#We'll log in to their github account and git some good information : ) 
		if tokens or student.profile.github_user_name:
			github_username = student.profile.github_user_name


		#If the user is a parent and they don't have approved access, kick them 
		if hasattr(user, 'studentguardian'):

			if not Relationship.objects.filter(student=student, guardian=user.studentguardian, student_approved=True):
				return render(request, 'attendance/unauthorized.html', {'error_message': 'You dont have access to this page yet'})

		#Kick any student's that are trying to access this page without permission

		if hasattr(user, 'studentprofile'):

			if user.studentprofile.student != student:
				return render(request, 'attendance/unauthorized.html', {})
				

		profile = student.profile
		enrollments = Enrollment.objects.filter(student=student).values_list('_class', 'coach_id')
		upcoming_sessions = []
		num_upcoming = 0
		for clas in enrollments:
			dic = {}
			dic['class'] = get_object_or_404(Class, pk=clas[0])
			dic['coach'] = get_object_or_404(Coach, pk=clas[1])
			sessions = ClassSession.objects.filter(coach=clas[1], _class=clas[0], class_date__gte=datetime.now()).order_by('class_date')
			num_upcoming += len(sessions)
			dic['sessions'] = sessions
			upcoming_sessions.append(dic)
		
		goals_met = StudentGoal.objects.filter(student=student, met=True)
		goals_set = StudentGoal.objects.filter(student=student)

		notes = CoachNote.objects.filter(student=student)

		skills = Subskill.objects.all()
		skills_met = StudentProgress.objects.filter(student=student, achieved=True)

		percentage = round(Decimal(len(skills_met)/len(skills)),2)*100

		new_relations = Relationship.objects.filter(student=student, student_approved=False)
		return render(request, 'attendance/student_profile.html', {'student': student, 'profile': profile, 'upcoming': upcoming_sessions, 'num_upcoming': num_upcoming, 'goals_met': len(goals_met), 'goals_set': len(goals_set), 'notes': len(notes), 'skills': len(skills), 'skills_met': len(skills_met), 'percent_complete': percentage, 'new_relations': len(new_relations), 'github_username': github_username})

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
			return render(request, 'attendance/unauthorized.html', {})
	#No precious, they musnt access this page 
	else:
		return render(request, 'attendance/unauthorized.html', {})

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
		return render(request, 'attendance/unauthorized.html', {})


#Have a view for coaches to signup
def coach_signup(request):
	#If it's a post then we'll authenticate and store the data entered
	if request.method == 'POST':

		username = request.POST['username']
		email = request.POST['email']
		password = request.POST['password']
		first_name = request.POST['first_name']
		last_name = request.POST['last_name']
			
		if request.POST['coach_phrase'] == PassPhrase.objects.get(pk=1).pass_phrase:
			
			try:

				#Create a user object for these fields
				user = User.objects.create_user(username, email, password)
				user.first_name = first_name
				user.last_name = last_name
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


@user_passes_test(group_check)
def coach_dashboard(request):
	#Grab all coaches
	coaches = Coach.objects.all()

	coach_list = []

	#Go through all the coaches and then gather how many classes they are teaching 
	for coach in coaches:
		coach_dict = {}
		coach_dict['coach'] = coach
		#This query will return a dictionary of all the unique classes this coach teaches
		classes = Team.objects.filter(head_coach=coach)
		coach_dict['classes'] = classes
		teams = TeamMember.objects.filter(assistant_coach=coach)
		coach_dict['num'] = len(classes)
		coach_dict['num_assistant'] = len(teams)

		coach_list.append(coach_dict)


	return render(request, 'attendance/coach_dashboard.html', {'coaches': coach_list})

#View to help parent's add their users
@login_required
def add_relation(request, guardian_id):

	if hasattr(request.user, 'studentguardian'):
		guardian = get_object_or_404(StudentGuardian, pk=guardian_id)
		
		if request.user.studentguardian == guardian:
			
			if request.method == 'POST':
				students = request.POST.getlist('student')
				#For all the student ids passed in we'll create a relation--these won't be approved yet however
				for student_id in students:
					student = get_object_or_404(Student, pk=int(student_id))
					Relationship.objects.create(guardian=guardian, student=student)

				my_students = Relationship.objects.filter(guardian=guardian)
				return redirect('attendance:parent_home', guardian_id=guardian.guardian_id)
			#Otherwise we'll show them the table where they can add students
			else:
				students = Student.objects.all()
				return render(request, 'attendance/guardian_reg.html', {'guardian': guardian, 'students': students})
		else:
			return render(request, 'attendance/unauthorized.html', {})
	else:
		return render(request, 'attendance/unauthorized.html', {})


#View to pull up a parent's main page
@login_required
def parent_home(request, guardian_id):

	#Get the guardian
	guardian = get_object_or_404(StudentGuardian, pk=guardian_id)

	#If this user has a guardian profile, then we'll compare them 
	if hasattr(request.user, 'studentguardian'):

		if request.user.studentguardian == guardian:
			my_students = Relationship.objects.filter(guardian=guardian)

			return render(request, 'attendance/parent_home.html', {'guardian': guardian, 'students': my_students })

		else:
			return render(request, 'attendance/unauthorized.html', {})
	else:
		return render(request, 'attendance/unauthorized.html', {})
	
#For the leave note view we make the user has coach permissions
@user_passes_test(group_check)
def leave_note(request, student_id):
	if request.user.is_authenticated():

		student = get_object_or_404(Student, pk=student_id)
		#Then we create a new coach note object 
		if request.method == 'POST':
			note = request.POST['note']
			CoachNote.objects.create(coach=request.user.coach, note=note, student=student)
			return HttpResponseRedirect(reverse('attendance:student_profile', args=(student.student_id,)))
		else:
			return render(request, 'attendance/leave_note.html', {'student': student})

	else: 
		return render(request, 'attendance/unauthorized.html', {})



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
			return render(request, 'attendance/unauthorized.html', {})
	#No precious, they musnt access this page 
	else:
		return render(request, 'attendance/unauthorized.html', {})

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
			return render(request, 'attendance/unauthorized.html', {})
	#No precious, they musnt access this page 
	else:
		return render(request, 'attendance/unauthorized.html', {})


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



#View that appears when a coach goes into a student profile and marks student progress
@user_passes_test(group_check)
def mark_skill(request, student_id, skill_id):
	student = get_object_or_404(Student, pk=student_id)
	skill = get_object_or_404(Skill, pk=skill_id)

	#Grab all the subskills for this particular skill
	subskills_for_skill = Subskill.objects.filter(skill=skill)

	if request.method == 'POST':

		#For all the subskills for this particular skill
		for subskill in subskills_for_skill:

			#Grab this particular progress object, if it exists
			progress_obj = StudentProgress.objects.filter(student=student, subskill=subskill)

			#If that skill id is not in the achieved column, then we'll either create a new progress object and mark it as not achieved, or we'll update it
			if str(subskill.sub_id) not in request.POST.getlist('achieved'):
				if not progress_obj:
					StudentProgress.objects.create(student=student, achieved=False, subskill=subskill)

				else:
					#Update the first object returned
					progress_obj[0].achieved = False
					progress_obj[0].save()
			else:
				if not progress_obj:
					StudentProgress.objects.create(student=student, achieved=True, subskill=subskill)

				else:
					#Update the first object returned 
					progress_obj[0].achieved = True
					progress_obj[0].save()

		return HttpResponseRedirect(reverse('attendance:skill_overview', args=(student_id, skill.skill_id)))
	
	else:
		#Grab all the subskills and all the ones the student has met
		subskills = Subskill.objects.filter(skill=skill)
		student_met = StudentProgress.objects.filter(student=student, achieved=True).values_list('subskill', flat=True)


		subskill_list = []
		#Go through all the subskills 
		for subskill in subskills:
			#Create a dict that holds the subskill and if it was achieved
			subskill_dict = {}
			if subskill.sub_id in student_met:
				subskill_dict['achieved'] = True
			else:
				subskill_dict['achieved'] = False

			subskill_dict['subskill'] = subskill

			#Append that dict to the list of subskills
			subskill_list.append(subskill_dict)


		return render(request, 'attendance/mark_skill.html', {'student':student, 'skill': skill, 'subskills': subskill_list})




#View that shows a student's overall progress for a particular skill
@login_required
def skill_overview(request, student_id, skill_id):
	#Get this student, and get this particular skill
	student = get_object_or_404(Student, pk=student_id)
	skill = get_object_or_404(Skill, pk=skill_id)

	#Grab all the subskills and all the ones the student has met
	subskills = Subskill.objects.filter(skill=skill).order_by('level')
	student_met = StudentProgress.objects.filter(student=student, achieved=True).values_list('subskill', flat=True)

	subskill_list = []
	level_dict = {}
	level = -1
	#Go through all the subskills 
	for subskill in subskills:
		if subskill.level > level:
			level = subskill.level
			level_dict[level] = []
		#Create a dict that holds the subskill and if it was achieved
		subskill_dict = {}
		if subskill.sub_id in student_met:
			subskill_dict['achieved'] = True
		else:
			subskill_dict['achieved'] = False

		subskill_dict['subskill'] = subskill
		

		#Append that dict to the list of subskills
		level_dict[subskill.level].append(subskill_dict)

	subskill_list = level_dict

	return render(request, 'attendance/skill_overview.html', {'student':student, 'skill': skill, 'subskills': subskill_list})


#View that shows an overview of all the skills and this students progress towards achieving them
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
		
		#Grab all the subskills for this skill
		subskills = Subskill.objects.filter(skill=skill)
		#Now grab those this student has achieved
		student_met = StudentProgress.objects.filter(subskill__skill=skill,student=student, achieved=True)

		skill_dict['met'] = len(student_met)
		skill_dict['total'] = len(subskills)

		#Add them to the final list 
		skill_list.append(skill_dict)

	return render(request, 'attendance/skills.html', {'student': student, 'skills': skill_list})



@login_required
def approve_parent(request, student_id):

	student = get_object_or_404(Student, pk=student_id)

	if request.user.is_authenticated():

		if hasattr(request.user, 'studentprofile'):

			if request.user.studentprofile == student.profile:

				#Grab all the current relationships for this user
				relationships = Relationship.objects.filter(student=student)
				#Figure out which one's we need to update in the database
				if request.method == 'POST':

					approved = request.POST.getlist('approved')
					
					#Update all the relationships based on what's approved and what's not approved
					for relation in relationships:
						if str(relation.relation_id) in approved:
							relation.student_approved = True
							relation.save()
						else:
							relation.student_approved = False
							relation.save()

					remove = request.POST.getlist('remove')

					#Delete all checked removal boxes here
					for relation_id in remove:
						relation = get_object_or_404(Relationship, pk=relation_id)
						relation.delete()


					return redirect('attendance:student_profile', student_id=student.student_id)
				else:

					return render(request, 'attendance/approve_parent.html', {'relationships': relationships, 'student': student})
				


			else:
				return render(request, 'attendance/unauthorized.html', {})


		else:
			return render(request, 'attendance/unauthorized.html', {})

	else:
		return render(request, 'attendance/unauthorized.html', {})



#Short view to verify that a coach is being signed up
def coach_verify(request):

	if request.method == 'POST':

		if request.POST['coach_phrase'] == 'rule #22':

			return resolve('accounts/github/login')
		else:
			pass_phrase = PassPhrase.objects.get(pk=1)
			return render(request, 'attendance/coach_verify.html', {'wrong_phrase': True, 'pass_phrase': PassPhrase.objects.get(pk=1).pass_phrase})

	request.session['coach_signup'] = True

	return render(request, 'attendance/coach_verify.html', { 'pass_phrase': PassPhrase.objects.get(pk=1).pass_phrase})

