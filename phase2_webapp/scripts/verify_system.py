#!/usr/bin/env python3
"""
Healthrix System Verification & Health Check
=============================================

Comprehensive production readiness verification script with colorful output.
"""

import sys
import os
from typing import List, Tuple, Dict
from datetime import datetime

# ANSI Color Codes
class Colors:
    """Terminal color codes for beautiful output."""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

    # Background colors
    BG_GREEN = '\033[42m'
    BG_RED = '\033[41m'
    BG_YELLOW = '\033[43m'
    BG_BLUE = '\033[44m'

    # Emojis
    CHECK = '✅'
    CROSS = '❌'
    WARNING_EMOJI = '⚠️'
    ROCKET = '🚀'
    SHIELD = '🔐'
    DATABASE = '🗄️'
    API = '🌐'
    GEAR = '⚙️'
    FIRE = '🔥'
    STAR = '⭐'
    PARTY = '🎉'


def print_banner():
    """Print colorful application banner."""
    banner = f"""
{Colors.OKCYAN}{Colors.BOLD}
╔══════════════════════════════════════════════════════════════════════╗
║                                                                      ║
║  {Colors.OKGREEN}██╗  ██╗███████╗ █████╗ ██╗  ████████╗██╗  ██╗██████╗ ██╗██╗  ██╗{Colors.OKCYAN}  ║
║  {Colors.OKGREEN}██║  ██║██╔════╝██╔══██╗██║  ╚══██╔══╝██║  ██║██╔══██╗██║╚██╗██╔╝{Colors.OKCYAN}  ║
║  {Colors.OKGREEN}███████║█████╗  ███████║██║     ██║   ███████║██████╔╝██║ ╚███╔╝ {Colors.OKCYAN}  ║
║  {Colors.OKGREEN}██╔══██║██╔══╝  ██╔══██║██║     ██║   ██╔══██║██╔══██╗██║ ██╔██╗ {Colors.OKCYAN}  ║
║  {Colors.OKGREEN}██║  ██║███████╗██║  ██║███████╗██║   ██║  ██║██║  ██║██║██╔╝ ██╗{Colors.OKCYAN}  ║
║  {Colors.OKGREEN}╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚══════╝╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝╚═╝  ╚═╝{Colors.OKCYAN}  ║
║                                                                      ║
║           {Colors.HEADER}Productivity System - Production Verification{Colors.OKCYAN}             ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
{Colors.ENDC}"""
    print(banner)


def print_section(title: str, emoji: str = "📋"):
    """Print a section header."""
    print(f"\n{Colors.BOLD}{Colors.OKBLUE}{'='*70}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.HEADER}{emoji}  {title}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.OKBLUE}{'='*70}{Colors.ENDC}\n")


def print_test(name: str, status: bool, details: str = ""):
    """Print a test result."""
    status_icon = Colors.CHECK if status else Colors.CROSS
    status_color = Colors.OKGREEN if status else Colors.FAIL

    print(f"{status_icon}  {Colors.BOLD}{name:<50}{Colors.ENDC} {status_color}{'PASS' if status else 'FAIL'}{Colors.ENDC}")
    if details:
        print(f"   {Colors.OKCYAN}└─ {details}{Colors.ENDC}")


def print_info(message: str):
    """Print info message."""
    print(f"{Colors.OKCYAN}ℹ️  {message}{Colors.ENDC}")


def print_warning(message: str):
    """Print warning message."""
    print(f"{Colors.WARNING}⚠️  {message}{Colors.ENDC}")


def print_success(message: str):
    """Print success message."""
    print(f"{Colors.OKGREEN}✅ {message}{Colors.ENDC}")


def print_error(message: str):
    """Print error message."""
    print(f"{Colors.FAIL}❌ {message}{Colors.ENDC}")


