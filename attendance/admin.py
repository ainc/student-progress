from django.contrib import admin

from .models import Coach, Student, Class, ClassSession, AttendanceRecord, Enrollment, StudentGuardian, StudProfile

# Register your models here.

admin.site.register(Coach)
admin.site.register(ClassSession)
admin.site.register(AttendanceRecord)
admin.site.register(Class)
admin.site.register(Student)
admin.site.register(Enrollment)
admin.site.register(StudentGuardian)
admin.site.register(StudProfile)
