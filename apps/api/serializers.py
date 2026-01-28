"""
API Serializers for School Management System.
"""
from rest_framework import serializers
from apps.accounts.models import User
from apps.core.models import SchoolProfile, AcademicYear
from apps.academics.models import Standard, Section, Subject
from apps.students.models import Student
from apps.staff.models import Staff
from apps.fees.models import FeeCategory, FeeStructure, StudentFee, FeePayment
from apps.attendance.models import StudentAttendance, AttendanceSummary
from apps.examinations.models import Exam, ExamResult, ReportCard


# =============================================================================
# AUTH SERIALIZERS
# =============================================================================

class UserSerializer(serializers.ModelSerializer):
    """User serializer for authentication."""
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 
                  'full_name', 'role', 'phone', 'is_active']
        read_only_fields = ['id', 'is_active']


class UserProfileSerializer(serializers.ModelSerializer):
    """Detailed user profile."""
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name',
                  'role', 'phone', 'profile_photo', 'date_joined']
        read_only_fields = ['id', 'username', 'role', 'date_joined']


# =============================================================================
# CORE SERIALIZERS
# =============================================================================

class SchoolProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = SchoolProfile
        fields = '__all__'


class AcademicYearSerializer(serializers.ModelSerializer):
    class Meta:
        model = AcademicYear
        fields = ['id', 'name', 'start_date', 'end_date', 'is_current']


# =============================================================================
# ACADEMICS SERIALIZERS
# =============================================================================

class StandardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Standard
        fields = ['id', 'name', 'code', 'order', 'is_active']


class SectionSerializer(serializers.ModelSerializer):
    standard_name = serializers.CharField(source='standard.name', read_only=True)
    class_teacher_name = serializers.CharField(source='class_teacher.full_name', read_only=True)
    
    class Meta:
        model = Section
        fields = ['id', 'name', 'standard', 'standard_name', 'academic_year',
                  'class_teacher', 'class_teacher_name', 'room_number', 'capacity']


class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = ['id', 'name', 'code', 'subject_type', 'is_elective']


# =============================================================================
# STUDENT SERIALIZERS
# =============================================================================

class StudentListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for student lists."""
    full_name = serializers.CharField(read_only=True)
    current_class = serializers.CharField(source='current_section.standard.name', read_only=True)
    section = serializers.CharField(source='current_section.name', read_only=True)
    
    class Meta:
        model = Student
        fields = ['id', 'admission_number', 'full_name', 'current_class', 
                  'section', 'phone', 'is_active']


class StudentDetailSerializer(serializers.ModelSerializer):
    """Detailed student serializer."""
    full_name = serializers.CharField(read_only=True)
    age = serializers.IntegerField(read_only=True)
    current_section_detail = SectionSerializer(source='current_section', read_only=True)
    
    class Meta:
        model = Student
        fields = [
            'id', 'admission_number', 'first_name', 'middle_name', 'last_name',
            'full_name', 'date_of_birth', 'age', 'gender', 'blood_group',
            'nationality', 'religion', 'category', 'aadhar_number',
            'current_section', 'current_section_detail', 'roll_number',
            'admission_date', 'phone', 'email', 'address',
            'father_name', 'father_phone', 'mother_name', 'mother_phone',
            'photo', 'is_active', 'is_rte'
        ]


class StudentCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating students."""
    
    class Meta:
        model = Student
        exclude = ['created_at', 'updated_at']


# =============================================================================
# STAFF SERIALIZERS
# =============================================================================

class StaffListSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(read_only=True)
    department_name = serializers.CharField(source='department.name', read_only=True)
    
    class Meta:
        model = Staff
        fields = ['id', 'employee_id', 'full_name', 'designation', 
                  'department_name', 'phone', 'is_active']


class StaffDetailSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(read_only=True)
    
    class Meta:
        model = Staff
        fields = '__all__'


# =============================================================================
# FEE SERIALIZERS
# =============================================================================

class FeeCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = FeeCategory
        fields = ['id', 'name', 'code', 'description']


class FeeStructureSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    
    class Meta:
        model = FeeStructure
        fields = ['id', 'category', 'category_name', 'standard', 
                  'amount', 'due_date', 'academic_year']


class StudentFeeSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.full_name', read_only=True)
    fee_structure_name = serializers.CharField(source='fee_structure.category.name', read_only=True)
    
    class Meta:
        model = StudentFee
        fields = ['id', 'student', 'student_name', 'fee_structure', 
                  'fee_structure_name', 'amount', 'discount', 'final_amount',
                  'paid_amount', 'balance', 'status', 'due_date']


class FeePaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeePayment
        fields = ['id', 'student', 'receipt_number', 'payment_date',
                  'amount', 'payment_mode', 'remarks']


# =============================================================================
# ATTENDANCE SERIALIZERS
# =============================================================================

class StudentAttendanceSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.full_name', read_only=True)
    
    class Meta:
        model = StudentAttendance
        fields = ['id', 'student', 'student_name', 'date', 'status', 'remarks']


class AttendanceMarkSerializer(serializers.Serializer):
    """Serializer for bulk attendance marking."""
    student_id = serializers.IntegerField()
    status = serializers.ChoiceField(choices=['present', 'absent', 'late', 'half_day', 'leave'])
    remarks = serializers.CharField(required=False, allow_blank=True)


class BulkAttendanceSerializer(serializers.Serializer):
    """Serializer for bulk attendance submission."""
    section_id = serializers.IntegerField()
    date = serializers.DateField()
    attendance = serializers.ListField(child=AttendanceMarkSerializer())


class AttendanceSummarySerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.full_name', read_only=True)
    attendance_percentage = serializers.FloatField(read_only=True)
    
    class Meta:
        model = AttendanceSummary
        fields = ['id', 'student', 'student_name', 'month', 'year',
                  'total_working_days', 'present_days', 'absent_days',
                  'late_days', 'attendance_percentage']


# =============================================================================
# EXAMINATION SERIALIZERS
# =============================================================================

class ExamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exam
        fields = ['id', 'name', 'exam_type', 'academic_year', 
                  'start_date', 'end_date', 'is_published']


class ExamResultSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.full_name', read_only=True)
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    
    class Meta:
        model = ExamResult
        fields = ['id', 'student', 'student_name', 'exam', 'subject', 
                  'subject_name', 'marks_obtained', 'max_marks', 
                  'percentage', 'grade', 'is_pass']


class ReportCardSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.full_name', read_only=True)
    exam_name = serializers.CharField(source='exam.name', read_only=True)
    
    class Meta:
        model = ReportCard
        fields = ['id', 'student', 'student_name', 'exam', 'exam_name',
                  'total_marks', 'marks_obtained', 'percentage', 
                  'overall_grade', 'rank', 'remarks']


# =============================================================================
# PARENT PORTAL SERIALIZERS
# =============================================================================

class ParentDashboardSerializer(serializers.Serializer):
    """Dashboard data for parent portal."""
    student = StudentDetailSerializer()
    attendance_summary = AttendanceSummarySerializer()
    pending_fees = StudentFeeSerializer(many=True)
    recent_results = ReportCardSerializer(many=True)
    

class ChildSummarySerializer(serializers.Serializer):
    """Summary of child information for parent."""
    student = StudentDetailSerializer()
    attendance_percentage = serializers.FloatField()
    total_pending_fees = serializers.DecimalField(max_digits=12, decimal_places=2)
    last_exam_percentage = serializers.FloatField(allow_null=True)
