"""
Department Service
CRUD operations and business logic for departments, programs, batches, semesters, subjects.
"""
from datetime import date
from app import db
from app.models.department import Department
from app.models.program import Program
from app.models.batch import Batch
from app.models.semester import Semester
from app.models.subject import Subject
from app.utils.helpers import generate_slug
from app.utils.cascade import (
    cascade_delete_departments, cascade_delete_programs, cascade_delete_batches,
    cascade_delete_semesters, cascade_delete_subjects,
)

# Columns that need type coercion when assigned from raw form data (always strings).
_BOOLEAN_FIELDS = {'is_active'}
_INTEGER_FIELDS = {
    'sort_order', 'total_semesters', 'start_year', 'end_year', 'number',
    'credit_hours', 'department_id', 'program_id', 'batch_id', 'semester_id',
    'teacher_id',
}


_DATE_FIELDS = {'start_date', 'end_date'}


def _coerce(field, value):
    """Convert a raw form-string value to the type its column expects.
    HTML checkboxes only submit a value ('1'/'on'/etc.) when checked and are
    absent entirely when unchecked — callers must handle the absent case
    themselves; this only coerces values that ARE present."""
    if value is None or value == '':
        return None
    if field in _BOOLEAN_FIELDS:
        if isinstance(value, bool):
            return value
        return str(value).strip().lower() in ('1', 'true', 'on', 'yes')
    if field in _INTEGER_FIELDS:
        try:
            return int(value)
        except (TypeError, ValueError):
            return None
    if field in _DATE_FIELDS:
        if isinstance(value, date):
            return value
        try:
            return date.fromisoformat(str(value))
        except ValueError:
            return None
    return value


def _apply_fields(obj, data, fields, checkbox_fields=()):
    """Assign `fields` from `data` onto `obj` with type coercion.
    `checkbox_fields` are treated as HTML checkboxes: since an unchecked box
    sends no key at all, its absence from `data` means False, not "leave
    unchanged" — so those fields are always set, present or not."""
    for field in fields:
        if field in checkbox_fields:
            setattr(obj, field, field in data and _coerce(field, data[field]))
        elif field in data:
            setattr(obj, field, _coerce(field, data[field]))


