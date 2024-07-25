from collections import defaultdict
from django.shortcuts import render
from django.db.models.fields import files
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
import json
from django.contrib import admin, messages
from django.urls.conf import path
from django.contrib.auth.models import auth
from django.shortcuts import get_object_or_404
from django.core.files.storage import FileSystemStorage
from great_alliance_portal.forms import *
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse
from django.views.generic import ListView
import json
from great_alliance_portal.models import *
from django.core.mail import send_mail
import logging
import smtplib

def admin_homepage(request):
    return render(request, "hod_templates/admin_homepage.html")
def manage_staffs(request):
    return render(request, "hod_templates/manage_staffs.html")
def manage_students(request):
    return render(request, "hod_templates/manage_students.html")
def academic_affairs(request):
    return render(request, "hod_templates/academic_affairs.html")
def about(request):
    return render(request, "hod_templates/about.html")
from django.shortcuts import render
from .models import Students, StudentLevel

def students_by_level(request):
    # Get all student levels for the dropdown
    levels = StudentLevel.objects.all()
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
    
    return render(request, 'hod_templates/students_by_level.html', context)



def view_student_results(request, student_id):
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

    return render(request, 'hod_templates/view_student_results.html', context)




def add_bursar(request):
    form = AddBursarForm()
    return render(request, "hod_templates/add_bursar.html", {"form":form})
def add_staff(request):
    form = AddStaffForm()
    return render(request, "hod_templates/add_staff.html", {"form": form})


def manage_course(request):
    courses = Courses.objects.all().order_by(
        'student_level_id')
    return render(request, "hod_templates/manage_course.html", {"courses": courses})


def manage_programme(request):
    programmes = Programmes.objects.all()
    return render(request, "hod_templates/manage_programme.html", {
        "programmes": programmes
    })


def view_staffs(request):
    staffs = Staffs.objects.all()
    return render(request, "hod_templates/view_staffs.html", {"staffs": staffs})

def add_bursar_save(request):
    if request.method != "POST":
        return HttpResponse("Method not allowed")
    else:
        gender = request.POST.get("gender")
        form = AddBursarForm(request.POST, request.FILES)
        if form.is_valid():
            email = form.cleaned_data["email"]
            first_name = form.cleaned_data["first_name"]
            last_name = form.cleaned_data["last_name"]
            username = (first_name[0] + last_name).lower()
            phone_number = form.cleaned_data["phone_number"]
            gender = form.cleaned_data["gender"]
            address1 = form.cleaned_data["address1"]
            address2 = form.cleaned_data["address2"]
            date_of_birth = form.cleaned_data["date_of_birth"]
            staff_profile_pic = request.FILES['staff_profile_pic']
            fs = FileSystemStorage()
            filename = fs.save(staff_profile_pic.name, staff_profile_pic)
            profile_pic_url = fs.url(filename)
            try:
                password = CustomUser.objects.make_random_password(
                    length=8, allowed_chars="abcdefghjkmnpqrstuvwxyz01234567889")
                user = CustomUser.objects.create_user(
                    username=username, password=password, email=email, last_name=last_name, first_name=first_name, user_type=4)
                user.bursar.address1 = address1
                user.bursar.address2 = address2
                user.bursar.phone_number = phone_number
                user.bursar.gender = gender
                user.bursar.date_of_birth = date_of_birth
                user.bursar.staff_profile_pic = profile_pic_url
                user.save()
                try:
                    send_mail(
                        'Login details for Great Alliance portal',
                        f'Login credentials for Great Alliance portal:\nUsername: {username}\nPassword: {password}',
                        from_email=None,
                        recipient_list=[email],
                        fail_silently=False,
                    )
                except smtplib.SMTPException as e:
                    logger.error(f"Failed to send email: {e}", exc_info=True)
                    messages.error(request, f"Failed to send email: {e}")
                    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
                messages.success(
                    request, message="Form submitted, username and password has been sent to " + email + ".")
                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
            except Exception as e:
                logger.error(f"Error creating user: {e}", exc_info=True)
                messages.error(request, "An error occurred while creating the user.")
                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        else:
            form = AddBursarForm(request.POST)
            return render(request, "hod_templates/add_bursar.html", {"form": form})


logger = logging.getLogger(__name__)

