"""
CMS Model
Content Management System for static website pages.
"""
from datetime import datetime
from app import db


class CMSPage(db.Model):
    __tablename__ = 'cms_pages'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(500), nullable=False)
    slug = db.Column(db.String(500), unique=True, nullable=False, index=True)
    content = db.Column(db.Text)
    meta_title = db.Column(db.String(500))
    meta_description = db.Column(db.Text)

    # Page type for special rendering
    page_type = db.Column(db.String(50), default='custom')  # home, about, contact, department, admission, custom

    banner_image = db.Column(db.String(500))
    is_published = db.Column(db.Boolean, default=True)
    show_in_menu = db.Column(db.Boolean, default=True)
    menu_order = db.Column(db.Integer, default=0)
    parent_id = db.Column(db.Integer, db.ForeignKey('cms_pages.id'))

    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    children = db.relationship('CMSPage', backref=db.backref('parent', remote_side='CMSPage.id'), lazy=True)
    sections = db.relationship('CMSSection', backref='page', lazy=True, cascade='all, delete-orphan',
                               order_by='CMSSection.sort_order')
    author = db.relationship('User', backref='cms_pages')

    def __repr__(self):
        return f'<CMSPage {self.slug}>'


class CMSSection(db.Model):
    """Modular page sections that admin can edit individually."""
    __tablename__ = 'cms_sections'

    id = db.Column(db.Integer, primary_key=True)
    page_id = db.Column(db.Integer, db.ForeignKey('cms_pages.id'), nullable=False)
    section_key = db.Column(db.String(100), nullable=False)  # hero, features, cta, content_block, etc.
    title = db.Column(db.String(500))
    content = db.Column(db.Text)
    image = db.Column(db.String(500))
    extra_data = db.Column(db.Text)  # JSON for flexible section data
    sort_order = db.Column(db.Integer, default=0)
    is_visible = db.Column(db.Boolean, default=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<CMSSection {self.section_key}>'
