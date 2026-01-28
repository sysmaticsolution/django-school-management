"""
API ViewSets for School Management System.
"""
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Sum, Avg
from django.utils import timezone
from drf_spectacular.utils import extend_schema, extend_schema_view

from apps.accounts.models import User
from apps.core.models import SchoolProfile, AcademicYear
from apps.academics.models import Standard, Section, Subject
from apps.students.models import Student
from apps.staff.models import Staff
from apps.fees.models import FeeCategory, FeeStructure, StudentFee, FeePayment
from apps.attendance.models import StudentAttendance, AttendanceSummary
from apps.examinations.models import Exam, ExamResult, ReportCard

from .serializers import (
    UserSerializer, UserProfileSerializer,
    SchoolProfileSerializer, AcademicYearSerializer,
    StandardSerializer, SectionSerializer, SubjectSerializer,
    StudentListSerializer, StudentDetailSerializer, StudentCreateSerializer,
    StaffListSerializer, StaffDetailSerializer,
    FeeCategorySerializer, FeeStructureSerializer, StudentFeeSerializer, FeePaymentSerializer,
    StudentAttendanceSerializer, BulkAttendanceSerializer, AttendanceSummarySerializer,
    ExamSerializer, ExamResultSerializer, ReportCardSerializer,
    ParentDashboardSerializer, ChildSummarySerializer
)
from .permissions import IsAdminOrReadOnly, IsTeacherOrAdmin, IsParentAccessingChild


# =============================================================================
# AUTH VIEWS
# =============================================================================

class CurrentUserView(APIView):
    """Get current authenticated user profile."""
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(responses=UserProfileSerializer)
    def get(self, request):
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data)
    
    @extend_schema(request=UserProfileSerializer, responses=UserProfileSerializer)
    def patch(self, request):
        serializer = UserProfileSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# =============================================================================
# CORE VIEWSETS
# =============================================================================

class SchoolProfileViewSet(viewsets.ReadOnlyModelViewSet):
    """School profile information."""
    queryset = SchoolProfile.objects.all()
    serializer_class = SchoolProfileSerializer
    permission_classes = [permissions.IsAuthenticated]


class AcademicYearViewSet(viewsets.ReadOnlyModelViewSet):
    """Academic years."""
    queryset = AcademicYear.objects.all()
    serializer_class = AcademicYearSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def current(self, request):
        """Get current academic year."""
        year = AcademicYear.objects.filter(is_current=True).first()
        if year:
            return Response(AcademicYearSerializer(year).data)
        return Response({'error': 'No current academic year set'}, status=status.HTTP_404_NOT_FOUND)


# =============================================================================
# ACADEMICS VIEWSETS
# =============================================================================

@extend_schema_view(
    list=extend_schema(tags=['Academics']),
    retrieve=extend_schema(tags=['Academics']),
)
class StandardViewSet(viewsets.ReadOnlyModelViewSet):
    """Standards/Classes."""
    queryset = Standard.objects.filter(is_active=True)
    serializer_class = StandardSerializer
    permission_classes = [permissions.IsAuthenticated]


@extend_schema_view(
    list=extend_schema(tags=['Academics']),
    retrieve=extend_schema(tags=['Academics']),
)
class SectionViewSet(viewsets.ReadOnlyModelViewSet):
    """Sections."""
    queryset = Section.objects.select_related('standard', 'class_teacher', 'academic_year').all()
    serializer_class = SectionSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['standard', 'academic_year']
    search_fields = ['name', 'standard__name']


@extend_schema_view(
    list=extend_schema(tags=['Academics']),
    retrieve=extend_schema(tags=['Academics']),
)
class SubjectViewSet(viewsets.ReadOnlyModelViewSet):
    """Subjects."""
    queryset = Subject.objects.filter(is_active=True)
    serializer_class = SubjectSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['standard', 'subject_type']


# =============================================================================
# STUDENT VIEWSETS
# =============================================================================

