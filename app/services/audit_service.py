"""
Audit Service
Thin wrapper over the existing AuditLog model for sensitive actions.
"""
from app import db
from app.models.log import AuditLog


class AuditService:

    @staticmethod
    def log(user_id, action, entity=None, entity_id=None, ip_address=None, details=None):
        """Record a sensitive action. Best-effort; never breaks the caller."""
        try:
            entry = AuditLog(
                user_id=user_id,
                action=action,
                resource_type=entity,
                resource_id=entity_id,
                ip_address=ip_address,
                details=details,
            )
            db.session.add(entry)
            db.session.commit()
        except Exception:
            db.session.rollback()
