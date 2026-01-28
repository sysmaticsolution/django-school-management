"""
PDF Report Generation for School Management System.
Uses ReportLab for PDF creation.
"""
import io
from datetime import date
from decimal import Decimal

from django.http import HttpResponse
from django.conf import settings
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    Image, PageBreak, HRFlowable
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT


class SchoolReportMixin:
    """Common functionality for school reports."""
    
    @staticmethod
    def get_school_info():
        """Get school profile information."""
        from apps.core.models import SchoolProfile
        try:
            return SchoolProfile.objects.first()
        except:
            return None
    
    @staticmethod
    def create_header(school):
        """Create report header with school info."""
        elements = []
        styles = getSampleStyleSheet()
        
        # School name
        title_style = ParagraphStyle(
            'SchoolTitle',
            parent=styles['Heading1'],
            fontSize=18,
            alignment=TA_CENTER,
            spaceAfter=6
        )
        elements.append(Paragraph(school.name if school else "School Name", title_style))
        
        # Address
        address_style = ParagraphStyle(
            'Address',
            parent=styles['Normal'],
            fontSize=10,
            alignment=TA_CENTER,
            spaceAfter=12
        )
        if school:
            address = f"{school.address}, {school.city}, {school.state} - {school.pincode}"
            elements.append(Paragraph(address, address_style))
            if school.phone:
                elements.append(Paragraph(f"Phone: {school.phone} | Email: {school.email}", address_style))
        
        # Horizontal line
        elements.append(HRFlowable(width="100%", thickness=1, color=colors.black, spaceAfter=10))
        
        return elements


class StudentReportCard:
    """Generate student report cards."""
    
    def __init__(self, student, exam):
        self.student = student
        self.exam = exam
        self.school = SchoolReportMixin.get_school_info()
        self.styles = getSampleStyleSheet()
    
    def generate(self):
        """Generate report card PDF."""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=1*cm,
            leftMargin=1*cm,
            topMargin=1*cm,
            bottomMargin=1*cm
        )
        
        elements = []
        
        # Header
        elements.extend(SchoolReportMixin.create_header(self.school))
        
        # Report Title
        title_style = ParagraphStyle(
            'ReportTitle',
            parent=self.styles['Heading2'],
            fontSize=14,
            alignment=TA_CENTER,
            spaceAfter=20
        )
        elements.append(Paragraph(f"REPORT CARD - {self.exam.name}", title_style))
        
        # Student Info Table
        elements.extend(self._create_student_info())
        elements.append(Spacer(1, 20))
        
        # Marks Table
        elements.extend(self._create_marks_table())
        elements.append(Spacer(1, 20))
        
        # Summary
        elements.extend(self._create_summary())
        elements.append(Spacer(1, 40))
        
        # Signatures
        elements.extend(self._create_signatures())
        
        doc.build(elements)
        buffer.seek(0)
        return buffer
    
    def _create_student_info(self):
        """Create student information section."""
        elements = []
        
        info_data = [
            ["Student Name:", self.student.full_name, "Admission No:", self.student.admission_number],
            ["Class:", f"{self.student.current_section.standard.name} - {self.student.current_section.name}", 
             "Roll No:", str(self.student.roll_number or '-')],
            ["Father's Name:", self.student.father_name or '-', "Mother's Name:", self.student.mother_name or '-'],
        ]
        
        table = Table(info_data, colWidths=[2.5*cm, 6*cm, 2.5*cm, 6*cm])
        table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        elements.append(table)
        return elements
    
    def _create_marks_table(self):
        """Create marks table."""
        from apps.examinations.models import ExamResult
        
        elements = []
        results = ExamResult.objects.filter(
            student=self.student,
            exam=self.exam
        ).select_related('subject').order_by('subject__name')
        
        # Table header
        data = [["Subject", "Max Marks", "Marks Obtained", "Percentage", "Grade", "Result"]]
        
        for result in results:
            data.append([
                result.subject.name,
                str(result.max_marks),
                str(result.marks_obtained),
                f"{result.percentage:.1f}%",
                result.grade,
                "Pass" if result.is_pass else "Fail"
            ])
        
        table = Table(data, colWidths=[5*cm, 2*cm, 2.5*cm, 2.5*cm, 2*cm, 2*cm])
        table.setStyle(TableStyle([
            # Header
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c3e50')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            # Body
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
            ('ALIGN', (0, 1), (0, -1), 'LEFT'),
            # Grid
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
        ]))
        elements.append(table)
        return elements
    
    def _create_summary(self):
        """Create summary section."""
        from apps.examinations.models import ReportCard
        
        elements = []
        
        try:
            report_card = ReportCard.objects.get(student=self.student, exam=self.exam)
            
            summary_data = [
                ["Total Marks:", f"{report_card.marks_obtained} / {report_card.total_marks}"],
                ["Percentage:", f"{report_card.percentage:.2f}%"],
                ["Overall Grade:", report_card.overall_grade],
                ["Class Rank:", str(report_card.rank) if report_card.rank else '-'],
                ["Result:", "PASS" if report_card.percentage >= 33 else "FAIL"],
            ]
            
            table = Table(summary_data, colWidths=[4*cm, 4*cm])
            table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 11),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('BOX', (0, 0), (-1, -1), 1, colors.black),
                ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#ecf0f1')),
            ]))
            elements.append(table)
            
            if report_card.remarks:
                elements.append(Spacer(1, 10))
                elements.append(Paragraph(f"<b>Remarks:</b> {report_card.remarks}", self.styles['Normal']))
                
        except ReportCard.DoesNotExist:
            elements.append(Paragraph("Report card not generated yet.", self.styles['Normal']))
        
        return elements
    
    def _create_signatures(self):
        """Create signature section."""
        elements = []
        
        sig_data = [
            ["_________________", "_________________", "_________________"],
            ["Class Teacher", "Principal", "Parent/Guardian"],
        ]
        
        table = Table(sig_data, colWidths=[5.5*cm, 5.5*cm, 5.5*cm])
        table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 1), (-1, 1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 1), (-1, 1), 8),
        ]))
        elements.append(table)
        return elements


