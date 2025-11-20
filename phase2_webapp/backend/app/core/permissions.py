"""
Permissions and Authorization System
=====================================

Role-based access control (RBAC) for Healthrix system.
"""

from typing import List, Optional, Set
from enum import Enum
from fastapi import HTTPException, status

from ..models.user import UserRole


class Permission(str, Enum):
    """System permissions."""

    # User Management
    USER_CREATE = "user:create"
    USER_READ = "user:read"
    USER_UPDATE = "user:update"
    USER_DELETE = "user:delete"
    USER_ACTIVATE = "user:activate"
    USER_DEACTIVATE = "user:deactivate"
    USER_CHANGE_ROLE = "user:change_role"

    # Department Management
    DEPT_CREATE = "department:create"
    DEPT_READ = "department:read"
    DEPT_UPDATE = "department:update"
    DEPT_DELETE = "department:delete"
    DEPT_ASSIGN_MANAGER = "department:assign_manager"

    # Performance Management
    PERF_CALCULATE = "performance:calculate"
    PERF_VIEW_ALL = "performance:view_all"
    PERF_VIEW_DEPARTMENT = "performance:view_department"
    PERF_VIEW_OWN = "performance:view_own"
    PERF_EDIT = "performance:edit"

    # Activity Management
    ACTIVITY_CREATE_OWN = "activity:create_own"
    ACTIVITY_CREATE_ANY = "activity:create_any"
    ACTIVITY_VIEW_ALL = "activity:view_all"
    ACTIVITY_VIEW_DEPARTMENT = "activity:view_department"
    ACTIVITY_VIEW_OWN = "activity:view_own"
    ACTIVITY_EDIT_ANY = "activity:edit_any"
    ACTIVITY_DELETE_ANY = "activity:delete_any"

    # Report Management
    REPORT_GENERATE_ALL = "report:generate_all"
    REPORT_GENERATE_DEPARTMENT = "report:generate_department"
    REPORT_VIEW_ALL = "report:view_all"
    REPORT_VIEW_DEPARTMENT = "report:view_department"
    REPORT_VIEW_OWN = "report:view_own"

    # System Settings
    SETTINGS_MANAGE = "settings:manage"
    SETTINGS_VIEW = "settings:view"

    # Task Standards
    STANDARDS_MANAGE = "standards:manage"
    STANDARDS_VIEW = "standards:view"


