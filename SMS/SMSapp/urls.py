from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path("", views.login, name="login"),
    path("home/", views.home, name="home"),
    path("logout/", views.logout, name="logout"),
    # Url edit table method and academics (attendance and grades)
    path("academics/", views.attendance_view, name="academics"),
    path('academics/update_attendance/<int:student_id>/', views.update_attendance, name='update_attendance'),
    path("grades/", views.grades_view, name="grades_view"),
    path('grades/', views.grades_view, name='grades'),
    path('update-grades/', views.update_grades, name='update_grades'),
    # Url for edit gwa button in student grouping
    path("reset/", views.reset, name="reset"),
    # Url methods for the add, edit and delete functions of the student record table
    path('studentlist/', views.studentlist, name='studentlist'),
    path('student/delete/<int:id>/', views.delete_student, name='delete_student'),
    path('student/edit/<int:id>/', views.edit_student, name='edit_student'),
    path('student/add/', views.add_student, name='add_student'),
    # Url for Smart Analuytics
    path('smart-analytics/', views.smart_analytics_view, name='smart_analytics'),
    path('get_student_insights/<int:student_id>/', views.get_student_insights, name='get_student_insights'),

]