class FeeReceiptPDF:
    """Generate fee receipt PDF."""
    
    def __init__(self, payment):
        self.payment = payment
        self.school = SchoolReportMixin.get_school_info()
        self.styles = getSampleStyleSheet()
    
    def generate(self):
        """Generate fee receipt PDF."""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=1*cm,
            bottomMargin=1*cm
        )
        
        elements = []
        
        # Header
        elements.extend(SchoolReportMixin.create_header(self.school))
        
        # Title
        title_style = ParagraphStyle(
            'ReceiptTitle',
            parent=self.styles['Heading2'],
            fontSize=14,
            alignment=TA_CENTER,
            spaceAfter=20
        )
        elements.append(Paragraph("FEE RECEIPT", title_style))
        
        # Receipt details
        elements.extend(self._create_receipt_info())
        elements.append(Spacer(1, 20))
        
        # Fee details table
        elements.extend(self._create_fee_table())
        elements.append(Spacer(1, 30))
        
        # Footer
        elements.extend(self._create_footer())
        
        doc.build(elements)
        buffer.seek(0)
        return buffer
    
    def _create_receipt_info(self):
        """Create receipt information section."""
        elements = []
        student = self.payment.student
        
        info_data = [
            ["Receipt No:", self.payment.receipt_number, "Date:", self.payment.payment_date.strftime('%d/%m/%Y')],
            ["Student Name:", student.full_name, "Admission No:", student.admission_number],
            ["Class:", f"{student.current_section.standard.name} - {student.current_section.name}",
             "Payment Mode:", self.payment.get_payment_mode_display()],
        ]
        
        table = Table(info_data, colWidths=[2.5*cm, 5.5*cm, 2.5*cm, 5.5*cm])
        table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        elements.append(table)
        return elements
    
    def _create_fee_table(self):
        """Create fee details table."""
        elements = []
        
        # Get payment details
        details = self.payment.details.select_related('student_fee__fee_structure__category')
        
        data = [["S.No.", "Fee Type", "Amount (₹)"]]
        
        for idx, detail in enumerate(details, 1):
            data.append([
                str(idx),
                detail.student_fee.fee_structure.category.name,
                f"₹ {detail.amount:,.2f}"
            ])
        
        # Total row
        data.append(["", "Total Amount", f"₹ {self.payment.amount:,.2f}"])
        
        table = Table(data, colWidths=[2*cm, 10*cm, 4*cm])
        table.setStyle(TableStyle([
            # Header
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#27ae60')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            # Body
            ('FONTNAME', (0, 1), (-1, -2), 'Helvetica'),
            ('ALIGN', (0, 1), (0, -1), 'CENTER'),
            ('ALIGN', (2, 1), (2, -1), 'RIGHT'),
            # Total row
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#ecf0f1')),
            # Grid
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
        ]))
        elements.append(table)
        return elements
    
    def _create_footer(self):
        """Create receipt footer."""
        elements = []
        
        # Amount in words
        amount_words = self._amount_to_words(int(self.payment.amount))
        elements.append(Paragraph(f"<b>Amount in words:</b> {amount_words} Rupees Only", self.styles['Normal']))
        elements.append(Spacer(1, 30))
        
        # Signature
        sig_style = ParagraphStyle('Signature', alignment=TA_RIGHT, fontSize=10)
        elements.append(Paragraph("_______________________", sig_style))
        elements.append(Paragraph("Authorized Signatory", sig_style))
        
        elements.append(Spacer(1, 20))
        
        # Note
        note_style = ParagraphStyle('Note', fontSize=8, textColor=colors.grey)
        elements.append(Paragraph("This is a computer-generated receipt and does not require a signature.", note_style))
        
        return elements
    
    def _amount_to_words(self, amount):
        """Convert amount to words (Indian format)."""
        ones = ['', 'One', 'Two', 'Three', 'Four', 'Five', 'Six', 'Seven', 'Eight', 'Nine',
                'Ten', 'Eleven', 'Twelve', 'Thirteen', 'Fourteen', 'Fifteen', 'Sixteen',
                'Seventeen', 'Eighteen', 'Nineteen']
        tens = ['', '', 'Twenty', 'Thirty', 'Forty', 'Fifty', 'Sixty', 'Seventy', 'Eighty', 'Ninety']
        
        if amount == 0:
            return 'Zero'
        
        def convert_less_than_thousand(n):
            if n < 20:
                return ones[n]
            elif n < 100:
                return tens[n // 10] + (' ' + ones[n % 10] if n % 10 else '')
            else:
                return ones[n // 100] + ' Hundred' + (' and ' + convert_less_than_thousand(n % 100) if n % 100 else '')
        
        # Indian numbering system
        crore = amount // 10000000
        amount %= 10000000
        lakh = amount // 100000
        amount %= 100000
        thousand = amount // 1000
        amount %= 1000
        
        result = ''
        if crore:
            result += convert_less_than_thousand(crore) + ' Crore '
        if lakh:
            result += convert_less_than_thousand(lakh) + ' Lakh '
        if thousand:
            result += convert_less_than_thousand(thousand) + ' Thousand '
        if amount:
            result += convert_less_than_thousand(amount)
        
        return result.strip()


class AttendanceReportPDF:
    """Generate attendance report PDF."""
    
    def __init__(self, section, month, year):
        self.section = section
        self.month = month
        self.year = year
        self.school = SchoolReportMixin.get_school_info()
        self.styles = getSampleStyleSheet()
    
    def generate(self):
        """Generate attendance report PDF."""
        from calendar import monthrange, month_name
        from apps.attendance.models import StudentAttendance
        from apps.students.models import Student
        
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=landscape(A4),
            rightMargin=0.5*cm,
            leftMargin=0.5*cm,
            topMargin=1*cm,
            bottomMargin=1*cm
        )
        
        elements = []
        
        # Header
        elements.extend(SchoolReportMixin.create_header(self.school))
        
        # Title
        title_style = ParagraphStyle('Title', fontSize=12, alignment=TA_CENTER, spaceAfter=10)
        elements.append(Paragraph(
            f"ATTENDANCE REGISTER - {self.section.standard.name} ({self.section.name}) - {month_name[self.month]} {self.year}",
            title_style
        ))
        
        # Get students and attendance data
        students = Student.objects.filter(current_section=self.section, is_active=True).order_by('roll_number')
        days_in_month = monthrange(self.year, self.month)[1]
        
        # Create header row with dates
        header = ['Roll', 'Student Name'] + [str(d) for d in range(1, days_in_month + 1)] + ['P', 'A', '%']
        data = [header]
        
        # Add student rows
        for student in students:
            row = [str(student.roll_number or '-'), student.full_name[:20]]
            present_count = 0
            absent_count = 0
            
            for day in range(1, days_in_month + 1):
                try:
                    att_date = date(self.year, self.month, day)
                    att = StudentAttendance.objects.filter(
                        student=student,
                        date=att_date
                    ).first()
                    
                    if att:
                        if att.status == 'present':
                            row.append('P')
                            present_count += 1
                        elif att.status == 'absent':
                            row.append('A')
                            absent_count += 1
                        elif att.status == 'late':
                            row.append('L')
                            present_count += 1
                        elif att.status == 'half_day':
                            row.append('H')
                            present_count += 0.5
                            absent_count += 0.5
                        else:
                            row.append('E')  # Leave/Excused
                    else:
                        row.append('-')
                except:
                    row.append('-')
            
            total_days = present_count + absent_count
            percentage = (present_count / total_days * 100) if total_days > 0 else 0
            row.extend([str(int(present_count)), str(int(absent_count)), f"{percentage:.0f}%"])
            data.append(row)
        
        # Create table
        col_widths = [0.8*cm, 3.5*cm] + [0.5*cm] * days_in_month + [0.8*cm, 0.8*cm, 1*cm]
        table = Table(data, colWidths=col_widths)
        table.setStyle(TableStyle([
            # Header
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#34495e')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 7),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            # Body
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 7),
            ('ALIGN', (0, 1), (0, -1), 'CENTER'),
            ('ALIGN', (2, 1), (-1, -1), 'CENTER'),
            # Grid
            ('GRID', (0, 0), (-1, -1), 0.25, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f5f5f5')]),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
        ]))
        elements.append(table)
        
        # Legend
        elements.append(Spacer(1, 10))
        legend_style = ParagraphStyle('Legend', fontSize=8)
        elements.append(Paragraph("P = Present, A = Absent, L = Late, H = Half Day, E = Excused/Leave, - = No Record", legend_style))
        
        doc.build(elements)
        buffer.seek(0)
        return buffer


# =============================================================================
# PDF VIEW HELPERS
# =============================================================================

def generate_report_card_pdf(request, student_id, exam_id):
    """View function to download report card PDF."""
    from apps.students.models import Student
    from apps.examinations.models import Exam
    
    student = Student.objects.get(pk=student_id)
    exam = Exam.objects.get(pk=exam_id)
    
    pdf = StudentReportCard(student, exam)
    buffer = pdf.generate()
    
    response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="report_card_{student.admission_number}_{exam.name}.pdf"'
    return response


def generate_fee_receipt_pdf(request, payment_id):
    """View function to download fee receipt PDF."""
    from apps.fees.models import FeePayment
    
    payment = FeePayment.objects.get(pk=payment_id)
    
    pdf = FeeReceiptPDF(payment)
    buffer = pdf.generate()
    
    response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="fee_receipt_{payment.receipt_number}.pdf"'
    return response


def generate_attendance_report_pdf(request, section_id, month, year):
    """View function to download attendance report PDF."""
    from apps.academics.models import Section
    
    section = Section.objects.get(pk=section_id)
    
    pdf = AttendanceReportPDF(section, int(month), int(year))
    buffer = pdf.generate()
    
    response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="attendance_{section.standard.name}_{section.name}_{month}_{year}.pdf"'
    return response
