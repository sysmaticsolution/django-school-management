"""
API URL Configuration.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

from .views import (
    CurrentUserView,
    SchoolProfileViewSet, AcademicYearViewSet,
    StandardViewSet, SectionViewSet, SubjectViewSet,
    StudentViewSet, StaffViewSet,
    FeeCategoryViewSet, StudentFeeViewSet, FeePaymentViewSet,
    AttendanceViewSet, AttendanceSummaryViewSet,
    ExamViewSet, ExamResultViewSet, ReportCardViewSet,
    ParentDashboardView, ChildDetailView,
)

# Create router
router = DefaultRouter()

# Core
router.register('school', SchoolProfileViewSet, basename='school')
router.register('academic-years', AcademicYearViewSet, basename='academic-years')

# Academics
router.register('standards', StandardViewSet, basename='standards')
router.register('sections', SectionViewSet, basename='sections')
router.register('subjects', SubjectViewSet, basename='subjects')

# Students & Staff
router.register('students', StudentViewSet, basename='students')
router.register('staff', StaffViewSet, basename='staff')

# Fees
router.register('fee-categories', FeeCategoryViewSet, basename='fee-categories')
router.register('student-fees', StudentFeeViewSet, basename='student-fees')
router.register('fee-payments', FeePaymentViewSet, basename='fee-payments')

# Attendance
router.register('attendance', AttendanceViewSet, basename='attendance')
router.register('attendance-summary', AttendanceSummaryViewSet, basename='attendance-summary')

# Examinations
router.register('exams', ExamViewSet, basename='exams')
router.register('exam-results', ExamResultViewSet, basename='exam-results')
router.register('report-cards', ReportCardViewSet, basename='report-cards')

urlpatterns = [
    # JWT Authentication
    path('auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    
    # Current User
    path('auth/me/', CurrentUserView.as_view(), name='current-user'),
    
    # Parent Portal
    path('parent/dashboard/', ParentDashboardView.as_view(), name='parent-dashboard'),
    path('parent/child/<int:student_id>/', ChildDetailView.as_view(), name='child-detail'),
    
    # API Schema & Documentation
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    
    # Router URLs
    path('', include(router.urls)),
]
