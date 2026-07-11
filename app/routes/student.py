"""
Student Routes
Student panel — dashboard, chat, downloads, quizzes, flashcards, profile.
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, Response, stream_with_context
from flask_login import login_required, current_user

from app.utils.decorators import student_required
from app.controllers.student_controller import StudentController
from app.services.chat_service import ChatService
from app.services.notification_service import NotificationService
from app.services.download_service import DownloadService
from app.services.department_service import DepartmentService
from app.services.allocation_service import AllocationService
from app.utils.file_handler import save_upload

student_bp = Blueprint('student', __name__)


@student_bp.before_request
def before_request():
    """Require login for all student routes."""
    if not current_user.is_authenticated:
        flash('Please log in to access the student portal.', 'warning')
        return redirect(url_for('auth.login', next=request.url))


@student_bp.context_processor
def inject_unread():
    try:
        if current_user.is_authenticated:
            return {'unread_count': NotificationService.unread_count(current_user.id)}
    except Exception:
        pass
    return {'unread_count': 0}


# ───────────── DASHBOARD ─────────────

@student_bp.route('/')
def dashboard():
    data = StudentController.get_dashboard_data()
    return render_template('student/dashboard/index.html', **data)


# ───────────── AI CHAT ─────────────

@student_bp.route('/chat')
@student_bp.route('/chat/<int:session_id>')
def chat(session_id=None):
    sessions = ChatService.get_user_sessions(current_user.id)
    messages = []
    current_session = None
    if session_id:
        current_session = ChatService.get_session(session_id, current_user.id)
        if current_session:
            messages = ChatService.get_messages(session_id)
    subjects = DepartmentService.get_subjects_for_semester(current_user.semester_id) if current_user.semester_id else []
    return render_template('student/chat/index.html',
                           sessions=sessions, messages=messages,
                           current_session=current_session, subjects=subjects)


@student_bp.route('/chat/new', methods=['POST'])
def chat_new():
    session = ChatService.create_session(
        user_id=current_user.id,
        department_id=current_user.department_id,
        program_id=current_user.program_id,
        batch_id=current_user.batch_id,
        semester_id=current_user.semester_id,
    )
    return redirect(url_for('student.chat', session_id=session.id))


def _parse_int(val):
    """Safely parse an integer from form/JSON data."""
    if val is None or val == '' or val == 'null':
        return None
    try:
        return int(val)
    except (ValueError, TypeError):
        return None


def _load_user_for_ai():
    """Load the current user with relationships eagerly attached for AI context."""
    from app import db
    from app.models.user import User
    user = db.session.get(User, current_user.id)
    # Force-load lazy relationships so they survive outside the session
    _ = user.department.name if user.department else None
    _ = user.program.name if user.program else None
    _ = user.student_batch.label if user.student_batch else None
    _ = user.student_semester.name if user.student_semester else None
    return user


@student_bp.route('/chat/send', methods=['POST'])
def chat_send():
    data = request.get_json()
    session_id = _parse_int(data.get('session_id'))
    message = data.get('message', '').strip()
    subject_id = _parse_int(data.get('subject_id'))

    if not session_id or not message:
        return jsonify({'error': 'Missing session or message'}), 400

    try:
        user = _load_user_for_ai()
        response_text, metadata = StudentController.send_message(
            session_id, message, subject_id,
            user=user, ip=request.remote_addr, ua=request.user_agent.string,
        )
        return jsonify({
            'response': response_text,
            'provider': metadata.get('provider'),
            'response_time_ms': metadata.get('response_time_ms'),
            'resource_files': metadata.get('resource_files', []),
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@student_bp.route('/chat/stream', methods=['POST'])
def chat_stream():
    data = request.get_json()
    session_id = _parse_int(data.get('session_id'))
    message = data.get('message', '').strip()
    subject_id = _parse_int(data.get('subject_id'))

    if not session_id or not message:
        return jsonify({'error': 'Missing data'}), 400

    # Eagerly load user + relationships before generator starts
    user = _load_user_for_ai()
    ip = request.remote_addr
    ua = request.user_agent.string

    def generate():
        try:
            from app.ai.context_manager import ContextManager
            for chunk in ContextManager.process_message_stream(
                user=user,
                session_id=session_id,
                user_message=message,
                subject_id=subject_id,
                ip_address=ip,
                user_agent=ua,
            ):
                yield f"data: {chunk}\n\n"
            yield "data: [DONE]\n\n"
        except Exception as e:
            yield f"data: Error: {str(e)}\n\n"

    return Response(stream_with_context(generate()), mimetype='text/event-stream')


@student_bp.route('/chat/rename', methods=['POST'])
def chat_rename():
    data = request.get_json()
    ChatService.rename_session(data.get('session_id'), current_user.id, data.get('title', 'Untitled'))
    return jsonify({'status': 'ok'})


@student_bp.route('/chat/bookmark', methods=['POST'])
def chat_bookmark():
    data = request.get_json()
    ChatService.toggle_bookmark(data.get('session_id'), current_user.id)
    return jsonify({'status': 'ok'})


@student_bp.route('/chat/delete/<int:session_id>', methods=['POST'])
def chat_delete(session_id):
    ChatService.delete_session(session_id, current_user.id)
    flash('Chat deleted.', 'info')
    return redirect(url_for('student.chat'))


@student_bp.route('/chat/feedback', methods=['POST'])
def chat_feedback():
    data = request.get_json()
    ChatService.feedback_message(data.get('message_id'), data.get('is_liked'))
    return jsonify({'status': 'ok'})


# ───────────── SUBJECTS ─────────────

@student_bp.route('/subjects')
def subjects():
    from app.services.allocation_service import AllocationService
    subjs = AllocationService.get_enrolled_subjects(current_user.id)
    return render_template('student/subjects/index.html', subjects=subjs)


# ───────────── QUIZ ─────────────

@student_bp.route('/quiz')
def quiz():
    """AI quiz generator + list of teacher-authored quizzes for enrolled subjects."""
    from app.services.allocation_service import AllocationService
    from app.services.quiz_service import QuizService
    subjs = AllocationService.get_enrolled_subjects(current_user.id)
    teacher_quizzes = QuizService.list_all_quizzes_for_student(current_user.id)
    my_results = QuizService.get_my_results(current_user.id)
    return render_template('student/quiz/index.html', subjects=subjs,
                           teacher_quizzes=teacher_quizzes, my_results=my_results)


@student_bp.route('/quiz/<int:quiz_id>/start', methods=['POST'])
def quiz_start(quiz_id):
    from app.services.quiz_service import QuizService
    attempt = QuizService.start_attempt(quiz_id, current_user.id)
    return redirect(url_for('student.quiz_attempt', attempt_id=attempt.id))


@student_bp.route('/quiz/attempt/<int:attempt_id>', methods=['GET', 'POST'])
def quiz_attempt(attempt_id):
    from app.services.quiz_service import QuizService
    attempt = QuizService.get_attempt(attempt_id)
    if not attempt or attempt.student_id != current_user.id:
        flash('Attempt not found.', 'danger')
        return redirect(url_for('student.quiz'))
    quiz_obj = QuizService.get_quiz(attempt.quiz_id)
    if request.method == 'POST':
        answers_map = {k.replace('q_', ''): v for k, v in request.form.items() if k.startswith('q_')}
        QuizService.submit_attempt(attempt_id, current_user.id, answers_map)
        flash('Quiz submitted.', 'success')
        return redirect(url_for('student.quiz_result', attempt_id=attempt_id))
    return render_template('student/quiz/attempt.html', attempt=attempt, quiz=quiz_obj)


@student_bp.route('/quiz/result/<int:attempt_id>')
def quiz_result(attempt_id):
    from app.services.quiz_service import QuizService
    from app.models.quiz import QuizAnswer
    attempt = QuizService.get_attempt(attempt_id)
    if not attempt or attempt.student_id != current_user.id:
        flash('Result not found.', 'danger')
        return redirect(url_for('student.quiz'))
    quiz_obj = QuizService.get_quiz(attempt.quiz_id)
    answers = {a.question_id: a for a in QuizAnswer.query.filter_by(attempt_id=attempt.id).all()}
    return render_template('student/quiz/result.html', attempt=attempt, quiz=quiz_obj, answers=answers)


@student_bp.route('/quiz/generate', methods=['POST'])
def quiz_generate():
    """Generate quiz questions via AI."""
    data = request.get_json()
    subject_id = _parse_int(data.get('subject_id'))
    topic = data.get('topic', '').strip()
    count = int(data.get('count', 10))
    difficulty = data.get('difficulty', 'medium')

    if not subject_id:
        return jsonify({'error': 'Please select a subject'}), 400

    try:
        from app.ai.provider_factory import get_provider
        from app.services.knowledge_service import KnowledgeService
        from app.models.subject import Subject

        subject = Subject.query.get(subject_id)
        subject_name = subject.name if subject else 'General'

        # Get knowledge context for this subject
        knowledge_context, _ = KnowledgeService.get_context_for_student(
            department_id=current_user.department_id,
            program_id=current_user.program_id,
            batch_id=current_user.batch_id,
            semester_id=current_user.semester_id,
            subject_id=subject_id,
        )

        prompt = f"""Generate a {difficulty} difficulty quiz with exactly {count} multiple-choice questions about {topic or subject_name}.

