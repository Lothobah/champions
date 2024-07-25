from decimal import Decimal
import decimal
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from great_alliance_portal.models import Bursar, StudentLevel, Students, Fees
from django.contrib import messages
from django.db.models import Q
def bursar_homepage(request):
    bursar = Bursar.objects.get(admin=request.user.id)
    return render(request, "bursar_templates/bursar_homepage.html", {
        "bursar":bursar
    })
def select_level_to_view_fees(request):
    if request.method == 'POST':
        student_level_id = request.POST.get("student_level")
        return redirect('view_fees', student_level_id=student_level_id)

    student_levels = StudentLevel.objects.all()
    return render(request, 'bursar_templates/select_level_to_view_fees.html', {'student_levels': student_levels})


def view_fees(request, student_level_id):
    student_level = get_object_or_404(StudentLevel, id=student_level_id)

    # Get all students associated with the student level
    students = Students.objects.filter(student_level_id=student_level_id)

    # Get fees for each student
    fees_by_level = {}
    for student in students:
        # Filter fees based on the search query if present
        search_query = request.GET.get('search_query')
        if search_query:
            fees = Fees.objects.filter(
                Q(student_id=student) &
                (Q(student_id__admin__first_name__icontains=search_query) |
                 Q(student_id__admin__last_name__icontains=search_query))
            )
        else:
            fees = Fees.objects.filter(student_id=student)

        fees_by_level[student] = fees

    return render(request, 'bursar_templates/view_fees.html', {
        'student_level': student_level,
        'fees_by_level': fees_by_level,
    })


def update_fees(request, fee_id):
    fee = get_object_or_404(Fees, id=fee_id)

    if request.method == 'POST':
        amount_paid_str = request.POST.get("amount_paid")
        arrears_str = request.POST.get("arrears_from_last_term")

        try:
            amount_paid = Decimal(amount_paid_str) if amount_paid_str else Decimal('0.00')
        except decimal.InvalidOperation:
            return render(request, 'bursar_templates/update_fees.html', {'fee': fee, 'error_message': 'Invalid amount paid'})

        try:
            arrears_from_last_term = Decimal(arrears_str) if arrears_str else None
        except decimal.InvalidOperation:
            return render(request, 'bursar_templates/update_fees.html', {'fee': fee, 'error_message': 'Invalid arrears from last term'})

        if amount_paid < 0:
            return render(request, 'bursar_templates/update_fees.html', {'fee': fee, 'error_message': 'Amount paid cannot be negative'})

        if arrears_from_last_term is not None:
            fee.arrears_from_last_term = arrears_from_last_term
            fee.overall_fees += fee.arrears_from_last_term

        if fee.amount_paid is None:
            fee.amount_paid = Decimal('0.00')

        if fee.arrears_from_last_term is None:
            fee.arrears_from_last_term = Decimal('0.00')

        # Deduct amount_paid from both overall_fees and arrears_from_last_term
        fee.amount_paid += amount_paid
        fee.overall_fees -= amount_paid
        fee.arrears_from_last_term -= amount_paid

        if fee.overall_fees < Decimal('0.00'):
            fee.overall_fees = Decimal('0.00')

        if fee.arrears_from_last_term < Decimal('0.00'):
            fee.arrears_from_last_term = Decimal('0.00')

        fee.save()

        return redirect('view_fees', student_level_id=fee.student_id.student_level_id.id)

    return render(request, 'bursar_templates/update_fees.html', {'fee': fee})

def add_fees_to_students(request):
    if request.method == 'POST':
        student_level_id = request.POST.get("student_level")
        student_level = get_object_or_404(StudentLevel, id=student_level_id)
        
        school_fees = Decimal(request.POST.get("school_fees"))
        extra_classes = Decimal(request.POST.get("extra_classes"))
        stationary = Decimal(request.POST.get("stationary"))
        sport_culture = Decimal(request.POST.get("sport_culture"))
        ict = Decimal(request.POST.get("ict"))
        pta = Decimal(request.POST.get("pta"))
        maintenance = Decimal(request.POST.get("maintenance"))
        light_bill = Decimal(request.POST.get("light_bill"))
        
        total_fees = school_fees + extra_classes + stationary + sport_culture + ict + pta + maintenance + light_bill
        
        students = Students.objects.filter(student_level_id=student_level)
        for student in students:
            fee, created = Fees.objects.get_or_create(
                student_id=student,
                student_level_id=student_level,
                defaults={
                    'school_fees': school_fees,
                    'extra_classes': extra_classes,
                    'stationary': stationary,
                    'sport_culture': sport_culture,
                    'ict': ict,
                    'pta': pta,
                    'maintenance': maintenance,
                    'light_bill': light_bill,
                    'total_fees': total_fees,
                    'overall_fees': total_fees,
                    'amount_paid': Decimal('0.00'),
                    'arrears_from_last_term': Decimal('0.00')
                }
            )
            if not created:
                # If the fee entry already exists, update the necessary fields
                fee.school_fees = school_fees
                fee.extra_classes = extra_classes
                fee.stationary = stationary
                fee.sport_culture = sport_culture
                fee.ict = ict
                fee.pta = pta
                fee.maintenance = maintenance
                fee.light_bill = light_bill
                fee.total_fees = total_fees
                fee.overall_fees = total_fees
                fee.amount_paid = Decimal('0.00')
                fee.arrears_from_last_term = Decimal('0.00')
                fee.save()
                
        messages.success(request, "Fees Saved...")
        return redirect("add_fees_to_students")

    student_levels = StudentLevel.objects.all()
    return render(request, 'bursar_templates/add_fees_to_students.html', {"student_levels": student_levels})


