"""
Knowledge Base Service
CRUD for knowledge entries, file uploads, versioning, and AI context retrieval.
"""
from datetime import datetime
from app import db
from app.models.knowledge_base import KnowledgeBase, KnowledgeFile, KnowledgeVersion
from app.utils.helpers import generate_slug
from app.utils.file_handler import save_upload, extract_text_from_file, delete_upload


class KnowledgeService:

    @staticmethod
    def get_all(page=1, per_page=20, search=None, department_id=None, subject_id=None, status=None):
        q = KnowledgeBase.query.order_by(KnowledgeBase.updated_at.desc())
        if search:
            like = f'%{search}%'
            q = q.filter(
                db.or_(
                    KnowledgeBase.title.ilike(like),
                    KnowledgeBase.content.ilike(like),
                    KnowledgeBase.tags.ilike(like),
                )
            )
        if department_id:
            q = q.filter_by(department_id=department_id)
        if subject_id:
            q = q.filter_by(subject_id=subject_id)
        if status:
            q = q.filter_by(status=status)
        return q.paginate(page=page, per_page=per_page, error_out=False)

    @staticmethod
    def get_by_id(kb_id):
        return db.session.get(KnowledgeBase, kb_id)

    @staticmethod
    def create(data, user_id=None):
        kb = KnowledgeBase(
            title=data['title'],
            content=data.get('content', ''),
            department_id=data.get('department_id'),
            program_id=data.get('program_id'),
            batch_id=data.get('batch_id'),
            semester_id=data.get('semester_id'),
            subject_id=data.get('subject_id'),
            chapter=data.get('chapter'),
            topic=data.get('topic'),
            status=data.get('status', 'published'),
            content_type=data.get('content_type', 'text'),
            tags=data.get('tags'),
            created_by=user_id,
        )
        db.session.add(kb)
        db.session.commit()
        return kb

    @staticmethod
    def update(kb, data, user_id=None):
        # Save version before updating
        KnowledgeService._save_version(kb, user_id)

        for field in ['title', 'content', 'department_id', 'program_id', 'batch_id',
                       'semester_id', 'subject_id', 'chapter', 'topic', 'status', 'content_type', 'tags']:
            if field in data:
                setattr(kb, field, data[field])
        kb.version += 1
        db.session.commit()
        return kb

    @staticmethod
    def delete(kb):
        # Delete associated files from disk
        for f in kb.files:
            delete_upload(f.file_path)
        db.session.delete(kb)
        db.session.commit()

    @staticmethod
    def add_file(kb_id, file_obj):
        """Upload a file and attach it to a knowledge entry. Extracts text for AI context."""
        filename, file_path, file_size = save_upload(file_obj, 'knowledge_base')
        if not filename:
            return None
        extracted = extract_text_from_file(file_path)
        ext = filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''
        kf = KnowledgeFile(
            knowledge_id=kb_id,
            filename=filename,
            original_name=file_obj.filename,
            file_path=file_path,
            file_type=ext,
            file_size=file_size,
            extracted_text=extracted,
        )
        db.session.add(kf)
        db.session.commit()
        return kf

    @staticmethod
    def delete_file(file_id):
        kf = db.session.get(KnowledgeFile, file_id)
        if kf:
            delete_upload(kf.file_path)
            db.session.delete(kf)
            db.session.commit()

    @staticmethod
    def get_context_for_student(department_id=None, program_id=None, batch_id=None,
                                 semester_id=None, subject_id=None):
        """Retrieve all relevant knowledge entries for a student's academic context.
        Includes entries at the student's level and all broader scopes. Most
        specific match wins; entries fall back to progressively broader scope:
        subject -> semester -> batch -> program -> department -> institution-wide.
        """
        q = KnowledgeBase.query.filter_by(status='published')

        filters = []

        # Specific subject entries
        if subject_id:
            filters.append(KnowledgeBase.subject_id == subject_id)

        # All entries for the student's semester (any subject in that semester)
        if semester_id:
            filters.append(KnowledgeBase.semester_id == semester_id)

        # Batch-level entries (no semester specified)
        if batch_id:
            filters.append(
                db.and_(KnowledgeBase.batch_id == batch_id, KnowledgeBase.semester_id.is_(None))
            )

        # Program-level entries (no batch specified)
        if program_id:
            filters.append(
                db.and_(KnowledgeBase.program_id == program_id, KnowledgeBase.batch_id.is_(None))
            )

        # Department-level entries (no program specified)
        if department_id:
            filters.append(
                db.and_(KnowledgeBase.department_id == department_id, KnowledgeBase.program_id.is_(None))
            )

        # Institution-wide entries (no scope)
        filters.append(
            db.and_(
                KnowledgeBase.department_id.is_(None), KnowledgeBase.program_id.is_(None),
                KnowledgeBase.batch_id.is_(None), KnowledgeBase.semester_id.is_(None),
                KnowledgeBase.subject_id.is_(None),
            )
        )

        q = q.filter(db.or_(*filters))

        entries = q.all()

        # Build combined context text
        context_parts = []
        resource_files = []
        for entry in entries:
            context_parts.append(f"### {entry.title}\n{entry.content}")
            for f in entry.files:
                if f.extracted_text:
                    context_parts.append(f"[File: {f.original_name}]\n{f.extracted_text}")
                resource_files.append({
                    'id': f.id,
                    'name': f.original_name,
                    'type': f.file_type,
                    'filename': f.filename,
                })

        return '\n\n'.join(context_parts), resource_files

    @staticmethod
    def _save_version(kb, user_id):
        """Snapshot current state before modification."""
        v = KnowledgeVersion(
            knowledge_id=kb.id,
            version_number=kb.version,
            title=kb.title,
            content=kb.content,
            changed_by=user_id,
        )
        db.session.add(v)

    @staticmethod
    def get_versions(kb_id):
        return KnowledgeVersion.query.filter_by(knowledge_id=kb_id).order_by(
            KnowledgeVersion.version_number.desc()
        ).all()

    @staticmethod
    def count():
        return KnowledgeBase.query.filter_by(status='published').count()
