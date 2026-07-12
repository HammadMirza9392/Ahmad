"""
Allocation Service
Auto-allocates subjects to students from their current semester, and supports
manual HOD/Admin enroll/unenroll overrides.
"""
from datetime import datetime
from app import db
from app.models.enrollment import Enrollment
from app.models.subject import Subject


class AllocationService:

    @staticmethod
    def allocate_subjects_for_student(student):
        """Create auto Enrollment rows for every subject linked to the student's
        current semester that they are not already enrolled in. Safe to call repeatedly."""
        if not student or not student.semester_id:
            return 0
        subject_ids = [s.id for s in
                       Subject.query.filter_by(semester_id=student.semester_id).all()]
        if not subject_ids:
            return 0
        existing = {e.subject_id for e in
                    Enrollment.query.filter_by(student_id=student.id).all()}
        created = 0
        for sid in subject_ids:
            if sid in existing:
                continue
            db.session.add(Enrollment(
                student_id=student.id,
                subject_id=sid,
                source='auto',
                allocated_at=datetime.utcnow(),
            ))
            created += 1
        if created:
            db.session.commit()
        return created

    @staticmethod
    def get_enrolled_subjects(student_id):
        """Return Subject objects a student is enrolled in (auto or manual)."""
        return (db.session.query(Subject)
                .join(Enrollment, Enrollment.subject_id == Subject.id)
                .filter(Enrollment.student_id == student_id)
                .order_by(Subject.sort_order, Subject.name)
                .all())

    @staticmethod
    def enroll(student_id, subject_id, allocated_by=None):
        """Manually enroll a student in a subject (HOD/Admin override)."""
        existing = Enrollment.query.filter_by(student_id=student_id, subject_id=subject_id).first()
        if existing:
            return existing
        enrollment = Enrollment(
            student_id=student_id,
            subject_id=subject_id,
            source='manual',
            allocated_by=allocated_by,
            allocated_at=datetime.utcnow(),
        )
        db.session.add(enrollment)
        db.session.commit()
        return enrollment

    @staticmethod
    def is_enrolled(student_id, subject_id):
        """Return True if the student is enrolled in the given subject."""
        return Enrollment.query.filter_by(student_id=student_id, subject_id=subject_id).first() is not None

    @staticmethod
    def unenroll(student_id, subject_id):
        """Remove an enrollment (manual override)."""
        enrollment = Enrollment.query.filter_by(student_id=student_id, subject_id=subject_id).first()
        if enrollment:
            db.session.delete(enrollment)
            db.session.commit()
            return True
        return False

    @staticmethod
    def get_students_for_subject(subject_id):
        """Return student users enrolled in a subject."""
        from app.models.user import User
        return (db.session.query(User)
                .join(Enrollment, Enrollment.student_id == User.id)
                .filter(Enrollment.subject_id == subject_id)
                .order_by(User.full_name)
                .all())

    @staticmethod
    def get_subjects_for_teacher(teacher_id):
        """Return Subject objects a teacher is assigned to teach."""
        return (Subject.query
                .filter_by(teacher_id=teacher_id)
                .order_by(Subject.sort_order, Subject.name)
                .all())

    @staticmethod
    def get_students_for_teacher(teacher_id):
        """Return every student enrolled in any subject taught by this
        teacher, deduplicated, ordered by name. This is the enforcement
        boundary for "list my students" — it can never include a student
        from a subject this teacher does not teach."""
        from app.models.user import User
        return (db.session.query(User)
                .join(Enrollment, Enrollment.student_id == User.id)
                .join(Subject, Subject.id == Enrollment.subject_id)
                .filter(Subject.teacher_id == teacher_id)
                .distinct()
                .order_by(User.full_name)
                .all())

    @staticmethod
    def promote_student(student):
        """Advance a student's semester_id to the next Semester (by number) in the
        same batch. Returns (success, message)."""
        from app.models.semester import Semester
        from app.services.department_service import DepartmentService
        if not student.semester_id:
            return False, 'Student has no current semester to promote from.'
        current = db.session.get(Semester, student.semester_id)
        if not current:
            return False, 'Current semester not found.'
        next_sem = DepartmentService.get_next_semester(current)
        if not next_sem:
            return False, f'{student.full_name} is already in the final semester of this batch.'
        student.semester_id = next_sem.id
        db.session.commit()
        AllocationService.allocate_subjects_for_student(student)
        return True, f'{student.full_name} promoted to {next_sem.name}.'
