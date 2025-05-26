from django.db import models
from django.utils import timezone
from django.db.models import Avg, Sum

# When a new student is created then generate an id
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
    gwa = models.FloatField(default=0.0)  
    profile = models.CharField(max_length=50, null=True, blank=True)  # e.g., Advanced, Average
    dropout_risk = models.CharField(max_length=50, null=True, blank=True)  # e.g., Low, Medium, High
    performance_analysis = models.TextField(null=True, blank=True)
    performance_level = models.CharField(max_length=50, null=True, blank=True)
    profile_reasoning = models.TextField(blank=True, null=True)
    dropout_risk_reasoning = models.TextField(blank=True, null=True)
    performance_insights = models.TextField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.student_id:
            self.student_id = generate_student_id()
        super().save(*args, **kwargs)

    def calculate_gwa(self):
        grades = Grade.objects.filter(student=self)
        if not grades.exists():
            return None  # or 0.0 if you prefer

        total = sum(grade.final_grade for grade in grades)
        return total / grades.count()
    
    def generate_insights(self):
        grades = Grade.objects.filter(student=self)
        attendance = Attendance.objects.filter(student=self)

        # Calculate GWA
        gwa = grades.aggregate(Avg('final_grade'))['final_grade__avg'] or 0
        self.gwa = round(gwa, 2)

        # Profile Reasoning
        profile_reasoning = []
        if self.gwa >= 90:
            profile_reasoning.append(f"High GWA of {self.gwa}")
        elif self.gwa >= 85:
            profile_reasoning.append(f"Good GWA of {self.gwa}")
        else:
            profile_reasoning.append(f"GWA of {self.gwa}")

        if all(grade.final_grade >= 85 for grade in grades):
            profile_reasoning.append("Consistent grades above 85 in all subjects")

        # Dropout Risk Reasoning
        total_absent = attendance.aggregate(Sum('absent_days'))['absent_days__sum'] or 0
        total_excused = attendance.aggregate(Sum('excused_days'))['excused_days__sum'] or 0
        total_present = attendance.aggregate(Sum('present_days'))['present_days__sum'] or 0

        dropout_risk_reasoning = []
        if total_absent <= 2:
            dropout_risk_reasoning.append(f"Low number of absent days ({total_absent} total)")
        if total_present >= 50:
            dropout_risk_reasoning.append("Regular attendance (mostly present, very few excused)")

        # Performance Insights (textual breakdown, not the level)
        performance_insights = []
        for grade in grades:
            performance_insights.append(f"{grade.subject.code}: {int(grade.final_grade)}")

        performance_insights.append(f"GWA: {self.gwa}")
        performance_insights.append(
            f"Attendance: {total_absent} absent, {total_excused} excused, {total_present} present days"
        )

        # Assign generated values
        self.profile_reasoning = "\n- " + "\n- ".join(profile_reasoning)
        self.dropout_risk_reasoning = "\n- " + "\n- ".join(dropout_risk_reasoning)
        self.performance_insights = "\n- " + "\n- ".join(performance_insights)

        self.save()

# Subject model
class Subject(models.Model):
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.code} - {self.name}"


# Attendance model to track attendance for each student
class Attendance(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, default=1)
    present_days = models.IntegerField(default=0)
    excused_days = models.IntegerField(default=0)
    absent_days = models.IntegerField(default=0)

    class Meta:
        unique_together = ('student', 'subject')

    def __str__(self):
        return f"{self.student.name} - {self.subject.code}"
    
# Grades model
class Grade(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    final_grade = models.DecimalField(max_digits=5, decimal_places=2)

    class Meta:
        unique_together = ('student', 'subject')

    def __str__(self):
        return f"{self.student.name} - {self.subject.code}: {self.final_grade}"
