from django.shortcuts import render, redirect
from great_alliance_portal.models import *
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.core import serializers
from django.contrib import messages
import json
from django.urls import reverse
from decimal import Decimal
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .forms import SubmissionForm, AssignmentForm, NotificationForm, ResourceForm, EnrollStudentsForm
import datetime
from uuid import uuid4
from django.shortcuts import get_object_or_404
#libraries for PDF document.
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, PageBreak, Table, TableStyle, Paragraph, Spacer, Image
import io
from collections import defaultdict
import os

def staff_view_students_by_level(request):
    # Get all student levels for the dropdown
    courses = Courses.objects.filter(staff_id=request.user.id)
    levels = StudentLevel.objects.filter(courses__in=courses).distinct()
    #levels = StudentLevel.objects.all()
    # Get the selected level from the request
    selected_level_id = request.GET.get('level_id', None)
    
    # Filter students based on the selected level
    if selected_level_id:
        students = Students.objects.filter(student_level_id=selected_level_id).order_by("gender","admin__first_name")
    else:
        students = Students.objects.none()  # No students to display if no level is selected
    
    context = {
        'levels': levels,
        'students': students,
        'selected_level': selected_level_id,
    }
    
    return render(request, 'staff_templates/staff_view_students_by_level.html', context)



def staff_view_students_results(request, student_id):
    try:
        student = Students.objects.get(id=student_id)
    except Students.DoesNotExist:
        # Handle the case where the student does not exist
        return render(request, '404.html', status=404)

    academic_years = Academic_Year.objects.all()
    semesters = Semester.objects.all()

    academic_year_id = request.GET.get('academic_year_id', None)
    semester_id = request.GET.get('semester_id', None)

    results = StudentResults.objects.filter(
        student_id=student_id,
        academic_year_id=academic_year_id,
        semester_id=semester_id
    )

    context = {
        'student': student,
        'results': results,
        'academic_years': academic_years,
        'semesters': semesters,
        'selected_academic_year': academic_year_id,
        'selected_semester': semester_id
    }

    return render(request, 'staff_templates/staff_view_students_results.html', context)


@login_required
def get_students_for_course(request, course_id):
    try:
        course = Courses.objects.get(id=course_id)
        students = Students.objects.filter(student_level_id=course.student_level_id)
        student_data = [{'id': student.id, 'full_name': student.admin.get_full_name()} for student in students]
        return JsonResponse({'students': student_data})
    except Courses.DoesNotExist:
        return JsonResponse({'students': []})


@login_required
def enroll_students(request):
    if request.method == 'POST':
        form = EnrollStudentsForm(request.POST, staff=request.user)
        if form.is_valid():
            course = form.cleaned_data['course']
            students = form.cleaned_data['students']
            for student in students:
                student.courses.add(course)
            messages.success(request, 'Students successfully enrolled in the subject.')
            return redirect('enroll_students')
    else:
        form = EnrollStudentsForm(staff=request.user)

    return render(request, 'staff_templates/enroll_students.html', {'form': form})


def staff_homepage(request):
    staff = Staffs.objects.get(admin=request.user.id)
    courses = Courses.objects.filter(staff_id=request.user.id)
    staff_assigned_to_a_level = StudentLevel.objects.filter(staff_id=request.user.id)
    programme_id_list = []
    
    final_programme = []
    #removing Duplicate Course ID
    
    staff = Staffs.objects.get(admin=request.user.id)
    course_count = courses.count()

    student_list = []
    student_list_attendance_present = []
    student_list_attendance_absent = []
    return render(request, "staff_templates/staff_homepage.html",
                  {
                   "course_count": course_count,"staff":staff,
                   "student_list": student_list, "present_list": student_list_attendance_present,
                   "absent_list": student_list_attendance_absent,
                   "staff_assigned_to_a_level":staff_assigned_to_a_level})

@csrf_exempt
def staff_fcmtoken_save(request):
    token = request.POST.get("token")
    try:
        staff = Staffs.objects.get(admin=request.user.id)
        staff.fcm_token = token
        staff.save()
        return HttpResponse("True")
    except:
        return HttpResponse("False")


def staff_about(request):
    return render(request, "staff_templates/about.html")


def staff_manage_students(request):
    return render(request, "staff_templates/manage_student.html")


def staff_apply_leave(request):
    staff_obj = Staffs.objects.get(admin=request.user.id)
    leave_data = StaffLeaveReport.objects.filter(staff_id=staff_obj)
    return render(request, "staff_templates/staff_apply_leave.html", {"leave_data": leave_data})


def staff_apply_leave_save(request):
    if request.method != "POST":
        return HttpResponseRedirect(reverse("staff_apply_leave"))
    else:
        leave_date = request.POST.get("leave_date")
        leave_reason = request.POST.get("leave_reason")

        staff_obj = Staffs.objects.get(admin=request.user.id)
        try:
            leave_report = StaffLeaveReport(
                staff_id=staff_obj, leave_date=leave_date, leave_message=leave_reason, leave_status=0)
            leave_report.save()
            messages.success(request, "Leave message sent.")
            return HttpResponseRedirect(reverse("staff_apply_leave"))
        except:
            messages.error(request, "An error occurred!")
            return HttpResponseRedirect(reverse("staff_apply_leave"))

