"""
Theme Settings Model
Singleton row holding the active portal theme configuration.
"""
from datetime import datetime
from app import db


class ThemeSettings(db.Model):
    __tablename__ = 'theme_settings'

    id = db.Column(db.Integer, primary_key=True)
    logo_url = db.Column(db.String(500))
    favicon_url = db.Column(db.String(500))
    primary_color = db.Column(db.String(20), default='#667eea')
    secondary_color = db.Column(db.String(20), default='#764ba2')
    accent_color = db.Column(db.String(20), default='#f59e0b')
    bg_color = db.Column(db.String(20), default='#f8f9fa')
    text_color = db.Column(db.String(20), default='#1f2937')
    banner_text_color = db.Column(db.String(20), default='#ffffff')  # text over hero/page-banner gradients
    sidebar_text_color = db.Column(db.String(20), default='#ffffff')  # nav labels in the dashboard sidebar
    link_color = db.Column(db.String(20))  # optional override; falls back to primary_color when unset
    font_display = db.Column(db.String(100), default='Inter')
    font_body = db.Column(db.String(100), default='Inter')
    mode = db.Column(db.String(10), default='light')  # light, dark, auto
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    updated_by = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)

    def __repr__(self):
        return f'<ThemeSettings {self.id}>'