@extend_schema_view(
    list=extend_schema(tags=['Students']),
    retrieve=extend_schema(tags=['Students']),
    create=extend_schema(tags=['Students']),
    update=extend_schema(tags=['Students']),
    partial_update=extend_schema(tags=['Students']),
)
class StudentViewSet(viewsets.ModelViewSet):
    """Student management."""
    queryset = Student.objects.select_related('current_section', 'current_section__standard').all()
    permission_classes = [IsTeacherOrAdmin]
    filterset_fields = ['current_section', 'gender', 'is_active', 'is_rte']
    search_fields = ['first_name', 'last_name', 'admission_number', 'phone']
    ordering_fields = ['admission_number', 'first_name', 'created_at']
    ordering = ['admission_number']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return StudentListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return StudentCreateSerializer
        return StudentDetailSerializer
    
    @action(detail=True, methods=['get'])
    def fees(self, request, pk=None):
        """Get student's fee details."""
        student = self.get_object()
        fees = StudentFee.objects.filter(student=student)
        serializer = StudentFeeSerializer(fees, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def attendance(self, request, pk=None):
        """Get student's attendance."""
        student = self.get_object()
        month = request.query_params.get('month', timezone.now().month)
        year = request.query_params.get('year', timezone.now().year)
        
        attendance = StudentAttendance.objects.filter(
            student=student,
            date__month=month,
            date__year=year
        ).order_by('date')
        serializer = StudentAttendanceSerializer(attendance, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def results(self, request, pk=None):
        """Get student's exam results."""
        student = self.get_object()
        results = ReportCard.objects.filter(student=student).select_related('exam')
        serializer = ReportCardSerializer(results, many=True)
        return Response(serializer.data)


# =============================================================================
# STAFF VIEWSETS
# =============================================================================

@extend_schema_view(
    list=extend_schema(tags=['Staff']),
    retrieve=extend_schema(tags=['Staff']),
)
class StaffViewSet(viewsets.ModelViewSet):
    """Staff management."""
    queryset = Staff.objects.select_related('department', 'user').all()
    permission_classes = [IsAdminOrReadOnly]
    filterset_fields = ['department', 'designation', 'is_active']
    search_fields = ['first_name', 'last_name', 'employee_id']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return StaffListSerializer
        return StaffDetailSerializer


# =============================================================================
# FEE VIEWSETS
# =============================================================================

@extend_schema_view(
    list=extend_schema(tags=['Fees']),
    retrieve=extend_schema(tags=['Fees']),
)
class FeeCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """Fee categories."""
    queryset = FeeCategory.objects.all()
    serializer_class = FeeCategorySerializer
    permission_classes = [permissions.IsAuthenticated]


@extend_schema_view(
    list=extend_schema(tags=['Fees']),
    retrieve=extend_schema(tags=['Fees']),
)
class StudentFeeViewSet(viewsets.ModelViewSet):
    """Student fees."""
    queryset = StudentFee.objects.select_related('student', 'fee_structure').all()
    serializer_class = StudentFeeSerializer
    permission_classes = [IsTeacherOrAdmin]
    filterset_fields = ['student', 'status', 'fee_structure__category']
    search_fields = ['student__first_name', 'student__admission_number']
    
    @action(detail=False, methods=['get'])
    def pending(self, request):
        """Get all pending fees."""
        pending = self.get_queryset().filter(status__in=['pending', 'partial'])
        serializer = self.get_serializer(pending, many=True)
        return Response(serializer.data)


@extend_schema_view(
    list=extend_schema(tags=['Fees']),
    create=extend_schema(tags=['Fees']),
)
class FeePaymentViewSet(viewsets.ModelViewSet):
    """Fee payments."""
    queryset = FeePayment.objects.select_related('student').all()
    serializer_class = FeePaymentSerializer
    permission_classes = [IsTeacherOrAdmin]
    filterset_fields = ['student', 'payment_mode', 'payment_date']


# =============================================================================
# ATTENDANCE VIEWSETS
# =============================================================================

@extend_schema_view(
    list=extend_schema(tags=['Attendance']),
    retrieve=extend_schema(tags=['Attendance']),
)
class AttendanceViewSet(viewsets.ModelViewSet):
    """Attendance management."""
    queryset = StudentAttendance.objects.select_related('student', 'section').all()
    serializer_class = StudentAttendanceSerializer
    permission_classes = [IsTeacherOrAdmin]
    filterset_fields = ['section', 'date', 'status']
    
    @extend_schema(request=BulkAttendanceSerializer, tags=['Attendance'])
    @action(detail=False, methods=['post'])
    def bulk_mark(self, request):
        """Mark attendance for multiple students."""
        serializer = BulkAttendanceSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            section = Section.objects.get(pk=data['section_id'])
            created_count = 0
            
            for record in data['attendance']:
                student = Student.objects.get(pk=record['student_id'])
                obj, created = StudentAttendance.objects.update_or_create(
                    student=student,
                    section=section,
                    date=data['date'],
                    defaults={
                        'status': record['status'],
                        'remarks': record.get('remarks', ''),
                        'marked_by': request.user
                    }
                )
                if created:
                    created_count += 1
            
            return Response({
                'message': f'Attendance marked for {len(data["attendance"])} students',
                'created': created_count,
                'updated': len(data['attendance']) - created_count
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema_view(
    list=extend_schema(tags=['Attendance']),
)
class AttendanceSummaryViewSet(viewsets.ReadOnlyModelViewSet):
    """Attendance summaries."""
    queryset = AttendanceSummary.objects.select_related('student', 'section').all()
    serializer_class = AttendanceSummarySerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['section', 'month', 'year']


# =============================================================================
# EXAMINATION VIEWSETS
# =============================================================================

@extend_schema_view(
    list=extend_schema(tags=['Examinations']),
    retrieve=extend_schema(tags=['Examinations']),
)
class ExamViewSet(viewsets.ReadOnlyModelViewSet):
    """Examinations."""
    queryset = Exam.objects.all()
    serializer_class = ExamSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['academic_year', 'is_published']


@extend_schema_view(
    list=extend_schema(tags=['Examinations']),
    retrieve=extend_schema(tags=['Examinations']),
)
class ExamResultViewSet(viewsets.ModelViewSet):
    """Exam results."""
    queryset = ExamResult.objects.select_related('student', 'exam', 'subject').all()
    serializer_class = ExamResultSerializer
    permission_classes = [IsTeacherOrAdmin]
    filterset_fields = ['exam', 'student', 'subject', 'is_pass']


@extend_schema_view(
    list=extend_schema(tags=['Examinations']),
    retrieve=extend_schema(tags=['Examinations']),
)
class ReportCardViewSet(viewsets.ReadOnlyModelViewSet):
    """Report cards."""
    queryset = ReportCard.objects.select_related('student', 'exam').all()
    serializer_class = ReportCardSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['exam', 'student']


# =============================================================================
# PARENT PORTAL VIEWS
# =============================================================================

class ParentDashboardView(APIView):
    """Parent dashboard with child information."""
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(responses=ChildSummarySerializer(many=True), tags=['Parent Portal'])
    def get(self, request):
        """Get dashboard data for parent's children."""
        user = request.user
        
        if user.role != 'parent':
            return Response(
                {'error': 'This endpoint is only for parents'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Get children linked to this parent
        children = Student.objects.filter(
            models.Q(father_phone=user.phone) | 
            models.Q(mother_phone=user.phone)
        ).filter(is_active=True)
        
        result = []
        for child in children:
            # Calculate attendance
            current_month = timezone.now().month
            current_year = timezone.now().year
            summary = AttendanceSummary.objects.filter(
                student=child,
                month=current_month,
                year=current_year
            ).first()
            
            attendance_pct = 0
            if summary and summary.total_working_days > 0:
                attendance_pct = (summary.present_days / summary.total_working_days) * 100
            
            # Calculate pending fees
            pending_fees = StudentFee.objects.filter(
                student=child,
                status__in=['pending', 'partial']
            ).aggregate(total=Sum('balance'))['total'] or 0
            
            # Last exam result
            last_report = ReportCard.objects.filter(
                student=child
            ).order_by('-exam__end_date').first()
            
            result.append({
                'student': StudentDetailSerializer(child).data,
                'attendance_percentage': round(attendance_pct, 2),
                'total_pending_fees': pending_fees,
                'last_exam_percentage': last_report.percentage if last_report else None
            })
        
        return Response(result)


class ChildDetailView(APIView):
    """Detailed view for a specific child."""
    permission_classes = [permissions.IsAuthenticated, IsParentAccessingChild]
    
    @extend_schema(responses=ParentDashboardSerializer, tags=['Parent Portal'])
    def get(self, request, student_id):
        """Get detailed information for a child."""
        try:
            student = Student.objects.get(pk=student_id)
        except Student.DoesNotExist:
            return Response({'error': 'Student not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Get attendance summary
        current_month = timezone.now().month
        current_year = timezone.now().year
        attendance = AttendanceSummary.objects.filter(
            student=student,
            month=current_month,
            year=current_year
        ).first()
        
        # Get pending fees
        pending_fees = StudentFee.objects.filter(
            student=student,
            status__in=['pending', 'partial']
        )
        
        # Get recent results
        recent_results = ReportCard.objects.filter(
            student=student
        ).order_by('-exam__end_date')[:5]
        
        return Response({
            'student': StudentDetailSerializer(student).data,
            'attendance_summary': AttendanceSummarySerializer(attendance).data if attendance else None,
            'pending_fees': StudentFeeSerializer(pending_fees, many=True).data,
            'recent_results': ReportCardSerializer(recent_results, many=True).data
        })