class HealthChecker:
    """System health checker with comprehensive validation."""

    def __init__(self):
        self.results: List[Tuple[str, bool, str]] = []
        self.critical_failures = 0
        self.warnings = 0
        self.successes = 0

    def check_python_version(self) -> bool:
        """Check Python version."""
        version = sys.version_info
        required_major, required_minor = 3, 11

        is_valid = version.major >= required_major and version.minor >= required_minor

        details = f"Python {version.major}.{version.minor}.{version.micro}"
        if not is_valid:
            details += f" (Required: {required_major}.{required_minor}+)"

        self.results.append(("Python Version", is_valid, details))
        return is_valid

    def check_imports(self) -> Dict[str, bool]:
        """Check all required imports."""
        print_info("Checking Python package imports...")

        packages = {
            "FastAPI": "fastapi",
            "SQLAlchemy": "sqlalchemy",
            "Pydantic": "pydantic",
            "JWT (PyJWT)": "jwt",
            "Bcrypt (passlib)": "passlib",
            "PostgreSQL Driver": "psycopg2",
            "Redis": "redis",
            "Uvicorn": "uvicorn",
        }

        results = {}
        for name, package in packages.items():
            try:
                __import__(package)
                results[name] = True
                self.results.append((f"Import: {name}", True, f"{package} installed"))
            except ImportError:
                results[name] = False
                self.results.append((f"Import: {name}", False, f"{package} not found"))

        return results

    def check_models(self) -> bool:
        """Check database models."""
        try:
            from app.models import User, UserRole, Department, TaskStandard, Activity
            from app.models import DailyMetric, PerformanceScore

            # Check UserRole enum
            roles = [UserRole.SUPER_ADMIN, UserRole.ADMIN, UserRole.HR,
                    UserRole.DEPARTMENT_HEAD, UserRole.EMPLOYEE]

            self.results.append(("Database Models", True, "All 7 models loaded"))
            self.results.append(("UserRole Enum", True, f"5 roles defined"))
            return True
        except Exception as e:
            self.results.append(("Database Models", False, str(e)))
            return False

    def check_permissions(self) -> bool:
        """Check permission system."""
        try:
            from app.core.permissions import Permission, PermissionChecker, ROLE_PERMISSIONS
            from app.models.user import UserRole

            # Count permissions
            permission_count = len([p for p in Permission])

            # Check role permissions are defined
            all_roles_defined = all(
                role in ROLE_PERMISSIONS
                for role in [UserRole.SUPER_ADMIN, UserRole.ADMIN, UserRole.HR,
                           UserRole.DEPARTMENT_HEAD, UserRole.EMPLOYEE]
            )

            self.results.append(("Permission System", True, f"{permission_count} permissions defined"))
            self.results.append(("Role Permission Mapping", all_roles_defined, "All 5 roles mapped"))
            return True
        except Exception as e:
            self.results.append(("Permission System", False, str(e)))
            return False

    def check_endpoints(self) -> bool:
        """Check API endpoints."""
        try:
            from app.api.v1.endpoints import auth, users, departments, activities, performance

            endpoints = {
                "Authentication": auth.router,
                "User Management": users.router,
                "Department Management": departments.router,
                "Activities": activities.router,
                "Performance": performance.router,
            }

            for name, router in endpoints.items():
                route_count = len(router.routes)
                self.results.append((f"Endpoint: {name}", True, f"{route_count} routes"))

            return True
        except Exception as e:
            self.results.append(("API Endpoints", False, str(e)))
            return False

    def check_schemas(self) -> bool:
        """Check Pydantic schemas."""
        try:
            from app.schemas.user import (
                UserCreate, UserUpdate, UserResponse, UserListResponse,
                PasswordChange, UserActivation, UserLogin, Token
            )
            from app.schemas.department import (
                DepartmentCreate, DepartmentUpdate, DepartmentResponse,
                DepartmentWithManagerResponse, DepartmentListResponse
            )

            user_schemas = 8
            dept_schemas = 5

            self.results.append(("User Schemas", True, f"{user_schemas} schemas"))
            self.results.append(("Department Schemas", True, f"{dept_schemas} schemas"))
            return True
        except Exception as e:
            self.results.append(("Pydantic Schemas", False, str(e)))
            return False

    def check_files(self) -> bool:
        """Check all required files exist."""
        required_files = [
            ("app/models/user.py", "User Model"),
            ("app/models/department.py", "Department Model"),
            ("app/core/permissions.py", "Permission System"),
            ("app/api/v1/endpoints/users.py", "User API"),
            ("app/api/v1/endpoints/departments.py", "Department API"),
            ("app/schemas/user.py", "User Schemas"),
            ("app/schemas/department.py", "Department Schemas"),
        ]

        all_exist = True
        for filepath, name in required_files:
            exists = os.path.exists(filepath)
            if exists:
                size = os.path.getsize(filepath)
                self.results.append((f"File: {name}", True, f"{size} bytes"))
            else:
                self.results.append((f"File: {name}", False, "Not found"))
                all_exist = False

        return all_exist

    def check_deployment_files(self) -> bool:
        """Check deployment files."""
        deployment_files = [
            ("../../deployment/ubuntu/UBUNTU_DEPLOYMENT.md", "Ubuntu Guide"),
            ("../../deployment/ubuntu/setup.sh", "Setup Script"),
            ("../../deployment/ubuntu/healthrix-backend.service", "Systemd Service"),
            ("../../deployment/ubuntu/nginx-healthrix.conf", "Nginx Config"),
        ]

        all_exist = True
        for filepath, name in deployment_files:
            exists = os.path.exists(filepath)
            if exists:
                size = os.path.getsize(filepath)
                self.results.append((f"Deploy: {name}", True, f"{size} bytes"))
            else:
                self.results.append((f"Deploy: {name}", False, "Not found"))
                all_exist = False

        return all_exist

    def run_all_checks(self):
        """Run all health checks."""
        print_banner()

        # System Checks
        print_section("System Requirements", Colors.GEAR)
        self.check_python_version()
        self.check_imports()

        # Code Checks
        print_section("Code Structure", "📁")
        self.check_files()
        self.check_models()
        self.check_permissions()
        self.check_schemas()
        self.check_endpoints()

        # Deployment Checks
        print_section("Deployment Files", Colors.ROCKET)
        self.check_deployment_files()

        # Print Results
        self.print_results()

    def print_results(self):
        """Print all results."""
        print_section("Verification Results", "📊")

        for name, status, details in self.results:
            print_test(name, status, details)
            if status:
                self.successes += 1
            else:
                self.critical_failures += 1

        # Summary
        print_section("Summary", Colors.PARTY)

        total = len(self.results)
        pass_rate = (self.successes / total * 100) if total > 0 else 0

        print(f"\n{Colors.BOLD}Total Tests:{Colors.ENDC} {total}")
        print(f"{Colors.OKGREEN}{Colors.BOLD}Passed:{Colors.ENDC} {self.successes}")
        print(f"{Colors.FAIL}{Colors.BOLD}Failed:{Colors.ENDC} {self.critical_failures}")
        print(f"{Colors.WARNING}{Colors.BOLD}Warnings:{Colors.ENDC} {self.warnings}")
        print(f"\n{Colors.BOLD}Pass Rate:{Colors.ENDC} {pass_rate:.1f}%")

        # Overall Status
        if self.critical_failures == 0:
            print(f"\n{Colors.BG_GREEN}{Colors.BOLD} ✅ SYSTEM IS PRODUCTION READY! {Colors.ENDC}\n")
            return 0
        else:
            print(f"\n{Colors.BG_RED}{Colors.BOLD} ❌ SYSTEM HAS CRITICAL ISSUES! {Colors.ENDC}\n")
            return 1


def main():
    """Main entry point."""
    checker = HealthChecker()

    # Change to backend directory
    os.chdir('/home/user/healthrix/phase2_webapp/backend')
    sys.path.insert(0, os.getcwd())

    exit_code = checker.run_all_checks()

    print(f"\n{Colors.OKCYAN}Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Colors.ENDC}\n")

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
