import unittest

from flask import Flask

from app import db
from app.models.department import Department
from app.models.subject import Subject
from app.models.enrollment import Enrollment
from app.models.user import User
from app.ai.context_manager import _build_teacher_context
from app.ai.prompt_builder import PromptBuilder
from app.services.allocation_service import AllocationService
from app.services.auth_service import AuthService


class TeacherChatScopingTests(unittest.TestCase):
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

    def _build_two_teacher_scenario(self):
        teacher, _ = AuthService.create_user(email='t@example.com', password='x',
                                             full_name='Mr Teach', role='teacher')
        other_teacher, _ = AuthService.create_user(email='t2@example.com', password='x',
                                                    full_name='Other Teacher', role='teacher')

        dept = Department(name='CS', slug='cs')
        db.session.add(dept)
        db.session.flush()

        my_subject = Subject(name='Programming', slug='prog', department_id=dept.id,
                             teacher_id=teacher.id)
        other_subject = Subject(name='Databases', slug='db', department_id=dept.id,
                                teacher_id=other_teacher.id)
        db.session.add_all([my_subject, other_subject])
        db.session.flush()

        my_student, _ = AuthService.create_user(email='s1@example.com', password='x',
                                                 full_name='My Student', role='student')
        other_student, _ = AuthService.create_user(email='s2@example.com', password='x',
                                                    full_name='Other Student', role='student')
        db.session.add(Enrollment(student_id=my_student.id, subject_id=my_subject.id, source='manual'))
        db.session.add(Enrollment(student_id=other_student.id, subject_id=other_subject.id, source='manual'))
        db.session.commit()

        return dict(teacher=teacher, other_teacher=other_teacher, my_subject=my_subject,
                   other_subject=other_subject, my_student=my_student, other_student=other_student)

    def test_get_subjects_for_teacher_excludes_other_teachers(self):
        ids = self._build_two_teacher_scenario()
        subjects = AllocationService.get_subjects_for_teacher(ids['teacher'].id)
        self.assertEqual([s.id for s in subjects], [ids['my_subject'].id])

    def test_get_students_for_teacher_excludes_other_teachers_students(self):
        ids = self._build_two_teacher_scenario()
        students = AllocationService.get_students_for_teacher(ids['teacher'].id)
        self.assertEqual([s.id for s in students], [ids['my_student'].id])

    def test_teacher_prompt_never_includes_other_teachers_data(self):
        ids = self._build_two_teacher_scenario()
        subjects, students_by_subject, kb_ctx, files, quizzes = _build_teacher_context(ids['teacher'].id)

        prompt = PromptBuilder.build_teacher_system_prompt(
            user=ids['teacher'], subjects=subjects, students_by_subject=students_by_subject,
            knowledge_context=kb_ctx, resource_files=files, quizzes=quizzes,
        )

        self.assertIn('Programming', prompt)
        self.assertIn('My Student', prompt)
        self.assertNotIn('Databases', prompt)
        self.assertNotIn('Other Student', prompt)

    def test_teacher_with_no_subjects_gets_empty_scope(self):
        teacher, _ = AuthService.create_user(email='lonely@example.com', password='x',
                                             full_name='Lonely Teacher', role='teacher')
        subjects, students_by_subject, kb_ctx, files, quizzes = _build_teacher_context(teacher.id)
        self.assertEqual(subjects, [])
        self.assertEqual(students_by_subject, {})

        prompt = PromptBuilder.build_teacher_system_prompt(
            user=teacher, subjects=subjects, students_by_subject=students_by_subject,
        )
        self.assertIn('None assigned yet.', prompt)


if __name__ == '__main__':
    unittest.main()
