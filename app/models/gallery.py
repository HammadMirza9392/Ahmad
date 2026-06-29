"""
Gallery Model
Photo gallery for institution and department images.
"""
from datetime import datetime
from app import db


class GalleryAlbum(db.Model):
    __tablename__ = 'gallery_albums'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(500), nullable=False)
    description = db.Column(db.Text)
    cover_image = db.Column(db.String(500))

    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'))

    is_active = db.Column(db.Boolean, default=True)
    sort_order = db.Column(db.Integer, default=0)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    images = db.relationship('GalleryImage', backref='album', lazy=True, cascade='all, delete-orphan')
    department = db.relationship('Department', backref='gallery_albums')

    def __repr__(self):
        return f'<GalleryAlbum {self.title}>'


class GalleryImage(db.Model):
    __tablename__ = 'gallery_images'

    id = db.Column(db.Integer, primary_key=True)
    album_id = db.Column(db.Integer, db.ForeignKey('gallery_albums.id'), nullable=False)
    title = db.Column(db.String(500))
    image = db.Column(db.String(500), nullable=False)
    sort_order = db.Column(db.Integer, default=0)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<GalleryImage {self.id}>'
