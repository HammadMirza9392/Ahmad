"""Seed dummy data for programs, classes, subjects, students, and university info."""
from app import create_app, db
from app.models.program import Program
from app.models.classes import Class, ClassSubject
from app.models.subject import Subject
from app.models.department import Department
from app.models.institution import Institution
from app.models.user import User
from app.services.auth_service import AuthService

app = create_app('development')
with app.app_context():
    # Update institution with university info
    inst = Institution.query.first()
    inst.university_name = 'University of the Punjab, Lahore'
    inst.history = (
        'Government Graduate College Jhang was established in 1947. It is one of the oldest and most '
        'prestigious educational institutions in District Jhang, Punjab, Pakistan. The college is affiliated '
        'with the University of the Punjab, Lahore and offers intermediate, graduate, and postgraduate programs '
        'across multiple disciplines. Over the decades, the college has produced thousands of graduates who have '
        'excelled in various fields including education, civil services, medicine, engineering, and business.'
    )
    inst.principal_name = 'Prof. Dr. Muhammad Ahmad'
    inst.principal_message = (
        'Welcome to Government Graduate College Jhang. Our institution is committed to providing quality education '
        'and nurturing the next generation of leaders. We believe in holistic development of our students through '
        'academic excellence, character building, and community service.'
    )
    inst.office_timing = 'Monday - Saturday: 8:00 AM - 2:00 PM'
    inst.vc_name = 'Prof. Dr. Khalid Mahmood'
    inst.vc_message = (
        'The University of the Punjab is committed to supporting affiliated colleges in their mission to '
        'provide accessible and quality higher education across Punjab.'
    )
    db.session.commit()
    print('Institution updated with university details.')

    # Get departments
    depts = {d.slug: d for d in Department.query.all()}
    cs = depts['computer-science']
    physics = depts['physics']
    chemistry = depts['chemistry']
    math = depts['mathematics']
    commerce = depts['commerce']
    english = depts['english']
    bio = depts['biology']
    urdu = depts['urdu']

    # Seed Programs
    if not Program.query.first():
        programs_data = [
            Program(name='ICS', slug='ics', description='Intermediate in Computer Science', duration='2 Years', degree_type='Intermediate', department_id=cs.id, sort_order=1),
            Program(name='BS Computer Science', slug='bs-cs', description='Bachelor of Science in Computer Science', duration='4 Years', degree_type='Bachelor', department_id=cs.id, sort_order=2),
            Program(name='FSc Pre-Engineering', slug='fsc-pre-eng', description='Intermediate in Pre-Engineering', duration='2 Years', degree_type='Intermediate', department_id=physics.id, sort_order=1),
            Program(name='BS Physics', slug='bs-physics', description='Bachelor of Science in Physics', duration='4 Years', degree_type='Bachelor', department_id=physics.id, sort_order=2),
            Program(name='FSc Pre-Medical', slug='fsc-pre-med', description='Intermediate in Pre-Medical', duration='2 Years', degree_type='Intermediate', department_id=chemistry.id, sort_order=1),
            Program(name='BS Mathematics', slug='bs-math', description='Bachelor of Science in Mathematics', duration='4 Years', degree_type='Bachelor', department_id=math.id, sort_order=1),
            Program(name='I.Com', slug='icom', description='Intermediate in Commerce', duration='2 Years', degree_type='Intermediate', department_id=commerce.id, sort_order=1),
            Program(name='B.Com', slug='bcom', description='Bachelor of Commerce', duration='2 Years', degree_type='Bachelor', department_id=commerce.id, sort_order=2),
            Program(name='FA', slug='fa', description='Faculty of Arts - Intermediate', duration='2 Years', degree_type='Intermediate', department_id=english.id, sort_order=1),
            Program(name='BA', slug='ba', description='Bachelor of Arts', duration='2 Years', degree_type='Bachelor', department_id=english.id, sort_order=2),
            Program(name='FSc Pre-Medical Bio', slug='fsc-bio', description='Intermediate with Biology Focus', duration='2 Years', degree_type='Intermediate', department_id=bio.id, sort_order=1),
        ]
        db.session.add_all(programs_data)
        db.session.commit()
        print(f'Programs seeded: {len(programs_data)}')
    else:
        print('Programs already exist.')

    # Seed Classes
    if not Class.query.first():
        progs = {p.slug: p for p in Program.query.all()}
        classes_data = [
            Class(name='ICS Part 1', slug='ics-part-1', year='1st Year', program_id=progs['ics'].id, sort_order=1),
            Class(name='ICS Part 2', slug='ics-part-2', year='2nd Year', program_id=progs['ics'].id, sort_order=2),
            Class(name='BS CS Semester 1-2', slug='bs-cs-sem-1', year='1st Year', program_id=progs['bs-cs'].id, sort_order=1),
            Class(name='BS CS Semester 3-4', slug='bs-cs-sem-2', year='2nd Year', program_id=progs['bs-cs'].id, sort_order=2),
            Class(name='FSc Pre-Eng Part 1', slug='fsc-eng-part-1', year='1st Year', program_id=progs['fsc-pre-eng'].id, sort_order=1),
            Class(name='FSc Pre-Eng Part 2', slug='fsc-eng-part-2', year='2nd Year', program_id=progs['fsc-pre-eng'].id, sort_order=2),
            Class(name='FSc Pre-Med Part 1', slug='fsc-med-part-1', year='1st Year', program_id=progs['fsc-pre-med'].id, sort_order=1),
            Class(name='FSc Pre-Med Part 2', slug='fsc-med-part-2', year='2nd Year', program_id=progs['fsc-pre-med'].id, sort_order=2),
            Class(name='I.Com Part 1', slug='icom-part-1', year='1st Year', program_id=progs['icom'].id, sort_order=1),
            Class(name='I.Com Part 2', slug='icom-part-2', year='2nd Year', program_id=progs['icom'].id, sort_order=2),
            Class(name='FA Part 1', slug='fa-part-1', year='1st Year', program_id=progs['fa'].id, sort_order=1),
            Class(name='FA Part 2', slug='fa-part-2', year='2nd Year', program_id=progs['fa'].id, sort_order=2),
        ]
        db.session.add_all(classes_data)
        db.session.commit()
        print(f'Classes seeded: {len(classes_data)}')
    else:
        print('Classes already exist.')

    # Seed Subjects
    if not Subject.query.first():
        subjects_data = [
            Subject(name='Computer Science', slug='computer-science-sub', code='CS-101', department_id=cs.id, credit_hours=3, sort_order=1),
            Subject(name='Programming Fundamentals', slug='programming-fundamentals', code='CS-102', department_id=cs.id, credit_hours=4, sort_order=2),
            Subject(name='Data Structures', slug='data-structures', code='CS-201', department_id=cs.id, credit_hours=3, sort_order=3),
            Subject(name='Database Systems', slug='database-systems', code='CS-202', department_id=cs.id, credit_hours=3, sort_order=4),
            Subject(name='Web Development', slug='web-development', code='CS-203', department_id=cs.id, credit_hours=3, sort_order=5),
            Subject(name='Physics', slug='physics-sub', code='PHY-101', department_id=physics.id, credit_hours=3, sort_order=1),
            Subject(name='Mechanics', slug='mechanics', code='PHY-201', department_id=physics.id, credit_hours=3, sort_order=2),
            Subject(name='Electricity & Magnetism', slug='electricity-magnetism', code='PHY-202', department_id=physics.id, credit_hours=3, sort_order=3),
            Subject(name='Chemistry', slug='chemistry-sub', code='CHM-101', department_id=chemistry.id, credit_hours=3, sort_order=1),
            Subject(name='Organic Chemistry', slug='organic-chemistry', code='CHM-201', department_id=chemistry.id, credit_hours=3, sort_order=2),
            Subject(name='Mathematics', slug='mathematics-sub', code='MTH-101', department_id=math.id, credit_hours=3, sort_order=1),
            Subject(name='Calculus', slug='calculus', code='MTH-201', department_id=math.id, credit_hours=4, sort_order=2),
            Subject(name='Linear Algebra', slug='linear-algebra', code='MTH-202', department_id=math.id, credit_hours=3, sort_order=3),
            Subject(name='Accounting', slug='accounting', code='COM-101', department_id=commerce.id, credit_hours=3, sort_order=1),
            Subject(name='Business Studies', slug='business-studies', code='COM-102', department_id=commerce.id, credit_hours=3, sort_order=2),
            Subject(name='English Literature', slug='english-literature', code='ENG-101', department_id=english.id, credit_hours=3, sort_order=1),
            Subject(name='English Composition', slug='english-composition', code='ENG-102', department_id=english.id, credit_hours=3, sort_order=2),
            Subject(name='Biology', slug='biology-sub', code='BIO-101', department_id=bio.id, credit_hours=3, sort_order=1),
            Subject(name='Zoology', slug='zoology', code='BIO-201', department_id=bio.id, credit_hours=3, sort_order=2),
            Subject(name='Botany', slug='botany', code='BIO-202', department_id=bio.id, credit_hours=3, sort_order=3),
            Subject(name='Urdu', slug='urdu-sub', code='URD-101', department_id=urdu.id, credit_hours=3, sort_order=1),
            Subject(name='Pakistan Studies', slug='pak-studies', code='PST-101', department_id=english.id, credit_hours=2, sort_order=10),
            Subject(name='Islamiat', slug='islamiat', code='ISL-101', department_id=english.id, credit_hours=2, sort_order=11),
        ]
        db.session.add_all(subjects_data)
        db.session.commit()
        print(f'Subjects seeded: {len(subjects_data)}')
    else:
        print('Subjects already exist.')

    # Assign subjects to ICS Part 1
    ics1 = Class.query.filter_by(slug='ics-part-1').first()
    if ics1 and not ClassSubject.query.filter_by(class_id=ics1.id).first():
        codes = ['CS-101', 'CS-102', 'MTH-101', 'PHY-101', 'ENG-101', 'URD-101', 'PST-101', 'ISL-101']
        for code in codes:
            subj = Subject.query.filter_by(code=code).first()
            if subj:
                db.session.add(ClassSubject(class_id=ics1.id, subject_id=subj.id))
        db.session.commit()
        print('Subjects assigned to ICS Part 1.')

    # Seed Students
    if User.query.filter_by(role='student').count() == 0:
        ics_prog = Program.query.filter_by(slug='ics').first()
        students = [
            {'email': 'ahmed.khan@student.ggcjhang.edu.pk', 'full_name': 'Ahmed Khan', 'roll_number': 'ICS-2024-001'},
            {'email': 'fatima.noor@student.ggcjhang.edu.pk', 'full_name': 'Fatima Noor', 'roll_number': 'ICS-2024-002'},
            {'email': 'ali.hassan@student.ggcjhang.edu.pk', 'full_name': 'Ali Hassan', 'roll_number': 'ICS-2024-003'},
            {'email': 'ayesha.malik@student.ggcjhang.edu.pk', 'full_name': 'Ayesha Malik', 'roll_number': 'ICS-2024-004'},
            {'email': 'usman.shah@student.ggcjhang.edu.pk', 'full_name': 'Usman Shah', 'roll_number': 'ICS-2024-005'},
            {'email': 'zainab.ali@student.ggcjhang.edu.pk', 'full_name': 'Zainab Ali', 'roll_number': 'ICS-2024-006'},
            {'email': 'bilal.ahmad@student.ggcjhang.edu.pk', 'full_name': 'Bilal Ahmad', 'roll_number': 'ICS-2024-007'},
            {'email': 'sana.iqbal@student.ggcjhang.edu.pk', 'full_name': 'Sana Iqbal', 'roll_number': 'ICS-2024-008'},
            {'email': 'hamza.raza@student.ggcjhang.edu.pk', 'full_name': 'Hamza Raza', 'roll_number': 'ICS-2024-009'},
            {'email': 'maria.tariq@student.ggcjhang.edu.pk', 'full_name': 'Maria Tariq', 'roll_number': 'ICS-2024-010'},
        ]
        for s in students:
            user = User(
                email=s['email'],
                password_hash=AuthService.hash_password('Student@123'),
                role='student',
                full_name=s['full_name'],
                roll_number=s['roll_number'],
                department_id=cs.id,
                program_id=ics_prog.id if ics_prog else None,
                class_id=ics1.id if ics1 else None,
                semester='1st',
                is_active=True,
                email_verified=True,
            )
            db.session.add(user)
        db.session.commit()
        print(f'Students seeded: {len(students)}')
    else:
        print('Students already exist.')

    print()
    print('=== ALL DUMMY DATA SEEDED ===')
    print(f'Programs: {Program.query.count()}')
    print(f'Classes: {Class.query.count()}')
    print(f'Subjects: {Subject.query.count()}')
    print(f'Students: {User.query.filter_by(role="student").count()}')