class DepartmentService:

    # ───────────── DEPARTMENTS ─────────────

    @staticmethod
    def get_all(active_only=False):
        q = Department.query.order_by(Department.sort_order, Department.name)
        if active_only:
            q = q.filter_by(is_active=True)
        return q.all()

    @staticmethod
    def get_by_id(dept_id):
        return db.session.get(Department, dept_id)

    @staticmethod
    def get_by_slug(slug):
        return Department.query.filter_by(slug=slug).first()

    @staticmethod
    def create(data):
        dept = Department(
            name=data['name'],
            slug=generate_slug(data['name']),
            description=data.get('description', ''),
            image=data.get('image'),
            hod_name=data.get('hod_name'),
            hod_image=data.get('hod_image'),
            hod_message=data.get('hod_message'),
            hod_email=data.get('hod_email'),
            hod_phone=data.get('hod_phone'),
            sort_order=_coerce('sort_order', data.get('sort_order')) or 0,
            is_active='is_active' in data and _coerce('is_active', data['is_active']),
        )
        db.session.add(dept)
        db.session.commit()
        return dept

    @staticmethod
    def update(dept, data):
        updatable = [
            'name', 'description', 'image', 'hod_name', 'hod_image',
            'hod_message', 'hod_email', 'hod_phone', 'sort_order', 'is_active',
        ]
        _apply_fields(dept, data, updatable, checkbox_fields={'is_active'})
        if 'name' in data:
            dept.slug = generate_slug(data['name'])
        db.session.commit()
        return dept

    @staticmethod
    def delete(dept):
        """Delete a department and every dependent record beneath it:
        programs, batches, semesters, subjects, students/teachers scoped to
        it, and knowledge base entries."""
        cascade_delete_departments(Department.query.filter_by(id=dept.id))
        db.session.commit()

    # ───────────── PROGRAMS ─────────────

    @staticmethod
    def get_programs(department_id=None, active_only=False):
        q = Program.query.order_by(Program.sort_order, Program.name)
        if department_id:
            q = q.filter_by(department_id=department_id)
        if active_only:
            q = q.filter_by(is_active=True)
        return q.all()

    @staticmethod
    def get_program_by_id(program_id):
        return db.session.get(Program, program_id)

    @staticmethod
    def create_program(data):
        prog = Program(
            name=data['name'],
            slug=generate_slug(data['name']),
            description=data.get('description', ''),
            duration=data.get('duration'),
            total_semesters=_coerce('total_semesters', data.get('total_semesters')),
            degree_type=data.get('degree_type'),
            department_id=_coerce('department_id', data['department_id']),
            is_active='is_active' in data and _coerce('is_active', data['is_active']),
            sort_order=_coerce('sort_order', data.get('sort_order')) or 0,
        )
        db.session.add(prog)
        db.session.commit()
        return prog

    @staticmethod
    def update_program(prog, data):
        fields = ['name', 'description', 'duration', 'total_semesters',
                  'degree_type', 'department_id', 'sort_order', 'is_active']
        _apply_fields(prog, data, fields, checkbox_fields={'is_active'})
        if 'name' in data:
            prog.slug = generate_slug(data['name'])
        db.session.commit()
        return prog

    @staticmethod
    def delete_program(prog):
        """Delete a program and everything beneath it: batches, semesters,
        subjects, students/teachers scoped to it, and knowledge base entries."""
        cascade_delete_programs(Program.query.filter_by(id=prog.id))
        db.session.commit()

    # ───────────── BATCHES ─────────────

    @staticmethod
    def get_batches(program_id=None, active_only=False):
        q = Batch.query.order_by(Batch.sort_order, Batch.start_year, Batch.name)
        if program_id:
            q = q.filter_by(program_id=program_id)
        if active_only:
            q = q.filter_by(is_active=True)
        return q.all()

    @staticmethod
    def get_batch_by_id(batch_id):
        return db.session.get(Batch, batch_id)

    @staticmethod
    def create_batch(data):
        start_year = _coerce('start_year', data.get('start_year'))
        end_year = _coerce('end_year', data.get('end_year'))
        name = data.get('name') or (f"{start_year}-{end_year}" if start_year and end_year else 'New Batch')
        batch = Batch(
            name=name,
            slug=generate_slug(f"{name}-{data['program_id']}"),
            start_year=start_year,
            end_year=end_year,
            status=data.get('status', 'active'),
            program_id=_coerce('program_id', data['program_id']),
            is_active='is_active' in data and _coerce('is_active', data['is_active']),
            sort_order=_coerce('sort_order', data.get('sort_order')) or 0,
        )
        db.session.add(batch)
        db.session.commit()
        return batch

    @staticmethod
    def update_batch(batch, data):
        fields = ['name', 'start_year', 'end_year', 'status', 'program_id', 'sort_order', 'is_active']
        _apply_fields(batch, data, fields, checkbox_fields={'is_active'})
        db.session.commit()
        return batch

    @staticmethod
    def delete_batch(batch):
        """Delete a batch and everything beneath it: semesters, subjects,
        students scoped to it, and knowledge base entries."""
        cascade_delete_batches(Batch.query.filter_by(id=batch.id))
        db.session.commit()

    # ───────────── SEMESTERS ─────────────

    @staticmethod
    def get_semesters(batch_id=None, active_only=False):
        q = Semester.query.order_by(Semester.sort_order, Semester.number, Semester.name)
        if batch_id:
            q = q.filter_by(batch_id=batch_id)
        if active_only:
            q = q.filter_by(is_active=True)
        return q.all()

    @staticmethod
    def get_semester_by_id(semester_id):
        return db.session.get(Semester, semester_id)

    @staticmethod
    def create_semester(data):
        sem = Semester(
            name=data['name'],
            slug=generate_slug(f"{data['name']}-{data['batch_id']}"),
            number=_coerce('number', data.get('number')),
            start_date=_coerce('start_date', data.get('start_date')),
            end_date=_coerce('end_date', data.get('end_date')),
            batch_id=_coerce('batch_id', data['batch_id']),
            is_active='is_active' in data and _coerce('is_active', data['is_active']),
            sort_order=_coerce('sort_order', data.get('sort_order')) or 0,
        )
        db.session.add(sem)
        db.session.commit()
        return sem

    @staticmethod
    def update_semester(sem, data):
        fields = ['name', 'number', 'start_date', 'end_date', 'batch_id', 'sort_order', 'is_active']
        _apply_fields(sem, data, fields, checkbox_fields={'is_active'})
        db.session.commit()
        return sem

    @staticmethod
    def delete_semester(sem):
        """Delete a semester and everything beneath it: subjects, students
        scoped to it, and knowledge base entries."""
        cascade_delete_semesters(Semester.query.filter_by(id=sem.id))
        db.session.commit()

    @staticmethod
    def get_next_semester(current_semester):
        """Return the next-higher-number Semester in the same batch, or None."""
        if current_semester.number is None:
            return None
        return (Semester.query
                .filter(Semester.batch_id == current_semester.batch_id,
                        Semester.number > current_semester.number)
                .order_by(Semester.number.asc())
                .first())

    # ───────────── SUBJECTS ─────────────

    @staticmethod
    def get_subjects(department_id=None, semester_id=None, active_only=False):
        q = Subject.query.order_by(Subject.sort_order, Subject.name)
        if department_id:
            q = q.filter_by(department_id=department_id)
        if semester_id:
            q = q.filter_by(semester_id=semester_id)
        if active_only:
            q = q.filter_by(is_active=True)
        return q.all()

    @staticmethod
    def get_subject_by_id(subject_id):
        return db.session.get(Subject, subject_id)

    @staticmethod
    def create_subject(data):
        subj = Subject(
            name=data['name'],
            slug=generate_slug(data['name']),
            code=data.get('code'),
            description=data.get('description', ''),
            credit_hours=_coerce('credit_hours', data.get('credit_hours')),
            department_id=_coerce('department_id', data['department_id']),
            semester_id=_coerce('semester_id', data.get('semester_id')),
            teacher_id=_coerce('teacher_id', data.get('teacher_id')),
            is_active='is_active' in data and _coerce('is_active', data['is_active']),
            sort_order=_coerce('sort_order', data.get('sort_order')) or 0,
        )
        db.session.add(subj)
        db.session.commit()
        return subj

    @staticmethod
    def update_subject(subj, data):
        fields = ['name', 'code', 'description', 'credit_hours', 'department_id',
                  'semester_id', 'teacher_id', 'sort_order', 'is_active']
        _apply_fields(subj, data, fields, checkbox_fields={'is_active'})
        if 'name' in data:
            subj.slug = generate_slug(data['name'])
        db.session.commit()
        return subj

    @staticmethod
    def delete_subject(subj):
        """Delete a subject and its dependents: enrollments, study
        materials, assignments, quizzes, and knowledge base entries.
        Leaves the assigned teacher's account untouched."""
        cascade_delete_subjects(Subject.query.filter_by(id=subj.id))
        db.session.commit()

    @staticmethod
    def get_subjects_for_semester(semester_id):
        """Get all subjects belonging to a specific semester."""
        if not semester_id:
            return []
        return Subject.query.filter_by(semester_id=semester_id).order_by(Subject.sort_order, Subject.name).all()