@csrf_exempt
def get_students(request):
    student_level_id = request.POST.get("student_level")
    student_level = StudentLevel.objects.get(id=student_level_id)
    students = Students.objects.filter(student_level_id=student_level)

    student_data = serializers.serialize("python", students)
    list_data = []

    for student in students:
        data_small = {"id": student.admin.id,
                      "name": student.admin.last_name+" "+student.admin.first_name}
        list_data.append(data_small)
    return JsonResponse(list_data, content_type="application/json", safe=False)

@csrf_exempt
@login_required
def get_courses_by_level(request):
    if request.method == "POST" and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        student_level_id = request.POST.get("student_level")
        staff_id = request.user.id
        
        try:
            courses = Courses.objects.filter(staff_id=staff_id, student_level_id=student_level_id)
            course_list = [{"id": course.id, "course_name": course.course_name} for course in courses]
            return JsonResponse({"courses": course_list})
        
        except Courses.DoesNotExist:
            return JsonResponse({'error': 'No courses found for this level'}, status=404)
        
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error fetching courses: {e}", exc_info=True)
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Invalid request method or not AJAX'}, status=400)

@csrf_exempt
@login_required
def get_students_by_subjects(request):
    if request.method == "POST" and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        student_level_id = request.POST.get("student_level")
        course_id = request.POST.get("course_id")
        staff_id = request.user.id
        
        print(f"Received student_level_id: {student_level_id}, course_id: {course_id}, staff_id: {staff_id}")

        try:
            # Fetch the course to ensure it's taught by the logged-in staff
            course = Courses.objects.get(id=course_id, staff_id=staff_id)
            print(f"Found course: {course}")

            # Fetch students based on student level and course
            students = Students.objects.filter(student_level_id=student_level_id, courses=course)
            student_data = []
            for student in students:
                student_info = {
                    "id": student.id,
                    "name": f"{student.admin.first_name} {student.admin.last_name}",
                    "courses": [{"id": course.id, "course_name": course.course_name}]
                }
                student_data.append(student_info)
            return JsonResponse({"students": student_data})
        
        except Courses.DoesNotExist:
            return JsonResponse({'error': 'Course not found for the selected criteria'}, status=404)
        
        except Students.DoesNotExist:
            return JsonResponse({'error': 'No students found for the selected criteria'}, status=404)
        
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error fetching students: {e}", exc_info=True)
            print(f"Error: {e}")
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Invalid request method or not AJAX'}, status=400)

@login_required
def staff_take_attendance(request):
    # Fetch student levels where the staff is directly assigned as class tutor
    student_levels = StudentLevel.objects.filter(staff_id=request.user.id)
    academic_years = Academic_Year.objects.all()
    semesters = Semester.objects.all()

    return render(request, "staff_templates/staff_take_attendance.html", 
                  {"student_levels": student_levels, "academic_years": academic_years, "semesters": semesters})

@csrf_exempt  # it is added so you don't need to add csrf Token for saving data using Ajax
def save_attendance_data(request):
    student_ids = request.POST.get("student_ids")
    student_level_id = request.POST.get("student_level_id")
    attendance_date = request.POST.get("attendance_date")
    academic_year_id = request.POST.get("academic_year_id")
    semester_id = request.POST.get("semester_id")
    print(f"Received student_level_id: {academic_year_id}")  # Debug print
    student_level = StudentLevel.objects.get(id=student_level_id)
    #course = Courses.objects.filter(student_level_id=student_level).first() # Fetch only one course
    academic_year_model = Academic_Year.objects.get(id=academic_year_id)
    semester_model = Semester.objects.get(id=semester_id)
    json_student = json.loads(student_ids)
    #print(data[0]["id"])
    try:
        attendance = Attendance(
            #course_id=course,
            student_level_id=student_level,
            attendance_date=attendance_date,
            academic_year_id=academic_year_model,
            semester_id=semester_model)
        attendance.save()

        for stud in json_student:
            student = Students.objects.get(admin=stud["id"])
            attendance_report = AttendanceReport(
                student_id=student, attendance_id=attendance, status=stud["status"])
            attendance_report.save()
        return HttpResponse("OK")
    except:
        return HttpResponse("ERROR")


@csrf_exempt
def get_attendance_dates(request):
    #course = request.POST.get("course")
    student_level_id = request.POST.get("student_level_id")
    academic_year_id = request.POST.get("academic_year_id")
    semester_id = request.POST.get("semester_id")
    academic_year_obj = Academic_Year.objects.get(id=academic_year_id)
    semester_obj = Semester.objects.get(id=semester_id)
    #course_obj = Courses.objects.get(id=course)
    student_level_obj = StudentLevel.objects.get(id=student_level_id)
    attendance = Attendance.objects.filter(
        student_level_id=student_level_obj,
        academic_year_id=academic_year_obj, semester_id=semester_obj)
    attendance_obj = []
    for attendance_single in attendance:
        data = {"id": attendance_single.id, "attendance_date": attendance_single.attendance_date,
                "academic_year_id": attendance_single.academic_year_id.id, "semester_id": attendance_single.semester_id.id}
        attendance_obj.append(data)
    return JsonResponse(attendance_obj, safe=False)

