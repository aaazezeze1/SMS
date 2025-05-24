from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from SMSapp.models import Student, Grade, Attendance, Subject
import numpy as np

def convert_to_gpa(score):
    """Convert base-50 grade to GPA scale (1.00–5.00)."""
    if score >= 96:
        return 1.00
    elif score >= 91:
        return 1.25
    elif score >= 86:
        return 1.50
    elif score >= 81:
        return 1.75
    elif score >= 76:
        return 2.00
    elif score >= 71:
        return 2.25
    elif score >= 66:
        return 2.50
    elif score >= 61:
        return 2.75
    elif score >= 56:
        return 3.00
    else:
        return 5.00

def generate_analytics():
    subjects = ['CMSC204', 'CSEL301', 'CSEL302', 'ITEC106']
    students = Student.objects.all()
    data = []
    references = []

    for student in students:
        grades = []
        for code in subjects:
            subject = Subject.objects.get(code=code)
            grade = Grade.objects.filter(student=student, subject=subject).first()
            grades.append(float(grade.final_grade) if grade else 50.0)

        attendance = Attendance.objects.filter(student=student).first()
        total_days = sum([
            attendance.present_days,
            attendance.excused_days,
            attendance.absent_days,
        ]) if attendance else 0

        attendance_rate = attendance.present_days / total_days if total_days > 0 else 0
        grades.append(attendance_rate)

        data.append(grades)
        references.append((student, grades, attendance_rate))

    if not data:
        return "No data to analyze."

    from sklearn.preprocessing import StandardScaler
    from sklearn.cluster import KMeans
    import numpy as np

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(data)

    kmeans = KMeans(n_clusters=3, random_state=42)
    labels = kmeans.fit_predict(X_scaled)

    clusters = sorted(zip(kmeans.cluster_centers_, range(3)), key=lambda x: np.mean(x[0]))
    profile_map = {idx: label for label, (_, idx) in zip(['Struggling', 'Average', 'Advanced'], clusters)}

    for (student, grades, attendance_rate), label in zip(references, labels):
        gwa = np.mean(grades[:4])
        gpa = convert_to_gpa(gwa)

        # Dropout Risk
        risk = "High" if attendance_rate < 0.7 or gwa < 75 else "Medium" if gwa < 85 else "Low"

        # Performance Level 
        if gwa >= 95:
            level = "Excellent"
        elif gwa >= 90:
            level = "Very Satisfactory"
        elif gwa >= 85:
            level = "Satisfactory"
        elif gwa >= 80:
            level = "Fairly Satisfactory"
        elif gwa >= 75:
            level = "Passed"
        else:
            level = "Failed"


        student.profile = profile_map[label]
        student.dropout_risk = risk
        student.performance_level = level  
        student.save()

    return "Analytics generated and updated for all students."