# Role-based permission mapping
ROLE_PERMISSIONS: dict[UserRole, Set[Permission]] = {
    UserRole.SUPER_ADMIN: {
        # Full system access
        Permission.USER_CREATE,
        Permission.USER_READ,
        Permission.USER_UPDATE,
        Permission.USER_DELETE,
        Permission.USER_ACTIVATE,
        Permission.USER_DEACTIVATE,
        Permission.USER_CHANGE_ROLE,
        Permission.DEPT_CREATE,
        Permission.DEPT_READ,
        Permission.DEPT_UPDATE,
        Permission.DEPT_DELETE,
        Permission.DEPT_ASSIGN_MANAGER,
        Permission.PERF_CALCULATE,
        Permission.PERF_VIEW_ALL,
        Permission.PERF_VIEW_DEPARTMENT,
        Permission.PERF_VIEW_OWN,
        Permission.PERF_EDIT,
        Permission.ACTIVITY_CREATE_OWN,
        Permission.ACTIVITY_CREATE_ANY,
        Permission.ACTIVITY_VIEW_ALL,
        Permission.ACTIVITY_VIEW_DEPARTMENT,
        Permission.ACTIVITY_VIEW_OWN,
        Permission.ACTIVITY_EDIT_ANY,
        Permission.ACTIVITY_DELETE_ANY,
        Permission.REPORT_GENERATE_ALL,
        Permission.REPORT_GENERATE_DEPARTMENT,
        Permission.REPORT_VIEW_ALL,
        Permission.REPORT_VIEW_DEPARTMENT,
        Permission.REPORT_VIEW_OWN,
        Permission.SETTINGS_MANAGE,
        Permission.SETTINGS_VIEW,
        Permission.STANDARDS_MANAGE,
        Permission.STANDARDS_VIEW,
    },

    UserRole.ADMIN: {
        # Can manage most operations, cannot create super admins
        Permission.USER_CREATE,
        Permission.USER_READ,
        Permission.USER_UPDATE,
        Permission.USER_DELETE,
        Permission.USER_ACTIVATE,
        Permission.USER_DEACTIVATE,
        # USER_CHANGE_ROLE is limited - handled in authorization logic
        Permission.DEPT_CREATE,
        Permission.DEPT_READ,
        Permission.DEPT_UPDATE,
        Permission.DEPT_DELETE,
        Permission.DEPT_ASSIGN_MANAGER,
        Permission.PERF_CALCULATE,
        Permission.PERF_VIEW_ALL,
        Permission.PERF_VIEW_DEPARTMENT,
        Permission.PERF_VIEW_OWN,
        Permission.PERF_EDIT,
        Permission.ACTIVITY_CREATE_OWN,
        Permission.ACTIVITY_CREATE_ANY,
        Permission.ACTIVITY_VIEW_ALL,
        Permission.ACTIVITY_VIEW_DEPARTMENT,
        Permission.ACTIVITY_VIEW_OWN,
        Permission.ACTIVITY_EDIT_ANY,
        Permission.ACTIVITY_DELETE_ANY,
        Permission.REPORT_GENERATE_ALL,
        Permission.REPORT_GENERATE_DEPARTMENT,
        Permission.REPORT_VIEW_ALL,
        Permission.REPORT_VIEW_DEPARTMENT,
        Permission.REPORT_VIEW_OWN,
        Permission.SETTINGS_VIEW,
        Permission.STANDARDS_MANAGE,
        Permission.STANDARDS_VIEW,
    },

    UserRole.HR: {
        # Can manage employees and view all performance data
        Permission.USER_CREATE,
        Permission.USER_READ,
        Permission.USER_UPDATE,
        Permission.USER_ACTIVATE,
        Permission.USER_DEACTIVATE,
        Permission.DEPT_READ,
        Permission.PERF_CALCULATE,
        Permission.PERF_VIEW_ALL,
        Permission.PERF_VIEW_DEPARTMENT,
        Permission.PERF_VIEW_OWN,
        Permission.ACTIVITY_CREATE_OWN,
        Permission.ACTIVITY_VIEW_ALL,
        Permission.ACTIVITY_VIEW_DEPARTMENT,
        Permission.ACTIVITY_VIEW_OWN,
        Permission.REPORT_GENERATE_ALL,
        Permission.REPORT_GENERATE_DEPARTMENT,
        Permission.REPORT_VIEW_ALL,
        Permission.REPORT_VIEW_DEPARTMENT,
        Permission.REPORT_VIEW_OWN,
        Permission.SETTINGS_VIEW,
        Permission.STANDARDS_VIEW,
    },

    UserRole.DEPARTMENT_HEAD: {
        # Can manage department employees and view department performance
        Permission.USER_READ,
        Permission.DEPT_READ,
        Permission.PERF_CALCULATE,
        Permission.PERF_VIEW_DEPARTMENT,
        Permission.PERF_VIEW_OWN,
        Permission.ACTIVITY_CREATE_OWN,
        Permission.ACTIVITY_VIEW_DEPARTMENT,
        Permission.ACTIVITY_VIEW_OWN,
        Permission.REPORT_GENERATE_DEPARTMENT,
        Permission.REPORT_VIEW_DEPARTMENT,
        Permission.REPORT_VIEW_OWN,
        Permission.SETTINGS_VIEW,
        Permission.STANDARDS_VIEW,
    },

    UserRole.EMPLOYEE: {
        # Can view own data and submit activities
        Permission.PERF_VIEW_OWN,
        Permission.ACTIVITY_CREATE_OWN,
        Permission.ACTIVITY_VIEW_OWN,
        Permission.REPORT_VIEW_OWN,
        Permission.SETTINGS_VIEW,
        Permission.STANDARDS_VIEW,
    },
}