@csrf_exempt
def staff_update_attendance(request):
    if request.method == 'POST':
        student_level_id = request.POST.get('student_level')
        academic_year_id = request.POST.get('academic_year')
        semester_id = request.POST.get('semester')

        attendance_reports = AttendanceReport.objects.filter(
            attendance_id__student_level_id=student_level_id,
            attendance_id__academic_year_id=academic_year_id,
            attendance_id__semester_id=semester_id,
        )

        students = Students.objects.filter(student_level_id=student_level_id)
        attendance_data = []

        for student in students:
            total_attendance = attendance_reports.filter(student_id=student).count()
            attendance_present = attendance_reports.filter(student_id=student, status=True).count()
            attendance_absent = attendance_reports.filter(student_id=student, status=False).count()
            
            attendance_data.append({
                'student_name': student.admin.get_full_name(),
                'total_attendance': total_attendance,
                'attendance_present': attendance_present,
                'attendance_absent': attendance_absent,
            })
        
        return JsonResponse({'attendance_data': attendance_data})

    else:
        student_levels = StudentLevel.objects.filter(staff_id=request.user.id)
        academic_years = Academic_Year.objects.all()
        semesters = Semester.objects.all()
        context = {
            'student_levels': student_levels,
            'academic_years': academic_years,
            'semesters': semesters,
        }
        return render(request, 'staff_templates/staff_update_attendance.html', context)

@csrf_exempt
def get_attendance_student(request):
    attendance_date = request.POST.get("attendance_date")

    attendance = Attendance.objects.get(id=attendance_date)
    attendance_data = AttendanceReport.objects.filter(attendance_id=attendance)
    list_data = []

    for student in attendance_data:
        data_small = {"id": student.student_id.admin.id, "name": student.student_id.admin.last_name +
                      " "+student.student_id.admin.first_name, "status": student.status}
        list_data.append(data_small)
    return JsonResponse(list_data, content_type="application/json", safe=False)


@csrf_exempt
def save_update_attendance_data(request):
    student_ids = request.POST.get("student_ids")
    attendance_date = request.POST.get("attendance_date")
    attendance = Attendance.objects.get(id=attendance_date)
    json_student = json.loads(student_ids)
    try:

        for stud in json_student:
            student = Students.objects.get(admin=stud["id"])
            attendance_report = AttendanceReport.objects.get(
                student_id=student, attendance_id=attendance)
            attendance_report.status = stud['status']
            attendance_report.save()
        return HttpResponse("OK")
    except:
        return HttpResponse("ERROR")


def staff_add_result(request):
    # Fetch student levels based on the courses the staff teaches
    courses = Courses.objects.filter(staff_id=request.user.id)
    student_levels = StudentLevel.objects.filter(courses__in=courses).distinct()
    academic_years = Academic_Year.objects.all()
    semesters = Semester.objects.all()
    return render(request, "staff_templates/staff_add_result.html", 
                  {"student_levels": student_levels, "academic_years": academic_years, "semesters": semesters,
                   "courses":courses})

