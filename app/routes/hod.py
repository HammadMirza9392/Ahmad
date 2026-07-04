"""
HOD Routes
Department-scoped management for Heads of Department.
Every handler re-derives scope from the DB, never trusting a URL id.
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user

from app import db
from app.utils.decorators import hod_required
from app.utils.scoping import require_department_scope, require_subject_ownership
from app.services.department_service import DepartmentService
from app.services.student_service import StudentService
from app.services.auth_service import AuthService
from app.services.allocation_service import AllocationService
from app.services.quiz_service import QuizService
from app.services.audit_service import AuditService
from app.models.user import User
from app.models.subject import Subject

hod_bp = Blueprint('hod', __name__)


def _dept_id():
    """Resolve the current HOD's department, aborting if none."""
    dept_id = current_user.department_id
    if not dept_id and not current_user.is_admin():
        abort(403)
    return dept_id


# ───────────── DASHBOARD ─────────────

@hod_bp.route('/')
@login_required
@hod_required
def dashboard():
    dept_id = _dept_id()
    dept = DepartmentService.get_by_id(dept_id) if dept_id else None
    teachers = User.query.filter_by(role='teacher', department_id=dept_id).all() if dept_id else []
    students = User.query.filter_by(role='student', department_id=dept_id).count() if dept_id else 0
    subjects = DepartmentService.get_subjects(department_id=dept_id) if dept_id else []
    programs = DepartmentService.get_programs(department_id=dept_id) if dept_id else []
    stats = {
        'teachers': len(teachers),
        'students': students,
        'subjects': len(subjects),
        'programs': len(programs),
    }
    return render_template('hod/dashboard.html', dept=dept, stats=stats,
                           teachers=teachers, subjects=subjects)


# ───────────── TEACHERS ─────────────

@hod_bp.route('/teachers')
@login_required
@hod_required
def teachers():
    dept_id = _dept_id()
    teacher_list = User.query.filter_by(role='teacher', department_id=dept_id).order_by(User.full_name).all()
    return render_template('hod/teachers/index.html', teachers=teacher_list)


@hod_bp.route('/teachers/create', methods=['GET', 'POST'])
@login_required
@hod_required
def teacher_create():
    dept_id = _dept_id()
    if request.method == 'POST':
        data = request.form.to_dict()
        user, error = AuthService.create_user(
            email=data['email'],
            password=data.get('password') or 'Teacher@123',
            full_name=data['full_name'],
            role='teacher',
            phone=data.get('phone'),
            department_id=dept_id,
            is_active=True,
        )
        if error:
            flash(error, 'danger')
        else:
            AuditService.log(current_user.id, 'create_teacher', 'user', user.id, request.remote_addr)
            flash('Teacher created.', 'success')
            return redirect(url_for('hod.teachers'))
    return render_template('hod/teachers/create.html')


@hod_bp.route('/teachers/edit/<int:teacher_id>', methods=['GET', 'POST'])
@login_required
@hod_required
def teacher_edit(teacher_id):
    teacher = db.session.get(User, teacher_id)
    if not teacher or teacher.role != 'teacher':
        flash('Teacher not found.', 'danger')
        return redirect(url_for('hod.teachers'))
    require_department_scope(teacher.department_id)
    if request.method == 'POST':
        data = request.form.to_dict()
        for field in ['full_name', 'phone']:
            if field in data:
                setattr(teacher, field, data[field])
        if data.get('password'):
            teacher.password_hash = AuthService.hash_password(data['password'])
        teacher.is_active = 'is_active' in data
        db.session.commit()
        flash('Teacher updated.', 'success')
        return redirect(url_for('hod.teachers'))
    return render_template('hod/teachers/edit.html', teacher=teacher)


