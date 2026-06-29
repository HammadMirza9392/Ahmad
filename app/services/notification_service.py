"""
Notification Service
Create, target, and deliver notifications to students.
"""
from datetime import datetime
from sqlalchemy import desc

from app import db
from app.models.notification import Notification, UserNotification
from app.models.user import User


class NotificationService:

    @staticmethod
    def create(data, created_by=None):
        notif = Notification(
            title=data['title'],
            content=data['content'],
            notification_type=data['notification_type'],
            target_type=data.get('target_type', 'all'),
            department_id=data.get('department_id'),
            class_id=data.get('class_id'),
            semester=data.get('semester'),
            priority=data.get('priority', 'normal'),
            created_by=created_by,
            expires_at=data.get('expires_at'),
        )
        db.session.add(notif)
        db.session.commit()

        # Distribute to targeted students
        NotificationService._distribute(notif)
        return notif

    @staticmethod
    def _distribute(notif):
        """Create UserNotification records for all targeted students."""
        q = User.query.filter_by(role='student', is_active=True)
        if notif.target_type == 'department' and notif.department_id:
            q = q.filter_by(department_id=notif.department_id)
        elif notif.target_type == 'class' and notif.class_id:
            q = q.filter_by(class_id=notif.class_id)
        elif notif.target_type == 'semester' and notif.semester:
            q = q.filter_by(semester=notif.semester)

        students = q.all()
        for s in students:
            un = UserNotification(user_id=s.id, notification_id=notif.id)
            db.session.add(un)
        db.session.commit()

    @staticmethod
    def get_all(page=1, per_page=20):
        return Notification.query.order_by(desc(Notification.created_at)).paginate(
            page=page, per_page=per_page, error_out=False
        )

    @staticmethod
    def get_by_id(notif_id):
        return db.session.get(Notification, notif_id)

    @staticmethod
    def update(notif, data):
        for field in ['title', 'content', 'notification_type', 'target_type',
                       'department_id', 'class_id', 'semester', 'priority', 'is_active', 'expires_at']:
            if field in data:
                setattr(notif, field, data[field])
        db.session.commit()
        return notif

    @staticmethod
    def delete(notif):
        db.session.delete(notif)
        db.session.commit()

    @staticmethod
    def get_for_user(user_id, unread_only=False):
        q = UserNotification.query.filter_by(user_id=user_id).join(Notification).filter(
            Notification.is_active == True
        ).order_by(desc(Notification.created_at))
        if unread_only:
            q = q.filter(UserNotification.is_read == False)
        return q.all()

    @staticmethod
    def mark_read(user_id, notification_id):
        un = UserNotification.query.filter_by(user_id=user_id, notification_id=notification_id).first()
        if un and not un.is_read:
            un.is_read = True
            un.read_at = datetime.utcnow()
            db.session.commit()

    @staticmethod
    def mark_all_read(user_id):
        UserNotification.query.filter_by(user_id=user_id, is_read=False).update({
            'is_read': True,
            'read_at': datetime.utcnow(),
        })
        db.session.commit()

    @staticmethod
    def unread_count(user_id):
        return UserNotification.query.filter_by(user_id=user_id, is_read=False).join(
            Notification
        ).filter(Notification.is_active == True).count()