def save_student_result(request):
    if request.method != "POST":
        return HttpResponseRedirect(reverse("staff_add_result"))

    semester_id = request.POST.get("semester")
    academic_year_id = request.POST.get("academic_year")
    success_messages = []
    error_messages = []

    try:
        courses_taught_by_staff = Courses.objects.filter(staff_id=request.user.id)

        for student_id in request.POST.getlist("student_id[]"):
            student_obj = get_object_or_404(Students, id=student_id)
            overral_mark = 0.0

            for course_id in request.POST.getlist(f"course_id_{student_id}[]"):
                course_obj = get_object_or_404(Courses, id=course_id)

                # Ensure the course is taught by the current staff
                if course_obj not in courses_taught_by_staff:
                    error_messages.append(f"You are not authorized to add results for course ID {course_id}.")
                    continue

                try:
                    # Fetch existing result from the database
                    existing_result = StudentResults.objects.filter(
                        student_id=student_obj,
                        course_id=course_obj,
                        academic_year_id=academic_year_id,
                        semester_id=semester_id
                    ).first()

                    if existing_result:
                        existing_individual_test_score = float(existing_result.individual_test_score)
                        existing_group_work_score = float(existing_result.group_work_score)
                        existing_class_test_score = float(existing_result.class_test_score)
                        existing_project_score = float(existing_result.project_score)
                        #existing_assignment_mark = float(existing_result.assignment_mark)
                        existing_exam_mark = float((existing_result.exam_mark / 50) * 100)  # Reverse the percentage to get the original input value
                    else:
                        existing_individual_test_score = 0.0
                        existing_group_work_score = 0.0
                        existing_class_test_score = 0.0
                        existing_project_score = 0.0
                        #existing_assignment_mark = 0.0
                        existing_exam_mark = 0.0

                    # Get the input values and keep existing values if no new input is provided
                    individual_test_score_input = request.POST.get(f'individual_test_score_{student_id}_{course_id}', '')
                    group_work_score_input = request.POST.get(f'group_work_score_{student_id}_{course_id}', '')
                    class_test_score_input = request.POST.get(f'class_test_score_{student_id}_{course_id}', '')
                    project_score_input = request.POST.get(f'project_score_{student_id}_{course_id}', '')
                    #assignment_mark_input = request.POST.get(f'assignment_mark_{student_id}_{course_id}', '')
                    exam_mark_input = request.POST.get(f'exam_mark_{student_id}_{course_id}', '')

                    individual_test_score = float(individual_test_score_input) if individual_test_score_input.strip() != '' else existing_individual_test_score
                    group_work_score = float(group_work_score_input) if group_work_score_input.strip() != '' else existing_group_work_score
                    class_test_score = float(class_test_score_input) if class_test_score_input.strip() != '' else existing_class_test_score
                    project_score = float(project_score_input) if project_score_input.strip() != '' else existing_project_score
                    
                    #assignment_mark = float(assignment_mark_input) if assignment_mark_input.strip() != '' else existing_assignment_mark
                    exam_mark = float(exam_mark_input) if exam_mark_input.strip() != '' else existing_exam_mark
                    #assignment mark acts as the total for all the class assessments.
                    assignment_mark = ((individual_test_score + group_work_score + class_test_score + project_score)/60) * 50
                    exam_mark_percentage = (exam_mark / 100) * 50
                    total_mark = float(assignment_mark) + float(exam_mark_percentage)
                    overral_mark += total_mark
                    overral_mark_average = 0.0

                    if total_mark >= 80:
                        grade = "A"
                        remark = "EXCELLENT"
                    elif total_mark >= 70:
                        grade = "B"
                        remark = "VERY GOOD"
                    elif total_mark >= 60:
                        grade = "C"
                        remark = "GOOD"
                    elif total_mark >= 45:
                        grade = "D"
                        remark = "AVERAGE"
                    elif total_mark >= 35:
                        grade = "E"
                        remark = "PASS"
                    else:
                        grade = "F"
                        remark = "FAIL"

                    semester_obj = get_object_or_404(Semester, id=semester_id)
                    academic_year_model = get_object_or_404(Academic_Year, id=academic_year_id)

                    if existing_result:
                        existing_result.individual_test_score = individual_test_score
                        existing_result.group_work_score = group_work_score
                        existing_result.class_test_score = class_test_score
                        existing_result.project_score = project_score
                        existing_result.assignment_mark = assignment_mark
                        existing_result.exam_mark = exam_mark_percentage
                        existing_result.total_mark = total_mark
                        existing_result.overral_mark = overral_mark
                        existing_result.overral_mark_average = overral_mark_average
                        existing_result.grade = grade
                        existing_result.remark = remark
                        existing_result.save()
                        
                    else:
                        StudentResults.objects.create(
                            student_id=student_obj,
                            course_id=course_obj,
                            individual_test_score=individual_test_score,
                            group_work_score=group_work_score,
                            class_test_score=class_test_score,
                            project_score=project_score,
                            assignment_mark=assignment_mark,
                            academic_year_id=academic_year_model,
                            exam_mark=exam_mark_percentage,
                            total_mark=total_mark,
                            overral_mark=overral_mark,
                            overral_mark_average=overral_mark_average,
                            grade=grade,
                            semester_id=semester_obj,
                            remark=remark
                        )

                    success_messages.append(f"Results added/updated successfully for course ID {course_id}.")
                except ValueError:
                    error_messages.append(f"Invalid input for student ID {student_id} and course ID {course_id}. Assignment or Exam mark must be in range!")
                    continue
    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")
        return HttpResponseRedirect(reverse("staff_add_result"))

    if success_messages:
        messages.success(request, "Results added/updated successfully.")

    return HttpResponseRedirect(reverse("staff_add_result"))
    #except:
        #messages.error(request, "Owps...an error occurred")
        #return HttpResponseRedirect(reverse("staff_add_result"))


def staff_profile(request):
    user = CustomUser.objects.get(id=request.user.id)
    staff = Staffs.objects.get(admin=user)
    return render(request, "staff_templates/staff_profile.html", {"user": user, "staff": staff})


def edit_staff_profile_save(request):
    if request.method != "POST":
        return HttpResponseRedirect(reverse("staff_profile"))
    else:
        #first_name = request.POST.get("first_name")
        #last_name = request.POST.get("last_name")
        password = request.POST.get("password")
        address1 = request.POST.get("address1")
        address2 = request.POST.get("address2")
        email = request.POST.get("email")
        #date_of_birth = request.POST.get("date_of_birth")
        phone_number = request.POST.get("phone_number")

        try:
            custom_user = CustomUser.objects.get(id=request.user.id)

            custom_user.email = email
            custom_user.save()
            staff = Staffs.objects.get(admin=custom_user.id)
            staff.address1 = address1
            staff.address2 = address2

            staff.phone_number = phone_number
            #staff.gender = gender
            staff.save()
            messages.success(
                request, "Profile Updated.")
            return HttpResponseRedirect(reverse("staff_profile"))
        except:
            messages.error(request, "owps an error occurred!")
            return HttpResponseRedirect(reverse("staff_profile"))

