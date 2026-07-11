"""
Admin Routes
All admin panel routes — dashboard, CRUD, settings.
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user

from app import db
from app.models.subject import Subject
from app.utils.decorators import admin_required, super_admin_required
from app.controllers.admin_controller import AdminController
from app.services.department_service import DepartmentService
from app.services.student_service import StudentService
from app.services.knowledge_service import KnowledgeService
from app.services.ai_service import AIService
from app.services.notification_service import NotificationService
from app.services.download_service import DownloadService
from app.services.cms_service import CMSService
from app.services.chat_service import ChatService
from app.services.analytics_service import AnalyticsService
from app.utils.file_handler import save_upload

admin_bp = Blueprint('admin', __name__)


# ───────────── DASHBOARD ─────────────

@admin_bp.route('/')
@login_required
@admin_required
def dashboard():
    data = AdminController.get_dashboard_data()
    return render_template('admin/dashboard/index.html', **data)


# ───────────── INSTITUTION ─────────────

@admin_bp.route('/institution', methods=['GET', 'POST'])
@login_required
@admin_required
def institution():
    inst = AdminController.get_institution()
    if request.method == 'POST':
        data = request.form.to_dict()
        AdminController.update_institution(data, request.files)
        flash('Institution updated successfully.', 'success')
        return redirect(url_for('admin.institution'))
    return render_template('admin/institution/index.html', inst=inst)


# ───────────── CMS PAGES ─────────────

@admin_bp.route('/cms')
@login_required
@admin_required
def cms_pages():
    pages = CMSService.get_all_pages()
    return render_template('admin/cms/index.html', pages=pages)


@admin_bp.route('/cms/edit/<int:page_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def cms_edit(page_id):
    page = CMSService.get_by_id(page_id)
    if not page:
        flash('Page not found.', 'danger')
        return redirect(url_for('admin.cms_pages'))
    if request.method == 'POST':
        data = request.form.to_dict()
        data['is_published'] = 'is_published' in data
        data['show_in_menu'] = 'show_in_menu' in data
        banner = request.files.get('banner_image')
        if banner and banner.filename:
            fname, path, size = save_upload(banner, 'cms')
            if fname:
                data['banner_image'] = f'/static/uploads/cms/{fname}'
        CMSService.update_page(page, data)
        flash('Page updated.', 'success')
        return redirect(url_for('admin.cms_pages'))
    return render_template('admin/cms/edit.html', page=page)


@admin_bp.route('/cms/create', methods=['GET', 'POST'])
@login_required
@admin_required
def cms_create():
    if request.method == 'POST':
        data = request.form.to_dict()
        CMSService.create_page(data, current_user.id)
        flash('Page created.', 'success')
        return redirect(url_for('admin.cms_pages'))
    return render_template('admin/cms/create.html')


@admin_bp.route('/cms/delete/<int:page_id>', methods=['POST'])
@login_required
@admin_required
def cms_delete(page_id):
    page = CMSService.get_by_id(page_id)
    if page:
        CMSService.delete_page(page)
        flash('Page deleted.', 'success')
    return redirect(url_for('admin.cms_pages'))


# ───────────── DEPARTMENTS ─────────────

@admin_bp.route('/departments')
@login_required
@admin_required
def departments():
    depts = DepartmentService.get_all()
    return render_template('admin/departments/index.html', departments=depts)


@admin_bp.route('/departments/create', methods=['GET', 'POST'])
@login_required
@admin_required
def department_create():
    if request.method == 'POST':
        data = request.form.to_dict()
        image = request.files.get('image')
        if image and image.filename:
            fname, path, size = save_upload(image, 'departments')
            if fname:
                data['image'] = f'/static/uploads/departments/{fname}'
        DepartmentService.create(data)
        flash('Department created.', 'success')
        return redirect(url_for('admin.departments'))
    return render_template('admin/departments/create.html')


@admin_bp.route('/departments/edit/<int:dept_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def department_edit(dept_id):
    dept = DepartmentService.get_by_id(dept_id)
    if not dept:
        flash('Department not found.', 'danger')
        return redirect(url_for('admin.departments'))
    if request.method == 'POST':
        data = request.form.to_dict()
        image = request.files.get('image')
        if image and image.filename:
            fname, path, size = save_upload(image, 'departments')
            if fname:
                data['image'] = f'/static/uploads/departments/{fname}'
        DepartmentService.update(dept, data)
        flash('Department updated.', 'success')
        return redirect(url_for('admin.departments'))
    return render_template('admin/departments/edit.html', dept=dept)


@admin_bp.route('/departments/delete/<int:dept_id>', methods=['POST'])
@login_required
@admin_required
def department_delete(dept_id):
    dept = DepartmentService.get_by_id(dept_id)
    if dept:
        DepartmentService.delete(dept)
        flash('Department deleted.', 'success')
    return redirect(url_for('admin.departments'))


# ───────────── PROGRAMS ─────────────

@admin_bp.route('/programs')
@login_required
@admin_required
def programs():
    progs = DepartmentService.get_programs()
    depts = DepartmentService.get_all()
    return render_template('admin/programs/index.html', programs=progs, departments=depts)


@admin_bp.route('/programs/create', methods=['GET', 'POST'])
@login_required
@admin_required
def program_create():
    if request.method == 'POST':
        DepartmentService.create_program(request.form.to_dict())
        flash('Program created.', 'success')
        return redirect(url_for('admin.programs'))
    depts = DepartmentService.get_all()
    return render_template('admin/programs/create.html', departments=depts)


@admin_bp.route('/programs/edit/<int:prog_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def program_edit(prog_id):
    prog = DepartmentService.get_program_by_id(prog_id)
    if not prog:
        flash('Program not found.', 'danger')
        return redirect(url_for('admin.programs'))
    if request.method == 'POST':
        DepartmentService.update_program(prog, request.form.to_dict())
        flash('Program updated.', 'success')
        return redirect(url_for('admin.programs'))
    depts = DepartmentService.get_all()
    return render_template('admin/programs/edit.html', prog=prog, departments=depts)


@admin_bp.route('/programs/delete/<int:prog_id>', methods=['POST'])
@login_required
@admin_required
def program_delete(prog_id):
    prog = DepartmentService.get_program_by_id(prog_id)
    if prog:
        DepartmentService.delete_program(prog)
        flash('Program deleted.', 'success')
    return redirect(url_for('admin.programs'))


# ───────────── BATCHES ─────────────

@admin_bp.route('/batches')
@login_required
@admin_required
def batches():
    batch_list = DepartmentService.get_batches()
    progs = DepartmentService.get_programs()
    return render_template('admin/batches/index.html', batches=batch_list, programs=progs)


@admin_bp.route('/batches/create', methods=['GET', 'POST'])
@login_required
@admin_required
def batch_create():
    if request.method == 'POST':
        DepartmentService.create_batch(request.form.to_dict())
        flash('Batch created.', 'success')
        return redirect(url_for('admin.batches'))
    progs = DepartmentService.get_programs()
    return render_template('admin/batches/create.html', programs=progs)


@admin_bp.route('/batches/edit/<int:batch_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def batch_edit(batch_id):
    batch = DepartmentService.get_batch_by_id(batch_id)
    if not batch:
        flash('Batch not found.', 'danger')
        return redirect(url_for('admin.batches'))
    if request.method == 'POST':
        DepartmentService.update_batch(batch, request.form.to_dict())
        flash('Batch updated.', 'success')
        return redirect(url_for('admin.batches'))
    progs = DepartmentService.get_programs()
    return render_template('admin/batches/edit.html', batch=batch, programs=progs)


@admin_bp.route('/batches/delete/<int:batch_id>', methods=['POST'])
@login_required
@admin_required
def batch_delete(batch_id):
    batch = DepartmentService.get_batch_by_id(batch_id)
    if batch:
        DepartmentService.delete_batch(batch)
        flash('Batch deleted.', 'success')
    return redirect(url_for('admin.batches'))


# ───────────── SEMESTERS ─────────────

@admin_bp.route('/semesters')
@login_required
@admin_required
def semesters():
    sem_list = DepartmentService.get_semesters()
    batch_list = DepartmentService.get_batches()
    return render_template('admin/semesters/index.html', semesters=sem_list, batches=batch_list)


@admin_bp.route('/semesters/create', methods=['GET', 'POST'])
@login_required
@admin_required
def semester_create():
    if request.method == 'POST':
        DepartmentService.create_semester(request.form.to_dict())
        flash('Semester created.', 'success')
        return redirect(url_for('admin.semesters'))
    batch_list = DepartmentService.get_batches()
    return render_template('admin/semesters/create.html', batches=batch_list)


@admin_bp.route('/semesters/edit/<int:sem_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def semester_edit(sem_id):
    sem = DepartmentService.get_semester_by_id(sem_id)
    if not sem:
        flash('Semester not found.', 'danger')
        return redirect(url_for('admin.semesters'))
    if request.method == 'POST':
        DepartmentService.update_semester(sem, request.form.to_dict())
        flash('Semester updated.', 'success')
        return redirect(url_for('admin.semesters'))
    batch_list = DepartmentService.get_batches()
    return render_template('admin/semesters/edit.html', sem=sem, batches=batch_list)


@admin_bp.route('/semesters/delete/<int:sem_id>', methods=['POST'])
@login_required
@admin_required
def semester_delete(sem_id):
    sem = DepartmentService.get_semester_by_id(sem_id)
    if sem:
        DepartmentService.delete_semester(sem)
        flash('Semester deleted.', 'success')
    return redirect(url_for('admin.semesters'))


# ───────────── SUBJECTS ─────────────

@admin_bp.route('/subjects')
@login_required
@admin_required
def subjects():
    subjs = DepartmentService.get_subjects()
    depts = DepartmentService.get_all()
    return render_template('admin/subjects/index.html', subjects=subjs, departments=depts)


@admin_bp.route('/subjects/create', methods=['GET', 'POST'])
@login_required
@admin_required
def subject_create():
    from app.models.user import User
    if request.method == 'POST':
        DepartmentService.create_subject(request.form.to_dict())
        flash('Subject created.', 'success')
        return redirect(url_for('admin.subjects'))
    depts = DepartmentService.get_all()
    teachers = User.query.filter_by(role='teacher').order_by(User.full_name).all()
    return render_template('admin/subjects/create.html', departments=depts, teachers=teachers)


@admin_bp.route('/subjects/edit/<int:subj_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def subject_edit(subj_id):
    from app.models.user import User
    subj = DepartmentService.get_subject_by_id(subj_id)
    if not subj:
        flash('Subject not found.', 'danger')
        return redirect(url_for('admin.subjects'))
    if request.method == 'POST':
        DepartmentService.update_subject(subj, request.form.to_dict())
        flash('Subject updated.', 'success')
        return redirect(url_for('admin.subjects'))
    depts = DepartmentService.get_all()
    teachers = User.query.filter_by(role='teacher').order_by(User.full_name).all()
    return render_template('admin/subjects/edit.html', subj=subj, departments=depts, teachers=teachers)


@admin_bp.route('/subjects/delete/<int:subj_id>', methods=['POST'])
@login_required
@admin_required
def subject_delete(subj_id):
    subj = DepartmentService.get_subject_by_id(subj_id)
    if subj:
        DepartmentService.delete_subject(subj)
        flash('Subject deleted.', 'success')
    return redirect(url_for('admin.subjects'))


# ───────────── TEACHERS ─────────────

@admin_bp.route('/teachers')
@login_required
@admin_required
def teachers():
    from app.models.user import User
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    dept_id = request.args.get('department_id', type=int)
    q = User.query.filter_by(role='teacher').order_by(User.full_name)
    if search:
        like = f'%{search}%'
        q = q.filter(db.or_(User.full_name.ilike(like), User.email.ilike(like)))
    if dept_id:
        q = q.filter_by(department_id=dept_id)
    pagination = q.paginate(page=page, per_page=20, error_out=False)
    depts = DepartmentService.get_all()
    return render_template('admin/teachers/index.html', pagination=pagination, departments=depts,
                           search=search, dept_id=dept_id)


@admin_bp.route('/teachers/create', methods=['GET', 'POST'])
@login_required
@admin_required
def teacher_create():
    from app.services.auth_service import AuthService
    if request.method == 'POST':
        data = request.form.to_dict()
        user, error = AuthService.create_user(
            email=data['email'],
            password=data.get('password') or 'Teacher@123',
            full_name=data['full_name'],
            role='teacher',
            phone=data.get('phone'),
            department_id=data.get('department_id') or None,
            is_active=True,
        )
        if error:
            flash(error, 'danger')
        else:
            flash('Teacher created.', 'success')
            return redirect(url_for('admin.teachers'))
    depts = DepartmentService.get_all()
    return render_template('admin/teachers/create.html', departments=depts)


@admin_bp.route('/teachers/edit/<int:teacher_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def teacher_edit(teacher_id):
    from app.models.user import User
    from app.services.auth_service import AuthService
    teacher = db.session.get(User, teacher_id)
    if not teacher or teacher.role != 'teacher':
        flash('Teacher not found.', 'danger')
        return redirect(url_for('admin.teachers'))
    if request.method == 'POST':
        data = request.form.to_dict()
        for field in ['full_name', 'phone']:
            if field in data:
                setattr(teacher, field, data[field])
        if 'department_id' in data:
            teacher.department_id = int(data['department_id']) if data['department_id'] else None
        if data.get('password'):
            teacher.password_hash = AuthService.hash_password(data['password'])
        teacher.is_active = 'is_active' in data
        db.session.commit()
        flash('Teacher updated.', 'success')
        return redirect(url_for('admin.teacher_edit', teacher_id=teacher.id))
    depts = DepartmentService.get_all()
    semesters = DepartmentService.get_semesters()
    assigned_subjects = DepartmentService.get_subjects(department_id=None)
    assigned_subjects = [s for s in assigned_subjects if s.teacher_id == teacher.id]
    return render_template('admin/teachers/edit.html', teacher=teacher, departments=depts,
                           semesters=semesters, assigned_subjects=assigned_subjects)


@admin_bp.route('/teachers/delete/<int:teacher_id>', methods=['POST'])
@login_required
@admin_required
def teacher_delete(teacher_id):
    from app.models.user import User
    teacher = db.session.get(User, teacher_id)
    if teacher and teacher.role == 'teacher':
        Subject.query.filter_by(teacher_id=teacher.id).update({'teacher_id': None})
        db.session.delete(teacher)
        db.session.commit()
        flash('Teacher deleted.', 'success')
    return redirect(url_for('admin.teachers'))


@admin_bp.route('/teachers/<int:teacher_id>/assign-semester', methods=['POST'])
@login_required
@admin_required
def teacher_assign_semester(teacher_id):
    """Assign a teacher to every subject in a given semester (within their own department)."""
    from app.models.user import User
    teacher = db.session.get(User, teacher_id)
    if not teacher or teacher.role != 'teacher':
        flash('Teacher not found.', 'danger')
        return redirect(url_for('admin.teachers'))
    semester_id = request.form.get('semester_id', type=int)
    if not semester_id:
        flash('Please select a semester.', 'danger')
        return redirect(url_for('admin.teacher_edit', teacher_id=teacher.id))
    subjects = DepartmentService.get_subjects(semester_id=semester_id)
    if teacher.department_id:
        subjects = [s for s in subjects if s.department_id == teacher.department_id]
    if not subjects:
        flash('No subjects found in that semester for this teacher\'s department.', 'warning')
        return redirect(url_for('admin.teacher_edit', teacher_id=teacher.id))
    for subj in subjects:
        subj.teacher_id = teacher.id
    db.session.commit()
    flash(f'Assigned {teacher.full_name} to {len(subjects)} subject(s) in that semester.', 'success')
    return redirect(url_for('admin.teacher_edit', teacher_id=teacher.id))


@admin_bp.route('/teachers/<int:teacher_id>/unassign-subject/<int:subject_id>', methods=['POST'])
@login_required
@admin_required
def teacher_unassign_subject(teacher_id, subject_id):
    subj = DepartmentService.get_subject_by_id(subject_id)
    if subj and subj.teacher_id == teacher_id:
        subj.teacher_id = None
        db.session.commit()
        flash('Subject unassigned.', 'success')
    return redirect(url_for('admin.teacher_edit', teacher_id=teacher_id))


# ───────────── STUDENTS ─────────────

@admin_bp.route('/students')
@login_required
@admin_required
def students():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    dept_id = request.args.get('department_id', type=int)
    pagination = StudentService.get_all(page=page, search=search, department_id=dept_id)
    depts = DepartmentService.get_all()
    return render_template('admin/students/index.html', pagination=pagination, departments=depts, search=search)


@admin_bp.route('/students/create', methods=['GET', 'POST'])
@login_required
@admin_required
def student_create():
    if request.method == 'POST':
        data = request.form.to_dict()
        data['password'] = data.get('password', 'Student@123')
        user, error = StudentService.create(data)
        if error:
            flash(error, 'danger')
        else:
            flash('Student created.', 'success')
            return redirect(url_for('admin.students'))
    depts = DepartmentService.get_all()
    return render_template('admin/students/create.html', departments=depts)


@admin_bp.route('/students/edit/<int:student_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def student_edit(student_id):
    student = StudentService.get_by_id(student_id)
    if not student:
        flash('Student not found.', 'danger')
        return redirect(url_for('admin.students'))
    if request.method == 'POST':
        data = request.form.to_dict()
        _, error = StudentService.update(student, data)
        if error:
            flash(error, 'danger')
        else:
            flash('Student updated.', 'success')
            return redirect(url_for('admin.student_edit', student_id=student.id))
    depts = DepartmentService.get_all()
    return render_template('admin/students/edit.html', student=student, departments=depts)


@admin_bp.route('/students/delete/<int:student_id>', methods=['POST'])
@login_required
@admin_required
def student_delete(student_id):
    student = StudentService.get_by_id(student_id)
    if student:
        StudentService.delete(student)
        flash('Student deleted.', 'success')
    return redirect(url_for('admin.students'))


@admin_bp.route('/students/<int:student_id>/promote', methods=['POST'])
@login_required
@admin_required
def student_promote(student_id):
    from app.services.allocation_service import AllocationService
    student = StudentService.get_by_id(student_id)
    if not student:
        flash('Student not found.', 'danger')
        return redirect(url_for('admin.students'))
    success, message = AllocationService.promote_student(student)
    flash(message, 'success' if success else 'info')
    return redirect(url_for('admin.students'))


@admin_bp.route('/students/import', methods=['POST'])
@login_required
@admin_required
def student_import():
    file = request.files.get('file')
    if not file or not file.filename.endswith('.csv'):
        flash('Please upload a CSV file.', 'danger')
        return redirect(url_for('admin.students'))
    dept_id = request.form.get('department_id', type=int)
    prog_id = request.form.get('program_id', type=int)
    batch_id = request.form.get('batch_id', type=int)
    semester_id = request.form.get('semester_id', type=int)
    success, errors = StudentService.import_from_csv(file.stream, dept_id, prog_id, batch_id, semester_id)
    flash(f'Imported {success} students. {len(errors)} errors.', 'info')
    for e in errors[:10]:
        flash(e, 'warning')
    return redirect(url_for('admin.students'))


@admin_bp.route('/students/export')
@login_required
@admin_required
def student_export():
    from flask import Response
    csv_data = StudentService.export_to_csv()
    return Response(csv_data, mimetype='text/csv',
                    headers={'Content-Disposition': 'attachment;filename=students_export.csv'})


# ───────────── KNOWLEDGE BASE ─────────────

@admin_bp.route('/knowledge-base')
@login_required
@admin_required
def knowledge_base():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    pagination = KnowledgeService.get_all(page=page, search=search)
    return render_template('admin/knowledge_base/index.html', pagination=pagination, search=search)


@admin_bp.route('/knowledge-base/create', methods=['GET', 'POST'])
@login_required
@admin_required
def knowledge_create():
    if request.method == 'POST':
        data = request.form.to_dict()
        kb = KnowledgeService.create(data, current_user.id)
        files = request.files.getlist('files')
        for f in files:
            if f and f.filename:
                KnowledgeService.add_file(kb.id, f)
        flash('Knowledge entry created.', 'success')
        return redirect(url_for('admin.knowledge_base'))
    depts = DepartmentService.get_all()
    return render_template('admin/knowledge_base/create.html', departments=depts)


@admin_bp.route('/knowledge-base/edit/<int:kb_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def knowledge_edit(kb_id):
    kb = KnowledgeService.get_by_id(kb_id)
    if not kb:
        flash('Entry not found.', 'danger')
        return redirect(url_for('admin.knowledge_base'))
    if request.method == 'POST':
        data = request.form.to_dict()
        KnowledgeService.update(kb, data, current_user.id)
        files = request.files.getlist('files')
        for f in files:
            if f and f.filename:
                KnowledgeService.add_file(kb.id, f)
        flash('Knowledge entry updated.', 'success')
        return redirect(url_for('admin.knowledge_base'))
    depts = DepartmentService.get_all()
    return render_template('admin/knowledge_base/edit.html', kb=kb, departments=depts)


@admin_bp.route('/knowledge-base/delete/<int:kb_id>', methods=['POST'])
@login_required
@admin_required
def knowledge_delete(kb_id):
    kb = KnowledgeService.get_by_id(kb_id)
    if kb:
        KnowledgeService.delete(kb)
        flash('Knowledge entry deleted.', 'success')
    return redirect(url_for('admin.knowledge_base'))


@admin_bp.route('/knowledge-base/file/delete/<int:file_id>', methods=['POST'])
@login_required
@admin_required
def knowledge_file_delete(file_id):
    KnowledgeService.delete_file(file_id)
    flash('File deleted.', 'success')
    return redirect(request.referrer or url_for('admin.knowledge_base'))


# ───────────── DOWNLOADS ─────────────

@admin_bp.route('/downloads')
@login_required
@admin_required
def downloads():
    page = request.args.get('page', 1, type=int)
    pagination = DownloadService.get_all(page=page)
    return render_template('admin/downloads/index.html', pagination=pagination)


@admin_bp.route('/downloads/create', methods=['GET', 'POST'])
@login_required
@admin_required
def download_create():
    if request.method == 'POST':
        data = request.form.to_dict()
        file = request.files.get('file')
        if not file or not file.filename:
            flash('Please upload a file.', 'danger')
        else:
            dl = DownloadService.create(data, file, current_user.id)
            if dl:
                flash('Download created.', 'success')
                return redirect(url_for('admin.downloads'))
            flash('Upload failed.', 'danger')
    depts = DepartmentService.get_all()
    categories = DownloadService.CATEGORIES
    return render_template('admin/downloads/create.html', departments=depts, categories=categories)


@admin_bp.route('/downloads/delete/<int:dl_id>', methods=['POST'])
@login_required
@admin_required
def download_delete(dl_id):
    dl = DownloadService.get_by_id(dl_id)
    if dl:
        DownloadService.delete(dl)
        flash('Download deleted.', 'success')
    return redirect(url_for('admin.downloads'))


# ───────────── GALLERY ─────────────

@admin_bp.route('/gallery')
@login_required
@admin_required
def gallery():
    albums = CMSService.get_albums(active_only=False)
    return render_template('admin/gallery/index.html', albums=albums)


# ───────────── EVENTS ─────────────

@admin_bp.route('/events')
@login_required
@admin_required
def events():
    page = request.args.get('page', 1, type=int)
    pagination = CMSService.get_events(page=page, active_only=False)
    return render_template('admin/events/index.html', pagination=pagination)


@admin_bp.route('/events/create', methods=['GET', 'POST'])
@login_required
@admin_required
def event_create():
    if request.method == 'POST':
        data = request.form.to_dict()
        image = request.files.get('image')
        if image and image.filename:
            fname, path, size = save_upload(image, 'gallery')
            if fname:
                data['image'] = f'/static/uploads/gallery/{fname}'
        CMSService.create_event(data, current_user.id)
        flash('Event created.', 'success')
        return redirect(url_for('admin.events'))
    depts = DepartmentService.get_all()
    return render_template('admin/events/create.html', departments=depts)


# ───────────── NEWS ─────────────

@admin_bp.route('/news')
@login_required
@admin_required
def news():
    page = request.args.get('page', 1, type=int)
    pagination = CMSService.get_news(page=page, published_only=False)
    return render_template('admin/news/index.html', pagination=pagination)


@admin_bp.route('/news/create', methods=['GET', 'POST'])
@login_required
@admin_required
def news_create():
    if request.method == 'POST':
        data = request.form.to_dict()
        image = request.files.get('image')
        if image and image.filename:
            fname, path, size = save_upload(image, 'cms')
            if fname:
                data['image'] = f'/static/uploads/cms/{fname}'
        CMSService.create_news(data, current_user.id)
        flash('News article created.', 'success')
        return redirect(url_for('admin.news'))
    depts = DepartmentService.get_all()
    return render_template('admin/news/create.html', departments=depts)


# ───────────── FAQS ─────────────

@admin_bp.route('/faqs')
@login_required
@admin_required
def faqs():
    faq_list = CMSService.get_faqs(active_only=False)
    return render_template('admin/faqs/index.html', faqs=faq_list)


@admin_bp.route('/faqs/create', methods=['GET', 'POST'])
@login_required
@admin_required
def faq_create():
    if request.method == 'POST':
        CMSService.create_faq(request.form.to_dict())
        flash('FAQ created.', 'success')
        return redirect(url_for('admin.faqs'))
    return render_template('admin/faqs/create.html')


# ───────────── NOTIFICATIONS ─────────────

@admin_bp.route('/notifications')
@login_required
@admin_required
def notifications():
    page = request.args.get('page', 1, type=int)
    pagination = NotificationService.get_all(page=page)
    return render_template('admin/notifications/index.html', pagination=pagination)


@admin_bp.route('/notifications/create', methods=['GET', 'POST'])
@login_required
@admin_required
def notification_create():
    if request.method == 'POST':
        NotificationService.create(request.form.to_dict(), current_user.id)
        flash('Notification sent.', 'success')
        return redirect(url_for('admin.notifications'))
    depts = DepartmentService.get_all()
    return render_template('admin/notifications/create.html', departments=depts)


@admin_bp.route('/notifications/batches-by-department')
@login_required
@admin_required
def get_batches_by_department():
    """AJAX: batches under all programs of a department, for notification targeting."""
    dept_id = request.args.get('department_id', type=int)
    if not dept_id:
        return jsonify([])
    progs = DepartmentService.get_programs(department_id=dept_id)
    result = []
    for p in progs:
        for b in DepartmentService.get_batches(program_id=p.id):
            result.append({'id': b.id, 'name': f'{p.name} — {b.label}'})
    return jsonify(result)


@admin_bp.route('/notifications/semesters-by-batch')
@login_required
@admin_required
def get_semesters_by_batch():
    """AJAX: semesters under a batch, for notification targeting."""
    batch_id = request.args.get('batch_id', type=int)
    if not batch_id:
        return jsonify([])
    sems = DepartmentService.get_semesters(batch_id=batch_id)
    return jsonify([{'id': s.id, 'name': s.name} for s in sems])


# ───────────── AI SETTINGS ─────────────

@admin_bp.route('/ai-settings')
@login_required
@admin_required
def ai_settings():
    providers = AIService.get_all_providers()
    provider_types = AIService.get_provider_types()
    return render_template('admin/ai_settings/index.html', providers=providers, provider_types=provider_types)


@admin_bp.route('/ai-settings/edit/<int:provider_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def ai_settings_edit(provider_id):
    provider = AIService.get_provider_by_id(provider_id)
    if not provider:
        flash('Provider not found.', 'danger')
        return redirect(url_for('admin.ai_settings'))
    if request.method == 'POST':
        data = request.form.to_dict()
        data['is_active'] = 'is_active' in data
        data['is_primary'] = 'is_primary' in data
        data['is_backup'] = 'is_backup' in data
        data['streaming'] = 'streaming' in data

        # Auto-set model and base URL per provider type (locked values)
        provider_defaults = {
            'gemini':      {'model_name': 'gemini-2.0-flash',                    'api_base_url': ''},
            'groq':        {'model_name': 'llama-3.3-70b-versatile',             'api_base_url': 'https://api.groq.com/openai/v1'},
            'openrouter':  {'model_name': 'meta-llama/llama-3.3-70b-instruct',   'api_base_url': 'https://openrouter.ai/api/v1'},
            'huggingface': {'model_name': 'mistralai/Mistral-7B-Instruct-v0.3',  'api_base_url': 'https://api-inference.huggingface.co/models/'},
            'deepseek':    {'model_name': 'deepseek-chat',                       'api_base_url': 'https://api.deepseek.com/v1'},
        }
        defaults = provider_defaults.get(provider.provider_type, {})
        data['model_name'] = defaults.get('model_name', data.get('model_name', ''))
        data['api_base_url'] = defaults.get('api_base_url', data.get('api_base_url', ''))

        # Auto-activate provider when API key is provided
        if data.get('api_key', '').strip():
            data['is_active'] = True

        AIService.update_provider(provider, data)

        # If "Save & Test" was clicked, test after saving
        if request.form.get('action') == 'save_and_test':
            success, msg = AIService.test_provider(provider_id)
            if success:
                flash(f'Provider saved and tested successfully! {msg}', 'success')
            else:
                flash(f'Provider saved but test failed: {msg}', 'warning')
        else:
            flash('Provider updated successfully.', 'success')

        return redirect(url_for('admin.ai_settings'))
    masked_key = AIService.get_decrypted_key(provider)
    return render_template('admin/ai_settings/edit.html', provider=provider, masked_key=masked_key)


@admin_bp.route('/ai-settings/test/<int:provider_id>', methods=['POST'])
@login_required
@admin_required
def ai_settings_test(provider_id):
    success, msg = AIService.test_provider(provider_id)
    return jsonify({'success': success, 'message': msg})


# ───────────── CHAT LOGS ─────────────

@admin_bp.route('/chat-logs')
@login_required
@admin_required
def chat_logs():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    pagination = ChatService.get_all_chats(page=page, search=search)
    return render_template('admin/chat_logs/index.html', pagination=pagination, search=search)


@admin_bp.route('/chat-logs/view/<int:session_id>')
@login_required
@admin_required
def chat_view(session_id):
    """View a specific student chat conversation."""
    from app.models.chat import ChatSession
    session = ChatSession.query.get_or_404(session_id)
    messages = ChatService.get_messages(session_id, limit=500)
    return render_template('admin/chat_logs/view.html', session=session, messages=messages)


# ───────────── ANALYTICS ─────────────

@admin_bp.route('/analytics')
@login_required
@admin_required
def analytics():
    data = AdminController.get_dashboard_data()
    return render_template('admin/analytics/index.html', **data)


# ───────────── HOD ASSIGNMENT ─────────────

@admin_bp.route('/departments/<int:dept_id>/hod', methods=['GET', 'POST'])
@login_required
@admin_required
def department_hod(dept_id):
    from app import db
    from app.models.user import User
    from app.services.audit_service import AuditService
    dept = DepartmentService.get_by_id(dept_id)
    if not dept:
        flash('Department not found.', 'danger')
        return redirect(url_for('admin.departments'))
    if request.method == 'POST':
        user_id = request.form.get('hod_user_id', type=int)
        if user_id:
            user = db.session.get(User, user_id)
            if not user:
                flash('User not found.', 'danger')
                return redirect(url_for('admin.department_hod', dept_id=dept_id))
            user.role = 'hod'
            user.department_id = dept.id
            dept.hod_user_id = user.id
            db.session.commit()
            AuditService.log(current_user.id, 'assign_hod', 'department', dept.id, request.remote_addr)
            flash(f'{user.full_name} assigned as HOD.', 'success')
        else:
            dept.hod_user_id = None
            db.session.commit()
            flash('HOD cleared.', 'info')
        return redirect(url_for('admin.departments'))
    candidates = User.query.filter(User.role.in_(('teacher', 'hod', 'admin'))).order_by(User.full_name).all()
    return render_template('admin/departments/hod.html', dept=dept, candidates=candidates)


# ───────────── USER ROLE MANAGEMENT ─────────────

@admin_bp.route('/users')
@login_required
@admin_required
def users():
    from app.models.user import User
    page = request.args.get('page', 1, type=int)
    pagination = User.query.order_by(User.role, User.full_name).paginate(page=page, per_page=25, error_out=False)
    depts = DepartmentService.get_all()
    return render_template('admin/users/index.html', pagination=pagination, departments=depts)


@admin_bp.route('/users/<int:user_id>/role', methods=['POST'])
@login_required
@admin_required
def user_role(user_id):
    from app import db
    from app.models.user import User
    from app.services.audit_service import AuditService
    user = db.session.get(User, user_id)
    if not user:
        flash('User not found.', 'danger')
        return redirect(url_for('admin.users'))
    new_role = request.form.get('role')
    valid = ('super_admin', 'admin', 'hod', 'teacher', 'student')
    if new_role not in valid:
        flash('Invalid role.', 'danger')
        return redirect(url_for('admin.users'))
    # Protect the last super_admin from demotion
    if user.role == 'super_admin' and new_role != 'super_admin':
        remaining = User.query.filter_by(role='super_admin').count()
        if remaining <= 1:
            flash('Cannot demote the only super admin.', 'danger')
            return redirect(url_for('admin.users'))
    old_role = user.role
    user.role = new_role
    dept_id = request.form.get('department_id', type=int)
    if dept_id and new_role in ('hod', 'teacher', 'student'):
        user.department_id = dept_id
    db.session.commit()
    AuditService.log(current_user.id, f'role_change:{old_role}->{new_role}', 'user', user.id, request.remote_addr)
    flash('Role updated.', 'success')
    return redirect(url_for('admin.users'))


# ───────────── CROSS-DEPARTMENT REPORTS ─────────────

@admin_bp.route('/reports')
@login_required
@admin_required
def reports():
    from app.services.quiz_service import QuizService
    rows = QuizService.cross_department_stats()
    return render_template('admin/reports/index.html', rows=rows)


# ───────────── THEME PORTAL (super admin) ─────────────

@admin_bp.route('/theme', methods=['GET', 'POST'])
@login_required
@super_admin_required
def theme():
    from app.services.theme_service import ThemeService
    if request.method == 'POST':
        ThemeService.update_theme(request.form.to_dict(), request.files, current_user.id)
        flash('Theme updated.', 'success')
        return redirect(url_for('admin.theme'))
    active = ThemeService.get_active_theme()
    return render_template('admin/theme/index.html', theme=active)