def add_staff_save(request):
    if request.method != "POST":
        return HttpResponse("Method not allowed")
    else:
        gender = request.POST.get("gender")
        form = AddStaffForm(request.POST, request.FILES)
        if form.is_valid():
            email = form.cleaned_data["email"]
            first_name = form.cleaned_data["first_name"]
            last_name = form.cleaned_data["last_name"]
            username = (first_name[0] + last_name).lower()
            phone_number = form.cleaned_data["phone_number"]
            gender = form.cleaned_data["gender"]
            address1 = form.cleaned_data["address1"]
            address2 = form.cleaned_data["address2"]
            date_of_birth = form.cleaned_data["date_of_birth"]
            staff_profile_pic = request.FILES['staff_profile_pic']
            fs = FileSystemStorage()
            filename = fs.save(staff_profile_pic.name, staff_profile_pic)
            profile_pic_url = fs.url(filename)
            try:
                password = CustomUser.objects.make_random_password(
                    length=8, allowed_chars="abcdefghjkmnpqrstuvwxyz01234567889")
                user = CustomUser.objects.create_user(
                    username=username, password=password, email=email, last_name=last_name, first_name=first_name, user_type=2)
                user.staffs.address1 = address1
                user.staffs.address2 = address2
                user.staffs.phone_number = phone_number
                user.staffs.gender = gender
                user.staffs.date_of_birth = date_of_birth
                user.staffs.staff_profile_pic = profile_pic_url
                user.save()
                try:
                    send_mail(
                        'Login details for Great Alliance portal',
                        f'Login credentials for Great Alliance portal:\nUsername: {username}\nPassword: {password}',
                        from_email=None,
                        recipient_list=[email],
                        fail_silently=False,
                    )
                except smtplib.SMTPException as e:
                    logger.error(f"Failed to send email: {e}", exc_info=True)
                    messages.error(request, f"Failed to send email: {e}")
                    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
                messages.success(
                    request, message="Form submitted, username and password has been sent to " + email + ".")
                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
            except Exception as e:
                logger.error(f"Error creating user: {e}", exc_info=True)
                messages.error(request, "An error occurred while creating the user.")
                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        else:
            form = AddStaffForm(request.POST)
            return render(request, "hod_templates/add_staff.html", {"form": form})

def edit_staff(request, staff_id):
    request.session['staff_id'] = staff_id
    staff = Staffs.objects.get(admin=staff_id)

    form = EditStaffForm()
    form.fields['email'].initial = staff.admin.email
    #form.fields['email2'].initial = staff.email2
    form.fields['first_name'].initial = staff.admin.first_name
    form.fields['last_name'].initial = staff.admin.last_name
    form.fields['username'].initial = staff.admin.username
    form.fields['phone_number'].initial = staff.phone_number
    #form.fields['staff_salary'].initial = staff.staff_salary
    form.fields['date_of_birth'].initial = staff.date_of_birth
    form.fields['address1'].initial = staff.address1
    form.fields['address2'].initial = staff.address2
    #form.fields['gender'].initial = staff.gender

    return render(request, "hod_templates/edit_staff.html",
                  {"staff": staff, "form": form, "id": staff_id})


def edit_staff_save(request):
    if request.method != "POST":
        return HttpResponse("<h2>Method not allowed</h2>")
    else:
        staff_id = request.session.get("staff_id")
        form = EditStaffForm(request.POST, request.FILES)
        if form.is_valid():
            first_name = form.cleaned_data["first_name"]
            last_name = form.cleaned_data["last_name"]
            #age = form.cleaned_data["age"]
            username = form.cleaned_data["username"]
            phone_number = form.cleaned_data["phone_number"]
            #staff_salary = form.cleaned_data["staff_salary"]
            date_of_birth = form.cleaned_data["date_of_birth"]
            address1 = form.cleaned_data["address1"]
            address2 = form.cleaned_data["address2"]
            #gender = form.cleaned_data["gender"]
            #email2 = form.cleaned_data["email2"]
            #primary_or_jhs_id = form.cleaned_data["primary_or_jhs_id"]
            if request.FILES.get('staff_profile_pic', False):
                staff_profile_pic = request.FILES['staff_profile_pic']
                fs = FileSystemStorage()
                filename = fs.save(staff_profile_pic.name, staff_profile_pic)
                profile_pic_url = fs.url(filename)
            else:
                profile_pic_url = None

            #class_id=form.cleaned_data["class_id"]
            #academic_year_id=form.cleaned_data["academic_year_id"]

            #try:
            user = CustomUser.objects.get(id=staff_id)
            user.first_name = first_name
            user.last_name = last_name
            user.username = username

            user.save()

            staff = Staffs.objects.get(admin=staff_id)
            staff.address1 = address1
            staff.address2 = address2
            #staff.email2 = email2
            staff.phone_number = phone_number
            #staff.staff_salary = staff_salary
            staff.date_of_birth = date_of_birth
            #staff.gender = gender
            if profile_pic_url != None:
                staff.staff_profile_pic = profile_pic_url

            staff.save()
            messages.success(request, "Staff updated successfully.")
            return HttpResponseRedirect(reverse("edit_staff", kwargs={"staff_id": staff_id}))
            #except:
            #messages.error(request, "owps an unexpected error occurred!")
            #return HttpResponseRedirect(reverse("edit_staff", kwargs={"staff_id": staff_id}))
        else:
            form = EditStaffForm(request.POST)
            staff = Staffs.objects.get(admin=staff_id)
            return render(request, "hod_templates/edit_staff.html", {"form": form, "id": staff_id, "username": staff.admin.username})


