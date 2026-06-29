"""
Download Service
Manages downloadable resources (books, notes, past papers, etc.).
"""
from sqlalchemy import desc

from app import db
from app.models.download import Download
from app.utils.file_handler import save_upload, delete_upload


class DownloadService:

    CATEGORIES = [
        ('book', 'Books'),
        ('notes', 'Notes'),
        ('assignment', 'Assignments'),
        ('past_paper', 'Past Papers'),
        ('practical', 'Practical Files'),
        ('timetable', 'Timetable'),
        ('prospectus', 'Prospectus'),
        ('admission_form', 'Admission Forms'),
        ('other', 'Other'),
    ]

    @staticmethod
    def get_all(page=1, per_page=20, category=None, department_id=None,
                subject_id=None, search=None):
        q = Download.query.filter_by(is_active=True).order_by(desc(Download.created_at))
        if category:
            q = q.filter_by(category=category)
        if department_id:
            q = q.filter_by(department_id=department_id)
        if subject_id:
            q = q.filter_by(subject_id=subject_id)
        if search:
            like = f'%{search}%'
            q = q.filter(
                db.or_(Download.title.ilike(like), Download.description.ilike(like))
            )
        return q.paginate(page=page, per_page=per_page, error_out=False)

    @staticmethod
    def get_by_id(dl_id):
        return db.session.get(Download, dl_id)

    @staticmethod
    def create(data, file_obj, user_id=None):
        filename, file_path, file_size = save_upload(file_obj, 'downloads')
        if not filename:
            return None
        ext = filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''
        dl = Download(
            title=data['title'],
            description=data.get('description', ''),
            category=data['category'],
            filename=filename,
            original_name=file_obj.filename,
            file_path=file_path,
            file_type=ext,
            file_size=file_size,
            department_id=data.get('department_id'),
            program_id=data.get('program_id'),
            class_id=data.get('class_id'),
            subject_id=data.get('subject_id'),
            sort_order=data.get('sort_order', 0),
            uploaded_by=user_id,
        )
        db.session.add(dl)
        db.session.commit()
        return dl

    @staticmethod
    def update(dl, data):
        for field in ['title', 'description', 'category', 'department_id', 'program_id',
                       'class_id', 'subject_id', 'sort_order', 'is_active']:
            if field in data:
                setattr(dl, field, data[field])
        db.session.commit()
        return dl

    @staticmethod
    def delete(dl):
        delete_upload(dl.file_path)
        db.session.delete(dl)
        db.session.commit()

    @staticmethod
    def increment_download(dl_id):
        dl = db.session.get(Download, dl_id)
        if dl:
            dl.download_count = (dl.download_count or 0) + 1
            db.session.commit()

    @staticmethod
    def count():
        return Download.query.filter_by(is_active=True).count()
