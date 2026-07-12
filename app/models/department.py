"""
Department Model
Academic departments within the institution.
"""
from datetime import datetime
from app import db


class Department(db.Model):
    __tablename__ = 'departments'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    slug = db.Column(db.String(255), unique=True, nullable=False, index=True)
    description = db.Column(db.Text)
    image = db.Column(db.String(500))

    # Leadership
    hod_name = db.Column(db.String(255))
    hod_image = db.Column(db.String(500))
    hod_message = db.Column(db.Text)
    hod_email = db.Column(db.String(255))
    hod_phone = db.Column(db.String(50))

    # Real access-control link to the HOD user account (distinct from public display fields above).
    # use_alter breaks the departments<->users circular FK dependency (users.department_id also
    # points back at departments) so DDL tools can create/drop these tables without a cycle error.
    hod_user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL', use_alter=True,
                                                       name='fk_departments_hod_user_id'), nullable=True)

    # Display
    sort_order = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    # NOTE: no ORM-level delete-orphan cascade on programs/subjects — both can be reassigned to a
    # different department (see DepartmentService.update_program/update_subject), and delete-orphan
    # would delete the row the moment it's disassociated from its current department. Deleting the
    # department itself is instead handled explicitly (see DepartmentService.delete /
    # app.utils.cascade) plus, on Postgres, at the DB level via each FK's ondelete='CASCADE'.
    programs = db.relationship('Program', backref='department', lazy=True)
    subjects = db.relationship('Subject', backref='department', lazy=True)
    hod = db.relationship('User', foreign_keys=[hod_user_id], backref='headed_department')

    def __repr__(self):
        return f'<Department {self.name}>'