def add_student(request):
    #programmes = Programmes.objects.all()
    level = StudentLevel.objects.all()
    form = AddStudentForm()
    return render(request, "hod_templates/add_student.html",
                  {"level": level, "form": form})

logger = logging.getLogger(__name__)
def add_student_save(request):
    if request.method != "POST":
        return HttpResponse("Method not allowed")
    else:
        student_level_id = request.POST.get("student_level_id")
        form = AddStudentForm(request.POST, request.FILES)
        if form.is_valid():
            #email = form.cleaned_data["email"]
            first_name = form.cleaned_data["first_name"]
            last_name = form.cleaned_data["last_name"]
            #username = form.cleaned_data["username"]
            username = (first_name[0] + last_name).lower()
            home_town = form.cleaned_data["home_town"]
            gender = form.cleaned_data["gender"]
            parent_name = form.cleaned_data["parent_name"]
            parent_phone = form.cleaned_data["parent_phone"]
            date_of_birth = form.cleaned_data["date_of_birth"]
            profile_pic = request.FILES['profile_pic']
            fs = FileSystemStorage()
            filename = fs.save(profile_pic.name, profile_pic)
            profile_pic_url = fs.url(filename)
             # Ensure the username is unique
            original_username = username
            counter = 1
            while CustomUser.objects.filter(username=username).exists():
                username = f"{original_username}{counter}"
                counter += 1
            try:
                #password = CustomUser.objects.make_random_password(
                    #length=8, allowed_chars="abcdefghjkmnpqrstuvwxyz01234567889")
                user = CustomUser.objects.create_user(
                    username=username, last_name=last_name,
                    first_name=first_name, user_type=3)
                user.students.home_town = home_town
                user.students.parent_name = parent_name
                user.students.parent_phone = parent_phone
                user.students.date_of_birth = date_of_birth
                user.students.gender = gender
                student_level_obj = StudentLevel.objects.get(id=student_level_id)
                user.students.student_level_id = student_level_obj
                user.students.profile_pic = profile_pic_url
                user.save()
                messages.success(request,
                                 "Student has been added.")
                return HttpResponseRedirect(reverse("add_student"))

            except Exception as e:
                logger.error("An error occurred: %s", e, exc_info=True)
                #messages.error(request, "An error occurred while processing the form.")
                return HttpResponseRedirect(reverse("add_student"))
       
def get_fee_for_level(level):
    # Retrieve the total fees for the given student level
    # Assume that Fees has been set with one entry per level
    fees_record = Fees.objects.filter(student_level_id=level).first()
    if fees_record:
        # Calculate the total fee from all individual components
        total_fees = (
            fees_record.school_fees +
            fees_record.extra_classes +
            fees_record.stationary +
            fees_record.sport_culture +
            fees_record.ict +
            fees_record.pta +
            fees_record.maintenance +
            fees_record.light_bill
        )
        return total_fees
    else:
        raise Exception("No fee record found for this level.")



def edit_student(request, student_id):
    request.session['student_id'] = student_id
    student = Students.objects.get(admin=student_id)
    programmes = Programmes.objects.all()
    level = StudentLevel.objects.all()
    #academic_year = Academic_Year.objects.all()
    #semester = Semester.objects.all()
    form = EditStudentForm()
    #form.fields['email'].initial = student.admin.email
    form.fields['first_name'].initial = student.admin.first_name
    form.fields['last_name'].initial = student.admin.last_name
    #form.fields['age'].initial = student.age
    form.fields['username'].initial = student.admin.username
    form.fields['home_town'].initial = student.home_town
    #form.fields['class_id'].initial=student.class_id.id
    form.fields['parent_name'].initial = student.parent_name
    form.fields['parent_phone'].initial = student.parent_phone
    #form.fields['academic_year_id'].initial = student.academic_year_id.id
    #form.fields['gender'].initial = student.gender
    #form.fields['date_of_birth'].initial = student.date_of_birth

    return render(request, "hod_templates/edit_student.html",
                  {"programmes": programmes, "level": level,
                   "form": form, "student": student})


