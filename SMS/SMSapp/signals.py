from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Student, Grade, Attendance

@receiver(post_save, sender=Student)
def generate_insights_on_student_create(sender, instance, created, **kwargs):
    if created:
        instance.generate_insights()

@receiver(post_save, sender=Grade)
def generate_insights_on_grade_update(sender, instance, **kwargs):
    instance.student.generate_insights()

@receiver(post_save, sender=Attendance)
def generate_insights_on_attendance_update(sender, instance, **kwargs):
    instance.student.generate_insights()
