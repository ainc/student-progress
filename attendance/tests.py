from django.test import TestCase
import datetime

#Basic attendance testing

from .models import Coach, Student, Class, ClassSession, AttendanceRecord


class AttendanceTests(TestCase):

	def createCoach(self):
		return Coach.objects.create(first_name='Coach', last_name='One')
	
	def createStudent(self):
		return Student.objects.create(first_name='Student', last_name='One')

	def createClass(self):
		return Class.objects.create(class_name='iOS')

	def createAttendanceRecord(self, coach_param, student_param, class_param, session_param, attendance_param):
		return AttendanceRecord.objects.create(coach=coach_param, student=student_param, _class=class_param, session=session_param, attended=attendance_param)

	def create_session_for_today(self, coach_param, class_param):
		return ClassSession.objects.create(coach=coach_param, _class=class_param, class_date=datetime.datetime.now())

	def create_session_at_seven_am(self, coach_param, class_param):
		return ClassSession.objects.create(coach=coach_param, _class=class_param, class_date=datetime.datetime(2016, 5, 24, 7, 45))

	def create_session_at_noon(self, coach_param, class_param):
		return ClassSession.objects.create(coach=coach_param, _class=class_param, class_date=datetime.datetime(2016, 5, 24, 12, 00))

	def create_session_at_six_pm(self, coach_param, class_param):
		return ClassSession.objects.create(coach=coach_param, _class=class_param, class_date=datetime.datetime(2016, 5, 24, 18, 00))

	def test_coach(self):
		coach = self.createCoach()
		self.assertTrue(isinstance(coach, Coach))
		self.assertEqual('Coach', coach.first_name)
		self.assertEqual('One', coach.last_name)

	def test_student(self):
		s = self.createStudent()
		self.assertTrue(isinstance(s, Student))
		self.assertEqual('Student', s.first_name)
		self.assertEqual('One', s.last_name)

	def test_class(self):
		c = self.createClass()
		self.assertTrue(isinstance(c, Class))
		self.assertEqual('iOS', c.class_name)

	def test_session(self):
		coach = self.createCoach()
		clas = self.createClass()
		c = self.create_session_at_noon(coach, clas)
		self.assertTrue(isinstance(c, ClassSession))

	def test_noon(self):
		coach = self.createCoach()
		clas = self.createClass()
		c = self.create_session_at_noon(coach, clas)
		self.assertEqual(12, c.class_date.hour)
		self.assertEqual(0, c.class_date.minute)
		self.assertEqual('05/24/16 12:00', c.formatted_time())

	def test_six_pm(self):
		coach = self.createCoach()
		clas = self.createClass()
		c = self.create_session_at_six_pm(coach, clas)
		self.assertEqual(18, c.class_date.hour)
		self.assertEqual(0, c.class_date.minute)
		self.assertEqual('05/24/16 06:00', c.formatted_time())

	def test_seven_am(self):
		coach = self.createCoach()
		clas = self.createClass()
		c = self.create_session_at_seven_am(coach, clas)
		self.assertEqual(7, c.class_date.hour)
		self.assertEqual(45, c.class_date.minute)
		self.assertEqual('05/24/16 07:45', c.formatted_time())

	def test_attendance_false(self):
		coach = self.createCoach()
		stud = self.createStudent()
		clas = self.createClass()
		sess = self.create_session_at_noon(coach, clas)
		rec = self.createAttendanceRecord(coach, stud, clas, sess, False)
		self.assertEqual(rec.attended, False)
		self.assertEqual(rec.did_attend(), False)

	def test_attendance_true(self):
		coach = self.createCoach()
		stud = self.createStudent()
		clas = self.createClass()
		sess = self.create_session_at_noon(coach, clas)
		rec = self.createAttendanceRecord(coach, stud, clas, sess, True)
		self.assertEqual(rec.did_attend(), True)

