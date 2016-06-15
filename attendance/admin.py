from django.contrib import admin

from .models import Coach, Student, Class, ClassSession, AttendanceRecord, Enrollment, StudentGuardian, StudentProfile, CoachNote, StudentGoal, Skill, Subskill, StudentProgress

# Register your models here.

admin.site.register(Coach)
admin.site.register(ClassSession)
admin.site.register(AttendanceRecord)
admin.site.register(Class)
admin.site.register(Student)
admin.site.register(Enrollment)
admin.site.register(StudentGuardian)
admin.site.register(StudentProfile)
admin.site.register(CoachNote)
admin.site.register(StudentGoal)
admin.site.register(Skill)
admin.site.register(Subskill)
admin.site.register(StudentProgress)


