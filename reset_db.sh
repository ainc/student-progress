rm -rf attendance/migrations/
echo "DROP DATABASE IF EXISTS awesome_student_progress; CREATE DATABASE awesome_student_progress;" | python manage.py dbshell
python manage.py makemigrations attendance
python manage.py migrate
echo "from django.contrib.auth.models import User; User.objects.create_superuser('admin', 'admin@example.com', 'awesomeinc')" | python manage.py shell
