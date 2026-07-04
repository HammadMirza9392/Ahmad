"""
Quiz Service
Two responsibilities:
  1. AI prompt building for the student AI-quiz generator (legacy, kept intact).
  2. DB-backed teacher/student/HOD/admin quiz workflow.
"""
import json
from datetime import datetime
from flask import abort

from app import db
from app.models.quiz import Quiz, QuizQuestion, QuizAttempt, QuizAnswer
from app.models.subject import Subject
from app.models.enrollment import Enrollment


class QuizService:

    # ───────────── TEACHER ─────────────

    @staticmethod
    def create_quiz(teacher_id, data):
        quiz = Quiz(
            subject_id=data['subject_id'],
            teacher_id=teacher_id,
            title=data['title'],
            description=data.get('description', ''),
            total_marks=int(data.get('total_marks') or 0),
            passing_marks=int(data.get('passing_marks') or 0),
            duration_minutes=int(data.get('duration_minutes') or 30),
            start_at=QuizService._parse_dt(data.get('start_at')),
            end_at=QuizService._parse_dt(data.get('end_at')),
        )
        db.session.add(quiz)
        db.session.commit()
        return quiz

    @staticmethod
    def update_quiz(quiz, data):
        for field in ['title', 'description']:
            if field in data:
                setattr(quiz, field, data[field])
        for field in ['total_marks', 'passing_marks', 'duration_minutes']:
            if field in data and data[field] not in (None, ''):
                setattr(quiz, field, int(data[field]))
        if 'start_at' in data:
            quiz.start_at = QuizService._parse_dt(data.get('start_at'))
        if 'end_at' in data:
            quiz.end_at = QuizService._parse_dt(data.get('end_at'))
        db.session.commit()
        return quiz

    @staticmethod
    def add_question(quiz_id, data):
        options = data.get('options')
        options_json = None
        if options:
            if isinstance(options, (list, tuple)):
                options_json = json.dumps([o for o in options if str(o).strip()])
            else:
                options_json = options
        question = QuizQuestion(
            quiz_id=quiz_id,
            type=data.get('type', 'mcq'),
            text=data['text'],
            options_json=options_json,
            correct_answer=data.get('correct_answer', ''),
            marks=int(data.get('marks') or 1),
            sort_order=int(data.get('sort_order') or 0),
        )
        db.session.add(question)
        db.session.commit()
        return question

    @staticmethod
    def delete_question(question_id):
        q = db.session.get(QuizQuestion, question_id)
        if q:
            db.session.delete(q)
            db.session.commit()

    @staticmethod
    def get_quiz(quiz_id):
        return db.session.get(Quiz, quiz_id)

    @staticmethod
    def list_quizzes_for_teacher(teacher_id):
        return Quiz.query.filter_by(teacher_id=teacher_id).order_by(Quiz.created_at.desc()).all()

    @staticmethod
    def get_attempts_for_quiz(quiz_id, teacher_id):
        """Return attempts for a quiz, enforcing teacher ownership (403 otherwise)."""
        quiz = db.session.get(Quiz, quiz_id)
        if not quiz or quiz.teacher_id != teacher_id:
            abort(403)
        return (QuizAttempt.query.filter_by(quiz_id=quiz_id)
                .order_by(QuizAttempt.started_at.desc()).all())

    @staticmethod
    def grade_answer(answer_id, is_correct, marks_awarded):
        answer = db.session.get(QuizAnswer, answer_id)
        if not answer:
            return None
        answer.is_correct = is_correct
        answer.marks_awarded = marks_awarded
        db.session.commit()
        # Recompute attempt score
        attempt = db.session.get(QuizAttempt, answer.attempt_id)
        if attempt:
            QuizService._recompute_score(attempt)
        return answer

    # ───────────── STUDENT ─────────────

    @staticmethod
    def list_available_quizzes(student_id):
        """Quizzes for subjects the student is enrolled in, that are active or upcoming."""
        subject_ids = [e.subject_id for e in
                       Enrollment.query.filter_by(student_id=student_id).all()]
        if not subject_ids:
            return []
        quizzes = Quiz.query.filter(Quiz.subject_id.in_(subject_ids)).order_by(Quiz.start_at).all()
        return [q for q in quizzes if q.status in ('active', 'upcoming')]

    @staticmethod
    def list_all_quizzes_for_student(student_id):
        """Every quiz for enrolled subjects, any status (for the list view)."""
        subject_ids = [e.subject_id for e in
                       Enrollment.query.filter_by(student_id=student_id).all()]
        if not subject_ids:
            return []
        return Quiz.query.filter(Quiz.subject_id.in_(subject_ids)).order_by(Quiz.start_at.desc()).all()

    @staticmethod
    def start_attempt(quiz_id, student_id):
        quiz = db.session.get(Quiz, quiz_id)
        if not quiz:
            abort(404)
        # Enrollment check
        enrolled = Enrollment.query.filter_by(student_id=student_id, subject_id=quiz.subject_id).first()
        if not enrolled:
            abort(403)
        prev = QuizAttempt.query.filter_by(quiz_id=quiz_id, student_id=student_id).count()
        attempt = QuizAttempt(
            quiz_id=quiz_id,
            student_id=student_id,
            attempt_no=prev + 1,
            status='in_progress',
        )
        db.session.add(attempt)
        db.session.commit()
        return attempt

    @staticmethod
    def submit_attempt(attempt_id, student_id, answers_map):
        """answers_map: {question_id: answer_text}. Auto-grades MCQ/true_false."""
        attempt = db.session.get(QuizAttempt, attempt_id)
        if not attempt or attempt.student_id != student_id:
            abort(403)
        quiz = db.session.get(Quiz, attempt.quiz_id)
        for question in quiz.questions:
            given = (answers_map.get(str(question.id)) or answers_map.get(question.id) or '').strip()
            is_correct = None
            marks_awarded = None
            if question.type in ('mcq', 'true_false'):
                correct = (question.correct_answer or '').strip()
                is_correct = given.lower() == correct.lower() and given != ''
                marks_awarded = question.marks if is_correct else 0
            answer = QuizAnswer(
                attempt_id=attempt.id,
                question_id=question.id,
                answer_text=given,
                is_correct=is_correct,
                marks_awarded=marks_awarded,
            )
            db.session.add(answer)
        attempt.submitted_at = datetime.utcnow()
        # If any short_answer questions exist, leave as 'submitted' (pending), else 'graded'
        has_manual = any(q.type == 'short_answer' for q in quiz.questions)
        attempt.status = 'submitted' if has_manual else 'graded'
        db.session.commit()
        QuizService._recompute_score(attempt)
        return attempt

    @staticmethod
    def get_my_results(student_id):
        return (QuizAttempt.query.filter_by(student_id=student_id)
                .filter(QuizAttempt.submitted_at.isnot(None))
                .order_by(QuizAttempt.submitted_at.desc()).all())

    @staticmethod
    def get_attempt(attempt_id):
        return db.session.get(QuizAttempt, attempt_id)

    # ───────────── HOD / ADMIN AGGREGATION ─────────────

    @staticmethod
    def department_activity(department_id):
        """Completion rate and avg score by subject within a department."""
        subjects = Subject.query.filter_by(department_id=department_id).all()
        rows = []
        for subj in subjects:
            quizzes = Quiz.query.filter_by(subject_id=subj.id).all()
            quiz_ids = [q.id for q in quizzes]
            attempts = (QuizAttempt.query.filter(QuizAttempt.quiz_id.in_(quiz_ids)).all()
                        if quiz_ids else [])
            enrolled = Enrollment.query.filter_by(subject_id=subj.id).count()
            completed = [a for a in attempts if a.submitted_at]
            scores = [a.score for a in completed if a.score is not None]
            rows.append({
                'subject': subj,
                'quiz_count': len(quizzes),
                'attempt_count': len(attempts),
                'completed_count': len(completed),
                'enrolled': enrolled,
                'completion_rate': round(100.0 * len(completed) / enrolled, 1) if enrolled else 0,
                'avg_score': round(sum(scores) / len(scores), 1) if scores else 0,
            })
        return rows

    @staticmethod
    def cross_department_stats():
        """Aggregate quiz stats across all departments."""
        from app.models.department import Department
        rows = []
        for dept in Department.query.order_by(Department.name).all():
            subject_ids = [s.id for s in Subject.query.filter_by(department_id=dept.id).all()]
            quiz_ids = ([q.id for q in Quiz.query.filter(Quiz.subject_id.in_(subject_ids)).all()]
                        if subject_ids else [])
            attempts = (QuizAttempt.query.filter(QuizAttempt.quiz_id.in_(quiz_ids)).all()
                        if quiz_ids else [])
            scores = [a.score for a in attempts if a.score is not None]
            rows.append({
                'department': dept,
                'quiz_count': len(quiz_ids),
                'attempt_count': len(attempts),
                'avg_score': round(sum(scores) / len(scores), 1) if scores else 0,
            })
        return rows

    # ───────────── HELPERS ─────────────

    @staticmethod
    def _recompute_score(attempt):
        answers = QuizAnswer.query.filter_by(attempt_id=attempt.id).all()
        if any(a.marks_awarded is None for a in answers):
            # Still pending manual grading — compute partial from graded ones
            graded = [a for a in answers if a.marks_awarded is not None]
            attempt.score = sum(a.marks_awarded for a in graded) if graded else None
        else:
            attempt.score = sum(a.marks_awarded or 0 for a in answers)
            attempt.status = 'graded'
        db.session.commit()

    @staticmethod
    def _parse_dt(val):
        if not val:
            return None
        for fmt in ('%Y-%m-%dT%H:%M', '%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M'):
            try:
                return datetime.strptime(val, fmt)
            except (ValueError, TypeError):
                continue
        return None

    # ───────────── AI PROMPT BUILDERS (legacy, unchanged) ─────────────

    @staticmethod
    def build_quiz_prompt(subject_name, topic=None, quiz_type='mixed', num_questions=10):
        """Build a structured prompt for the AI to generate a quiz.
        quiz_type: mcq, true_false, fill_blank, short, long, mixed
        """
        type_instructions = {
            'mcq': 'Generate only Multiple Choice Questions with 4 options (A, B, C, D). Mark the correct answer.',
            'true_false': 'Generate only True/False questions. State the correct answer.',
            'fill_blank': 'Generate only Fill in the Blank questions. Provide the correct answer.',
            'short': 'Generate only Short Answer questions (2-3 sentences each). Provide model answers.',
            'long': 'Generate only Long Answer questions (paragraph-length). Provide detailed model answers.',
            'mixed': 'Generate a mix of MCQs, True/False, Fill in the Blank, and Short Answer questions.',
        }

        topic_line = f"Topic: {topic}" if topic else "Cover the most important topics."

        prompt = f"""Generate a quiz for the subject: {subject_name}
{topic_line}
Number of questions: {num_questions}

{type_instructions.get(quiz_type, type_instructions['mixed'])}

Format your response as valid JSON with this structure:
{{
    "quiz_title": "Quiz on ...",
    "questions": [
        {{
            "id": 1,
            "type": "mcq|true_false|fill_blank|short|long",
            "question": "...",
            "options": ["A) ...", "B) ...", "C) ...", "D) ..."],
            "correct_answer": "...",
            "explanation": "..."
        }}
    ]
}}

For true_false questions, options should be ["True", "False"].
For fill_blank questions, options should be an empty list.
For short/long questions, options should be an empty list and correct_answer should contain the model answer.

Ensure all questions are academically accurate and relevant."""

        return prompt

    @staticmethod
    def build_score_prompt(quiz_data, student_answers):
        """Build a prompt to score student answers and identify weak areas."""
        prompt = f"""Score the following quiz answers and provide detailed feedback.

Quiz: {quiz_data.get('quiz_title', 'Quiz')}

Questions and Student Answers:
"""
        for i, q in enumerate(quiz_data.get('questions', [])):
            student_ans = student_answers.get(str(q['id']), 'No answer provided')
            prompt += f"""
Question {q['id']}: {q['question']}
Correct Answer: {q['correct_answer']}
Student's Answer: {student_ans}
"""

        prompt += """
Respond in valid JSON format:
{
    "total_score": <number>,
    "total_questions": <number>,
    "percentage": <number>,
    "results": [
        {
            "question_id": <number>,
            "is_correct": true/false,
            "student_answer": "...",
            "correct_answer": "...",
            "explanation": "..."
        }
    ],
    "weak_areas": ["topic1", "topic2"],
    "recommendations": "..."
}"""
        return prompt