@hod_bp.route('/teachers/delete/<int:teacher_id>', methods=['POST'])
@login_required
@hod_required
def teacher_delete(teacher_id):
    teacher = db.session.get(User, teacher_id)
    if teacher and teacher.role == 'teacher':
        require_department_scope(teacher.department_id)
        AuditService.log(current_user.id, 'delete_teacher', 'user', teacher.id, request.remote_addr)
        db.session.delete(teacher)
        db.session.commit()
        flash('Teacher deleted.', 'success')
    return redirect(url_for('hod.teachers'))


# ───────────── STUDENTS ─────────────

@hod_bp.route('/students')
@login_required
@hod_required
def students():
    dept_id = _dept_id()
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    pagination = StudentService.get_all(page=page, search=search, department_id=dept_id)
    return render_template('hod/students/index.html', pagination=pagination, search=search)


@hod_bp.route('/students/create', methods=['GET', 'POST'])
@login_required
@hod_required
def student_create():
    dept_id = _dept_id()
    if request.method == 'POST':
        data = request.form.to_dict()
        data['department_id'] = dept_id
        data['password'] = data.get('password') or 'Student@123'
        user, error = StudentService.create(data)
        if error:
            flash(error, 'danger')
        else:
            flash('Student created.', 'success')
            return redirect(url_for('hod.students'))
    programs = DepartmentService.get_programs(department_id=dept_id)
    prog_ids = {p.id for p in programs}
    batches = [b for p in programs for b in DepartmentService.get_batches(program_id=p.id)]
    semesters = [s for b in batches for s in DepartmentService.get_semesters(batch_id=b.id)]
    return render_template('hod/students/create.html', programs=programs, batches=batches, semesters=semesters)


@hod_bp.route('/students/edit/<int:student_id>', methods=['GET', 'POST'])
@login_required
@hod_required
def student_edit(student_id):
    student = StudentService.get_by_id(student_id)
    if not student:
        flash('Student not found.', 'danger')
        return redirect(url_for('hod.students'))
    require_department_scope(student.department_id)
    if request.method == 'POST':
        data = request.form.to_dict()
        data['department_id'] = current_user.department_id or student.department_id
        _, error = StudentService.update(student, data)
        if error:
            flash(error, 'danger')
        else:
            flash('Student updated.', 'success')
            return redirect(url_for('hod.students'))
    dept_id = _dept_id()
    programs = DepartmentService.get_programs(department_id=dept_id)
    batches = [b for p in programs for b in DepartmentService.get_batches(program_id=p.id)]
    semesters = [s for b in batches for s in DepartmentService.get_semesters(batch_id=b.id)]
    return render_template('hod/students/edit.html', student=student, programs=programs,
                           batches=batches, semesters=semesters)


@hod_bp.route('/students/delete/<int:student_id>', methods=['POST'])
@login_required
@hod_required
def student_delete(student_id):
    student = StudentService.get_by_id(student_id)
    if student:
        require_department_scope(student.department_id)
        StudentService.delete(student)
        flash('Student deleted.', 'success')
    return redirect(url_for('hod.students'))


@hod_bp.route('/students/<int:student_id>/promote', methods=['POST'])
@login_required
@hod_required
def student_promote(student_id):
    from app.services.allocation_service import AllocationService
    student = StudentService.get_by_id(student_id)
    if not student:
        flash('Student not found.', 'danger')
        return redirect(url_for('hod.students'))
    require_department_scope(student.department_id)
    success, message = AllocationService.promote_student(student)
    flash(message, 'success' if success else 'info')
    return redirect(url_for('hod.students'))


# ───────────── PROGRAMS / CLASSES / SUBJECTS (scoped) ─────────────

@hod_bp.route('/programs')
@login_required
@hod_required
def programs():
    dept_id = _dept_id()
    progs = DepartmentService.get_programs(department_id=dept_id)
    return render_template('hod/programs/index.html', programs=progs)


@hod_bp.route('/programs/create', methods=['GET', 'POST'])
@login_required
@hod_required
def program_create():
    dept_id = _dept_id()
    if request.method == 'POST':
        data = request.form.to_dict()
        data['department_id'] = dept_id
        DepartmentService.create_program(data)
        flash('Program created.', 'success')
        return redirect(url_for('hod.programs'))
    return render_template('hod/programs/create.html')


