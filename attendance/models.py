from datetime import datetime
from django.db import models
from django.contrib.auth.models import User
from datetime import datetime
from .choices import ICON_CHOICES

#Coach table
class Coach(models.Model):
	coach_id = models.AutoField(primary_key=True)
	first_name = models.CharField(max_length=20)
	last_name = models.CharField(max_length=20)
	user = models.OneToOneField(User, on_delete=models.CASCADE) 

	def __str__(self):
		to_string = ''
		to_string += self.first_name
		to_string += ' '
		to_string += self.last_name
		return to_string

	class Meta:
		verbose_name_plural = 'Coaches'

#Student table
class Student(models.Model):
	student_id = models.AutoField(primary_key=True)
	first_name = models.CharField(max_length=20)
	last_name = models.CharField(max_length=20)
	profile = models.OneToOneField('StudentProfile', on_delete=models.CASCADE)

	def __str__(self):
		to_string = ''
		to_string += self.first_name
		to_string += ' '
		to_string += self.last_name
		return to_string

#A student profile which will contain information about a student
class StudentProfile(models.Model):
	profile_id = models.AutoField(primary_key=True)
	email = models.EmailField(max_length=60, blank=False)
	phone = models.CharField(max_length=11)
	github_user_name = models.CharField(max_length=30)
	bio = models.CharField(max_length=140)
	user = models.OneToOneField(User, on_delete=models.CASCADE)

	class Meta:
		verbose_name_plural = 'Student profiles'

	def __str__(self):
		return str(self.email) + ' Profile'


#Table for a student's parents/guardian
class StudentGuardian(models.Model):
	guardian_id = models.AutoField(primary_key=True)
	name = models.CharField(max_length=200)
	user = models.OneToOneField(User, on_delete=models.CASCADE, default=10)

	def __str__(self):
		return self.name

#Table to hold relationships between student's and guardians
class Relationship(models.Model):
	relation_id = models.AutoField(primary_key=True)
	student = models.ForeignKey(Student, on_delete=models.CASCADE)
	guardian = models.ForeignKey(StudentGuardian, on_delete=models.CASCADE)
	student_approved = models.BooleanField(default=False)
	def __str__(self):
		return str(self.guardian)

#Class table 
class Class(models.Model):
	class_id = models.AutoField(primary_key=True)
	class_name = models.CharField(max_length=20)

	def __str__(self):
		return self.class_name

	class Meta:
		verbose_name_plural = 'Class'

#Table to show which classes a student is enrolled in, and who the primary coach is. 
class Enrollment(models.Model):
	enroll_id = models.AutoField(primary_key=True)
	_class = models.ForeignKey(Class, on_delete=models.CASCADE)
	student = models.ForeignKey(Student, on_delete=models.CASCADE)
	coach = models.ForeignKey(Coach, on_delete=models.CASCADE)

	def __str__(self):
		return '--'.join((str(self.student),str(self._class),str(self.coach)))


#Each note for a coach will be stored into the database. All coaches will be able to access this note. 
class CoachNote(models.Model):
	note_id = models.AutoField(primary_key=True)
	student = models.ForeignKey(Student, on_delete=models.CASCADE)
	note = models.CharField(max_length=1000)
	coach = models.ForeignKey(Coach, on_delete=models.CASCADE)
	created_at = models.DateTimeField( default=datetime.now)

	class Meta:
		ordering = ('-created_at',)


#Students can create goals 
class StudentGoal(models.Model):
	goal_id = models.AutoField(primary_key=True)
	student = models.ForeignKey(Student, on_delete=models.CASCADE)
	description = models.CharField(max_length=1000)
	created_at = models.DateTimeField(default=datetime.now)
	met = models.BooleanField(default=False)

	class Meta:
		ordering = ('met','created_at',)


#A skill will only have a title 
class Skill(models.Model):
	skill_id = models.AutoField(primary_key=True)
	title = models.CharField(max_length=30)
	#Go to fontawesome.io and find some sweet icons to add to a skill
	font_awesome_icon = models.CharField(max_length=20, default='fa-tasks', choices=ICON_CHOICES)

	def __str__(self):
		return self.title

	def subtree(self):
		#Return all the skills that constitute this subtree
		return Subskill.objects.filter(skill=self).order_by('sub_id')

#A subskill will have a field to note which skill it derives from
class Subskill(models.Model):
	sub_id = models.AutoField(primary_key=True)
	description = models.CharField(max_length=1000)
	skill = models.ForeignKey(Skill, on_delete=models.CASCADE)

	def __str__(self):
		return str(self.skill) + ' -- ' + self.description

#Student progress will keep track of a subskill, a student, and if they have created a
class StudentProgress(models.Model):
	progress_id = models.AutoField(primary_key=True)
	achieved = models.BooleanField(default=False)
	subskill = models.ForeignKey(Subskill, on_delete=models.CASCADE)
	student = models.ForeignKey(Student, on_delete=models.CASCADE)


#ClassSession table stores information about a specific class session i.e. week 1
class ClassSession(models.Model):
	session_id= models.AutoField(primary_key=True)
	class_date = models.DateTimeField('Class date')
	_class = models.ForeignKey(Class, on_delete=models.CASCADE)
	coach = models.ForeignKey(Coach, on_delete=models.CASCADE)

	# Formats as Peter Kaminski--iOS--May 23rd, 2016
	def __str__(self):
		return self.class_date.strftime('%m/%d/%y')
		

	def formatted_time(self):
		format_hour_str = ''
		#Format the hour to add a 0 if it's a single digit
		if(self.class_date.hour > 12):
			if(self.class_date.hour - 12 < 10):
				format_hour_str = '0' + str(self.class_date.hour - 12)
			else:
				format_hour_str.join((str(self.class_date.hour - 12)))
		elif(self.class_date.hour < 10):
			format_hour_str = '0' + str(self.class_date.hour)
		else:
			format_hour_str = str(self.class_date.hour)

		#Format the minute to add an extra 0 if it's a single digit
		if(self.class_date.minute < 10):
			format_min_str = '0' + str(self.class_date.minute)
		else: 
			format_min_str = str(self.class_date.minute)


		time_str = ':'.join((format_hour_str, format_min_str))

		return self.class_date.strftime('%m/%d/%y') + ' ' + time_str

#Attendance records will be created individually for every student at each session
class AttendanceRecord(models.Model):
	record_id = models.AutoField(primary_key=True)
	coach = models.ForeignKey(Coach, on_delete=models.CASCADE) #FK with the coach table
	student = models.ForeignKey(Student, on_delete=models.CASCADE) #FK with a student
	_class = models.ForeignKey(Class, on_delete=models.CASCADE) #FK with a class
	session = models.ForeignKey(ClassSession, on_delete=models.CASCADE) #FK for a specific class session
	attended = models.BooleanField() #Did the student attend? 
	note = models.CharField(max_length=250, default='')
	#String representation shows if student attended. Format -- Peter Kaminski attended iOS
	def __str__(self):
		to_string = ''
		to_string += str(self.student) 
		
		if(self.attended):
			to_string += ' attended '
		else:
			to_string += ' missed '
		
		to_string += str(self._class)
		to_string += ' on '

		to_string += self.session.formatted_time()
		return to_string

	def did_attend(self):
		return self.attended

	
