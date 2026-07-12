"""
News Model
Institution news articles and announcements.
"""
from datetime import datetime
from app import db


class News(db.Model):
    __tablename__ = 'news'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(500), nullable=False)
    slug = db.Column(db.String(500), unique=True, nullable=False, index=True)
    excerpt = db.Column(db.Text)
    content = db.Column(db.Text)
    image = db.Column(db.String(500))

    category = db.Column(db.String(100))
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id', ondelete='SET NULL'))

    is_published = db.Column(db.Boolean, default=True)
    is_featured = db.Column(db.Boolean, default=False)
    views = db.Column(db.Integer, default=0)

    created_by = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'))
    published_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    department = db.relationship('Department', backref='news_articles')
    author = db.relationship('User', backref='news_articles')

    def __repr__(self):
        return f'<News {self.title}>'