@hod_bp.route('/batches')
@login_required
@hod_required
def batches():
    dept_id = _dept_id()
    progs = DepartmentService.get_programs(department_id=dept_id)
    prog_ids = {p.id for p in progs}
    batch_list = [b for b in DepartmentService.get_batches() if b.program_id in prog_ids]
    return render_template('hod/batches/index.html', batches=batch_list, programs=progs)


@hod_bp.route('/batches/create', methods=['GET', 'POST'])
@login_required
@hod_required
def batch_create():
    dept_id = _dept_id()
    progs = DepartmentService.get_programs(department_id=dept_id)
    if request.method == 'POST':
        data = request.form.to_dict()
        prog = DepartmentService.get_program_by_id(int(data['program_id']))
        if not prog or prog.department_id != dept_id:
            abort(403)
        DepartmentService.create_batch(data)
        flash('Batch created.', 'success')
        return redirect(url_for('hod.batches'))
    return render_template('hod/batches/create.html', programs=progs)


@hod_bp.route('/batches/edit/<int:batch_id>', methods=['GET', 'POST'])
@login_required
@hod_required
def batch_edit(batch_id):
    dept_id = _dept_id()
    batch = DepartmentService.get_batch_by_id(batch_id)
    if not batch or batch.program.department_id != dept_id:
        flash('Batch not found.', 'danger')
        return redirect(url_for('hod.batches'))
    if request.method == 'POST':
        data = request.form.to_dict()
        prog = DepartmentService.get_program_by_id(int(data['program_id']))
        if not prog or prog.department_id != dept_id:
            abort(403)
        DepartmentService.update_batch(batch, data)
        flash('Batch updated.', 'success')
        return redirect(url_for('hod.batches'))
    progs = DepartmentService.get_programs(department_id=dept_id)
    return render_template('hod/batches/edit.html', batch=batch, programs=progs)


@hod_bp.route('/batches/delete/<int:batch_id>', methods=['POST'])
@login_required
@hod_required
def batch_delete(batch_id):
    dept_id = _dept_id()
    batch = DepartmentService.get_batch_by_id(batch_id)
    if batch and batch.program.department_id == dept_id:
        DepartmentService.delete_batch(batch)
        flash('Batch deleted.', 'success')
    return redirect(url_for('hod.batches'))


@hod_bp.route('/semesters')
@login_required
@hod_required
def semesters():
    dept_id = _dept_id()
    progs = DepartmentService.get_programs(department_id=dept_id)
    prog_ids = {p.id for p in progs}
    batch_list = [b for b in DepartmentService.get_batches() if b.program_id in prog_ids]
    batch_ids = {b.id for b in batch_list}
    sem_list = [s for s in DepartmentService.get_semesters() if s.batch_id in batch_ids]
    return render_template('hod/semesters/index.html', semesters=sem_list, batches=batch_list)


@hod_bp.route('/semesters/create', methods=['GET', 'POST'])
@login_required
@hod_required
def semester_create():
    dept_id = _dept_id()
    progs = DepartmentService.get_programs(department_id=dept_id)
    prog_ids = {p.id for p in progs}
    batch_list = [b for b in DepartmentService.get_batches() if b.program_id in prog_ids]
    if request.method == 'POST':
        data = request.form.to_dict()
        batch = DepartmentService.get_batch_by_id(int(data['batch_id']))
        if not batch or batch.program_id not in prog_ids:
            abort(403)
        DepartmentService.create_semester(data)
        flash('Semester created.', 'success')
        return redirect(url_for('hod.semesters'))
    return render_template('hod/semesters/create.html', batches=batch_list)