def update_fees_for_all_levels(request):
    if request.method == 'POST':
        student_levels = StudentLevel.objects.all()

        for level in student_levels:
            # Get all fee entries for this level
            fees_list = Fees.objects.filter(student_level_id=level.id)
            if not fees_list.exists():
                continue

            # Calculate total fees for this level
            #total_fees = sum(fee.school_fees + fee.extra_classes + fee.stationary + fee.sport_culture + fee.ict + fee.pta + fee.maintenance + fee.light_bill for fee in fees_list)
            # Get the total_fees from the first fee entry in the list
            fee = fees_list.first()
            total_fees = fee.total_fees
            # Update fees for each student in this level
            students = Students.objects.filter(student_level_id=level.id)
            for student in students:
                # Aggregate existing Fees objects
                existing_fees = Fees.objects.filter(
                    student_id=student,
                    student_level_id=level
                )
                
                if existing_fees.exists():
                    # Update all existing fee entries
                    for fee in existing_fees:
                        fee.total_fees = total_fees
                        fee.arrears_from_last_term = fee.overall_fees
                        fee.overall_fees = total_fees + fee.arrears_from_last_term
                        fee.save()
                else:
                    # Create a new Fees entry if none exists
                    Fees.objects.create(
                        student_id=student,
                        student_level_id=level,
                        total_fees=total_fees,
                        overall_fees=total_fees,
                        amount_paid=Decimal('0.00'),
                        arrears_from_last_term=Decimal('0.00'),
                        school_fees=Decimal('0.00'),
                        extra_classes=Decimal('0.00'),
                        stationary=Decimal('0.00'),
                        sport_culture=Decimal('0.00'),
                        ict=Decimal('0.00'),
                        pta=Decimal('0.00'),
                        maintenance=Decimal('0.00'),
                        light_bill=Decimal('0.00')
                    )
        messages.success(request, "Next term's fees added to students account.")
        return redirect('update_fees_for_all_levels')

    return render(request, 'bursar_templates/add_fees_to_students.html')


def bursar_update_fees(request):
    if request.method == 'POST':
        student_level_id = request.POST.get("student_level")
        student_level = get_object_or_404(StudentLevel, id=student_level_id)
        
        # Retrieve fee data from POST request
        school_fees = Decimal(request.POST.get("school_fees", '0.00'))
        extra_classes = Decimal(request.POST.get("extra_classes", '0.00'))
        stationary = Decimal(request.POST.get("stationary", '0.00'))
        sport_culture = Decimal(request.POST.get("sport_culture", '0.00'))
        ict = Decimal(request.POST.get("ict", '0.00'))
        pta = Decimal(request.POST.get("pta", '0.00'))
        maintenance = Decimal(request.POST.get("maintenance", '0.00'))
        light_bill = Decimal(request.POST.get("light_bill", '0.00'))
        
        # Calculate total fees
        total_fees = school_fees + extra_classes + stationary + sport_culture + ict + pta + maintenance + light_bill
        
        # Update all fee records for the selected student level
        fees_queryset = Fees.objects.filter(student_level_id=student_level)
        for fee in fees_queryset:
            fee.school_fees = school_fees
            fee.extra_classes = extra_classes
            fee.stationary = stationary
            fee.sport_culture = sport_culture
            fee.ict = ict
            fee.pta = pta
            fee.maintenance = maintenance
            fee.light_bill = light_bill
            fee.total_fees = total_fees
            fee.overall_fees = fee.arrears_from_last_term + fee.total_fees
            fee.save()
        
        messages.success(request, "Fees updated successfully for the selected level.")
        return redirect("bursar_update_fees")

    # Handle GET request to display the current fee data
    student_levels = StudentLevel.objects.all()
    selected_level_id = request.GET.get("student_level")
    fee_data = {}

    if selected_level_id:
        selected_level = get_object_or_404(StudentLevel, id=selected_level_id)
        fees_queryset = Fees.objects.filter(student_level_id=selected_level)
        if fees_queryset.exists():
            fee = fees_queryset.first()
            fee_data = {
                'school_fees': fee.school_fees,
                'extra_classes': fee.extra_classes,
                'stationary': fee.stationary,
                'sport_culture': fee.sport_culture,
                'ict': fee.ict,
                'pta': fee.pta,
                'maintenance': fee.maintenance,
                'light_bill': fee.light_bill,
            }
        else:
            fee_data = {
                'school_fees': Decimal('0.00'),
                'extra_classes': Decimal('0.00'),
                'stationary': Decimal('0.00'),
                'sport_culture': Decimal('0.00'),
                'ict': Decimal('0.00'),
                'pta': Decimal('0.00'),
                'maintenance': Decimal('0.00'),
                'light_bill': Decimal('0.00'),
            }

    return render(request, 'bursar_templates/bursar_update_fees.html', {
        "student_levels": student_levels,
        "fee_data": fee_data,
        "selected_level_id": selected_level_id
    })