#Does quasi the same things as json.loads from here: https://pypi.org/project/dynamodb-json/


class JSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return json.JSONEncoder.default(self, obj)


@csrf_exempt
def fetch_student_results(request):
    course_id = request.POST.get("course_id")
    student_id = request.POST.get("student_id")
    academic_year_id = request.POST.get("academic_year_id")
    semester_id = request.POST.get("semester_id")
    
    student_obj = get_object_or_404(Students, admin=student_id)
    academic_year_obj = get_object_or_404(Academic_Year, id=academic_year_id)
    semester_obj = get_object_or_404(Semester, id=semester_id)
    
    result = StudentResults.objects.filter(
        student_id=student_obj,
        course_id=course_id,
        academic_year_id=academic_year_obj,
        semester_id=semester_obj
    ).exists()

    if result:
        result = StudentResults.objects.get(
            student_id=student_obj,
            course_id=course_id,
            academic_year_id=academic_year_obj,
            semester_id=semester_obj
        )
        result_data = {
            "exam_mark": result.exam_mark,
            "assignment_mark": result.assignment_mark
        }
        return HttpResponse(json.dumps(result_data, cls=JSONEncoder))
    else:
        return HttpResponse("False")

def staff_view_all_results(request):
    courses = Courses.objects.filter(staff_id=request.user.id)
    student_levels = StudentLevel.objects.filter(courses__in=courses).distinct()
    academic_years = Academic_Year.objects.all()
    semesters = Semester.objects.all()
    
    return render(request, "staff_templates/staff_display_results.html", {
        "student_levels": student_levels,
        "academic_years": academic_years,
        "semesters": semesters,
        "courses": courses
    })
    #return render(request, "staff_templates/staff_display_results.html",
                  #{"sorted_results": sorted_results})

@login_required
def staff_get_student_results(request):
    if request.method == "POST":
        student_level_id = request.POST.get("student_level")
        academic_year_id = request.POST.get("academic_year")
        semester_id = request.POST.get("semester")

        student_level = get_object_or_404(StudentLevel, id=student_level_id)
        academic_year = get_object_or_404(Academic_Year, id=academic_year_id)
        semester = get_object_or_404(Semester, id=semester_id)

        # Check if the logged-in staff member is associated with the selected level
        staff_assigned_to_level = StudentLevel.objects.filter(id=student_level_id, staff_id=request.user.id).exists()
        
        if staff_assigned_to_level:
            courses = Courses.objects.filter(student_level_id=student_level).order_by('course_name')
            students = Students.objects.filter(student_level_id=student_level)
        else:
            courses = Courses.objects.filter(staff_id=request.user.id, student_level_id=student_level).order_by('course_name')
            students = Students.objects.filter(student_level_id=student_level)

        student_results = StudentResults.objects.filter(
            student_id__in=students,
            course_id__in=courses,
            academic_year_id=academic_year,
            semester_id=semester
        ).select_related('student_id', 'course_id').order_by('course_id__course_name')

        # Group results by student
        results_by_student = defaultdict(list)
        
        for result in student_results:
            results_by_student[result.student_id].append(result)
        
        if not results_by_student:
            messages.error(request, "No results for the selected criteria.")
            return HttpResponseRedirect("/staff_get_student_results")

        return render(request, "staff_templates/staff_display_results.html", {
            "student_levels": StudentLevel.objects.filter(courses__in=Courses.objects.filter(staff_id=request.user.id)).distinct(),
            "academic_years": Academic_Year.objects.all(),
            "semesters": Semester.objects.all(),
            "results_by_student": dict(results_by_student),
            "student_level_id": student_level_id,
            "academic_year_id": academic_year_id,
            "semester_id": semester_id,
            "staff_assigned_to_level": staff_assigned_to_level,
        })

    # Add a response for GET requests to handle initial form display
    return render(request, "staff_templates/staff_display_results.html", {
        "student_levels": StudentLevel.objects.filter(courses__in=Courses.objects.filter(staff_id=request.user.id)).distinct(),
        "academic_years": Academic_Year.objects.all(),
        "semesters": Semester.objects.all(),
    })

