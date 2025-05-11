from django.db import models
from django.utils import timezone

# when new student is created then generate an id
def generate_student_id():
    today = timezone.now()
    prefix = today.strftime('%m%y')  # e.g., "0525" for May 2025

    # Find the highest current number with this prefix
    last_student = Student.objects.filter(student_id__startswith=prefix).order_by('-student_id').first()

    if last_student:
        last_number = int(last_student.student_id.split('-')[1])
        new_number = last_number + 1
    else:
        new_number = 1000

    return f"{prefix}-{new_number}"

class Student(models.Model):
    student_id = models.CharField(max_length=20, unique=True, blank=True)
    name = models.CharField(max_length=100)
    contact = models.CharField(max_length=20)
    address = models.TextField()
    section = models.CharField(max_length=10, default="BSCS 2A")

    def save(self, *args, **kwargs):
        if not self.student_id:
            self.student_id = generate_student_id()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name

# Attendance model to track attendance for each student
class Attendance(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)  # Link to Student Class
    present_days = models.PositiveIntegerField(default=0)
    excused_days = models.PositiveIntegerField(default=0)
    absent_days = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"Attendance for {self.student.name}"  # Accessing student name
