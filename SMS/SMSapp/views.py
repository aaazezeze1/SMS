from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth import authenticate, logout as auth_logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.http import Http404
from .models import Student
from .models import Attendance

# Create your views here.
def home(request):
    return render(request, "home.html")

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

# change username and password
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

# student grouping
def studgroup(request):
    return render(request, 'studgroup.html')

# performance analysis
def perfanalysis(request):
    return render(request, 'perfanalysis.html')

# class management
def classman(request):
    return render(request, 'classman.html')

# drop out risk prediction
def droprisk(request):
    return render(request, 'droprisk.html')

# student record
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

# student record table delete student function
@csrf_exempt
def delete_student(request, id):
    if request.method == 'POST':
        try:
            student = Student.objects.get(pk=id)
            student.delete()
            return JsonResponse({'status': 'deleted'})
        except Student.DoesNotExist:
            return JsonResponse({'error': 'Student not found'}, status=404)

# student record table save the edited student function
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
        
# student record table add student function
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

# class management table
def attendance_view(request):
    # Get the section filter 
    section_filter = request.GET.get('section', '')  # If no section is selected, it's an empty string

    # filter by section else fetch all students
    if section_filter:
        students = Student.objects.filter(section=section_filter)
    else:
        students = Student.objects.all()

    # Fetch the attendance records for the students
    student_attendance = []
    for student in students:
        attendance = Attendance.objects.filter(student=student).first()  # Get the attendance for the student
        student_attendance.append({
            'student': student,
            'attendance': attendance
        })

    return render(request, "classman.html", {
        "student_attendance": student_attendance,
        "section_filter": section_filter,
    })

# edit button on class management attendance table
def update_attendance(request, student_id):
    if request.method == 'POST':
        present_days = request.POST.get('present_days')
        excused_days = request.POST.get('excused_days')
        absent_days = request.POST.get('absent_days')

        # Find the attendance object for the student
        attendance = Attendance.objects.get(student_id=student_id)

        # Update attendance values
        attendance.present_days = present_days
        attendance.excused_days = excused_days
        attendance.absent_days = absent_days

        # Save the changes
        attendance.save()

        # Redirect to the class management page
        return redirect('classman')