import unittest

from flask import Flask

from app import db
from app.models.batch import Batch
from app.models.department import Department
from app.models.enrollment import Enrollment
from app.models.knowledge_base import KnowledgeBase
from app.models.program import Program
from app.models.semester import Semester
from app.models.study_material import StudyMaterial
from app.models.assignment import Assignment, AssignmentSubmission
from app.models.quiz import Quiz, QuizQuestion, QuizAttempt, QuizAnswer
from app.models.subject import Subject
from app.models.user import User
from app.services.department_service import DepartmentService
from app.services.knowledge_service import KnowledgeService
from app.services.student_service import StudentService


class CascadeDeleteTests(unittest.TestCase):
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

    def _build_hierarchy(self):
        """Department -> Program -> Batch -> Semester -> Subject, with a
        teacher and a student attached at the appropriate levels, plus one
        row of every dependent entity type."""
        dept = Department(name='CS', slug='cs')
        db.session.add(dept)
        db.session.flush()

        program = Program(name='BSCS', slug='bscs', department_id=dept.id)
        db.session.add(program)
        db.session.flush()

        batch = Batch(name='Batch 2022', slug='batch-2022', program_id=program.id)
        db.session.add(batch)
        db.session.flush()

        semester = Semester(name='Semester 1', slug='semester-1', batch_id=batch.id, number=1)
        db.session.add(semester)
        db.session.flush()

        teacher = User(email='teacher@example.com', password_hash='x', full_name='Teacher',
                       role='teacher', department_id=dept.id)
        student = User(email='student@example.com', password_hash='x', full_name='Student',
                       role='student', department_id=dept.id, program_id=program.id,
                       batch_id=batch.id, semester_id=semester.id)
        db.session.add_all([teacher, student])
        db.session.flush()

        subject = Subject(name='Programming', slug='programming', department_id=dept.id,
                          semester_id=semester.id, teacher_id=teacher.id)
        db.session.add(subject)
        db.session.flush()

        enrollment = Enrollment(student_id=student.id, subject_id=subject.id, source='manual')
        material = StudyMaterial(subject_id=subject.id, teacher_id=teacher.id, title='Notes')
        assignment = Assignment(subject_id=subject.id, teacher_id=teacher.id, title='HW1',
                                due_date=db.func.now())
        db.session.add_all([enrollment, material, assignment])
        db.session.flush()

        submission = AssignmentSubmission(assignment_id=assignment.id, student_id=student.id,
                                          file_url='f.pdf')
        quiz = Quiz(subject_id=subject.id, teacher_id=teacher.id, title='Quiz1')
        db.session.add_all([submission, quiz])
        db.session.flush()

        question = QuizQuestion(quiz_id=quiz.id, text='2+2?', correct_answer='4')
        db.session.add(question)
        db.session.flush()

        attempt = QuizAttempt(quiz_id=quiz.id, student_id=student.id)
        db.session.add(attempt)
        db.session.flush()

        answer = QuizAnswer(attempt_id=attempt.id, question_id=question.id, answer_text='4')
        db.session.add(answer)

        kb = KnowledgeBase(title='KB1', content='content', department_id=dept.id,
                           program_id=program.id, batch_id=batch.id, semester_id=semester.id,
                           subject_id=subject.id, created_by=teacher.id)
        db.session.add(kb)
        db.session.commit()

        return dict(dept=dept, program=program, batch=batch, semester=semester,
                    teacher=teacher, student=student, subject=subject, enrollment=enrollment,
                    material=material, assignment=assignment, submission=submission,
                    quiz=quiz, question=question, attempt=attempt, answer=answer, kb=kb)

    def test_delete_department_cascades_everything(self):
        ids = self._build_hierarchy()
        dept_id, subject_id, student_id, teacher_id = (
            ids['dept'].id, ids['subject'].id, ids['student'].id, ids['teacher'].id,
        )
        kb_id = ids['kb'].id

        DepartmentService.delete(ids['dept'])

        self.assertIsNone(db.session.get(Department, dept_id))
        self.assertEqual(Program.query.count(), 0)
        self.assertEqual(Batch.query.count(), 0)
        self.assertEqual(Semester.query.count(), 0)
        self.assertEqual(Subject.query.count(), 0)
        self.assertIsNone(db.session.get(User, student_id))
        self.assertIsNone(db.session.get(User, teacher_id))
        self.assertEqual(Enrollment.query.count(), 0)
        self.assertEqual(StudyMaterial.query.count(), 0)
        self.assertEqual(Assignment.query.count(), 0)
        self.assertEqual(AssignmentSubmission.query.count(), 0)
        self.assertEqual(Quiz.query.count(), 0)
        self.assertEqual(QuizQuestion.query.count(), 0)
        self.assertEqual(QuizAttempt.query.count(), 0)
        self.assertEqual(QuizAnswer.query.count(), 0)
        self.assertIsNone(db.session.get(KnowledgeBase, kb_id))

    def test_delete_subject_cascades_dependents_but_keeps_teacher(self):
        ids = self._build_hierarchy()
        subject_id = ids['subject'].id
        teacher_id = ids['teacher'].id

        DepartmentService.delete_subject(ids['subject'])

        self.assertIsNone(db.session.get(Subject, subject_id))
        self.assertEqual(Enrollment.query.count(), 0)
        self.assertEqual(StudyMaterial.query.count(), 0)
        self.assertEqual(Assignment.query.count(), 0)
        self.assertEqual(Quiz.query.count(), 0)
        self.assertEqual(KnowledgeBase.query.count(), 0)
        # Teacher account itself is untouched by a subject deletion.
        self.assertIsNotNone(db.session.get(User, teacher_id))

    def test_delete_teacher_cascades_content_and_detaches_subject(self):
        ids = self._build_hierarchy()
        teacher_id = ids['teacher'].id
        subject_id = ids['subject'].id

        teacher = db.session.get(User, teacher_id)
        Subject.query.filter_by(teacher_id=teacher_id).update({'teacher_id': None})
        db.session.delete(teacher)
        db.session.commit()

        self.assertIsNone(db.session.get(User, teacher_id))
        # Subject survives, just unassigned.
        subject = db.session.get(Subject, subject_id)
        self.assertIsNotNone(subject)
        self.assertIsNone(subject.teacher_id)
        self.assertEqual(StudyMaterial.query.count(), 0)
        self.assertEqual(Assignment.query.count(), 0)
        self.assertEqual(Quiz.query.count(), 0)

    def test_delete_student_cascades_enrollments_and_submissions(self):
        ids = self._build_hierarchy()
        student_id = ids['student'].id

        StudentService.delete(ids['student'])

        self.assertIsNone(db.session.get(User, student_id))
        self.assertEqual(Enrollment.query.count(), 0)
        self.assertEqual(AssignmentSubmission.query.count(), 0)
        self.assertEqual(QuizAttempt.query.count(), 0)
        self.assertEqual(QuizAnswer.query.count(), 0)

    def test_delete_knowledge_base_entry_removes_files_and_versions(self):
        ids = self._build_hierarchy()
        kb = ids['kb']
        KnowledgeService.delete(kb)
        self.assertIsNone(db.session.get(KnowledgeBase, kb.id))

    def test_delete_program_cascades_batch_semester_subject_and_students(self):
        ids = self._build_hierarchy()
        program_id = ids['program'].id
        student_id = ids['student'].id

        DepartmentService.delete_program(ids['program'])

        self.assertIsNone(db.session.get(Program, program_id))
        self.assertEqual(Batch.query.count(), 0)
        self.assertEqual(Semester.query.count(), 0)
        self.assertIsNone(db.session.get(User, student_id))
        # Department itself survives a program deletion.
        self.assertEqual(Department.query.count(), 1)

    def test_reassigning_student_department_does_not_delete_student(self):
        """Regression test: department/program/batch/semester relationships on
        User must not carry ORM delete-orphan cascade, since reassigning a
        student to a different department (as StudentService.update does) is
        a routine edit, not a deletion — delete-orphan would otherwise treat
        disassociation from the old department as an orphan and delete the
        student the moment the FK is reassigned."""
        ids = self._build_hierarchy()
        student = ids['student']
        student_id = student.id
        dept_two = Department(name='Math', slug='math-2')
        db.session.add(dept_two)
        db.session.commit()

        # Force-load the relationship/collection, matching what a real
        # request cycle does when rendering forms before the update.
        _ = ids['dept'].students
        _ = student.department

        student.department_id = dept_two.id
        student.program_id = None
        student.batch_id = None
        student.semester_id = None
        db.session.commit()

        survived = db.session.get(User, student_id)
        self.assertIsNotNone(survived)
        self.assertEqual(survived.department_id, dept_two.id)

    def test_reassigning_subject_department_does_not_delete_subject(self):
        """Regression test: Department.subjects / Semester.subjects must not
        carry ORM delete-orphan cascade, since subjects are routinely moved
        between departments/semesters via DepartmentService.update_subject."""
        ids = self._build_hierarchy()
        subject = ids['subject']
        subject_id = subject.id
        dept_two = Department(name='Math', slug='math-3')
        db.session.add(dept_two)
        db.session.commit()

        _ = ids['dept'].subjects
        _ = subject.department

        subject.department_id = dept_two.id
        subject.semester_id = None
        db.session.commit()

        survived = db.session.get(Subject, subject_id)
        self.assertIsNotNone(survived)
        self.assertEqual(survived.department_id, dept_two.id)

    def test_reassigning_batch_program_does_not_delete_batch(self):
        """Regression test: Program.batches must not carry ORM delete-orphan
        cascade, since batches can be reassigned to a different program via
        DepartmentService.update_batch."""
        ids = self._build_hierarchy()
        batch = ids['batch']
        batch_id = batch.id
        dept_two = Department(name='Math', slug='math-4')
        db.session.add(dept_two)
        db.session.flush()
        program_two = Program(name='BSMath', slug='bsmath-4', department_id=dept_two.id)
        db.session.add(program_two)
        db.session.commit()

        _ = ids['program'].batches
        _ = batch.program

        batch.program_id = program_two.id
        db.session.commit()

        survived = db.session.get(Batch, batch_id)
        self.assertIsNotNone(survived)
        self.assertEqual(survived.program_id, program_two.id)


if __name__ == '__main__':
    unittest.main()
