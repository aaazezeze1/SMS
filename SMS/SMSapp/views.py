import json
import logging

from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, Http404
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt

from .models import Student, Attendance, Subject, Grade
from django.db.models import Avg
from .analytics.generator import generate_analytics

logger = logging.getLogger(__name__)

# Create your views here
def home(request):
    students = Student.objects.all()
    total = students.count()
    at_risk = students.filter(dropout_risk__in=['Moderate', 'High']).count()
    gwa_list = [s.calculate_gwa() for s in students if s.calculate_gwa()]
    avg_gwa = round(sum(gwa_list) / len(gwa_list), 2) if gwa_list else 0

    low = students.filter(dropout_risk='Low').count()
    moderate = students.filter(dropout_risk='Moderate').count()
    high = students.filter(dropout_risk='High').count()

    context = {
        'total_students': total,
        'at_risk_students': at_risk,
        'average_gwa': avg_gwa,
        'low_risk': low,
        'moderate_risk': moderate,
        'high_risk': high,
    }
    return render(request, 'home.html', context)

def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)

        if user is not None:
            # redirect to home page if login is successful
            auth_login(request, user)
            return redirect('home')  
        else:
            return render(request, 'login.html', {'error': 'Invalid Credentials. Please Try Again.'})
        
    return render(request, "login.html")

def logout(request):
    auth_logout(request)
    messages.success(request, ("You have been logged out"))
    return redirect("login")

# Change username and password
@login_required
def reset(request):
    user = request.user

    if request.method == 'POST':
        new_username = request.POST.get('username')
        new_password = request.POST.get('password')

        if new_username:
            user.username = new_username

        if new_password:
            user.set_password(new_password)

        user.save()

        # Update session *after* saving password
        update_session_auth_hash(request, user)

        messages.success(request, "Credentials updated successfully.")
        return redirect('home')

    return render(request, 'reset.html')

# Class management
def academics(request):
    return render(request, 'academics.html')

# Student record
def studentlist(request):
    # Get the section filter from the query string, if provided
    section_filter = request.GET.get('section', None)

    # Get the sorting field from the query string, with 'student_id' as default
    sort_by = request.GET.get('sort_by', 'student_id')
    allowed_fields = ['student_id', 'name', 'address']

    # Validate sort_by field
    if sort_by not in allowed_fields:
        sort_by = 'student_id'

    # Filter students by section if filter is applied
    if section_filter:
        students = Student.objects.filter(section=section_filter).order_by(sort_by)
    else:
        students = Student.objects.all().order_by(sort_by)

    # Return the rendered template with students, the current sorting, and section filter
    return render(request, 'studentlist.html', {
        'students': students,
        'current_sort': sort_by,
        'section_filter': section_filter
    })

# Student record table delete student function
@csrf_exempt
def delete_student(request, id):
    if request.method == 'POST':
        try:
            student = Student.objects.get(pk=id)
            student.delete()
            return JsonResponse({'status': 'deleted'})
        except Student.DoesNotExist:
            return JsonResponse({'error': 'Student not found'}, status=404)

# Student record table save the edited student function
@csrf_exempt
def edit_student(request, id):
    if request.method == 'POST':
        data = json.loads(request.body)
        try:
            student = Student.objects.get(pk=id)
            student.student_id = data.get('student_id')
            student.name = data.get('name')
            student.contact = data.get('contact')
            student.address = data.get('address')
            student.section = data.get('section')  
            student.save()
            return JsonResponse({'status': 'updated'})
        except Student.DoesNotExist:
            return JsonResponse({'error': 'Student not found'}, status=404)
        
