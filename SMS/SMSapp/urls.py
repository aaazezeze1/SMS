from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path("", views.login, name="login"),
    path("home/", views.home, name="home"),
    path("logout/", views.logout, name="logout"),
    # Url edit table method and class management
    path("classman/", views.attendance_view, name="classman"),
    path('classman/update_attendance/<int:student_id>/', views.update_attendance, name='update_attendance'),

    path("studgroup/", views.studgroup, name="studgroup"),
    path("droprisk/", views.droprisk, name="droprisk"),
    path("perfanalysis/", views.perfanalysis, name="perfanalysis"),
    path("reset/", views.reset, name="reset"),

    # Url methods for the add, edit and delete functions of the student record table
    path('studentlist/', views.studentlist, name='studentlist'),
    path('student/delete/<int:id>/', views.delete_student, name='delete_student'),
    path('student/edit/<int:id>/', views.edit_student, name='edit_student'),
    path('student/add/', views.add_student, name='add_student'),
    
]