@hod_bp.route('/semesters/edit/<int:sem_id>', methods=['GET', 'POST'])
@login_required
@hod_required
def semester_edit(sem_id):
    dept_id = _dept_id()
    sem = DepartmentService.get_semester_by_id(sem_id)
    if not sem or sem.batch.program.department_id != dept_id:
        flash('Semester not found.', 'danger')
        return redirect(url_for('hod.semesters'))
    if request.method == 'POST':
        data = request.form.to_dict()
        batch = DepartmentService.get_batch_by_id(int(data['batch_id']))
        if not batch or batch.program.department_id != dept_id:
            abort(403)
        DepartmentService.update_semester(sem, data)
        flash('Semester updated.', 'success')
        return redirect(url_for('hod.semesters'))
    progs = DepartmentService.get_programs(department_id=dept_id)
    prog_ids = {p.id for p in progs}
    batch_list = [b for b in DepartmentService.get_batches() if b.program_id in prog_ids]
    return render_template('hod/semesters/edit.html', sem=sem, batches=batch_list)


@hod_bp.route('/semesters/delete/<int:sem_id>', methods=['POST'])
@login_required
@hod_required
def semester_delete(sem_id):
    dept_id = _dept_id()
    sem = DepartmentService.get_semester_by_id(sem_id)
    if sem and sem.batch.program.department_id == dept_id:
        DepartmentService.delete_semester(sem)
        flash('Semester deleted.', 'success')
    return redirect(url_for('hod.semesters'))


@hod_bp.route('/subjects')
@login_required
@hod_required
def subjects():
    dept_id = _dept_id()
    subjs = DepartmentService.get_subjects(department_id=dept_id)
    teacher_list = User.query.filter_by(role='teacher', department_id=dept_id).all()
    return render_template('hod/subjects/index.html', subjects=subjs, teachers=teacher_list)


@hod_bp.route('/subjects/create', methods=['GET', 'POST'])
@login_required
@hod_required
def subject_create():
    dept_id = _dept_id()
    progs = DepartmentService.get_programs(department_id=dept_id)
    prog_ids = {p.id for p in progs}
    batch_list = [b for b in DepartmentService.get_batches() if b.program_id in prog_ids]
    batch_ids = {b.id for b in batch_list}
    sem_list = [s for s in DepartmentService.get_semesters() if s.batch_id in batch_ids]
    teacher_list = User.query.filter_by(role='teacher', department_id=dept_id).order_by(User.full_name).all()
    if request.method == 'POST':
        data = request.form.to_dict()
        data['department_id'] = dept_id
        DepartmentService.create_subject(data)
        flash('Subject created.', 'success')
        return redirect(url_for('hod.subjects'))
    return render_template('hod/subjects/create.html', semesters=sem_list, teachers=teacher_list)


@hod_bp.route('/subjects/assign-teacher/<int:subject_id>', methods=['POST'])
@login_required
@hod_required
def subject_assign_teacher(subject_id):
    subject = require_subject_ownership(subject_id)
    teacher_id = request.form.get('teacher_id', type=int)
    if teacher_id:
        teacher = db.session.get(User, teacher_id)
        if not teacher or teacher.role != 'teacher' or teacher.department_id != subject.department_id:
            abort(403)
        subject.teacher_id = teacher_id
    else:
        subject.teacher_id = None
    db.session.commit()
    AuditService.log(current_user.id, 'assign_teacher', 'subject', subject.id, request.remote_addr)
    flash('Teacher assignment updated.', 'success')
    return redirect(url_for('hod.subjects'))


# ───────────── QUIZ ACTIVITY / REPORTS ─────────────

@hod_bp.route('/quiz-activity')
@login_required
@hod_required
def quiz_activity():
    dept_id = _dept_id()
    rows = QuizService.department_activity(dept_id) if dept_id else []
    return render_template('hod/quiz_activity.html', rows=rows)


@hod_bp.route('/reports')
@login_required
@hod_required
def reports():
    dept_id = _dept_id()
    rows = QuizService.department_activity(dept_id) if dept_id else []
    dept = DepartmentService.get_by_id(dept_id) if dept_id else None
    return render_template('hod/reports.html', rows=rows, dept=dept)