def download_student_results(request, student_level_id, academic_year_id, semester_id):
    academic_year = get_object_or_404(Academic_Year, id=academic_year_id)
    semester = get_object_or_404(Semester, id=semester_id)
    student_level = get_object_or_404(StudentLevel, id=student_level_id)
    students = Students.objects.filter(student_level_id=student_level)
    student_total_marks = []

    attendance_reports = AttendanceReport.objects.filter(
        attendance_id__student_level_id=student_level_id,
        attendance_id__academic_year_id=academic_year_id,
        attendance_id__semester_id=semester_id,
    )

    subject_totals = {}

    for student in students:
        courses = Courses.objects.filter(student_level_id=student.student_level_id)
        student_results = StudentResults.objects.filter(
            student_id=student,
            course_id__in=courses,
            academic_year_id=academic_year,
            semester_id=semester
        )

        for result in student_results:
            if result.course_id.course_name not in subject_totals:
                subject_totals[result.course_id.course_name] = []
            subject_totals[result.course_id.course_name].append((student, result.total_mark))

        total_marks = sum(result.total_mark for result in student_results)
        total_marks = round(float(total_marks))
        student_total_marks.append((student, total_marks))

    student_total_marks.sort(key=lambda x: x[1], reverse=True)
    positions = {student.id: idx + 1 for idx, (student, _) in enumerate(student_total_marks)}

    subject_positions = {}
    for subject, marks in subject_totals.items():
        marks.sort(key=lambda x: x[1], reverse=True)
        subject_positions[subject] = {student.id: idx + 1 for idx, (student, _) in enumerate(marks)}

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, leftMargin=30, rightMargin=30)

    elements = []
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('Title', parent=styles['Heading1'], textColor=colors.black, fontSize=15, alignment=1, spaceAfter=8)
    terminal_title_style = ParagraphStyle('Title', parent=styles['Heading1'], textColor=colors.red, fontSize=10, alignment=1, spaceAfter=5)

    image_path = os.path.join('static', 'assets', 'img', 'clients', 'client-4.png')
    if not os.path.exists(image_path):
        image_path = None

    table_width = 580  # Adjust the table width to fit the page
    info_col_widths = [120, table_width - 120]
    result_col_widths = [170, 70, 70, 70, 60, 60, 80]  # Adjust column widths to fit content

    for idx, (student, total_marks) in enumerate(student_total_marks):
        if image_path:
            logo = Image(image_path, width=50, height=50)
            elements.append(logo)

        elements.append(Paragraph("GREAT ALLIANCE PREPARATORY/JHS", title_style))
        elements.append(Paragraph("TERMINAL REPORT", terminal_title_style))
        elements.append(Spacer(1, 10))

        total_attendance = attendance_reports.filter(student_id=student).count()
        attendance_present = attendance_reports.filter(student_id=student, status=True).count()

        position_suffix = 'TH'
        if positions[student.id] == 1:
            position_suffix = 'ST'
        elif positions[student.id] == 2:
            position_suffix = 'ND'
        elif positions[student.id] == 3:
            position_suffix = 'RD'

        position_str = f"{positions[student.id]}{position_suffix}"

        info_data = [
            ['NAME:', f"{student.admin.first_name.upper()} {student.admin.last_name.upper()}"],
            ['POSITION:', position_str],
            ['NO. ON ROLL:', f"{students.count()}"],
            ['CLASS:', student_level.level_name.upper()],
            ['ACADEMIC YEAR:', academic_year.academic_year.upper()],
            ['TERM:', semester.semester.upper()],
            ['ATTENDANCE:', f"{attendance_present} OUT OF {total_attendance}"]
        ]
        info_table = Table(info_data, colWidths=info_col_widths)
        info_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))

        elements.append(info_table)
        elements.append(Spacer(1, 10))

        student_results = StudentResults.objects.filter(
            student_id=student,
            course_id__in=courses,
            academic_year_id=academic_year,
            semester_id=semester
        ).select_related('course_id')

        if student_results.exists():
            result_data = [
                [
                    Paragraph('SUBJECTS', styles['Heading5']),
                    Paragraph('CLASS SCORE<br/>50%', styles['Heading5']),
                    Paragraph('EXAMS SCORE<br/>50%', styles['Heading5']),
                    Paragraph('TOTAL SCORE<br/>100%', styles['Heading5']),
                    Paragraph('POSITION IN<br/>SUBJECT', styles['Heading5']),
                    Paragraph('GRADE', styles['Heading5']),
                    Paragraph('REMARKS', styles['Heading5'])
                ]
            ]
            
            for result in student_results:
                assignment_mark_rounded = round(float(result.assignment_mark))
                exam_mark_rounded = round(float(result.exam_mark))
                total_mark_rounded = round(float(result.total_mark))

                subject_position = subject_positions[result.course_id.course_name][student.id]
                
                subject_position_suffix = 'TH'
                if subject_position == 1:
                    subject_position_suffix = 'ST'
                elif subject_position == 2:
                    subject_position_suffix = 'ND'
                elif subject_position == 3:
                    subject_position_suffix = 'RD'

                subject_position_str = f"{subject_position}{subject_position_suffix}"

                result_data.append([
                    Paragraph(result.course_id.course_name.upper(), styles['Normal']),
                    assignment_mark_rounded,
                    exam_mark_rounded,
                    total_mark_rounded,
                    subject_position_str,
                    result.grade.upper(),
                    result.remark.upper()
                ])

            # Ensure the TOTAL and other rows are appended properly
            result_data.append(['', '', 'TOTAL', total_marks, '', '', ''])

            # Determine the class teacher's remarks based on conditions
            if student_level.level_name in ["Basic 7", "Basic 8", "Basic 9"] and total_marks >= 600:
                class_teacher_remark = "EXCELLENT PERFORMANCE"
            elif student_level.level_name in ["Basic 7", "Basic 8", "Basic 9"] and total_marks >= 450:
                class_teacher_remark = "GOOD PERFORMANCE"
            elif student_level.level_name in ["Basic 7", "Basic 8", "Basic 9"] and total_marks >= 400:
                class_teacher_remark = "AVERAGE"
            else:
                class_teacher_remark = "MORE ROOM FOR IMPROVEMENT"

            # Adding additional rows for comments and signatures
            conduct_data = [
                ['CONDUCT:', '', '', '', '', '', ''],
                ['INTEREST:', '', '', '', '', '', ''],
                ["CLASS TEACHER'S REMARKS:", class_teacher_remark, '', '', '', '', ''],
                ["HEAD TEACHER'S SIGNATURE:", '', '', '', '', '', ''],
            ]

            # Append conduct_data rows to result_data
            result_data.extend(conduct_data)

            result_table = Table(result_data, colWidths=result_col_widths)
            result_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -6), 'CENTER'),
                ('ALIGN', (0, -4), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('SPAN', (1, -2), (-1, -2)),  # Merge cells from second column for 'CLASS TEACHER'S REMARKS:'
                ('SPAN', (0, -4), (-1, -4)),  # Merge cells for 'CONDUCT:'
                ('SPAN', (0, -3), (-1, -3)),  # Merge cells for 'INTEREST:'
                ('SPAN', (0, -1), (-1, -1)),  # Merge cells for 'HEAD TEACHER'S SIGNATURE:'
                ('LINEABOVE', (0, -5), (-1, -1), 1, colors.black),
                ('LINEBELOW', (0, -1), (-1, -1), 1, colors.black),
                ('LINEBEFORE', (0, -5), (0, -1), 1, colors.black),
                ('LINEAFTER', (-1, -5), (-1, -1), 1, colors.black),
            ]))

            elements.append(result_table)
            elements.append(Spacer(1, 10))
        
        if idx < len(students) - 1:
            elements.append(PageBreak())

    doc.build(elements)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="student_results_{student_level.level_name}_{academic_year_id}_{semester_id}.pdf"'
    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)
    return response