# Student record table add student function
@csrf_exempt
def add_student(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            student = Student(
                name=data['name'],
                contact=data['contact'],
                address=data['address'],
                section=data['section']  
            )
            student.save()  # student_id is generated here
            
            # Create attendance record for the new student
            Attendance.objects.create(
                student=student,
                present_days=0,
                excused_days=0,
                absent_days=0
            )

            # Create default grade records for required subjects
            subjects = Subject.objects.filter(code__in=['CMSC204', 'CSEL301', 'CSEL302', 'ITEC106'])
            for subject in subjects:
                Grade.objects.create(
                    student=student,
                    subject=subject,
                    final_grade=50.0
                )

            # Generate insights based on the new student data
            student.generate_insights()

            return JsonResponse({
                'success': True, 
                'student_id': student.student_id
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=400)
    return JsonResponse({'success': False}, status=400)

# Class management table
def attendance_view(request):
    section_filter = request.GET.get('section', '')  # filter by section
    subject_filter = request.GET.get('subject', '')  # filter by subject

    # Fetch all subjects for dropdown
    subjects = Subject.objects.all()

    # Filter students by section if any
    if section_filter:
        students = Student.objects.filter(section=section_filter)
    else:
        students = Student.objects.all()

    student_attendance = []

    for student in students:
        # Filter attendance by student AND subject if subject filter is applied
        if subject_filter:
            attendance = Attendance.objects.filter(student=student, subject__code=subject_filter).first()
        else:
            # fallback to any attendance record for student (if no subject filter)
            attendance = Attendance.objects.filter(student=student).first()

        student_attendance.append({
            'student': student,
            'attendance': attendance,
            'subject': attendance.subject if attendance else Subject.objects.get(code=subject_filter) if subject_filter else None
        })

    return render(request, "academics.html", {
    "student_attendance": student_attendance,
    "section_filter": section_filter,
    "subjects": subjects,
    "subject_filter": subject_filter,
    "selected_subject": subject_filter,
})

# Edit button on academics attendance table
@csrf_exempt
def update_attendance(request, student_id):
    if request.method == 'POST':
        try:

            present_days = int(request.POST.get('present_days', 0))
            excused_days = int(request.POST.get('excused_days', 0))
            absent_days = int(request.POST.get('absent_days', 0))
            subject_code = request.POST.get('subject')

            if not subject_code:
                return JsonResponse({'error': 'Subject code is missing'}, status=400)

            subject = Subject.objects.get(code=subject_code)
            student = Student.objects.get(id=student_id)

            attendance, created = Attendance.objects.get_or_create(
                student=student,
                subject=subject,
                defaults={
                    'present_days': 0,
                    'excused_days': 0,
                    'absent_days': 0
                }
            )

            total_days = present_days + excused_days + absent_days
            MAX_ALLOWED_DAYS = 100

            if total_days > MAX_ALLOWED_DAYS:
                return JsonResponse({
                    'error': f'Total attendance days exceed limit of {MAX_ALLOWED_DAYS}. Currently: {total_days}'
                }, status=400)

            attendance.present_days = present_days
            attendance.excused_days = excused_days
            attendance.absent_days = absent_days
            attendance.save()

            for student in Student.objects.all():
                student.generate_insights()


            return JsonResponse({'success': True})

        except Subject.DoesNotExist:
            return JsonResponse({'error': 'Subject not found'}, status=404)
        except Student.DoesNotExist:
            return JsonResponse({'error': 'Student not found'}, status=404)
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error updating attendance: {str(e)}")
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request'}, status=400)


#Student grades
def grades_view(request):
    section_filter = request.GET.get('section', '')

    # Filter students by section if any
    if section_filter:
        students = Student.objects.filter(section=section_filter)
    else:
        students = Student.objects.all()

    subjects = Subject.objects.all()
    student_grades = []

    for student in students:
        grade_dict = {'student': student}
        for subject in subjects:
            grade = Grade.objects.filter(student=student, subject=subject).first()
            grade_dict[subject.code] = grade.final_grade if grade else None
        grade_dict['gwa'] = student.gwa
        student_grades.append(grade_dict)

    return render(request, "grades.html", {
        "student_grades": student_grades,
        "subjects": subjects,
        "section_filter": section_filter
    })

# View to handle grade update
@csrf_exempt
def update_grades(request):
    if request.method == 'POST':
        try:
            student_id = request.POST.get('student_id')
            cmsc204 = float(request.POST.get('cmsc204'))
            csel301 = float(request.POST.get('csel301'))
            csel302 = float(request.POST.get('csel302'))
            itec106 = float(request.POST.get('itec106'))

            # Validate grades are between 50 and 100
            if not all(50 <= grade <= 100 for grade in [cmsc204, csel301, csel302, itec106]):
                return redirect('grades_view')

            student = get_object_or_404(Student, id=student_id)

            # Update or create grades for each subject
            subjects_map = {
                'CMSC204': cmsc204,
                'CSEL301': csel301,
                'CSEL302': csel302,
                'ITEC106': itec106,
            }

            for code, grade_value in subjects_map.items():
                subject = Subject.objects.get(code=code)
                grade_obj, created = Grade.objects.get_or_create(student=student, subject=subject)
                grade_obj.final_grade = grade_value
                grade_obj.save()

            # Recalculate and save GWA in student model
            student.gwa = student.calculate_gwa()
            student.save()

            for student in student:
                student.generate_insights()  # Regenerate insights from updated DB

            context = {
                'students': student,
    }
            # Redirect back to the grades table page with updated data
            return redirect('grades_view')

        except Exception as e:
            # On error, redirect back to grades page
            return redirect('grades_view')

    # If not POST, just redirect back
    return redirect('grades_view')

# SMART analytics
@login_required
def smart_analytics_view(request):
    students = Student.objects.all()

    section_filter = request.GET.get('section')
    if section_filter and section_filter != 'All':
        students = students.filter(section=section_filter)

    # Optional: force insights regeneration here (if needed)
    for student in students:
        student.generate_insights()

    # OR call the generate_analytics function if it does something else
    generate_analytics()

    # Add any necessary analytics data to the context here
    return render(request, 'smart_analytics.html', {
        'students': students,
        'section_filter': section_filter,
        # Add analytics data if needed
    })


# AJAX endpoint to fetch student insights
@csrf_exempt
def get_student_insights(request, student_id):
    if request.method == 'GET':
        try:
            student = get_object_or_404(Student, id=student_id)
            insights = student.generate_insights()
            return JsonResponse({'success': True, 'insights': insights})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
    return JsonResponse({'success': False, 'error': 'Invalid request'}, status=400)
