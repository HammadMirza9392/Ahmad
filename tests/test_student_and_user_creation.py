import unittest

from flask import Flask

from app import db
from app.models.batch import Batch
from app.models.department import Department
from app.models.enrollment import Enrollment
from app.models.program import Program
from app.models.semester import Semester
from app.models.study_material import StudyMaterial
from app.models.subject import Subject
from app.models.user import User
from app.services.auth_service import AuthService
from app.services.student_service import StudentService


class StudentAndUserCreationTests(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.app.config.update(
            TESTING=True,
            SECRET_KEY='test-secret',
            SQLALCHEMY_DATABASE_URI='sqlite:///:memory:',
            SQLALCHEMY_TRACK_MODIFICATIONS=False,
            WTF_CSRF_ENABLED=False,
        )
        db.init_app(self.app)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_create_user_persists_new_account(self):
        user, error = AuthService.create_user(
            email='newstudent@example.com',
            password='Student@123',
            full_name='New Student',
            role='student',
        )

        self.assertIsNone(error)
        self.assertIsNotNone(user)
        self.assertEqual(user.email, 'newstudent@example.com')
        self.assertTrue(User.query.filter_by(email='newstudent@example.com').first())

    def test_student_sees_only_materials_for_enrolled_subjects(self):
        teacher = User(email='teacher@example.com', password_hash='hashed', full_name='Teacher One', role='teacher')
        student = User(email='student-materials@example.com', password_hash='hashed', full_name='Student One', role='student')
        db.session.add_all([teacher, student])
        db.session.flush()

        department = Department(name='Science', slug='science')
        db.session.add(department)
        db.session.flush()

        enrolled_subject = Subject(name='Physics', slug='physics', department_id=department.id)
        other_subject = Subject(name='Chemistry', slug='chemistry', department_id=department.id)
        db.session.add_all([enrolled_subject, other_subject])
        db.session.flush()

        db.session.add(Enrollment(student_id=student.id, subject_id=enrolled_subject.id, source='manual'))
        db.session.add_all([
            StudyMaterial(subject_id=enrolled_subject.id, teacher_id=teacher.id, title='Visible Notes'),
            StudyMaterial(subject_id=other_subject.id, teacher_id=teacher.id, title='Hidden Notes'),
        ])
        db.session.commit()

        query = (
            StudyMaterial.query.join(Enrollment, Enrollment.subject_id == StudyMaterial.subject_id)
            .filter(Enrollment.student_id == student.id)
            .order_by(StudyMaterial.created_at.desc())
        )
        items = query.all()

        self.assertEqual(len(items), 1)
        self.assertEqual(items[0].title, 'Visible Notes')

    def test_update_student_reassigns_department_related_context(self):
        dept_one = Department(name='CS', slug='cs')
        dept_two = Department(name='Math', slug='math')
        db.session.add_all([dept_one, dept_two])
        db.session.flush()

        program_one = Program(name='BSCS', slug='bscs', department_id=dept_one.id)
        program_two = Program(name='BSMath', slug='bsmath', department_id=dept_two.id)
        db.session.add_all([program_one, program_two])
        db.session.flush()

        batch_one = Batch(name='Batch 2022', slug='batch-2022', program_id=program_one.id)
        batch_two = Batch(name='Batch 2023', slug='batch-2023', program_id=program_two.id)
        db.session.add_all([batch_one, batch_two])
        db.session.flush()

        semester_one = Semester(name='Semester 1', slug='semester-1', batch_id=batch_one.id, number=1)
        semester_two = Semester(name='Semester 1', slug='semester-1-2', batch_id=batch_two.id, number=1)
        db.session.add_all([semester_one, semester_two])
        db.session.flush()

        subject_one = Subject(name='Programming', slug='programming', department_id=dept_one.id, semester_id=semester_one.id)
        subject_two = Subject(name='Calculus', slug='calculus', department_id=dept_two.id, semester_id=semester_two.id)
        db.session.add_all([subject_one, subject_two])
        db.session.flush()

        student = User(
            email='student@example.com',
            password_hash='hashed',
            full_name='Student One',
            role='student',
            department_id=dept_one.id,
            program_id=program_one.id,
            batch_id=batch_one.id,
            semester_id=semester_one.id,
        )
        db.session.add(student)
        db.session.commit()

        db.session.add(Enrollment(student_id=student.id, subject_id=subject_one.id, source='auto'))
        db.session.commit()

        updated, error = StudentService.update(student, {
            'department_id': str(dept_two.id),
            'program_id': str(program_two.id),
            'batch_id': str(batch_two.id),
            'semester_id': str(semester_two.id),
        })

        self.assertIsNone(error)
        self.assertEqual(updated.department_id, dept_two.id)
        self.assertEqual(updated.program_id, program_two.id)
        self.assertEqual(updated.batch_id, batch_two.id)
        self.assertEqual(updated.semester_id, semester_two.id)
        self.assertEqual(Enrollment.query.filter_by(student_id=student.id).count(), 1)
        self.assertEqual(Enrollment.query.filter_by(student_id=student.id).first().subject_id, subject_two.id)


if __name__ == '__main__':
    unittest.main()