def staff_firebase_token_save(request):
    firebase_token = request.POST.get("firebase_token")
    try:
        staff = Staffs.objects.get(admin=request.user.id)
        staff.firebase_token = firebase_token
        staff.save()
        return HttpResponse("True")
    except:
        return HttpResponse("False")


def start_live_classroom(request):
    courses = Courses.objects.filter(staff_id=request.user.id)
    student_level = StudentLevel.objects.all()
    return render(request, "staff_templates/start_live_classroom.html", {"student_level": student_level, "courses": courses})


def start_live_classroom_process(request):
    student_level_id = request.POST.get("student_level")
    course = request.POST.get("course")

    course_obj = Courses.objects.get(id=course)
    student_level_obj = StudentLevel.objects.get(id=student_level_id)
    checks = OnlineClassRoom.objects.filter(
        course=course_obj, student_level_id=student_level_obj, is_active=True).exists()
    if checks:
        data = OnlineClassRoom.objects.get(
            course=course_obj, student_level_id=student_level_obj, is_active=True)
        room_pwd = data.room_pwd
        roomname = data.room_name
    else:
        room_pwd = datetime.now().strftime('%Y%m-%d%H-%M%S-') + str(uuid4())
        roomname = datetime.now().strftime('%Y%m-%d%H-%M%S-') + str(uuid4())
        staff_obj = Staffs.objects.get(admin=request.user.id)
        onlineClass = OnlineClassRoom(room_name=roomname, room_pwd=room_pwd, course=course_obj,
                                      student_level_id=student_level_obj, started_by=staff_obj, is_active=True)
        onlineClass.save()

    return render(request, "staff_templates/live_class_room_start.html", {"username": request.user.username, "password": room_pwd, "roomid": roomname, "course": course_obj.course_name, "student_level": student_level_obj})


def returnHtmlWidget(request):
    return render(request, "widget.html")


@login_required
def instructor_detail(request, course_id):
    #user = request.user
    #instructor = Instructor.objects.get(user=request.user)
    courses = Courses.objects.filter(staff_id=request.user.id)
    course = Courses.objects.get(id=course_id)

    context = {

        'course': course,
        'courses': courses,
    }

    return render(request, 'staff_templates/course_details.html', context)


## @brief view for the course's add-notification page
#
# This view is called by <course_id>/add_notification url.\n
# It returns the webpage containing a form to add notification and redirects to the course's detail page again after the form is submitted.
@login_required
def add_notification(request, course_id):
    form = NotificationForm(request.POST or None)
    course = Courses.objects.get(id=course_id)
    if form.is_valid():
        notification = form.save(commit=False)
        notification.course = course
        # get the current date,time and convert into string
        notification.time = datetime.datetime.now().strftime('%H:%M, %d/%m/%y')
        notification.save()
        return redirect('instructor_detail', course.id)

    return render(request, 'staff_templates/add_notification.html', {'course': course, 'form': form})