def edit_student_save(request):
    if request.method != "POST":
        return HttpResponse("<h2>Method not allowed</h2>")
    else:
        student_id = request.session.get("student_id")
        student_level_id = request.POST.get("student_level_id")
        form = EditStudentForm(request.POST, request.FILES)
        
        if form.is_valid():
            first_name = form.cleaned_data["first_name"]
            last_name = form.cleaned_data["last_name"]
            username = form.cleaned_data["username"]
            home_town = form.cleaned_data["home_town"]
            parent_name = form.cleaned_data["parent_name"]
            parent_phone = form.cleaned_data["parent_phone"]
            
            profile_pic_url = None
            if request.FILES.get('profile_pic', False):
                profile_pic = request.FILES['profile_pic']
                fs = FileSystemStorage()
                filename = fs.save(profile_pic.name, profile_pic)
                profile_pic_url = fs.url(filename)
            
            try:
                user = get_object_or_404(CustomUser, id=student_id)
                user.first_name = first_name
                user.last_name = last_name
                user.username = username
                user.save()
                
                student = get_object_or_404(Students, admin=student_id)
                new_level = get_object_or_404(StudentLevel, id=student_level_id)
                old_level = student.student_level_id
                student.student_level_id = new_level
                student.parent_name = parent_name
                student.parent_phone = parent_phone
                student.home_town = home_town
                
                if profile_pic_url:
                    student.profile_pic = profile_pic_url
                
                student.save()

                # Update the fees based on the new level
                old_fee_record = Fees.objects.filter(student_id=student, student_level_id=old_level).first()

                # Get the fee amount for the new level
                new_fee_amount = get_fee_for_level(new_level)  # Use the new function here

                if old_fee_record:
                    # Update the old record to reflect the new fees and potential arrears
                    arrears = old_fee_record.overall_fees 
                    #- old_fee_record.amount_paid
                    old_fee_record.student_level_id = new_level
                    old_fee_record.total_fees = new_fee_amount
                    old_fee_record.arrears_from_last_term = arrears
                    old_fee_record.overall_fees = new_fee_amount + arrears
                    old_fee_record.save()
                else:
                    # Create a new fee record if no existing one is found
                    Fees.objects.create(
                        student_id=student,
                        student_level_id=new_level,
                        total_fees=new_fee_amount,
                        overall_fees=new_fee_amount,
                        amount_paid=Decimal('0.00'),
                        arrears_from_last_term=Decimal('0.00')
                    )

                messages.success(request, "Student updated successfully.")
                return HttpResponseRedirect(reverse("edit_student", kwargs={"student_id": student_id}))
            except Exception as e:
                messages.error(request, f"Oops something went wrong! {str(e)}")
                return HttpResponseRedirect(reverse("edit_student", kwargs={"student_id": student_id}))
        else:
            student = get_object_or_404(Students, admin=student_id)
            return render(request, "hod_templates/edit_student.html", {"form": form, "id": student_id, "username": student.admin.username})

def delete_student(request, student_id):
    #student_id = request.session.get("student_id")
    #user = CustomUser.objects.get(id=student_id)

    request.session['student_id'] = student_id
    #student = CustomUser.objects.get(id=student_id)
    student = Students.objects.get(admin=student_id)

    if request.method == "POST":
        student_id = request.session.get("student_id")
        try:
            user = CustomUser.objects.get(id=student_id)

            user.delete()
            student = Students.objects.get(admin=student_id)
            student.delete()
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        except:
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    return render(request, "hod_templates/delete_student.html", {"id": student_id,
                                                                 "username": student.admin.username})


def delete_staff(request, staff_id):
    staff = Staffs.objects.get(admin=staff_id)

    if request.method == "POST":
        try:
            user = CustomUser.objects.get(id=staff_id)
            
            # Delete the Staff record
            staff.delete()

            # Delete the user record
            user.delete()
            
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        except CustomUser.DoesNotExist:
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        except Staffs.DoesNotExist:
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    return render(request, "hod_templates/view_staffs.html", {"id": staff_id,
        "username": staff.admin.username})


def add_level(request):
    staffs = CustomUser.objects.filter(user_type=2)
    return render(request, "hod_templates/add_level.html",{"staffs":staffs})


def add_level_save(request):
    if request.method != "POST":
        return HttpResponseRedirect(reverse("manage_session"))
    else:
        level_name = request.POST.get("level_name")
        staff_id = request.POST.get("staff_id")
        staff_obj = CustomUser.objects.get(id=staff_id)
        try:
            check_list = StudentLevel.objects.filter(level_name=level_name, staff_id=staff_obj)
            if check_list:
                level_model = StudentLevel.objects.get(level_name=level_name, staff_id=staff_obj)
                level_model.save()
                messages.success(request, "Already Saved.")
                return HttpResponseRedirect(reverse("add_level"))
            else:
                level_model = StudentLevel(level_name=level_name, staff_id=staff_obj)
                level_model.save()
                messages.success(request, "Success")
                return HttpResponseRedirect(reverse("add_level"))
        except:
            messages.error(request, "Oops an error occurred!!")
            return HttpResponseRedirect(reverse("add_level"))

