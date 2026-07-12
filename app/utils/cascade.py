"""
Cascade Delete Helpers
Explicitly deletes dependent rows before removing a Department, Program,
Batch, Semester, Subject, or User (teacher/student), rather than relying on
ORM in-session collection cascades — those fire on any disassociation
(e.g. reassigning a student to a different department), not just on the
parent's own deletion, which would silently destroy accounts/subjects during
routine edits. The actual delete-of-the-row is left to each caller via
db.session.delete(parent)/query.delete(); Postgres additionally enforces the
same cleanup at the DB level through each FK's ondelete=CASCADE/SET NULL.
"""
from app import db


def _ids(query, id_column):
    return [row[0] for row in query.with_entities(id_column).all()]


def _delete_quizzes(quiz_ids):
    from app.models.quiz import Quiz, QuizQuestion, QuizAttempt, QuizAnswer

    if not quiz_ids:
        return
    attempt_ids = _ids(QuizAttempt.query.filter(QuizAttempt.quiz_id.in_(quiz_ids)), QuizAttempt.id)
    question_ids = _ids(QuizQuestion.query.filter(QuizQuestion.quiz_id.in_(quiz_ids)), QuizQuestion.id)
    if attempt_ids or question_ids:
        QuizAnswer.query.filter(
            db.or_(QuizAnswer.attempt_id.in_(attempt_ids), QuizAnswer.question_id.in_(question_ids))
        ).delete(synchronize_session=False)
    QuizQuestion.query.filter(QuizQuestion.quiz_id.in_(quiz_ids)).delete(synchronize_session=False)
    QuizAttempt.query.filter(QuizAttempt.quiz_id.in_(quiz_ids)).delete(synchronize_session=False)
    Quiz.query.filter(Quiz.id.in_(quiz_ids)).delete(synchronize_session=False)


def _delete_chat_sessions(session_ids):
    from app.models.chat import ChatSession, ChatMessage

    if not session_ids:
        return
    ChatMessage.query.filter(ChatMessage.session_id.in_(session_ids)).delete(synchronize_session=False)
    ChatSession.query.filter(ChatSession.id.in_(session_ids)).delete(synchronize_session=False)


def _delete_knowledge_entries(kb_ids):
    from app.models.knowledge_base import KnowledgeBase, KnowledgeFile, KnowledgeVersion
    from app.utils.file_handler import delete_upload

    if not kb_ids:
        return
    for f in KnowledgeFile.query.filter(KnowledgeFile.knowledge_id.in_(kb_ids)):
        delete_upload(f.file_path)
    KnowledgeFile.query.filter(KnowledgeFile.knowledge_id.in_(kb_ids)).delete(synchronize_session=False)
    KnowledgeVersion.query.filter(KnowledgeVersion.knowledge_id.in_(kb_ids)).delete(synchronize_session=False)
    KnowledgeBase.query.filter(KnowledgeBase.id.in_(kb_ids)).delete(synchronize_session=False)


def cascade_delete_subjects(subject_query):
    """Delete every dependent row for each Subject in `subject_query`, then
    the subjects themselves. Leaves the owning teacher's account intact."""
    from app.models.subject import Subject
    from app.models.enrollment import Enrollment
    from app.models.study_material import StudyMaterial
    from app.models.assignment import Assignment, AssignmentSubmission
    from app.models.quiz import Quiz
    from app.models.knowledge_base import KnowledgeBase
    from app.models.chat import ChatSession
    from app.models.download import Download
    from app.models.analytics import AnalyticsEvent, TrendingQuestion

    subject_ids = _ids(subject_query, Subject.id)
    if not subject_ids:
        return

    Enrollment.query.filter(Enrollment.subject_id.in_(subject_ids)).delete(synchronize_session=False)
    StudyMaterial.query.filter(StudyMaterial.subject_id.in_(subject_ids)).delete(synchronize_session=False)

    assignment_ids = _ids(Assignment.query.filter(Assignment.subject_id.in_(subject_ids)), Assignment.id)
    if assignment_ids:
        AssignmentSubmission.query.filter(AssignmentSubmission.assignment_id.in_(assignment_ids)).delete(
            synchronize_session=False)
    Assignment.query.filter(Assignment.subject_id.in_(subject_ids)).delete(synchronize_session=False)

    _delete_quizzes(_ids(Quiz.query.filter(Quiz.subject_id.in_(subject_ids)), Quiz.id))
    _delete_knowledge_entries(_ids(KnowledgeBase.query.filter(KnowledgeBase.subject_id.in_(subject_ids)),
                                   KnowledgeBase.id))

    ChatSession.query.filter(ChatSession.subject_id.in_(subject_ids)).update(
        {ChatSession.subject_id: None}, synchronize_session=False)
    Download.query.filter(Download.subject_id.in_(subject_ids)).update(
        {Download.subject_id: None}, synchronize_session=False)
    AnalyticsEvent.query.filter(AnalyticsEvent.subject_id.in_(subject_ids)).update(
        {AnalyticsEvent.subject_id: None}, synchronize_session=False)
    TrendingQuestion.query.filter(TrendingQuestion.subject_id.in_(subject_ids)).update(
        {TrendingQuestion.subject_id: None}, synchronize_session=False)

    subject_query.delete(synchronize_session=False)


