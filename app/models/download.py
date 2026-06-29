"""
Download Model
Downloadable resources: books, notes, past papers, timetables, etc.
"""
from datetime import datetime
from app import db


class Download(db.Model):
    __tablename__ = 'downloads'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(500), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(100), nullable=False)  # book, notes, assignment, past_paper, practical, timetable, prospectus, admission_form

    # File
    filename = db.Column(db.String(500), nullable=False)
    original_name = db.Column(db.String(500), nullable=False)
    file_path = db.Column(db.String(1000), nullable=False)
    file_type = db.Column(db.String(50))
    file_size = db.Column(db.Integer)

    # Categorization
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'))
    program_id = db.Column(db.Integer, db.ForeignKey('programs.id'))
    class_id = db.Column(db.Integer, db.ForeignKey('classes.id'))
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'))

    download_count = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    sort_order = db.Column(db.Integer, default=0)

    uploaded_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    department = db.relationship('Department', backref='downloads')
    program = db.relationship('Program', backref='downloads')
    class_ref = db.relationship('Class', backref='downloads')
    subject = db.relationship('Subject', backref='downloads')
    uploader = db.relationship('User', backref='uploads')

    def __repr__(self):
        return f'<Download {self.title}>'