def manage_level(request):
    student_level = StudentLevel.objects.all().order_by("level_name")
    return render(request, "hod_templates/manage_level.html", {"student_level":student_level})
def edit_level(request, student_level_id):
    student_level = StudentLevel.objects.get(id=student_level_id)
    #academic_year = Academic_Year.objects.all()
    staffs = CustomUser.objects.filter(user_type=2)
    return render(request, "hod_templates/edit_level.html",{"student_level":student_level,"staffs":staffs})

def edit_level_save(request):
    if request.method != "POST":
        return HttpResponse("<h2>Method not allowed</h2>")
    else:
        student_level_id = request.POST.get("student_level_id")
        level_name = request.POST.get("level_name")
        staff_id = request.POST.get("staff")

        try:
            student_level = StudentLevel.objects.get(id=student_level_id)
            student_level.level_name = level_name
            staff = CustomUser.objects.get(id=staff_id)
            student_level.staff_id = staff
            student_level.save()
            messages.success(request, "Success")
            return HttpResponseRedirect(reverse("edit_level", kwargs={"student_level_id": student_level_id}))
        except StudentLevel.DoesNotExist:
            messages.error(request, "Student level not found.")
            return HttpResponseRedirect(reverse("edit_level", kwargs={"student_level_id": student_level_id}))
        except CustomUser.DoesNotExist:
            messages.error(request, "Staff not found.")
            return HttpResponseRedirect(reverse("edit_level", kwargs={"student_level_id": student_level_id}))
        except Exception as e:
            messages.error(request, f"Something went wrong: {e}")
            return HttpResponseRedirect(reverse("edit_level", kwargs={"student_level_id": student_level_id}))

def add_course(request):
    #semester = Semester.SEMESTER_CHOICES
    semester = Semester.objects.all()
    level = StudentLevel.objects.all()
    staffs = CustomUser.objects.filter(user_type=2)
    return render(request, "hod_templates/add_course.html",
                  {"staffs": staffs, "semester": semester, "level": level})


def add_course_save(request):
    if request.method != "POST":
        return HttpResponse("<h2>Method not allowed</h2")
    else:
        course_name = request.POST.get("course_name")
        course_code = request.POST.get("course_code")
        student_level_id = request.POST.get("level_name")
        level_model = StudentLevel.objects.get(id=student_level_id)
        staff_id = request.POST.get("staff")
        staff = CustomUser.objects.get(id=staff_id)
        #try:
        courses = Courses(course_name=course_name, course_code=course_code,
                          student_level_id=level_model,
                          staff_id=staff)
        courses.save()
        messages.success(request, "Success")
        return HttpResponseRedirect(reverse("add_course"))
        #except:
        #messages.error(request, "something went wrong!")
        #return HttpResponseRedirect(reverse("add_course"))


def edit_course(request, course_id):
    level = StudentLevel.objects.all()
    #academic_year = Academic_Year.objects.all()
    staffs = CustomUser.objects.filter(user_type=2)
    course = Courses.objects.get(id=course_id)
    return render(request, "hod_templates/edit_course.html",
                  {"course": course, "level": level, "staffs": staffs, "id": course_id})


def edit_course_save(request):
    if request.method != "POST":
        return HttpResponse("<h2>Method not allowed</>")
    else:
        course_id = request.POST.get("course_id")
        course_name = request.POST.get("course_name")
        #course_code = request.POST.get("course_code")
        student_level_id = request.POST.get("level_name")
        staff_id = request.POST.get("staff")
        try:
            course = Courses.objects.get(id=course_id)
            course.course_name = course_name
            level_model = StudentLevel.objects.get(id=student_level_id)
            course.student_level_id = level_model
            staff = CustomUser.objects.get(id=staff_id)
            course.staff_id = staff
            course.save()
            messages.success(request, "Success")
            return HttpResponseRedirect(reverse("edit_course", kwargs={"course_id": course_id}))
        except:
            messages.error(request, "something went wrong!")
            return HttpResponseRedirect(reverse("edit_course", kwargs={"course_id": course_id}))


def edit_programme(request, programme_id):
    staffs = CustomUser.objects.filter(user_type=2)
    programme = Programmes.objects.get(id=programme_id)
    return render(request, "hod_templates/edit_programme.html",
                  {"programme": programme, "staffs": staffs, "id": programme_id})


