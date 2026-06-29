"""
Institution Model
Stores all college/university information, editable from admin panel.
"""
from datetime import datetime
from app import db


class Institution(db.Model):
    __tablename__ = 'institution'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(500), nullable=False, default='Government Graduate College Jhang')
    institution_type = db.Column(db.String(50), default='college')  # college, university, both
    university_name = db.Column(db.String(500))

    # Branding
    logo = db.Column(db.String(500))
    banner = db.Column(db.String(500))
    favicon = db.Column(db.String(500))

    # Content
    about = db.Column(db.Text)
    vision = db.Column(db.Text)
    mission = db.Column(db.Text)
    history = db.Column(db.Text)
    principal_message = db.Column(db.Text)
    principal_name = db.Column(db.String(255))
    principal_image = db.Column(db.String(500))
    vc_message = db.Column(db.Text)
    vc_name = db.Column(db.String(255))
    vc_image = db.Column(db.String(500))

    # Contact
    address = db.Column(db.Text)
    phone = db.Column(db.String(50))
    email = db.Column(db.String(255))
    website = db.Column(db.String(500))
    google_map = db.Column(db.Text)
    office_timing = db.Column(db.String(255))

    # Social media
    facebook = db.Column(db.String(500))
    twitter = db.Column(db.String(500))
    instagram = db.Column(db.String(500))
    youtube = db.Column(db.String(500))
    linkedin = db.Column(db.String(500))

    # Theme
    primary_color = db.Column(db.String(20), default='#1a56db')
    secondary_color = db.Column(db.String(20), default='#7c3aed')

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<Institution {self.name}>'
