"""
Background Tasks for School Management System.
Uses Django 6.0's built-in Tasks framework for async operations.
"""
from django.tasks import task
from django.core.mail import send_mail
from django.conf import settings


@task
def send_fee_reminder_email(student_email: str, student_name: str, amount: float, due_date: str):
    """
    Send fee reminder email to parent/student.
    Uses Django 6.0 background task for async email sending.
    """
    subject = f"Fee Payment Reminder - {due_date}"
    message = f"""
Dear Parent/Guardian of {student_name},

This is a reminder that a fee payment of ₹{amount:,.2f} is due on {due_date}.

Please ensure timely payment to avoid late fee charges.

Thank you,
School Administration
    """
    return send_mail(
        subject=subject,
        message=message,
        from_email=None,  # Uses DEFAULT_FROM_EMAIL
        recipient_list=[student_email],
    )


@task
def send_attendance_alert(parent_email: str, student_name: str, date: str, status: str):
    """
    Send attendance alert to parents.
    Notifies when student is absent or late.
    """
    subject = f"Attendance Alert for {student_name} - {date}"
    message = f"""
Dear Parent/Guardian,

This is to inform you that {student_name} was marked as "{status}" on {date}.

If you believe this is an error, please contact the school office.

Thank you,
School Administration
    """
    return send_mail(
        subject=subject,
        message=message,
        from_email=None,
        recipient_list=[parent_email],
    )


@task
def send_exam_result_notification(parent_email: str, student_name: str, exam_name: str, percentage: float, grade: str):
    """
    Send exam result notification to parents.
    """
    subject = f"Exam Results - {exam_name}"
    message = f"""
Dear Parent/Guardian,

The results for {exam_name} have been declared.

Student: {student_name}
Percentage: {percentage:.2f}%
Grade: {grade}

You can view the detailed report card by logging into the parent portal.

Thank you,
School Administration
    """
    return send_mail(
        subject=subject,
        message=message,
        from_email=None,
        recipient_list=[parent_email],
    )


@task
def generate_report_card_pdf(student_id: int, exam_id: int):
    """
    Generate report card PDF in background.
    This is a placeholder - actual PDF generation would be implemented here.
    """
    # Import here to avoid circular imports
    from apps.students.models import Student
    from apps.examinations.models import Exam, ReportCard
    
    try:
        student = Student.objects.get(pk=student_id)
        exam = Exam.objects.get(pk=exam_id)
        
        # TODO: Implement actual PDF generation using reportlab or weasyprint
        # For now, just log the task
        print(f"Generating report card for {student.full_name} - {exam.name}")
        
        return {"status": "success", "student": student.full_name, "exam": exam.name}
    except (Student.DoesNotExist, Exam.DoesNotExist) as e:
        return {"status": "error", "message": str(e)}


@task
def send_bulk_sms(phone_numbers: list, message: str):
    """
    Send bulk SMS notifications.
    Placeholder for SMS gateway integration.
    """
    # TODO: Integrate with SMS gateway (MSG91, Twilio, etc.)
    sent_count = 0
    for phone in phone_numbers:
        # Simulate SMS sending
        print(f"Sending SMS to {phone}: {message[:50]}...")
        sent_count += 1
    
    return {"sent_count": sent_count, "total": len(phone_numbers)}


@task
def calculate_monthly_attendance_summary(month: int, year: int, section_id: int):
    """
    Calculate and store monthly attendance summary for a section.
    Heavy computation task run in background.
    """
    from apps.attendance.models import StudentAttendance, AttendanceSummary
    from apps.students.models import Student
    from apps.academics.models import Section
    from django.db.models import Count, Q
    
    section = Section.objects.get(pk=section_id)
    students = Student.objects.filter(current_section=section, is_active=True)
    
    for student in students:
        # Count attendance by status
        attendance_data = StudentAttendance.objects.filter(
            student=student,
            date__month=month,
            date__year=year
        ).aggregate(
            present=Count('id', filter=Q(status='present')),
            absent=Count('id', filter=Q(status='absent')),
            late=Count('id', filter=Q(status='late')),
            half_day=Count('id', filter=Q(status='half_day')),
            leave=Count('id', filter=Q(status='leave')),
            total=Count('id')
        )
        
        # Update or create summary
        AttendanceSummary.objects.update_or_create(
            student=student,
            section=section,
            academic_year=section.academic_year,
            month=month,
            year=year,
            defaults={
                'total_working_days': attendance_data['total'],
                'present_days': attendance_data['present'],
                'absent_days': attendance_data['absent'],
                'late_days': attendance_data['late'],
                'half_days': attendance_data['half_day'],
                'leave_days': attendance_data['leave'],
            }
        )
    
    return {"section": str(section), "students_processed": students.count()}
