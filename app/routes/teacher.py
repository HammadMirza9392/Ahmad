"""
Teacher Routes
Subject-scoped tools for teachers: quizzes, materials, announcements, marks.
Every handler re-derives ownership from the DB record.
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user

from app import db
from app.utils.decorators import teacher_required
from app.utils.scoping import require_subject_ownership
from app.services.quiz_service import QuizService
from app.services.allocation_service import AllocationService
from app.utils.file_handler import save_upload
from app.models.subject import Subject
from app.models.quiz import QuizAnswer
from app.models.study_material import StudyMaterial
from app.models.announcement import Announcement
from app.models.assignment import Assignment, AssignmentSubmission

teacher_bp = Blueprint('teacher', __name__)


def _my_subjects():
    return Subject.query.filter_by(teacher_id=current_user.id).order_by(Subject.name).all()


# ───────────── DASHBOARD ─────────────

@teacher_bp.route('/')
@login_required
@teacher_required
def dashboard():
    subjects = _my_subjects()
    quizzes = QuizService.list_quizzes_for_teacher(current_user.id)
    # Grading queue: submitted attempts with ungraded short answers
    grading_queue = []
    for quiz in quizzes:
        for attempt in quiz.attempts:
            if attempt.status == 'submitted':
                grading_queue.append((quiz, attempt))
    return render_template('teacher/dashboard.html', subjects=subjects,
                           quizzes=quizzes, grading_queue=grading_queue)


# ───────────── SUBJECTS & STUDENTS ─────────────

@teacher_bp.route('/subjects')
@login_required
@teacher_required
def subjects():
    return render_template('teacher/subjects.html', subjects=_my_subjects())


@teacher_bp.route('/subjects/<int:subject_id>/students')
@login_required
@teacher_required
def subject_students(subject_id):
    subject = require_subject_ownership(subject_id)
    students = AllocationService.get_students_for_subject(subject_id)
    return render_template('teacher/students.html', subject=subject, students=students)


# ───────────── QUIZ BUILDER ─────────────

@teacher_bp.route('/quizzes')
@login_required
@teacher_required
def quizzes():
    quiz_list = QuizService.list_quizzes_for_teacher(current_user.id)
    return render_template('teacher/quizzes/index.html', quizzes=quiz_list)


@teacher_bp.route('/quizzes/create', methods=['GET', 'POST'])
@login_required
@teacher_required
def quiz_create():
    subjects = _my_subjects()
    if request.method == 'POST':
        data = request.form.to_dict()
        subject_id = int(data['subject_id'])
        require_subject_ownership(subject_id)
        quiz = QuizService.create_quiz(current_user.id, data)
        flash('Quiz created. Now add questions.', 'success')
        return redirect(url_for('teacher.quiz_edit', quiz_id=quiz.id))
    return render_template('teacher/quizzes/create.html', subjects=subjects)


@teacher_bp.route('/quizzes/<int:quiz_id>', methods=['GET', 'POST'])
@login_required
@teacher_required
def quiz_edit(quiz_id):
    quiz = QuizService.get_quiz(quiz_id)
    if not quiz or quiz.teacher_id != current_user.id:
        abort(403)
    if request.method == 'POST':
        data = request.form.to_dict()
        # Collect MCQ options if present
        options = request.form.getlist('options')
        if options:
            data['options'] = options
        QuizService.add_question(quiz.id, data)
        flash('Question added.', 'success')
        return redirect(url_for('teacher.quiz_edit', quiz_id=quiz.id))
    return render_template('teacher/quizzes/edit.html', quiz=quiz)


@teacher_bp.route('/quizzes/<int:quiz_id>/question/<int:question_id>/delete', methods=['POST'])
@login_required
@teacher_required
def quiz_question_delete(quiz_id, question_id):
    quiz = QuizService.get_quiz(quiz_id)
    if not quiz or quiz.teacher_id != current_user.id:
        abort(403)
    QuizService.delete_question(question_id)
    flash('Question removed.', 'success')
    return redirect(url_for('teacher.quiz_edit', quiz_id=quiz_id))


@teacher_bp.route('/quizzes/<int:quiz_id>/attempts')
@login_required
@teacher_required
def quiz_attempts(quiz_id):
    attempts = QuizService.get_attempts_for_quiz(quiz_id, current_user.id)
    quiz = QuizService.get_quiz(quiz_id)
    return render_template('teacher/quizzes/attempts.html', quiz=quiz, attempts=attempts)


@teacher_bp.route('/attempts/<int:attempt_id>/grade', methods=['GET', 'POST'])
@login_required
@teacher_required
def attempt_grade(attempt_id):
    attempt = QuizService.get_attempt(attempt_id)
    if not attempt:
        abort(404)
    quiz = QuizService.get_quiz(attempt.quiz_id)
    if quiz.teacher_id != current_user.id:
        abort(403)
    answers = {a.question_id: a for a in QuizAnswer.query.filter_by(attempt_id=attempt.id).all()}
    if request.method == 'POST':
        for question in quiz.questions:
            if question.type != 'short_answer':
                continue
            ans = answers.get(question.id)
            if not ans:
                continue
            awarded = request.form.get(f'marks_{question.id}', type=float)
            if awarded is not None:
                QuizService.grade_answer(ans.id, awarded > 0, awarded)
        flash('Grades saved.', 'success')
        return redirect(url_for('teacher.quiz_attempts', quiz_id=quiz.id))
    return render_template('teacher/quizzes/grade.html', attempt=attempt, quiz=quiz, answers=answers)


# ───────────── STUDY MATERIALS ─────────────

@teacher_bp.route('/materials', methods=['GET', 'POST'])
@login_required
@teacher_required
def materials():
    subjects = _my_subjects()
    if request.method == 'POST':
        subject_id = request.form.get('subject_id', type=int)
        require_subject_ownership(subject_id)
        file_url = ''
        file = request.files.get('file')
        if file and file.filename:
            fname, _, _ = save_upload(file, 'materials')
            if fname:
                file_url = f'/static/uploads/materials/{fname}'
        material = StudyMaterial(
            subject_id=subject_id,
            teacher_id=current_user.id,
            title=request.form.get('title'),
            file_url=file_url or request.form.get('link', ''),
            material_type=request.form.get('material_type', 'notes'),
        )
        db.session.add(material)
        db.session.commit()
        flash('Study material added.', 'success')
        return redirect(url_for('teacher.materials'))
    subject_ids = [s.id for s in subjects]
    query = StudyMaterial.query.filter_by(teacher_id=current_user.id)
    if subject_ids:
        query = query.filter(StudyMaterial.subject_id.in_(subject_ids))
    material_list = query.order_by(StudyMaterial.created_at.desc()).all()
    return render_template('teacher/materials.html', subjects=subjects, materials=material_list)


# ───────────── ANNOUNCEMENTS ─────────────

@teacher_bp.route('/announcements', methods=['GET', 'POST'])
@login_required
@teacher_required
def announcements():
    subjects = _my_subjects()
    if request.method == 'POST':
        subject_id = request.form.get('subject_id', type=int)
        require_subject_ownership(subject_id)
        ann = Announcement(
            scope_type='subject',
            scope_id=subject_id,
            author_id=current_user.id,
            title=request.form.get('title'),
            body=request.form.get('body'),
        )
        db.session.add(ann)
        db.session.commit()
        flash('Announcement posted.', 'success')
        return redirect(url_for('teacher.announcements'))
    subject_ids = [s.id for s in subjects]
    ann_list = (Announcement.query.filter_by(scope_type='subject')
                .filter(Announcement.scope_id.in_(subject_ids))
                .order_by(Announcement.posted_at.desc()).all() if subject_ids else [])
    return render_template('teacher/announcements.html', subjects=subjects, announcements=ann_list)


# ───────────── ASSIGNMENTS ─────────────

@teacher_bp.route('/assignments', methods=['GET', 'POST'])
@login_required
@teacher_required
def assignments():
    subjects = _my_subjects()
    if request.method == 'POST':
        subject_id = request.form.get('subject_id', type=int)
        require_subject_ownership(subject_id)
        due_date = request.form.get('due_date')
        if not due_date:
            flash('Due date is required.', 'danger')
            return redirect(url_for('teacher.assignments'))
        file_url = None
        file = request.files.get('file')
        if file and file.filename:
            fname, _, _ = save_upload(file, 'assignments')
            if fname:
                file_url = f'/static/uploads/assignments/{fname}'
        assignment = Assignment(
            subject_id=subject_id,
            teacher_id=current_user.id,
            title=request.form.get('title'),
            description=request.form.get('description', ''),
            file_url=file_url,
            due_date=due_date,
            total_marks=request.form.get('total_marks', type=int),
        )
        db.session.add(assignment)
        db.session.commit()
        flash('Assignment posted.', 'success')
        return redirect(url_for('teacher.assignments'))
    subject_ids = [s.id for s in subjects]
    assignment_list = (Assignment.query.filter(Assignment.subject_id.in_(subject_ids))
                       .order_by(Assignment.due_date.desc()).all() if subject_ids else [])
    submission_counts = {
        a.id: AssignmentSubmission.query.filter_by(assignment_id=a.id).count()
        for a in assignment_list
    }
    enrolled_counts = {
        s.id: len(AllocationService.get_students_for_subject(s.id)) for s in subjects
    }
    return render_template('teacher/assignments/index.html', subjects=subjects,
                           assignments=assignment_list, submission_counts=submission_counts,
                           enrolled_counts=enrolled_counts)


@teacher_bp.route('/assignments/<int:assignment_id>/delete', methods=['POST'])
@login_required
@teacher_required
def assignment_delete(assignment_id):
    assignment = db.session.get(Assignment, assignment_id)
    if not assignment or assignment.teacher_id != current_user.id:
        abort(403)
    db.session.delete(assignment)
    db.session.commit()
    flash('Assignment deleted.', 'success')
    return redirect(url_for('teacher.assignments'))


@teacher_bp.route('/assignments/<int:assignment_id>/submissions')
@login_required
@teacher_required
def assignment_submissions(assignment_id):
    assignment = db.session.get(Assignment, assignment_id)
    if not assignment or assignment.teacher_id != current_user.id:
        abort(403)
    enrolled_students = AllocationService.get_students_for_subject(assignment.subject_id)
    submissions_by_student = {
        s.student_id: s for s in AssignmentSubmission.query.filter_by(assignment_id=assignment.id).all()
    }
    roster = [
        {'student': student, 'submission': submissions_by_student.get(student.id)}
        for student in enrolled_students
    ]
    return render_template('teacher/assignments/submissions.html', assignment=assignment, roster=roster)


@teacher_bp.route('/assignments/submissions/<int:submission_id>/grade', methods=['POST'])
@login_required
@teacher_required
def submission_grade(submission_id):
    submission = db.session.get(AssignmentSubmission, submission_id)
    if not submission or submission.assignment.teacher_id != current_user.id:
        abort(403)
    submission.marks_awarded = request.form.get('marks_awarded', type=int)
    submission.feedback = request.form.get('feedback', '')
    from datetime import datetime
    submission.graded_at = datetime.utcnow()
    db.session.commit()
    flash('Grade saved.', 'success')
    return redirect(url_for('teacher.assignment_submissions', assignment_id=submission.assignment_id))