Use ONLY this knowledge base to create questions:
{knowledge_context[:6000]}

Return ONLY valid JSON in this exact format, nothing else before or after:
{{"questions":[{{"q":"Question text here?","options":["Option A","Option B","Option C","Option D"],"answer":0}}]}}

Rules:
- "answer" is the index (0-3) of the correct option
- Each question must have exactly 4 options
- Questions must be based on the provided knowledge base
- Do NOT include any text outside the JSON"""

        provider = get_provider()
        response_text, _ = provider.generate([{'role': 'user', 'content': prompt}])

        # Extract JSON from response
        import json
        import re
        json_match = re.search(r'\{[\s\S]*"questions"[\s\S]*\}', response_text)
        if json_match:
            quiz_data = json.loads(json_match.group(0))
            return jsonify(quiz_data)
        else:
            return jsonify({'error': 'Could not generate quiz. Please try again.'}), 500

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ───────────── FLASHCARDS ─────────────

@student_bp.route('/flashcards')
def flashcards():
    subjs = DepartmentService.get_subjects_for_semester(current_user.semester_id) if current_user.semester_id else []
    return render_template('student/flashcards/index.html', subjects=subjs)


# ───────────── DOWNLOADS ─────────────

@student_bp.route('/downloads')
def downloads():
    page = request.args.get('page', 1, type=int)
    category = request.args.get('category', '')
    pagination = DownloadService.get_all(
        page=page, category=category or None,
        department_id=current_user.department_id,
    )
    categories = DownloadService.CATEGORIES
    return render_template('student/downloads/index.html', pagination=pagination, categories=categories)


@student_bp.route('/downloads/<int:dl_id>')
def download_file(dl_id):
    from flask import send_file
    dl = DownloadService.get_by_id(dl_id)
    if not dl:
        flash('File not found.', 'danger')
        return redirect(url_for('student.downloads'))
    DownloadService.increment_download(dl_id)
    return send_file(dl.file_path, as_attachment=True, download_name=dl.original_name)


# ───────────── NOTES ─────────────

@student_bp.route('/notes')
def notes():
    from sqlalchemy import desc

    from app.models.enrollment import Enrollment
    from app.models.study_material import StudyMaterial

    query = (
        StudyMaterial.query.join(Enrollment, Enrollment.subject_id == StudyMaterial.subject_id)
        .filter(Enrollment.student_id == current_user.id)
        .order_by(desc(StudyMaterial.created_at))
    )
    pagination = query.paginate(
        page=request.args.get('page', 1, type=int),
        per_page=12,
        error_out=False,
    )
    return render_template('student/notes/index.html', pagination=pagination)


# ───────────── ASSIGNMENTS ─────────────

@student_bp.route('/assignments')
def assignments():
    from app.models.assignment import Assignment, AssignmentSubmission
    subjects = AllocationService.get_enrolled_subjects(current_user.id)
    subject_ids = [s.id for s in subjects]
    assignment_list = (
        Assignment.query.filter(Assignment.subject_id.in_(subject_ids))
        .order_by(Assignment.due_date.asc()).all()
        if subject_ids else []
    )
    my_submissions = {
        s.assignment_id: s for s in
        AssignmentSubmission.query.filter_by(student_id=current_user.id).all()
    }
    rows = [(a, my_submissions.get(a.id)) for a in assignment_list]
    return render_template('student/assignments/index.html', rows=rows)


@student_bp.route('/assignments/<int:assignment_id>/submit', methods=['POST'])
def assignment_submit(assignment_id):
    from app.models.assignment import Assignment, AssignmentSubmission
    from app import db
    assignment = Assignment.query.get_or_404(assignment_id)
    if not AllocationService.is_enrolled(current_user.id, assignment.subject_id):
        flash('You are not enrolled in this subject.', 'danger')
        return redirect(url_for('student.assignments'))
    file = request.files.get('file')
    if not file or not file.filename:
        flash('Please choose a file to submit.', 'danger')
        return redirect(url_for('student.assignments'))
    fname, _, _ = save_upload(file, 'assignment_submissions')
    if not fname:
        flash('Upload failed. Please try a different file.', 'danger')
        return redirect(url_for('student.assignments'))
    file_url = f'/static/uploads/assignment_submissions/{fname}'

    existing = AssignmentSubmission.query.filter_by(
        assignment_id=assignment.id, student_id=current_user.id,
    ).first()
    if existing:
        existing.file_url = file_url
        from datetime import datetime
        existing.submitted_at = datetime.utcnow()
        existing.marks_awarded = None
        existing.feedback = None
        existing.graded_at = None
    else:
        db.session.add(AssignmentSubmission(
            assignment_id=assignment.id,
            student_id=current_user.id,
            file_url=file_url,
        ))
    db.session.commit()
    flash('Assignment submitted.', 'success')
    return redirect(url_for('student.assignments'))


# ───────────── NOTIFICATIONS ─────────────

@student_bp.route('/notifications')
def notifications():
    notifs = NotificationService.get_for_user(current_user.id)
    return render_template('student/notifications/index.html', notifications=notifs)


@student_bp.route('/notifications/read-all', methods=['POST'])
def notifications_read_all():
    NotificationService.mark_all_read(current_user.id)
    return redirect(url_for('student.notifications'))


# ───────────── PROFILE ─────────────

@student_bp.route('/profile')
def profile():
    return render_template('student/profile/index.html')