def edit_programme_save(request):
    if request.method != "POST":
        return HttpResponse("<h2>Method not allowed</>")
    else:
        #subject_id=request.POST.get("subject_id")
        #subject_name=request.POST.get("subject_name")

        programme_id = request.POST.get("programme_id")
        #class_name = request.POST.get("class_name")
        staff_id = request.POST.get("staff")
        try:
            programme = Programmes.objects.get(id=programme_id)
            #clas.class_name=class_name
            staff = CustomUser.objects.get(id=staff_id)
            programme.staff_id = staff
            #staff.staff_id = staff_id
            programme.save()
            messages.success(request, "Programme Info Updated.")
            return HttpResponseRedirect(reverse("edit_programme", kwargs={"programme_id": programme_id}))

        except:
            messages.error(request, "An error occurred!!!")
            return HttpResponseRedirect(reverse("edit_programme", kwargs={"programme_id": programme_id}))


def view_students(request):
    if request.method == 'POST':
        selected_level_id = request.POST.get('student_level')
        if selected_level_id:
            students = Students.objects.filter(student_level_id=selected_level_id)
        else:
            students = Students.objects.all()
    else:
        students = Students.objects.all()
        selected_level_id = None
        
    student_level = StudentLevel.objects.all()
    total_students = students.count()
    programmes = Programmes.objects.all()

    return render(request, "hod_templates/view_students.html", {
        "students": students,
        "total_students": total_students,
        "programmes": programmes,
        "student_level": student_level,
        "selected_level_id": selected_level_id
    })


def staff_permissions(request):
    leaves = StaffLeaveReport.objects.all()
    return render(request, "hod_templates/staff_permissions.html", {"leaves": leaves})


def staff_leave_view(request):
    leaves = StaffLeaveReport.objects.all()
    return render(request, "hod_templates/staff_permissions.html", {"leaves": leaves})


def staff_approve_leave(request, leave_id):
    leave = StaffLeaveReport.objects.get(id=leave_id)
    leave.leave_status = 1
    leave.save()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def staff_disapprove_leave(request, leave_id):
    leave = StaffLeaveReport.objects.get(id=leave_id)
    leave.leave_status = 2
    leave.save()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    #return HttpResponseRedirect(reverse("manage_staffs"))


@csrf_exempt
def check_email_exist(request):
    email = request.POST.get("email")
    user_obj = CustomUser.objects.filter(email=email).exists()
    if user_obj:
        return HttpResponse(True)
    else:
        return HttpResponse(False)


@csrf_exempt
def check_email2_exist(request):
    email2 = request.POST.get("email2")
    user_obj = Staffs.objects.filter(email2=email2).exists()
    if user_obj:
        return HttpResponse(True)
    else:
        return HttpResponse(False)


@csrf_exempt
def check_username_exist(request):
    username = request.POST.get("username")
    user_obj = CustomUser.objects.filter(username=username).exists()
    if user_obj:
        return HttpResponse(True)
    else:
        return HttpResponse(False)


def admin_profile(request):
    user = CustomUser.objects.get(id=request.user.id)
    return render(request, "hod_templates/admin_profile.html", {"user": user})


def edit_admin_profile_save(request):
    if request.method != "POST":
        return HttpResponseRedirect(reverse("admin_profile"))
    else:
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        password = request.POST.get("password")
        #username = request.POST.get("username")
        #email = request.POST.get("email")
        #try:
        custom_user = CustomUser.objects.get(id=request.user.id)
        custom_user.first_name = first_name
        custom_user.last_name = last_name
        #custom_user.email = email
        #custom_user.username = username
        if password != None and password != "":
            custom_user.set_password(password)

        custom_user.save()
        messages.success(request, "Your profile has been updated.")
        return HttpResponseRedirect(reverse("admin_profile"))
        #except:
        #messages.error(request, "Error in editing profile")
        #return HttpResponseRedirect(reverse("admin_profile"))


def add_programme(request):
    staffs = CustomUser.objects.filter(user_type=2)
    return render(request, "hod_templates/add_programme.html", {
        "staffs": staffs
    })