class PermissionChecker:
    """Permission checking utilities."""

    @staticmethod
    def has_permission(user_role: UserRole, permission: Permission) -> bool:
        """
        Check if a role has a specific permission.

        Args:
            user_role: The user's role
            permission: The permission to check

        Returns:
            True if the role has the permission, False otherwise
        """
        return permission in ROLE_PERMISSIONS.get(user_role, set())

    @staticmethod
    def has_any_permission(user_role: UserRole, permissions: List[Permission]) -> bool:
        """
        Check if a role has any of the specified permissions.

        Args:
            user_role: The user's role
            permissions: List of permissions to check

        Returns:
            True if the role has at least one permission, False otherwise
        """
        user_permissions = ROLE_PERMISSIONS.get(user_role, set())
        return any(perm in user_permissions for perm in permissions)

    @staticmethod
    def has_all_permissions(user_role: UserRole, permissions: List[Permission]) -> bool:
        """
        Check if a role has all of the specified permissions.

        Args:
            user_role: The user's role
            permissions: List of permissions to check

        Returns:
            True if the role has all permissions, False otherwise
        """
        user_permissions = ROLE_PERMISSIONS.get(user_role, set())
        return all(perm in user_permissions for perm in permissions)

    @staticmethod
    def require_permission(user_role: UserRole, permission: Permission) -> None:
        """
        Require a specific permission, raise HTTPException if not authorized.

        Args:
            user_role: The user's role
            permission: The required permission

        Raises:
            HTTPException: 403 Forbidden if user doesn't have permission
        """
        if not PermissionChecker.has_permission(user_role, permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required: {permission.value}"
            )

    @staticmethod
    def require_any_permission(user_role: UserRole, permissions: List[Permission]) -> None:
        """
        Require any of the specified permissions, raise HTTPException if not authorized.

        Args:
            user_role: The user's role
            permissions: List of required permissions (any)

        Raises:
            HTTPException: 403 Forbidden if user doesn't have any permission
        """
        if not PermissionChecker.has_any_permission(user_role, permissions):
            perm_names = [p.value for p in permissions]
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required any of: {', '.join(perm_names)}"
            )

    @staticmethod
    def require_all_permissions(user_role: UserRole, permissions: List[Permission]) -> None:
        """
        Require all specified permissions, raise HTTPException if not authorized.

        Args:
            user_role: The user's role
            permissions: List of required permissions (all)

        Raises:
            HTTPException: 403 Forbidden if user doesn't have all permissions
        """
        if not PermissionChecker.has_all_permissions(user_role, permissions):
            perm_names = [p.value for p in permissions]
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required all of: {', '.join(perm_names)}"
            )

    @staticmethod
    def can_manage_user_role(manager_role: UserRole, target_role: UserRole) -> bool:
        """
        Check if a manager can create/modify users with a specific role.

        Rules:
        - SUPER_ADMIN: Can manage all roles
        - ADMIN: Can manage all roles except SUPER_ADMIN
        - HR: Can manage EMPLOYEE, DEPARTMENT_HEAD
        - Others: Cannot manage user roles

        Args:
            manager_role: The role of the user trying to manage
            target_role: The role being assigned/modified

        Returns:
            True if manager can manage the target role, False otherwise
        """
        if manager_role == UserRole.SUPER_ADMIN:
            return True

        if manager_role == UserRole.ADMIN:
            return target_role != UserRole.SUPER_ADMIN

        if manager_role == UserRole.HR:
            return target_role in [UserRole.EMPLOYEE, UserRole.DEPARTMENT_HEAD]

        return False

    @staticmethod
    def get_role_hierarchy_level(role: UserRole) -> int:
        """
        Get the hierarchy level of a role (higher number = more permissions).

        Args:
            role: The user role

        Returns:
            Hierarchy level (0-4)
        """
        hierarchy = {
            UserRole.SUPER_ADMIN: 4,
            UserRole.ADMIN: 3,
            UserRole.HR: 2,
            UserRole.DEPARTMENT_HEAD: 1,
            UserRole.EMPLOYEE: 0,
        }
        return hierarchy.get(role, 0)

    @staticmethod
    def can_access_user_data(viewer_role: UserRole, viewer_emp_id: str,
                            viewer_dept_id: Optional[int],
                            target_emp_id: str, target_dept_id: Optional[int]) -> bool:
        """
        Check if a user can access another user's data based on role and department.

        Args:
            viewer_role: Role of the user trying to view data
            viewer_emp_id: Employee ID of the viewer
            viewer_dept_id: Department ID of the viewer
            target_emp_id: Employee ID of the target user
            target_dept_id: Department ID of the target user

        Returns:
            True if viewer can access target's data, False otherwise
        """
        # Can always view own data
        if viewer_emp_id == target_emp_id:
            return True

        # Super Admin and Admin can view all
        if viewer_role in [UserRole.SUPER_ADMIN, UserRole.ADMIN, UserRole.HR]:
            return True

        # Department Head can view their department
        if viewer_role == UserRole.DEPARTMENT_HEAD:
            return viewer_dept_id == target_dept_id and target_dept_id is not None

        # Employees can only view own data
        return False
