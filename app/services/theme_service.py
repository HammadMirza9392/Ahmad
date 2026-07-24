"""
Theme Service
Manages the singleton ThemeSettings row used across all layouts.
"""
import os
from pathlib import Path

from flask import current_app, url_for

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
    def get_display_logo_url(theme):
        """Return a usable public URL for the theme logo if it exists on disk."""
        if not theme:
            return None

        logo_value = getattr(theme, 'logo_url', None)
        if not logo_value:
            return None

        raw_value = str(logo_value).strip()
        if not raw_value:
            return None

        if raw_value.startswith(('http://', 'https://')):
            return raw_value

        normalized = raw_value.lstrip('/')
        if normalized.startswith('static/'):
            normalized = normalized[len('static/'):]

        if not normalized.startswith('uploads/'):
            normalized = f'uploads/{normalized}'

        static_path = os.path.join(current_app.root_path, 'static', normalized.replace('/', os.sep))
        if os.path.exists(static_path):
            return url_for('static', filename=normalized)

        filename = os.path.basename(normalized)
        upload_root = Path(current_app.config.get('UPLOAD_FOLDER', os.path.join(current_app.root_path, 'static', 'uploads')))
        matches = list(upload_root.rglob(filename))
        if matches:
            resolved_rel = os.path.relpath(matches[0], Path(current_app.root_path, 'static')).replace(os.sep, '/')
            return url_for('static', filename=resolved_rel)

        return None

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
