"""
Institution Service
Business logic for institution management.
"""
from app import db
from app.models.institution import Institution


class InstitutionService:

    @staticmethod
    def get_institution():
        """Return the single institution record, or None."""
        return Institution.query.first()

    @staticmethod
    def get_or_create():
        """Return existing institution or create with defaults."""
        inst = Institution.query.first()
        if not inst:
            inst = Institution(
                name='Government Graduate College Jhang',
                institution_type='college',
                about='Government Graduate College Jhang is a prestigious institution committed to academic excellence.',
                vision='To be a leading institution of higher education.',
                mission='To provide quality education and produce skilled graduates.',
            )
            db.session.add(inst)
            db.session.commit()
        return inst

    @staticmethod
    def update(institution, data):
        """Update institution fields from a dict."""
        updatable_fields = [
            'name', 'institution_type', 'university_name', 'logo', 'banner', 'favicon',
            'about', 'vision', 'mission', 'history',
            'principal_message', 'principal_name', 'principal_image',
            'vc_message', 'vc_name', 'vc_image',
            'address', 'phone', 'email', 'website', 'google_map', 'office_timing',
            'facebook', 'twitter', 'instagram', 'youtube', 'linkedin',
            'primary_color', 'secondary_color',
        ]
        for field in updatable_fields:
            if field in data:
                setattr(institution, field, data[field])
        db.session.commit()
        return institution
