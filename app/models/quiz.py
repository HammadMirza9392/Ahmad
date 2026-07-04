"""
Quiz Models
Teacher-authored quizzes, questions, student attempts, and answers.
Quiz lifecycle status is derived at read time, never stored.
"""
from datetime import datetime
from app import db


class Quiz(db.Model):
    __tablename__ = 'quizzes'

    id = db.Column(db.Integer, primary_key=True)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    total_marks = db.Column(db.Integer, default=0)
    passing_marks = db.Column(db.Integer, default=0)
    duration_minutes = db.Column(db.Integer, default=30)
    start_at = db.Column(db.DateTime)
    end_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    subject = db.relationship('Subject', backref='quizzes')
    teacher = db.relationship('User', backref='quizzes')
    questions = db.relationship('QuizQuestion', backref='quiz', lazy=True,
                                cascade='all, delete-orphan', order_by='QuizQuestion.sort_order')
    attempts = db.relationship('QuizAttempt', backref='quiz', lazy=True, cascade='all, delete-orphan')

    @property
    def status(self):
        """Derive lifecycle status from now vs start_at/end_at."""
        now = datetime.utcnow()
        if self.start_at and now < self.start_at:
            return 'upcoming'
        if self.end_at and now > self.end_at:
            return 'expired'
        if self.start_at and self.end_at and self.start_at <= now <= self.end_at:
            return 'active'
        # No window set -> treat as active/open
        return 'active'

    def __repr__(self):
        return f'<Quiz {self.title}>'


class QuizQuestion(db.Model):
    __tablename__ = 'quiz_questions'

    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quizzes.id'), nullable=False)
    type = db.Column(db.String(20), default='mcq')  # mcq, true_false, short_answer
    text = db.Column(db.Text, nullable=False)
    options_json = db.Column(db.Text)  # JSON list of options for MCQ
    correct_answer = db.Column(db.Text)
    marks = db.Column(db.Integer, default=1)
    sort_order = db.Column(db.Integer, default=0)

    answers = db.relationship('QuizAnswer', backref='question', lazy=True, cascade='all, delete-orphan')

    def options(self):
        import json
        if not self.options_json:
            return []
        try:
            return json.loads(self.options_json)
        except (ValueError, TypeError):
            return []

    def __repr__(self):
        return f'<QuizQuestion {self.id} type={self.type}>'


class QuizAttempt(db.Model):
    __tablename__ = 'quiz_attempts'

    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quizzes.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    attempt_no = db.Column(db.Integer, default=1)
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    submitted_at = db.Column(db.DateTime, nullable=True)
    score = db.Column(db.Float, nullable=True)
    status = db.Column(db.String(20), default='in_progress')  # in_progress, submitted, graded

    student = db.relationship('User', backref='quiz_attempts')
    answers = db.relationship('QuizAnswer', backref='attempt', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<QuizAttempt {self.id} quiz={self.quiz_id} student={self.student_id}>'


class QuizAnswer(db.Model):
    __tablename__ = 'quiz_answers'

    id = db.Column(db.Integer, primary_key=True)
    attempt_id = db.Column(db.Integer, db.ForeignKey('quiz_attempts.id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('quiz_questions.id'), nullable=False)
    answer_text = db.Column(db.Text)
    is_correct = db.Column(db.Boolean, nullable=True)  # None => pending manual grading
    marks_awarded = db.Column(db.Float, nullable=True)

    def __repr__(self):
        return f'<QuizAnswer attempt={self.attempt_id} question={self.question_id}>'