def add_programme_save(request):
    if request.method != "POST":
        return HttpResponse("Method Not Allowed")
    else:
        programme_name = request.POST.get("programme_name")
        staff_id = request.POST.get("staff_id")
        staff_obj = CustomUser.objects.get(id=staff_id)
        try:
            check_list = Programmes.objects.filter(programme_name=programme_name,
                                                   staff_id=staff_obj)
            check_programme = Programmes.objects.filter(
                programme_name=programme_name)
            if check_list:
                programme_model = Programmes.objects.get(programme_name=programme_name,
                                                         staff_id=staff_obj)
                programme_model.save()
                messages.success(
                    request, "The selected Programme and staff already exist.")
                return HttpResponseRedirect(reverse("add_programme"))
            elif check_programme:
                programme_model = Programmes.objects.get(
                    programme_name=programme_name)
                programme_model.save()
                messages.error(
                    request, "Programme you added was already added, so it has been updated with the staff you selected.")
                return HttpResponseRedirect(reverse("add_programme"))
            else:
                programme_model = Programmes(
                    programme_name=programme_name, staff_id=staff_obj)
                programme_model.save()
                messages.success(request, "Programme Saved.")
                return HttpResponseRedirect(reverse("add_programme"))
        except:
            messages.error(request, "Something went wrong!")
            return HttpResponseRedirect(reverse("add_programme"))


def add_academic_year(request):
    return render(request, "hod_templates/add_academic_year.html")


def add_academic_year_save(request):
    if request.method != "POST":
        return HttpResponseRedirect(reverse("manage_session"))
    else:
        academic_year = request.POST.get("academic_year")

        try:
            check_list = Academic_Year.objects.filter(
                academic_year=academic_year)
            if check_list:
                academic_year_model = Academic_Year.objects.get(
                    academic_year=academic_year)
                academic_year_model.save()
                messages.success(
                    request, "This Academic year has already been added!")
                return HttpResponseRedirect(reverse("add_academic_year"))
            else:
                academic_year_model = Academic_Year(
                    academic_year=academic_year)
                academic_year_model.save()
                messages.success(request, "Academic Year Added.")
                return HttpResponseRedirect(reverse("add_academic_year"))
        except:
            messages.error(request, "Failed to Add Academic Year")
            return HttpResponseRedirect(reverse("add_academic_year"))


def admin_view_attendance(request):
    courses = Courses.objects.all()
    academic_year_id = Academic_Year.objects.all()
    semester = Semester.objects.all()
    return render(request, "hod_templates/admin_view_attendance.html",
                  {"courses": courses, "academic_year_id": academic_year_id,
                   "semester": semester})


@csrf_exempt
def admin_get_attendance_dates(request):
    course = request.POST.get("course")
    academic_year_id = request.POST.get("academic_year_id")
    semester_id = request.POST.get("semester_id")
    semester_obj = Semester.objects.get(id=semester_id)
    academic_year_obj = Academic_Year.objects.get(id=academic_year_id)
    course_obj = Courses.objects.get(id=course)
    attendance = Attendance.objects.filter(
        course_id=course_obj,
        academic_year_id=academic_year_obj, semester_id=semester_obj)
    attendance_obj = []
    for attendance_single in attendance:
        data = {"id": attendance_single.id, "attendance_date": attendance_single.attendance_date,
                "academic_year_id": attendance_single.academic_year_id.id,
                "semester_id": attendance_single.semester_id.id}
        attendance_obj.append(data)
    return JsonResponse(attendance_obj, safe=False)


@csrf_exempt
def admin_get_attendance_student(request):
    attendance_date = request.POST.get("attendance_date")

    attendance = Attendance.objects.get(id=attendance_date)
    attendance_data = AttendanceReport.objects.filter(attendance_id=attendance)
    list_data = []

    for student in attendance_data:
        data_small = {"id": student.student_id.admin.id, "name": student.student_id.admin.last_name +
                      " "+student.student_id.admin.first_name, "status": student.status}
        list_data.append(data_small)
    return JsonResponse(list_data, content_type="application/json", safe=False)


def admin_view_student_results(request):
    #courses = Courses.objects.filter(staff_id=request.user.id)
    courses = Courses.objects.all()
    student_levels = StudentLevel.objects.filter(courses__in=courses).distinct()
    academic_years = Academic_Year.objects.all()
    semesters = Semester.objects.all()
    
    return render(request, "hod_templates/admin_view_student_results.html", {
        "student_levels": student_levels,
        "academic_years": academic_years,
        "semesters": semesters
    })

