from django.db import models

# Create your models here.

# Model for the Student Record Table
class Student(models.Model):
    student_id = models.TextField(max_length=9)
    name = models.TextField(max_length=100)
    contact = models.CharField(max_length=11)
    address = models.TextField(max_length=100)

    def __str__(self):
        return f"{self.student_id} - {self.name}"