def cascade_delete_users(user_query):
    """Delete every dependent row for each User (student/teacher) in
    `user_query`, then the users themselves. Detaches (does not delete) any
    Subject the user teaches — the Subject survives, just unassigned."""
    from app.models.subject import Subject
    from app.models.enrollment import Enrollment
    from app.models.study_material import StudyMaterial
    from app.models.assignment import Assignment, AssignmentSubmission
    from app.models.quiz import Quiz, QuizAttempt, QuizAnswer
    from app.models.chat import ChatSession
    from app.models.notification import UserNotification
    from app.models.user import User

    user_ids = _ids(user_query, User.id)
    if not user_ids:
        return

    Subject.query.filter(Subject.teacher_id.in_(user_ids)).update(
        {Subject.teacher_id: None}, synchronize_session=False)

    # allocated_by is just an audit trail of who allocated the enrollment — deleting that
    # user (e.g. the teacher/admin who ran allocation) must not delete the student's enrollment.
    Enrollment.query.filter(Enrollment.allocated_by.in_(user_ids)).update(
        {Enrollment.allocated_by: None}, synchronize_session=False)
    Enrollment.query.filter(Enrollment.student_id.in_(user_ids)).delete(synchronize_session=False)

    StudyMaterial.query.filter(StudyMaterial.teacher_id.in_(user_ids)).delete(synchronize_session=False)

    AssignmentSubmission.query.filter(AssignmentSubmission.student_id.in_(user_ids)).delete(
        synchronize_session=False)
    teacher_assignment_ids = _ids(Assignment.query.filter(Assignment.teacher_id.in_(user_ids)), Assignment.id)
    if teacher_assignment_ids:
        AssignmentSubmission.query.filter(AssignmentSubmission.assignment_id.in_(teacher_assignment_ids)).delete(
            synchronize_session=False)
    Assignment.query.filter(Assignment.teacher_id.in_(user_ids)).delete(synchronize_session=False)

    own_attempt_ids = _ids(QuizAttempt.query.filter(QuizAttempt.student_id.in_(user_ids)), QuizAttempt.id)
    if own_attempt_ids:
        QuizAnswer.query.filter(QuizAnswer.attempt_id.in_(own_attempt_ids)).delete(synchronize_session=False)
    QuizAttempt.query.filter(QuizAttempt.id.in_(own_attempt_ids)).delete(synchronize_session=False)
    _delete_quizzes(_ids(Quiz.query.filter(Quiz.teacher_id.in_(user_ids)), Quiz.id))

    _delete_chat_sessions(_ids(ChatSession.query.filter(ChatSession.user_id.in_(user_ids)), ChatSession.id))
    UserNotification.query.filter(UserNotification.user_id.in_(user_ids)).delete(synchronize_session=False)

    user_query.delete(synchronize_session=False)


def cascade_delete_semesters(semester_query):
    """Delete every dependent row for each Semester in `semester_query`
    (subjects and users scoped to it), then the semesters themselves."""
    from app.models.semester import Semester
    from app.models.subject import Subject
    from app.models.user import User
    from app.models.knowledge_base import KnowledgeBase

    semester_ids = _ids(semester_query, Semester.id)
    if not semester_ids:
        return

    cascade_delete_subjects(Subject.query.filter(Subject.semester_id.in_(semester_ids)))
    cascade_delete_users(User.query.filter(User.semester_id.in_(semester_ids)))
    _delete_knowledge_entries(_ids(KnowledgeBase.query.filter(KnowledgeBase.semester_id.in_(semester_ids)),
                                   KnowledgeBase.id))
    semester_query.delete(synchronize_session=False)


def cascade_delete_batches(batch_query):
    """Delete every dependent row for each Batch in `batch_query`
    (semesters, their subjects/users, and users scoped directly to the
    batch), then the batches themselves."""
    from app.models.batch import Batch
    from app.models.semester import Semester
    from app.models.user import User
    from app.models.knowledge_base import KnowledgeBase

    batch_ids = _ids(batch_query, Batch.id)
    if not batch_ids:
        return

    cascade_delete_semesters(Semester.query.filter(Semester.batch_id.in_(batch_ids)))
    cascade_delete_users(User.query.filter(User.batch_id.in_(batch_ids)))
    _delete_knowledge_entries(_ids(KnowledgeBase.query.filter(KnowledgeBase.batch_id.in_(batch_ids)),
                                   KnowledgeBase.id))
    batch_query.delete(synchronize_session=False)


def cascade_delete_programs(program_query):
    """Delete every dependent row for each Program in `program_query`
    (batches, their semesters/subjects/users, and users scoped directly to
    the program), then the programs themselves."""
    from app.models.program import Program
    from app.models.batch import Batch
    from app.models.user import User
    from app.models.knowledge_base import KnowledgeBase

    program_ids = _ids(program_query, Program.id)
    if not program_ids:
        return

    cascade_delete_batches(Batch.query.filter(Batch.program_id.in_(program_ids)))
    cascade_delete_users(User.query.filter(User.program_id.in_(program_ids)))
    _delete_knowledge_entries(_ids(KnowledgeBase.query.filter(KnowledgeBase.program_id.in_(program_ids)),
                                   KnowledgeBase.id))
    program_query.delete(synchronize_session=False)


def cascade_delete_departments(department_query):
    """Delete every dependent row for each Department in `department_query`
    (programs and their full hierarchy, subjects attached directly to the
    department, users scoped directly to the department, and department-level
    knowledge base entries), then the departments themselves."""
    from app.models.department import Department
    from app.models.program import Program
    from app.models.subject import Subject
    from app.models.user import User
    from app.models.knowledge_base import KnowledgeBase

    department_ids = _ids(department_query, Department.id)
    if not department_ids:
        return

    cascade_delete_programs(Program.query.filter(Program.department_id.in_(department_ids)))
    cascade_delete_subjects(Subject.query.filter(Subject.department_id.in_(department_ids)))
    cascade_delete_users(User.query.filter(User.department_id.in_(department_ids)))
    _delete_knowledge_entries(_ids(KnowledgeBase.query.filter(KnowledgeBase.department_id.in_(department_ids)),
                                   KnowledgeBase.id))
    department_query.delete(synchronize_session=False)