@csrf_exempt
def admin_get_student_results(request):
    #subject_id = request.POST.get("subject_id")
    #course_id = request.POST.get("course_id")
    if request.method == "POST":
        student_level_id = request.POST.get("student_level")
        academic_year_id = request.POST.get("academic_year")
        semester_id = request.POST.get("semester")
        student_level = get_object_or_404(StudentLevel, id=student_level_id)
        academic_year = get_object_or_404(Academic_Year, id=academic_year_id)
        semester = get_object_or_404(Semester, id=semester_id)
        #course_obj = Courses.objects.get(id=course_id)
        #student_level = StudentLevel.objects.get(id=student_level_id)
        #semester_obj = Semester.objects.get(id=semester_id)
        #academic_year_obj = Academic_Year.objects.get(id=academic_year_id)
        courses = Courses.objects.filter(student_level_id=student_level)
        # Fetch students who have been in the selected student level based on their results
        students = Students.objects.filter(
            studentresults__academic_year_id=academic_year, 
            studentresults__semester_id=semester, 
            studentresults__course_id__in=courses
        ).distinct()
        #subject_obj = Subjects.objects.get(id=subject_id)
        #class_obj = Programmes.objects.get(id=class_id)
        student_results = StudentResults.objects.filter(
            academic_year_id=academic_year,student_id__in=students,
            course_id__in=courses, semester_id=semester).select_related('student_id', 'course_id')
        results_by_student = defaultdict(list)
        
        for result in student_results:
            results_by_student[result.student_id].append(result)
        if not results_by_student:

            messages.error(request, "Results are not available at the moment.")
            return HttpResponseRedirect("/admin_view_student_results")

        return render(request, "hod_templates/admin_view_student_results.html", {
            #"student_levels": StudentLevel.objects.filter(courses__in=Courses.objects.filter(student_level_id=student_level)).distinct(),
            "student_levels":StudentLevel.objects.all(),
            "academic_years": Academic_Year.objects.all(),
            "semesters": Semester.objects.all(),
            "results_by_student": dict(results_by_student),
            "student_level_id": student_level_id,
            "academic_year_id": academic_year_id,
            "semester_id": semester_id,
            #"staff_assigned_to_level": staff_assigned_to_level,
        })
     # Add a response for GET requests to handle initial form display
    return render(request, "hod_templates/admin_view_student_results.html", {
        #"student_levels": StudentLevel.objects.filter(courses__in=Courses.objects.filter(student_level_id=student_level)).distinct(),
        "academic_years": Academic_Year.objects.all(),
        "student_levels":StudentLevel.objects.all(),
        "semesters": Semester.objects.all(),
    })
    #return render(request, "hod_templates/admin_view_student_results.html")


def all_programmes(request):
    return render(request, "hod_templates/all_classes.html")


def academic_sem_selection(request):
    academic_year = Academic_Year.objects.all()
    semester = Semester.objects.all()
    return render(request, "hod_templates/academic_sem_selection.html",
                  {"academic_year": academic_year, "semester": semester})


def add_semester(request):
    semester = Semester.objects.all()
    return render(request, "hod_templates/add_semester.html",{"semester":semester})


def add_semester_save(request):
    if request.method != "POST":
        return HttpResponseRedirect(reverse("manage_session"))
    else:
        semester = request.POST.get("semester")

        try:
            check_list = Semester.objects.filter(semester=semester)
            if check_list:
                semester_model = Semester.objects.get(semester=semester)
                semester_model.save()
                messages.success(request, "Semester Already Added.")
                return HttpResponseRedirect(reverse("add_semester"))
            else:
                semester_model = Semester(semester=semester)
                semester_model.save()
                messages.success(request, "Semester Added")
                return HttpResponseRedirect(reverse("add_semester"))
        except:
            messages.error(request, "Error in adding semester")
            return HttpResponseRedirect(reverse("add_semester"))


def admin_view_results_of_pupils(request):
    student_results = StudentResults.objects.all()
    semester = Semester.objects.all()
    academic_year = Academic_Year.objects.all()
    subjects = Subjects.objects.all()
    return render(request, "hod_templates/student_results.html",
                  {"student_results": student_results, "semester": semester,
                   "academic_year": academic_year, "subjects": subjects})


'''def view_student_results(request):
    subject_id = request.POST.get("subject_id")
    academic_year_id = request.POST.get("academic_year_id")
    semester_id = request.POST.get("semester_id")
    subject_obj = Subjects.objects.get(id=subject_id)
    academic_year_obj = Academic_Year.objects.get(id=academic_year_id)
    semeste_obj = Semester.objects.get(id=semester_id)
    try:
        student_results = StudentResults.objects.filter(
            subject_id=subject_obj, academic_year_id=academic_year_obj,
            semester_id=semester_obj)
        console.log(student_results)
        return render(request, "hod_templates/view_student_results.html")
    except:
        messages.error(request, "Results Not Available at the Moment")
'''

class InfoListView(ListView):
    model = Students
    template_name = 'hod_templates/view_students.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["qs_json"] = json.dumps(list(Students.objects.values()))
        return context


def fees(request):
    pass
def alumni(request):
    students = Students.objects.all()
    return render(request, "hod_templates/alumni.html",{"students":students})

def fees_save(request):
    pass
