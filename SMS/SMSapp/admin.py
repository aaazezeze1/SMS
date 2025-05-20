from django.contrib import admin
from .models import Student, Attendance
from .models import Grouping
from .models import Subject

# Register your models here.
admin.site.register(Student)
admin.site.register(Attendance)
admin.site.register(Grouping)
admin.site.register(Subject)