## @brief view for the course's add-assignment page.
#
# This view is called by <course_id>/add_assignment url.\n
# It returns the webpage containing a form to add an assignment and redirects to the course's detail page again after the form is submitted.
@login_required
def add_assignment(request, course_id):
    form = AssignmentForm(request.POST or None, request.FILES or None)
    course = Courses.objects.get(id=course_id)
    if form.is_valid():
        assignment = form.save(commit=False)
        assignment.file = request.FILES['file']
        assignment.post_time = datetime.datetime.now().strftime('%H:%M, %d/%m/%y')
        assignment.course = course
        assignment.save()
        notification = Notification()
        notification.content = "New Assignment Uploaded"
        notification.course = course
        notification.time = datetime.datetime.now().strftime('%H:%M, %d/%m/%y')
        notification.save()
        messages.success(request,
                         "Assignment uploaded.")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    return render(request, 'staff_templates/create_assignment.html', {'form': form, 'course': course})


## @brief view for the course's add-resource page.
#
# This view is called by <course_id>/add_resource url.\n
# It returns the webpage containing a form to add a resource and redirects to the course's detail page again after the form is submitted.
@login_required
def add_resource(request, course_id):
    form = ResourceForm(request.POST or None, request.FILES or None)
    staff = Staffs.objects.get(admin=request.user)
    course = Courses.objects.get(id=course_id)
    if form.is_valid():
        resource = form.save(commit=False)
        resource.file_resource = request.FILES['file_resource']
        resource.course = course
        resource.save()
        notification = Notification()
        notification.content = "New Resource Added - " + resource.title
        notification.course = course
        notification.time = datetime.datetime.now().strftime('%H:%M, %d/%m/%y')
        notification.save()
        messages.success(request,
                         "Course material uploaded.")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    return render(request, 'staff_templates/add_resource.html', {'form': form, 'course': course})


## @brief view for the assignments page of a course.
#
# This view is called by <course_id>/view_all_assignments url.\n
# It returns the webpage containing all the assignments of the course and links to their submissions and feedbacks given by the students.
@login_required
def view_all_assignments(request, course_id):
    course = Courses.objects.get(id=course_id)
    assignments = Assignment.objects.filter(course=course)
    return render(request, 'staff_templates/view_all_assignments.html', {'assignments': assignments, 'course': course})


## @brief view for the submissions page of an assignment.
#
# This view is called by <assignment_id>/view_all_submissions url.\n
# It returns the webpage containing links to all the submissions of an assignment.
@login_required
def view_all_submissions(request, assignment_id):
    assignment = Assignment.objects.get(id=assignment_id)
    submissions = Submission.objects.filter(assignment=assignment)
    course = assignment.course
    return render(request, 'staff_templates/view_all_submissions.html', {'submissions': submissions, 'course': course})


## @brief view for the feedback page containing an histogram of all the feddbacks provided by the students.
#
# This view is called by <assignment_id>/view_feedback url.\n
# It returns a webpage containing the feedback received by the students organized in the form of histogram.
@login_required
def view_feedback(request, assignment_id):
    import matplotlib.pyplot as plt
    import numpy as np
    from matplotlib.backends.backend_agg import FigureCanvasAgg
    import matplotlib.ticker as ticker

    assignment = Assignment.objects.get(id=assignment_id)
    submissions = Submission.objects.filter(assignment=assignment)

    # extract the feedbacks from the submissions list
    feedbacks1 = list(map(lambda x: x.feedback, submissions))
    feedbacks = np.array(feedbacks1)

    fig = plt.figure(figsize=(10, 6))
    fig.suptitle('Feedback received from the students',
                 fontsize=16, fontweight='bold')
    fig.subplots_adjust(bottom=0.3)
    ax = fig.add_subplot(111)

    ax.set_xlabel('Rating(out of 10)')
    ax.set_ylabel('Number of Students')
    x = feedbacks
    ax.hist(x, bins=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11], fc='lightblue',
            alpha=1, align='left', edgecolor='black', linewidth=1.0)
    ax.set_xticks([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11])
    # sets the difference between adjacent y-tics
    ax.yaxis.set_major_locator(ticker.MultipleLocator(1))

    plt.figtext(0.2, 0.1, 'Average Rating : ' + str(round(np.mean(feedbacks), 2)),
                bbox={'facecolor': 'lightblue', 'alpha': 0.5, 'pad': 10})  # adds box in graph to display mean rating
    plt.figtext(0.5, 0.1, 'Number of Students Students who rated : ' + str(len(feedbacks1)),
                bbox={'facecolor': 'lightblue', 'alpha': 0.5, 'pad': 10})  # adds box in graph to display number of students who rated

    canvas = FigureCanvasAgg(fig)
    response = HttpResponse(content_type='image/png')
    canvas.print_png(response)  # converts the figure to http response
    return response


def staff_courses(request):
    courses = Courses.objects.filter(staff_id=request.user.id)
    return render(request, "staff_templates/staff_courses.html", {"courses": courses})
