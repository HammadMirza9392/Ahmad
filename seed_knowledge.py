"""Seed Knowledge Base with real educational content for ICS Part 1 Computer Science."""
from app import create_app, db
from app.models.knowledge_base import KnowledgeBase
from app.models.department import Department
from app.models.program import Program
from app.models.classes import Class
from app.models.subject import Subject
from app.models.institution import Institution
from app.models.user import User

app = create_app('development')
with app.app_context():
    cs_dept = Department.query.filter_by(slug='computer-science').first()
    ics_prog = Program.query.filter_by(slug='ics').first()
    ics1_class = Class.query.filter_by(slug='ics-part-1').first()
    cs_subject = Subject.query.filter_by(code='CS-101').first()
    pf_subject = Subject.query.filter_by(code='CS-102').first()
    admin = User.query.filter_by(role='super_admin').first()

    # Update institution map
    inst = Institution.query.first()
    inst.google_map = '<iframe src="https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d3417.547!2d72.318!3d31.268!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x392171c615f88cf7%3A0x7a8d8f3e8c7c2b9a!2sGovt.%20Graduate%20College%2C%20Jhang!5e0!3m2!1sen!2spk!4v1" width="100%" height="400" style="border:0;border-radius:12px;" allowfullscreen loading="lazy" referrerpolicy="no-referrer-when-downgrade"></iframe>'
    db.session.commit()
    print('Map location updated.')

    if KnowledgeBase.query.count() > 0:
        print('Knowledge base already has data. Skipping.')
    else:
        entries = [
            # ── Entry 1: Paper Pattern ──
            KnowledgeBase(
                title='ICS Part 1 Computer Science Paper Pattern (2024-2025)',
                content="""## ICS Part 1 Computer Science Paper Pattern

**Board:** Board of Intermediate and Secondary Education (BISE)
**Total Marks:** 100 (75 Theory + 25 Practical)
**Time:** 3 Hours

### Theory Paper (75 Marks)

#### Section A — Multiple Choice Questions (MCQs)
- **17 MCQs** from the entire syllabus
- Each MCQ carries **1 mark**
- Total: **17 marks**

#### Section B — Short Questions
- **Attempt 10 out of 15** short questions
- Each question carries **3 marks**
- Total: **30 marks**
- Questions are from all chapters

#### Section C — Long Questions
- **Attempt 3 out of 5** long questions
- Each question carries **8 marks**
- May include sub-parts (a, b)
- Total: **24 marks**
- Questions are from Chapters 1, 2, 3, 4, 5

#### Important Note
- No question is optional in Section A (MCQs)
- Scientific calculator is NOT allowed
- Use blue/black pen only

### Practical (25 Marks)
- **Lab work and viva voce**
- Conducted separately by the college
- Includes: MS Word, MS Excel, MS PowerPoint exercises

### Chapter-wise Marks Distribution
| Chapter | Topic | Approx. Marks |
|---------|-------|---------------|
| 1 | Introduction to Computer | 12-15 |
| 2 | Information Networks | 10-12 |
| 3 | Data Communication | 10-12 |
| 4 | Application Software | 12-15 |
| 5 | Programming in C | 15-18 |
""",
                department_id=cs_dept.id,
                program_id=ics_prog.id,
                class_id=ics1_class.id,
                subject_id=cs_subject.id,
                chapter='General',
                topic='Paper Pattern',
                status='published',
                tags='paper pattern, exam, marks distribution',
                created_by=admin.id,
            ),

            # ── Entry 2: Chapter 1 - Introduction to Computer ──
            KnowledgeBase(
                title='Chapter 1: Introduction to Computer',
                content="""## Chapter 1: Introduction to Computer

### What is a Computer?
A computer is an electronic device that accepts data as input, processes it according to a set of instructions (program), and produces results as output. It can store data for future use.

### Characteristics of Computer
1. **Speed** — Performs millions of calculations per second (measured in MIPS)
2. **Accuracy** — Produces 99.99% accurate results (errors are human, not machine)
3. **Storage** — Can store large amounts of data permanently
4. **Diligence** — Does not get tired or bored; works consistently
5. **Versatility** — Can perform multiple types of tasks
6. **Automation** — Works automatically once programmed
7. **No IQ** — Cannot think on its own; follows instructions only

### Generations of Computer

| Generation | Period | Technology | Example |
|-----------|--------|------------|---------|
| 1st | 1940-1956 | Vacuum Tubes | ENIAC, UNIVAC |
| 2nd | 1956-1963 | Transistors | IBM 1401, IBM 7094 |
| 3rd | 1964-1971 | Integrated Circuits (ICs) | IBM 360, PDP-8 |
| 4th | 1971-Present | Microprocessors (VLSI) | IBM PC, Apple |
| 5th | Present-Future | Artificial Intelligence | Robots, AI Systems |

### Types of Computer by Size
1. **Supercomputer** — Fastest, used for weather forecasting, nuclear research. Example: Cray, IBM Summit
2. **Mainframe** — Large, used by banks, airlines. Example: IBM z15
3. **Minicomputer** — Medium, used in laboratories. Example: PDP-11
4. **Microcomputer** — Personal computer (PC), laptop, tablet
5. **Workstation** — High-performance PC for engineering/design

### Types of Computer by Purpose
1. **General Purpose** — Can perform multiple tasks (PC, Laptop)
2. **Special Purpose** — Designed for specific task (ATM, Traffic Light Controller)

### Components of Computer System
1. **Hardware** — Physical parts (Monitor, Keyboard, CPU, RAM)
2. **Software** — Programs and instructions
   - *System Software* — Operating System (Windows, Linux)
   - *Application Software* — MS Office, Chrome, Games
3. **Humanware** — People who use computers (Users, Programmers)

### Input Devices
Keyboard, Mouse, Scanner, Microphone, Webcam, Joystick, Light Pen, Barcode Reader, Touchscreen

### Output Devices
Monitor, Printer, Speaker, Plotter, Projector

### CPU (Central Processing Unit)
The brain of the computer. Has three parts:
1. **ALU (Arithmetic Logic Unit)** — Performs calculations (+, -, ×, ÷) and logical operations (AND, OR, NOT)
2. **CU (Control Unit)** — Controls and coordinates all computer operations
3. **Registers** — Small, fast temporary storage inside CPU

### Memory Types
1. **Primary Memory (Main Memory)**
   - **RAM (Random Access Memory)** — Volatile, temporary, fast. Data lost when power off.
   - **ROM (Read Only Memory)** — Non-volatile, permanent. Contains BIOS/startup instructions.
2. **Secondary Memory (Storage)**
   - Hard Disk (HDD/SSD), USB Drive, CD/DVD, Memory Card
""",
                department_id=cs_dept.id,
                program_id=ics_prog.id,
                class_id=ics1_class.id,
                subject_id=cs_subject.id,
                chapter='Chapter 1',
                topic='Introduction to Computer',
                status='published',
                tags='computer basics, generations, hardware, software, CPU, memory',
                created_by=admin.id,
            ),

            # ── Entry 3: Chapter 2 - Information Networks ──
            KnowledgeBase(
                title='Chapter 2: Information Networks',
                content="""## Chapter 2: Information Networks

### What is a Network?
A computer network is a collection of two or more computers connected together to share data, resources, and communication.

### Advantages of Networks
1. Resource sharing (printers, files, internet)
2. Communication (email, chat, video call)
3. Data backup and recovery
4. Cost reduction
5. Centralized management

### Types of Networks

#### 1. LAN (Local Area Network)
- Covers a **small area** (room, building, campus)
- **High speed** (100 Mbps to 10 Gbps)
- **Low cost** to set up
- Example: Computer lab network, office network

#### 2. MAN (Metropolitan Area Network)
- Covers a **city or town**
- Speed: 10-100 Mbps
- Example: Cable TV network, city-wide WiFi

#### 3. WAN (Wide Area Network)
- Covers **countries or the entire world**
- Uses telephone lines, satellites, fiber optics
- **Slower** than LAN but covers huge distances
- Example: **Internet** is the largest WAN

### Network Topologies

#### 1. Star Topology
- All computers connected to a **central hub/switch**
- If hub fails, entire network goes down
- Easy to add/remove computers
- Most commonly used

#### 2. Bus Topology
- All computers connected to a **single cable** (backbone)
- Cheap but slow
- If cable breaks, network fails

#### 3. Ring Topology
- Computers connected in a **circular loop**
- Data travels in one direction
- If one computer fails, network may fail

#### 4. Mesh Topology
- Every computer connected to **every other computer**
- Most reliable but most expensive
- Used in military, banking

### Internet
- The **largest WAN** in the world
- Connects billions of devices globally
- Uses **TCP/IP** protocol
- Started as **ARPANET** in 1969 (US Department of Defense)

### Internet Services
1. **WWW (World Wide Web)** — Web pages accessed via browser
2. **Email** — Electronic mail (Gmail, Outlook)
3. **FTP** — File Transfer Protocol (uploading/downloading files)
4. **VoIP** — Voice over Internet Protocol (Skype, WhatsApp calls)
5. **E-Commerce** — Online shopping (Daraz, Amazon)
6. **Social Media** — Facebook, Instagram, Twitter

### Web Browser vs Search Engine
| Web Browser | Search Engine |
|-------------|---------------|
| Software to access websites | Service to find websites |
| Chrome, Firefox, Edge | Google, Bing, Yahoo |
| Displays web pages | Searches web pages |
""",
                department_id=cs_dept.id,
                program_id=ics_prog.id,
                class_id=ics1_class.id,
                subject_id=cs_subject.id,
                chapter='Chapter 2',
                topic='Information Networks',
                status='published',
                tags='networking, LAN, WAN, MAN, internet, topology',
                created_by=admin.id,
            ),

            # ── Entry 4: Chapter 5 - Programming in C ──
            KnowledgeBase(
                title='Chapter 5: Programming in C (Basics)',
                content="""## Chapter 5: Programming in C

### What is Programming?
Programming is the process of writing instructions (code) that a computer can execute to perform a specific task.

### What is C Language?
- C is a **general-purpose programming language**
- Developed by **Dennis Ritchie** in **1972** at **Bell Labs**
- Known as the "mother of all languages"
- Used to develop operating systems (UNIX, Linux, Windows)

### Structure of a C Program

```c
#include <stdio.h>    // Header file (preprocessor directive)

int main()            // Main function - program starts here
{
    printf("Hello World!");   // Output statement
    return 0;                  // Return value
}
```

### Important Concepts

#### Variables
A variable is a named location in memory that stores data.
```c
int age = 18;           // Integer variable
float marks = 85.5;     // Decimal variable
char grade = 'A';       // Character variable
```

#### Data Types in C
| Data Type | Size | Range | Example |
|-----------|------|-------|---------|
| int | 2 bytes | -32768 to 32767 | int x = 10; |
| float | 4 bytes | 3.4e-38 to 3.4e+38 | float y = 3.14; |
| char | 1 byte | -128 to 127 | char c = 'A'; |
| double | 8 bytes | 1.7e-308 to 1.7e+308 | double d = 3.14159; |

#### Operators in C
1. **Arithmetic:** +, -, *, /, % (modulus)
2. **Relational:** ==, !=, <, >, <=, >=
3. **Logical:** && (AND), || (OR), ! (NOT)
4. **Assignment:** =, +=, -=, *=, /=

#### Input/Output
```c
// Output
printf("Your age is %d", age);

// Input
scanf("%d", &age);
```

#### Format Specifiers
- `%d` — Integer
- `%f` — Float
- `%c` — Character
- `%s` — String

#### If-Else Statement
```c
if (marks >= 50) {
    printf("Pass");
} else {
    printf("Fail");
}
```

#### For Loop
```c
for (int i = 1; i <= 10; i++) {
    printf("%d ", i);
}
// Output: 1 2 3 4 5 6 7 8 9 10
```

#### While Loop
```c
int i = 1;
while (i <= 5) {
    printf("%d ", i);
    i++;
}
```

### Important Programs for Exam
1. Print "Hello World"
2. Add two numbers
3. Find greater of two numbers
4. Check even or odd
5. Print multiplication table
6. Calculate factorial
7. Check prime number
8. Print Fibonacci series
""",
                department_id=cs_dept.id,
                program_id=ics_prog.id,
                class_id=ics1_class.id,
                subject_id=cs_subject.id,
                chapter='Chapter 5',
                topic='Programming in C',
                status='published',
                tags='C programming, variables, loops, if-else, operators',
                created_by=admin.id,
            ),

            # ── Entry 5: Admission Info ──
            KnowledgeBase(
                title='Admission Information - Government Graduate College Jhang',
                content="""## Admission Information

### Eligibility Criteria

#### ICS (Intermediate in Computer Science)
- **Minimum:** Matric/SSC with Science (at least 45% marks)
- **Required Subjects:** Mathematics, Physics in Matric
- **Age:** Maximum 19 years at the time of admission

#### FSc Pre-Engineering
- **Minimum:** Matric/SSC with Science (at least 45% marks)
- **Required Subjects:** Mathematics, Physics in Matric

#### FSc Pre-Medical
- **Minimum:** Matric/SSC with Science (at least 45% marks)
- **Required Subjects:** Biology in Matric

#### I.Com (Intermediate in Commerce)
- **Minimum:** Matric/SSC with any group (at least 40% marks)

#### FA (Faculty of Arts)
- **Minimum:** Matric/SSC with any group (at least 33% marks)

### Required Documents
1. Matric/SSC Marksheet (Original + 2 copies)
2. Matric/SSC Certificate (Original + 2 copies)
3. Character Certificate from previous school
4. Domicile Certificate
5. CNIC/B-Form (Original + 2 copies)
6. 4 Recent passport-size photographs
7. Migration Certificate (if from other board)
8. Father's CNIC copy

### Fee Structure (Approximate)
| Program | Admission Fee | Monthly Fee |
|---------|--------------|-------------|
| ICS | Rs. 5,000 | Rs. 1,200 |
| FSc | Rs. 5,000 | Rs. 1,200 |
| I.Com | Rs. 4,500 | Rs. 1,000 |
| FA | Rs. 4,000 | Rs. 900 |

### Admission Schedule
- Forms available: **July-August** every year
- Last date for submission: **Usually end of August**
- Merit lists displayed: **September**
- Classes start: **October**

### Contact for Admission
- Visit the Admission Office at the college campus
- Phone: +92-47-7620001
- Email: info@ggcjhang.edu.pk
""",
                department_id=None,
                program_id=None,
                class_id=None,
                subject_id=None,
                chapter=None,
                topic='Admission',
                status='published',
                tags='admission, eligibility, fee, documents',
                created_by=admin.id,
            ),

            # ── Entry 6: College Rules ──
            KnowledgeBase(
                title='College Rules and Regulations',
                content="""## College Rules and Regulations

### Attendance Policy
- Minimum **75% attendance** is required to sit in the exam
- Students with less than 75% attendance will be marked as "Short of Attendance"
- Medical leave requires a valid medical certificate submitted within 3 days

### Dress Code
- Students must wear **proper uniform** as prescribed by the college
- ID card must be worn at all times within the campus
- Casual/informal dressing is not allowed

### Examination Rules
- Students must carry their **Roll Number Slip** and **College ID Card** to every exam
- Use of mobile phones is **strictly prohibited** during exams
- Cheating or use of unfair means will result in cancellation of the paper and possible rustication

### Library Rules
- Library card is mandatory for borrowing books
- Maximum **2 books** can be borrowed at a time
- Books must be returned within **14 days**
- Fine of Rs. 10 per day for late returns

### Computer Lab Rules
- No food or drinks allowed in the lab
- Save your work on USB drive or cloud storage
- Report any hardware issues to the lab assistant
- Browsing social media during lab hours is not allowed

### Disciplinary Actions
- First offense: Written warning
- Second offense: Parent/guardian meeting
- Third offense: Suspension (1-2 weeks)
- Severe misconduct: Rustication from college
""",
                department_id=None,
                program_id=None,
                class_id=None,
                subject_id=None,
                chapter=None,
                topic='Rules and Regulations',
                status='published',
                tags='rules, attendance, dress code, library, exam rules',
                created_by=admin.id,
            ),
        ]

        db.session.add_all(entries)
        db.session.commit()
        print(f'Knowledge Base seeded: {len(entries)} entries')

    print()
    print('=== KNOWLEDGE BASE READY ===')
    print(f'Total entries: {KnowledgeBase.query.count()}')
    print()
    print('='*60)
    print('TEST QUESTIONS FOR AI CHATBOT')
    print('='*60)
    print('''
Login as: ahmed.khan@student.ggcjhang.edu.pk / Student@123

Then ask these questions in the AI Chat:

1. "What is the paper pattern for Computer Science?"
   → Should return full paper pattern with marks distribution

2. "What are the generations of computer?"
   → Should return 5 generations table from Chapter 1

3. "Explain the types of computer networks - LAN, WAN, MAN"
   → Should return detailed network types from Chapter 2

4. "Write a C program to check if a number is even or odd"
   → Should give C code from Chapter 5 knowledge

5. "What are the admission requirements for ICS?"
   → Should return eligibility, documents, and fee info

6. "What is the attendance policy of the college?"
   → Should return 75% rule from college regulations

7. "What are the types of network topologies?"
   → Should explain Star, Bus, Ring, Mesh from Chapter 2

8. "What is CPU and its components?"
   → Should explain ALU, CU, Registers from Chapter 1
''')
