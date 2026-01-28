"""
Custom API Permissions for School Management System.
"""
from rest_framework import permissions


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Allow read-only access for all authenticated users.
    Write access only for admin users.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated
        return request.user.is_authenticated and request.user.role in ['admin', 'principal']


class IsTeacherOrAdmin(permissions.BasePermission):
    """
    Allow access for teachers and admin users.
    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return request.user.role in ['admin', 'principal', 'teacher']


class IsAccountantOrAdmin(permissions.BasePermission):
    """
    Allow access for accountants and admin users.
    Fee-related permissions.
    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return request.user.role in ['admin', 'principal', 'accountant']


class IsLibrarianOrAdmin(permissions.BasePermission):
    """
    Allow access for librarians and admin users.
    Library-related permissions.
    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return request.user.role in ['admin', 'principal', 'librarian']


class IsParentAccessingChild(permissions.BasePermission):
    """
    Allow parents to access only their children's data.
    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        # Admin and teachers can access all
        if request.user.role in ['admin', 'principal', 'teacher']:
            return True
        
        # Parents can only access their children
        if request.user.role == 'parent':
            return True  # Object-level check will handle specifics
        
        return False
    
    def has_object_permission(self, request, view, obj):
        # Admin and teachers can access all
        if request.user.role in ['admin', 'principal', 'teacher']:
            return True
        
        # Parents can only access their children
        if request.user.role == 'parent':
            # Check if this student belongs to the parent
            from apps.students.models import Student
            if isinstance(obj, Student):
                return (
                    obj.father_phone == request.user.phone or
                    obj.mother_phone == request.user.phone
                )
            # For other models, check student relationship
            if hasattr(obj, 'student'):
                student = obj.student
                return (
                    student.father_phone == request.user.phone or
                    student.mother_phone == request.user.phone
                )
        
        return False


class IsStudentAccessingOwnData(permissions.BasePermission):
    """
    Allow students to access only their own data.
    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        # Admin, teachers can access all
        if request.user.role in ['admin', 'principal', 'teacher']:
            return True
        
        # Students can access their own data
        if request.user.role == 'student':
            return True
        
        return False
    
    def has_object_permission(self, request, view, obj):
        # Admin and teachers can access all
        if request.user.role in ['admin', 'principal', 'teacher']:
            return True
        
        # Students can only access their own data
        if request.user.role == 'student':
            from apps.students.models import Student
            try:
                student = Student.objects.get(user=request.user)
                if isinstance(obj, Student):
                    return obj == student
                if hasattr(obj, 'student'):
                    return obj.student == student
            except Student.DoesNotExist:
                return False
        
        return False


class CanManageAttendance(permissions.BasePermission):
    """
    Only class teachers can mark attendance for their sections.
    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        if request.method in permissions.SAFE_METHODS:
            return True
        
        return request.user.role in ['admin', 'principal', 'teacher']
