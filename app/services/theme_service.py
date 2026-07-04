"""
Theme Service
Manages the singleton ThemeSettings row used across all layouts.
"""
from app import db
from app.models.theme import ThemeSettings
from app.utils.file_handler import save_upload


class ThemeService:

    @staticmethod
    def get_active_theme():
        """Return the theme singleton, creating a sensible default if none exists."""
        theme = ThemeSettings.query.first()
        if not theme:
            theme = ThemeSettings()
            db.session.add(theme)
            db.session.commit()
        return theme

    @staticmethod
    def update_theme(data, files=None, updated_by=None):
        theme = ThemeService.get_active_theme()
        fields = [
            'primary_color', 'secondary_color', 'accent_color', 'bg_color',
            'text_color', 'banner_text_color', 'sidebar_text_color',
            'font_display', 'font_body', 'mode',
        ]
        for field in fields:
            if field in data and data[field]:
                setattr(theme, field, data[field])
        # link_color is optional: an explicit blank means "clear override, use primary".
        if 'link_color' in data:
            theme.link_color = data['link_color'] or None

        if files:
            logo = files.get('logo')
            if logo and logo.filename:
                fname, _, _ = save_upload(logo, 'theme')
                if fname:
                    theme.logo_url = f'/static/uploads/theme/{fname}'
            favicon = files.get('favicon')
            if favicon and favicon.filename:
                fname, _, _ = save_upload(favicon, 'theme')
                if fname:
                    theme.favicon_url = f'/static/uploads/theme/{fname}'

        if updated_by:
            theme.updated_by = updated_by
        db.session.commit()
        return theme
