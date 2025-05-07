from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path("", views.login, name="login"),
    path("home/", views.home, name="home"),
    path("logout/", views.logout, name="logout"),
    path("studentlist/", views.studentlist, name="studentlist"),
    path("classman/", views.classman, name="classman"),
    path("studgroup/", views.studgroup, name="studgroup"),
    path("droprisk/", views.droprisk, name="droprisk"),
    path("perfanalysis/", views.perfanalysis, name="perfanalysis"),
    path("reset/", views.reset, name="reset")
]