# User Management System

Complete guide to the Healthrix Productivity System's multi-role user management and department hierarchy.

## Table of Contents

- [Role Hierarchy](#role-hierarchy)
- [Permissions System](#permissions-system)
- [API Endpoints](#api-endpoints)
- [User Workflows](#user-workflows)
- [Department Management](#department-management)
- [Security Best Practices](#security-best-practices)

---

## Role Hierarchy

The Healthrix system implements a five-tier role hierarchy with granular permissions:

```
┌─────────────────────────────────────────────────────────────┐
│                      SUPER ADMIN                            │
│  Full system access, manage all users and settings          │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────┴──────────────────────────────────────┐
│                         ADMIN                               │
│  Manage operations, create users (except super admins)      │
└──────────────────────┬──────────────────────────────────────┘
                       │
         ┌─────────────┴─────────────┐
         │                           │
┌────────┴────────┐         ┌────────┴────────────┐
│       HR        │         │  DEPARTMENT HEAD    │
│  Manage emp,    │         │  Manage dept emp,   │
│  view all perf  │         │  view dept perf     │
└────────┬────────┘         └────────┬────────────┘
         │                           │
         └─────────────┬─────────────┘
                       │
         ┌─────────────┴────────────┐
         │        EMPLOYEE          │
         │  View own data, submit   │
         │  activities              │
         └──────────────────────────┘
```

### Role Descriptions

#### Super Admin
- **Level**: 4 (Highest)
- **Access**: Complete system control
- **Capabilities**:
  - Create, update, delete any user (including other admins)
  - Manage all departments
  - View and edit all performance data
  - Modify system settings and task standards
  - Access all reports and analytics
- **Use Case**: System administrators, IT team

#### Admin
- **Level**: 3
- **Access**: Nearly full system control (cannot manage super admins)
- **Capabilities**:
  - Create users with roles: Admin, HR, Department Head, Employee
  - Manage departments and assign managers
  - View and edit all performance data
  - Generate company-wide reports
  - Modify task standards
- **Use Case**: Management team, operations managers

#### HR
- **Level**: 2
- **Access**: Employee management and reporting
- **Capabilities**:
  - Create and manage employee accounts
  - Activate/deactivate user accounts
  - View all performance data (read-only across departments)
  - Generate company-wide reports
  - View department information
- **Use Case**: Human resources team

#### Department Head
- **Level**: 1
- **Access**: Department-scoped access
- **Capabilities**:
  - View employees in their department
  - Calculate and view department performance
  - Generate department reports
  - Monitor department activities
- **Use Case**: Team leaders, department managers

#### Employee
- **Level**: 0 (Standard user)
- **Access**: Personal data only
- **Capabilities**:
  - View own performance metrics
  - Submit daily activities
  - View own reports
  - View task standards
- **Use Case**: All employees

---

## Permissions System

### Permission Categories

| Category | Permissions | Description |
|----------|------------|-------------|
| **User Management** | `user:create`, `user:read`, `user:update`, `user:delete`, `user:activate`, `user:deactivate`, `user:change_role` | Control over user accounts |
| **Department Management** | `department:create`, `department:read`, `department:update`, `department:delete`, `department:assign_manager` | Department hierarchy control |
| **Performance Management** | `performance:calculate`, `performance:view_all`, `performance:view_department`, `performance:view_own`, `performance:edit` | Performance data access |
| **Activity Management** | `activity:create_own`, `activity:create_any`, `activity:view_all`, `activity:view_department`, `activity:view_own`, `activity:edit_any`, `activity:delete_any` | Activity logging control |
| **Report Management** | `report:generate_all`, `report:generate_department`, `report:view_all`, `report:view_department`, `report:view_own` | Reporting capabilities |
| **System Settings** | `settings:manage`, `settings:view` | System configuration |
| **Task Standards** | `standards:manage`, `standards:view` | Task scoring standards |

### Permission Matrix

| Permission | Super Admin | Admin | HR | Dept Head | Employee |
|------------|:-----------:|:-----:|:--:|:---------:|:--------:|
| **User Management** |
| Create users | ✅ | ✅ (limited) | ✅ (limited) | ❌ | ❌ |
| View users | ✅ | ✅ | ✅ | 🔸 Dept only | 🔸 Self only |
| Update users | ✅ | ✅ | ✅ (limited) | ❌ | ❌ |
| Delete users | ✅ | ✅ (limited) | ❌ | ❌ | ❌ |
| Change roles | ✅ | 🔸 Not to SA | ❌ | ❌ | ❌ |
| **Performance** |
| View all performance | ✅ | ✅ | ✅ | ❌ | ❌ |
| View dept performance | ✅ | ✅ | ✅ | ✅ | ❌ |
| View own performance | ✅ | ✅ | ✅ | ✅ | ✅ |
| Edit performance | ✅ | ✅ | ❌ | ❌ | ❌ |
| **Departments** |
| Create departments | ✅ | ✅ | ❌ | ❌ | ❌ |
| Assign managers | ✅ | ✅ | ❌ | ❌ | ❌ |
| **Reports** |
| Company-wide reports | ✅ | ✅ | ✅ | ❌ | ❌ |
| Department reports | ✅ | ✅ | ✅ | ✅ | ❌ |
| Own reports | ✅ | ✅ | ✅ | ✅ | ✅ |

**Legend:**
- ✅ Full access
- 🔸 Limited access (with conditions)
- ❌ No access

---

## API Endpoints

### User Management

#### Create User
```http
POST /api/v1/users/
```

**Required Permission**: `user:create`

**Request Body**:
```json
{
  "emp_id": "EMP001",
  "email": "john.doe@company.com",
  "password": "SecurePass123",
  "name": "John Doe",
  "department": "Engineering",
  "department_id": 1,
  "role": "employee",
  "is_active": true,
  "hire_date": "2024-01-15"
}
```

**Response**: `201 Created`
```json
{
  "emp_id": "EMP001",
  "email": "john.doe@company.com",
  "name": "John Doe",
  "department": "Engineering",
  "department_id": 1,
  "role": "employee",
  "is_active": true,
  "hire_date": "2024-01-15T00:00:00",
  "created_at": "2024-11-20T10:30:00",
  "updated_at": "2024-11-20T10:30:00"
}
```

#### List Users
```http
GET /api/v1/users/?skip=0&limit=100&role=employee&department_id=1&search=john
```

**Response**: `200 OK`
```json
{
  "users": [...],
  "total": 150,
  "skip": 0,
  "limit": 100
}
```

#### Get Current User
```http
GET /api/v1/users/me
```

**Response**: `200 OK` (User object)

#### Get User by ID
```http
GET /api/v1/users/{emp_id}
```

#### Update User
```http
PUT /api/v1/users/{emp_id}
```

**Request Body**:
```json
{
  "name": "John Doe Jr.",
  "department_id": 2,
  "role": "department_head"
}
```

#### Change Password
```http
POST /api/v1/users/{emp_id}/change-password
```

**Request Body**:
```json
{
  "old_password": "OldPass123",
  "new_password": "NewSecurePass456"
}
```

#### Activate User
```http
POST /api/v1/users/{emp_id}/activate
```

#### Deactivate User
```http
POST /api/v1/users/{emp_id}/deactivate
```

#### Delete User
```http
DELETE /api/v1/users/{emp_id}
```

### Department Management

#### Create Department
```http
POST /api/v1/departments/
```

**Request Body**:
```json
{
  "dept_code": "ENG",
  "dept_name": "Engineering",
  "description": "Software engineering department",
  "manager_emp_id": "EMP001",
  "is_active": true
}
```

#### List Departments
```http
GET /api/v1/departments/?skip=0&limit=100
```

#### Get Department
```http
GET /api/v1/departments/{dept_id}
```

**Response**:
```json
{
  "id": 1,
  "dept_code": "ENG",
  "dept_name": "Engineering",
  "description": "Software engineering department",
  "manager_emp_id": "EMP001",
  "manager_name": "John Doe",
  "employee_count": 25,
  "is_active": true,
  "created_at": "2024-01-01T00:00:00",
  "updated_at": "2024-11-20T10:30:00"
}
```

#### Update Department
```http
PUT /api/v1/departments/{dept_id}
```

#### Assign Department Manager
```http
POST /api/v1/departments/{dept_id}/assign-manager?manager_emp_id=EMP002
```

#### Delete Department
```http
DELETE /api/v1/departments/{dept_id}?force=true
```

---

## User Workflows

### Workflow 1: Onboarding New Employee

**Actors**: HR or Admin

1. **Create user account**:
   ```bash
   POST /api/v1/users/
   {
     "emp_id": "EMP123",
     "email": "new.employee@company.com",
     "password": "TempPass@123",
     "name": "New Employee",
     "role": "employee",
     "department_id": 5,
     "hire_date": "2024-11-20"
   }
   ```

2. **Send welcome email** (manual or automated):
   - Credentials
   - System access instructions
   - Request password change

3. **Employee first login**:
   - Changes password using `/users/me/change-password`
   - Views task standards
   - Starts submitting activities

### Workflow 2: Promoting Employee to Department Head

**Actors**: Admin or Super Admin

1. **Update user role**:
   ```bash
   PUT /api/v1/users/EMP123
   {
     "role": "department_head"
   }
   ```

2. **Assign as department manager**:
   ```bash
   POST /api/v1/departments/5/assign-manager?manager_emp_id=EMP123
   ```

3. **Notify user** of new responsibilities

### Workflow 3: Employee Transfer Between Departments

**Actors**: HR or Admin

1. **Update department assignment**:
   ```bash
   PUT /api/v1/users/EMP123
   {
     "department_id": 7
   }
   ```

2. **Historical data** remains intact with old department
3. **New performance calculations** use new department

### Workflow 4: Deactivating Leaving Employee

**Actors**: HR or Admin

1. **Deactivate account** (preserves data):
   ```bash
   POST /api/v1/users/EMP123/deactivate
   ```

2. **Account locked** - user cannot log in
3. **Historical data preserved** for reports and audits
4. **Optional**: Delete after retention period

---

## Department Management

### Department Hierarchy

```
Company
│
├── Engineering (ENG)
│   ├── Manager: John Doe (EMP001)
│   └── Employees: 25
│
├── Sales (SALES)
│   ├── Manager: Jane Smith (EMP050)
│   └── Employees: 40
│
├── HR (HR)
│   ├── Manager: Bob Johnson (EMP100)
│   └── Employees: 5
│
└── Operations (OPS)
    ├── Manager: Alice Williams (EMP075)
    └── Employees: 30
```

### Department Best Practices

1. **Unique Department Codes**: Use short, uppercase codes (e.g., "ENG", "SALES")
2. **Assign Managers**: Always assign a department head for accountability
3. **Active Status**: Mark inactive departments instead of deleting (preserves history)
4. **Employee Count**: Monitor department sizes for workload balancing

---

## Security Best Practices

### Password Requirements

Enforced by the system:
- Minimum 8 characters
- At least one letter
- At least one digit
- Recommended: Mix of uppercase, lowercase, numbers, and symbols

### Role Assignment Rules

1. **Super Admin** can manage all roles
2. **Admin** cannot create/modify Super Admin users
3. **HR** can only create Employee and Department Head roles
4. **Users cannot change their own role**

### Account Security

1. **Force password change** for new accounts
2. **Deactivate rather than delete** for audit trail
3. **Regular password rotation** (recommended every 90 days)
4. **Monitor failed login attempts**

### API Security

1. **JWT tokens** for authentication
2. **Token expiration**: 30 minutes (configurable)
3. **Refresh tokens**: 7 days (configurable)
4. **HTTPS only** in production

### Data Access Rules

1. **Employees**: Can only view own data
2. **Department Heads**: Can view data within their department
3. **HR/Admin**: Can view all data
4. **Audit logging**: Track all user modifications

---

## Example: Complete User Management Flow

### Scenario: Setting up a new department with team

```bash
# 1. Create department (as Admin)
POST /api/v1/departments/
{
  "dept_code": "TECH",
  "dept_name": "Technology",
  "description": "IT and software development",
  "is_active": true
}
# Response: {"id": 10, ...}

# 2. Create department head
POST /api/v1/users/
{
  "emp_id": "TECH001",
  "email": "tech.lead@company.com",
  "password": "TempPass@123",
  "name": "Tech Lead",
  "role": "department_head",
  "department_id": 10,
  "hire_date": "2024-11-01"
}

# 3. Assign as department manager
POST /api/v1/departments/10/assign-manager?manager_emp_id=TECH001

# 4. Create team members
POST /api/v1/users/
{
  "emp_id": "TECH002",
  "email": "dev1@company.com",
  "password": "TempPass@123",
  "name": "Developer 1",
  "role": "employee",
  "department_id": 10,
  "hire_date": "2024-11-10"
}

# Repeat for more employees...

# 5. Verify department setup
GET /api/v1/departments/10
# Response includes: manager_name, employee_count

# 6. Department head logs in and views team
GET /api/v1/users/?department_id=10
# Can see all department employees
```

---

## API Authentication

All API endpoints (except `/api/v1/auth/login`) require authentication.

### Get Token

```bash
POST /api/v1/auth/login
{
  "email": "user@company.com",
  "password": "password123"
}
```

**Response**:
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer"
}
```

### Use Token

```bash
GET /api/v1/users/me
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
```

---

## Troubleshooting

### Common Issues

**Issue**: Cannot create super admin user
- **Solution**: Only existing super admins can create new super admins

**Issue**: Department head cannot view employees
- **Solution**: Ensure they are assigned to a department with `department_id`

**Issue**: Password validation error
- **Solution**: Ensure password has at least 8 chars, includes letter and digit

**Issue**: 403 Forbidden on user update
- **Solution**: Check role permissions; admins cannot modify super admins

---

## API Reference

Complete API documentation available at:
- **Swagger UI**: `http://your-server/docs`
- **ReDoc**: `http://your-server/redoc`

---

**Next Steps**: See [UBUNTU_DEPLOYMENT.md](../deployment/ubuntu/UBUNTU_DEPLOYMENT.md) for deployment instructions.
