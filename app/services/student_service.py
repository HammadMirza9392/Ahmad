"""
Student Service
CRUD, import/export, and student-specific business logic.
"""
import csv
import io
from app import db
from app.models.user import User
from app.services.auth_service import AuthService


class StudentService:

    @staticmethod
    def get_all(page=1, per_page=20, search=None, department_id=None, program_id=None,
                batch_id=None, semester_id=None):
        """Paginated student list with filters."""
        q = User.query.filter_by(role='student').order_by(User.created_at.desc())
        if search:
            like = f'%{search}%'
            q = q.filter(
                db.or_(
                    User.full_name.ilike(like),
                    User.email.ilike(like),
                    User.roll_number.ilike(like),
                    User.registration_number.ilike(like),
                )
            )
        if department_id:
            q = q.filter_by(department_id=department_id)
        if program_id:
            q = q.filter_by(program_id=program_id)
        if batch_id:
            q = q.filter_by(batch_id=batch_id)
        if semester_id:
            q = q.filter_by(semester_id=semester_id)
        return q.paginate(page=page, per_page=per_page, error_out=False)

    @staticmethod
    def get_by_id(student_id):
        user = db.session.get(User, student_id)
        if user and user.role == 'student':
            return user
        return None

    @staticmethod
    def create(data):
        """Create a student account. Returns (user, error). Auto-allocates subjects."""
        user, error = AuthService.create_user(
            email=data['email'],
            password=data['password'],
            full_name=data['full_name'],
            role='student',
            roll_number=data.get('roll_number'),
            registration_number=data.get('registration_number'),
            phone=data.get('phone'),
            department_id=data.get('department_id'),
            program_id=data.get('program_id'),
            batch_id=data.get('batch_id'),
            semester_id=data.get('semester_id'),
            semester=data.get('semester'),
            enrollment_status=data.get('enrollment_status', 'active'),
            is_active=data.get('is_active', True),
        )
        if user and user.semester_id:
            from app.services.allocation_service import AllocationService
            AllocationService.allocate_subjects_for_student(user)
        return user, error

    @staticmethod
    def update(student, data):
        """Update student profile fields. Re-allocates subjects if semester changes."""
        old_semester_id = student.semester_id
        updatable = [
            'full_name', 'phone', 'roll_number', 'registration_number', 'department_id',
            'program_id', 'batch_id', 'semester_id', 'semester', 'enrollment_status',
            'is_active', 'avatar',
        ]
        for field in updatable:
            if field in data:
                setattr(student, field, data[field])
        if 'email' in data and data['email'] != student.email:
            existing = User.query.filter_by(email=data['email'].lower().strip()).first()
            if existing and existing.id != student.id:
                return student, 'Email already in use.'
            student.email = data['email'].lower().strip()
        if 'password' in data and data['password']:
            student.password_hash = AuthService.hash_password(data['password'])
        db.session.commit()
        if student.semester_id and str(student.semester_id) != str(old_semester_id or ''):
            from app.services.allocation_service import AllocationService
            AllocationService.allocate_subjects_for_student(student)
        return student, None

    @staticmethod
    def delete(student):
        db.session.delete(student)
        db.session.commit()

    @staticmethod
    def count():
        return User.query.filter_by(role='student').count()

    @staticmethod
    def count_active():
        return User.query.filter_by(role='student', is_active=True).count()

    @staticmethod
    def import_from_csv(file_stream, department_id=None, program_id=None, batch_id=None, semester_id=None):
        """Import students from CSV. Expected columns: full_name, email, roll_number, password.
        Returns (success_count, error_list).
        """
        reader = csv.DictReader(io.TextIOWrapper(file_stream, encoding='utf-8'))
        success = 0
        errors = []
        for idx, row in enumerate(reader, start=2):
            name = row.get('full_name', '').strip()
            email = row.get('email', '').strip()
            roll = row.get('roll_number', '').strip()
            password = row.get('password', '').strip() or 'Student@123'
            if not name or not email:
                errors.append(f'Row {idx}: Missing name or email.')
                continue
            user, err = AuthService.create_user(
                email=email,
                password=password,
                full_name=name,
                role='student',
                roll_number=roll,
                department_id=department_id,
                program_id=program_id,
                batch_id=batch_id,
                semester_id=semester_id,
            )
            if err:
                errors.append(f'Row {idx} ({email}): {err}')
            else:
                if user and user.semester_id:
                    from app.services.allocation_service import AllocationService
                    AllocationService.allocate_subjects_for_student(user)
                success += 1
        return success, errors

    @staticmethod
    def export_to_csv():
        """Export all students as a CSV string."""
        students = User.query.filter_by(role='student').order_by(User.full_name).all()
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['Roll Number', 'Registration Number', 'Full Name', 'Email', 'Phone',
                          'Department', 'Program', 'Batch', 'Semester', 'Enrollment Status', 'Status'])
        for s in students:
            writer.writerow([
                s.roll_number or '',
                s.registration_number or '',
                s.full_name,
                s.email,
                s.phone or '',
                s.department.name if s.department else '',
                s.program.name if s.program else '',
                s.student_batch.label if s.student_batch else '',
                s.student_semester.name if s.student_semester else '',
                s.enrollment_status or '',
                'Active' if s.is_active else 'Inactive',
            ])
        return output.getvalue()
