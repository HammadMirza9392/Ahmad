"""
Knowledge Base Model
Stores training data for the AI, organized hierarchically.
"""
from datetime import datetime
from app import db


class KnowledgeBase(db.Model):
    __tablename__ = 'knowledge_base'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(500), nullable=False)
    content = db.Column(db.Text, nullable=False)

    # Hierarchical categorization
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id', ondelete='CASCADE'))
    program_id = db.Column(db.Integer, db.ForeignKey('programs.id', ondelete='CASCADE'))
    batch_id = db.Column(db.Integer, db.ForeignKey('batches.id', ondelete='CASCADE'))
    semester_id = db.Column(db.Integer, db.ForeignKey('semesters.id', ondelete='CASCADE'))
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id', ondelete='CASCADE'))
    chapter = db.Column(db.String(255))
    topic = db.Column(db.String(255))

    # Publishing
    status = db.Column(db.String(20), default='published')  # draft, published, archived
    version = db.Column(db.Integer, default=1)

    # Metadata
    content_type = db.Column(db.String(50), default='text')  # text, file, mixed
    tags = db.Column(db.Text)  # comma-separated

    created_by = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    files = db.relationship('KnowledgeFile', backref='knowledge', lazy=True, cascade='all, delete-orphan')
    versions = db.relationship('KnowledgeVersion', backref='knowledge', lazy='dynamic', cascade='all, delete-orphan')
    department = db.relationship('Department', backref=db.backref('knowledge_entries', cascade='all, delete-orphan'))
    program = db.relationship('Program', backref=db.backref('knowledge_entries', cascade='all, delete-orphan'))
    batch = db.relationship('Batch', backref=db.backref('knowledge_entries', cascade='all, delete-orphan'))
    semester = db.relationship('Semester', backref=db.backref('knowledge_entries', cascade='all, delete-orphan'))
    author = db.relationship('User', backref='knowledge_entries')

    def __repr__(self):
        return f'<KnowledgeBase {self.title}>'


class KnowledgeFile(db.Model):
    __tablename__ = 'knowledge_files'

    id = db.Column(db.Integer, primary_key=True)
    knowledge_id = db.Column(db.Integer, db.ForeignKey('knowledge_base.id', ondelete='CASCADE'), nullable=False)
    filename = db.Column(db.String(500), nullable=False)
    original_name = db.Column(db.String(500), nullable=False)
    file_path = db.Column(db.String(1000), nullable=False)
    file_type = db.Column(db.String(50))  # pdf, docx, txt, csv, xlsx, image
    file_size = db.Column(db.Integer)
    extracted_text = db.Column(db.Text)  # text extracted from files for AI context

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<KnowledgeFile {self.original_name}>'


class KnowledgeVersion(db.Model):
    __tablename__ = 'knowledge_versions'

    id = db.Column(db.Integer, primary_key=True)
    knowledge_id = db.Column(db.Integer, db.ForeignKey('knowledge_base.id', ondelete='CASCADE'), nullable=False)
    version_number = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String(500))
    content = db.Column(db.Text)
    changed_by = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'))

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    editor = db.relationship('User', backref='knowledge_edits')

    def __repr__(self):
        return f'<KnowledgeVersion {self.knowledge_id} v{self.version_number}>'
