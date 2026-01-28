"""
Report URL configuration.
"""
from django.urls import path
from . import pdf_generators, excel_generators

app_name = 'reports'

urlpatterns = [
    # PDF Downloads
    path('report-card/<int:student_id>/<int:exam_id>/', 
         pdf_generators.generate_report_card_pdf, name='download-report-card'),
    path('fee-receipt/<int:payment_id>/', 
         pdf_generators.generate_fee_receipt_pdf, name='download-fee-receipt'),
    path('attendance-pdf/<int:section_id>/<int:month>/<int:year>/', 
         pdf_generators.generate_attendance_report_pdf, name='download-attendance-report'),
    
    # Excel Downloads
    path('students-excel/', 
         excel_generators.download_student_list_excel, name='download-students-excel'),
    path('students-excel/<int:section_id>/', 
         excel_generators.download_student_list_excel, name='download-students-section-excel'),
    path('fee-defaulters-excel/', 
         excel_generators.download_fee_defaulters_excel, name='download-fee-defaulters'),
    path('attendance-excel/<int:section_id>/<int:month>/<int:year>/', 
         excel_generators.download_attendance_excel, name='download-attendance-excel'),
    path('exam-results-excel/<int:exam_id>/', 
         excel_generators.download_exam_results_excel, name='download-exam-results'),
    path('exam-results-excel/<int:exam_id>/<int:section_id>/', 
         excel_generators.download_exam_results_excel, name='download-exam-results-section'),
]
