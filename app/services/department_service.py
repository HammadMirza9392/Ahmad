"""
Department Service
CRUD operations and business logic for departments, programs, classes, subjects.
"""
from app import db
from app.models.department import Department
from app.models.program import Program
from app.models.classes import Class, ClassSubject
from app.models.subject import Subject
from app.utils.helpers import generate_slug


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
            sort_order=data.get('sort_order', 0),
            is_active=data.get('is_active', True),
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
        for field in updatable:
            if field in data:
                setattr(dept, field, data[field])
        if 'name' in data:
            dept.slug = generate_slug(data['name'])
        db.session.commit()
        return dept

    @staticmethod
    def delete(dept):
        db.session.delete(dept)
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
            degree_type=data.get('degree_type'),
            department_id=data['department_id'],
            is_active=data.get('is_active', True),
            sort_order=data.get('sort_order', 0),
        )
        db.session.add(prog)
        db.session.commit()
        return prog

    @staticmethod
    def update_program(prog, data):
        for field in ['name', 'description', 'duration', 'degree_type', 'department_id', 'is_active', 'sort_order']:
            if field in data:
                setattr(prog, field, data[field])
        if 'name' in data:
            prog.slug = generate_slug(data['name'])
        db.session.commit()
        return prog

    @staticmethod
    def delete_program(prog):
        db.session.delete(prog)
        db.session.commit()

    # ───────────── CLASSES ─────────────

    @staticmethod
    def get_classes(program_id=None, active_only=False):
        q = Class.query.order_by(Class.sort_order, Class.name)
        if program_id:
            q = q.filter_by(program_id=program_id)
        if active_only:
            q = q.filter_by(is_active=True)
        return q.all()

    @staticmethod
    def get_class_by_id(class_id):
        return db.session.get(Class, class_id)

    @staticmethod
    def create_class(data):
        cls = Class(
            name=data['name'],
            slug=generate_slug(data['name']),
            section=data.get('section'),
            year=data.get('year'),
            program_id=data['program_id'],
            is_active=data.get('is_active', True),
            sort_order=data.get('sort_order', 0),
        )
        db.session.add(cls)
        db.session.commit()
        return cls

    @staticmethod
    def update_class(cls, data):
        for field in ['name', 'section', 'year', 'program_id', 'is_active', 'sort_order']:
            if field in data:
                setattr(cls, field, data[field])
        if 'name' in data:
            cls.slug = generate_slug(data['name'])
        db.session.commit()
        return cls

    @staticmethod
    def delete_class(cls):
        db.session.delete(cls)
        db.session.commit()

    # ───────────── SUBJECTS ─────────────

    @staticmethod
    def get_subjects(department_id=None, active_only=False):
        q = Subject.query.order_by(Subject.sort_order, Subject.name)
        if department_id:
            q = q.filter_by(department_id=department_id)
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
            credit_hours=data.get('credit_hours'),
            department_id=data['department_id'],
            is_active=data.get('is_active', True),
            sort_order=data.get('sort_order', 0),
        )
        db.session.add(subj)
        db.session.commit()
        return subj

    @staticmethod
    def update_subject(subj, data):
        for field in ['name', 'code', 'description', 'credit_hours', 'department_id', 'is_active', 'sort_order']:
            if field in data:
                setattr(subj, field, data[field])
        if 'name' in data:
            subj.slug = generate_slug(data['name'])
        db.session.commit()
        return subj

    @staticmethod
    def delete_subject(subj):
        db.session.delete(subj)
        db.session.commit()

    # ───────────── CLASS-SUBJECT BRIDGE ─────────────

    @staticmethod
    def assign_subject_to_class(class_id, subject_id):
        existing = ClassSubject.query.filter_by(class_id=class_id, subject_id=subject_id).first()
        if not existing:
            cs = ClassSubject(class_id=class_id, subject_id=subject_id)
            db.session.add(cs)
            db.session.commit()

    @staticmethod
    def remove_subject_from_class(class_id, subject_id):
        cs = ClassSubject.query.filter_by(class_id=class_id, subject_id=subject_id).first()
        if cs:
            db.session.delete(cs)
            db.session.commit()

    @staticmethod
    def get_subjects_for_class(class_id):
        """Get all subjects assigned to a specific class."""
        results = db.session.query(Subject).join(ClassSubject).filter(ClassSubject.class_id == class_id).all()
        return results
