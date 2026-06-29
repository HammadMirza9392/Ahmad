-- =============================================================================
-- AI Powered College & University LMS — Complete Database Schema
-- Target: Supabase PostgreSQL
-- =============================================================================

-- ===================== INSTITUTION =====================
CREATE TABLE IF NOT EXISTS institution (
    id SERIAL PRIMARY KEY,
    name VARCHAR(500) NOT NULL DEFAULT 'Government Graduate College Jhang',
    institution_type VARCHAR(50) DEFAULT 'college',
    university_name VARCHAR(500),

    logo VARCHAR(500),
    banner VARCHAR(500),
    favicon VARCHAR(500),

    about TEXT,
    vision TEXT,
    mission TEXT,
    history TEXT,
    principal_message TEXT,
    principal_name VARCHAR(255),
    principal_image VARCHAR(500),
    vc_message TEXT,
    vc_name VARCHAR(255),
    vc_image VARCHAR(500),

    address TEXT,
    phone VARCHAR(50),
    email VARCHAR(255),
    website VARCHAR(500),
    google_map TEXT,
    office_timing VARCHAR(255),

    facebook VARCHAR(500),
    twitter VARCHAR(500),
    instagram VARCHAR(500),
    youtube VARCHAR(500),
    linkedin VARCHAR(500),

    primary_color VARCHAR(20) DEFAULT '#1a56db',
    secondary_color VARCHAR(20) DEFAULT '#7c3aed',

    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- ===================== USERS =====================
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'student',

    full_name VARCHAR(255) NOT NULL,
    phone VARCHAR(20),
    avatar VARCHAR(500),
    roll_number VARCHAR(50),

    department_id INTEGER,
    program_id INTEGER,
    class_id INTEGER,
    semester VARCHAR(20),

    is_active BOOLEAN DEFAULT TRUE,
    email_verified BOOLEAN DEFAULT FALSE,
    last_login TIMESTAMP,
    password_reset_token VARCHAR(255),
    password_reset_expires TIMESTAMP,

    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_roll ON users(roll_number);
CREATE INDEX idx_users_role ON users(role);

-- ===================== DEPARTMENTS =====================
CREATE TABLE IF NOT EXISTS departments (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(255) UNIQUE NOT NULL,
    description TEXT,
    image VARCHAR(500),

    hod_name VARCHAR(255),
    hod_image VARCHAR(500),
    hod_message TEXT,
    hod_email VARCHAR(255),
    hod_phone VARCHAR(50),

    sort_order INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,

    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_departments_slug ON departments(slug);

-- ===================== PROGRAMS =====================
CREATE TABLE IF NOT EXISTS programs (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(255) UNIQUE NOT NULL,
    description TEXT,
    duration VARCHAR(50),
    degree_type VARCHAR(100),

    department_id INTEGER NOT NULL REFERENCES departments(id) ON DELETE CASCADE,

    is_active BOOLEAN DEFAULT TRUE,
    sort_order INTEGER DEFAULT 0,

    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_programs_slug ON programs(slug);

-- ===================== CLASSES =====================
CREATE TABLE IF NOT EXISTS classes (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(255) NOT NULL,
    section VARCHAR(50),
    year VARCHAR(50),

    program_id INTEGER NOT NULL REFERENCES programs(id) ON DELETE CASCADE,

    is_active BOOLEAN DEFAULT TRUE,
    sort_order INTEGER DEFAULT 0,

    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_classes_slug ON classes(slug);

-- ===================== SUBJECTS =====================
CREATE TABLE IF NOT EXISTS subjects (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(255) NOT NULL,
    code VARCHAR(50),
    description TEXT,
    credit_hours INTEGER,

    department_id INTEGER NOT NULL REFERENCES departments(id) ON DELETE CASCADE,

    is_active BOOLEAN DEFAULT TRUE,
    sort_order INTEGER DEFAULT 0,

    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_subjects_slug ON subjects(slug);

-- Bridge: which subjects belong to which class
CREATE TABLE IF NOT EXISTS class_subjects (
    id SERIAL PRIMARY KEY,
    class_id INTEGER NOT NULL REFERENCES classes(id) ON DELETE CASCADE,
    subject_id INTEGER NOT NULL REFERENCES subjects(id) ON DELETE CASCADE,
    UNIQUE(class_id, subject_id)
);

-- Add foreign keys to users after department/program/class tables exist
ALTER TABLE users ADD CONSTRAINT fk_users_department FOREIGN KEY (department_id) REFERENCES departments(id) ON DELETE SET NULL;
ALTER TABLE users ADD CONSTRAINT fk_users_program FOREIGN KEY (program_id) REFERENCES programs(id) ON DELETE SET NULL;
ALTER TABLE users ADD CONSTRAINT fk_users_class FOREIGN KEY (class_id) REFERENCES classes(id) ON DELETE SET NULL;

-- ===================== KNOWLEDGE BASE =====================
CREATE TABLE IF NOT EXISTS knowledge_base (
    id SERIAL PRIMARY KEY,
    title VARCHAR(500) NOT NULL,
    content TEXT NOT NULL,

    department_id INTEGER REFERENCES departments(id) ON DELETE SET NULL,
    program_id INTEGER REFERENCES programs(id) ON DELETE SET NULL,
    class_id INTEGER REFERENCES classes(id) ON DELETE SET NULL,
    subject_id INTEGER REFERENCES subjects(id) ON DELETE SET NULL,
    chapter VARCHAR(255),
    topic VARCHAR(255),

    status VARCHAR(20) DEFAULT 'published',
    version INTEGER DEFAULT 1,
    content_type VARCHAR(50) DEFAULT 'text',
    tags TEXT,

    created_by INTEGER REFERENCES users(id) ON DELETE SET NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS knowledge_files (
    id SERIAL PRIMARY KEY,
    knowledge_id INTEGER NOT NULL REFERENCES knowledge_base(id) ON DELETE CASCADE,
    filename VARCHAR(500) NOT NULL,
    original_name VARCHAR(500) NOT NULL,
    file_path VARCHAR(1000) NOT NULL,
    file_type VARCHAR(50),
    file_size INTEGER,
    extracted_text TEXT,

    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS knowledge_versions (
    id SERIAL PRIMARY KEY,
    knowledge_id INTEGER NOT NULL REFERENCES knowledge_base(id) ON DELETE CASCADE,
    version_number INTEGER NOT NULL,
    title VARCHAR(500),
    content TEXT,
    changed_by INTEGER REFERENCES users(id) ON DELETE SET NULL,

    created_at TIMESTAMP DEFAULT NOW()
);

-- ===================== AI PROVIDERS =====================
CREATE TABLE IF NOT EXISTS ai_providers (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    slug VARCHAR(100) UNIQUE NOT NULL,
    provider_type VARCHAR(50) NOT NULL,

    api_key_encrypted TEXT,
    api_base_url VARCHAR(500),

    model_name VARCHAR(255),
    temperature FLOAT DEFAULT 0.7,
    top_p FLOAT DEFAULT 0.9,
    max_tokens INTEGER DEFAULT 2048,
    streaming BOOLEAN DEFAULT TRUE,
    timeout INTEGER DEFAULT 30,

    default_prompt TEXT,

    is_active BOOLEAN DEFAULT FALSE,
    is_primary BOOLEAN DEFAULT FALSE,
    is_backup BOOLEAN DEFAULT FALSE,

    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- ===================== CHAT =====================
CREATE TABLE IF NOT EXISTS chat_sessions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(500) DEFAULT 'New Chat',

    department_id INTEGER REFERENCES departments(id) ON DELETE SET NULL,
    program_id INTEGER REFERENCES programs(id) ON DELETE SET NULL,
    class_id INTEGER REFERENCES classes(id) ON DELETE SET NULL,
    subject_id INTEGER REFERENCES subjects(id) ON DELETE SET NULL,

    is_bookmarked BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,

    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_chat_sessions_user ON chat_sessions(user_id);

CREATE TABLE IF NOT EXISTS chat_messages (
    id SERIAL PRIMARY KEY,
    session_id INTEGER NOT NULL REFERENCES chat_sessions(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL,
    content TEXT NOT NULL,

    provider_used VARCHAR(100),
    model_used VARCHAR(255),
    response_time_ms INTEGER,
    tokens_used INTEGER,

    is_liked BOOLEAN,
    feedback TEXT,

    ip_address VARCHAR(45),
    user_agent VARCHAR(500),

    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_chat_messages_session ON chat_messages(session_id);

-- ===================== ANALYTICS =====================
CREATE TABLE IF NOT EXISTS analytics_events (
    id SERIAL PRIMARY KEY,
    event_type VARCHAR(100) NOT NULL,
    user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    department_id INTEGER REFERENCES departments(id) ON DELETE SET NULL,
    subject_id INTEGER REFERENCES subjects(id) ON DELETE SET NULL,

    event_data TEXT,

    ip_address VARCHAR(45),
    user_agent VARCHAR(500),
    device_type VARCHAR(50),

    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_analytics_type ON analytics_events(event_type);
CREATE INDEX idx_analytics_date ON analytics_events(created_at);

CREATE TABLE IF NOT EXISTS trending_questions (
    id SERIAL PRIMARY KEY,
    question_text VARCHAR(1000) NOT NULL,
    normalized_text VARCHAR(1000),
    count INTEGER DEFAULT 1,
    department_id INTEGER REFERENCES departments(id) ON DELETE SET NULL,
    subject_id INTEGER REFERENCES subjects(id) ON DELETE SET NULL,
    last_asked TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_trending_normalized ON trending_questions(normalized_text);

-- ===================== NOTIFICATIONS =====================
CREATE TABLE IF NOT EXISTS notifications (
    id SERIAL PRIMARY KEY,
    title VARCHAR(500) NOT NULL,
    content TEXT NOT NULL,
    notification_type VARCHAR(50) NOT NULL,

    target_type VARCHAR(50) DEFAULT 'all',
    department_id INTEGER REFERENCES departments(id) ON DELETE SET NULL,
    class_id INTEGER REFERENCES classes(id) ON DELETE SET NULL,
    semester VARCHAR(20),

    is_active BOOLEAN DEFAULT TRUE,
    priority VARCHAR(20) DEFAULT 'normal',

    created_by INTEGER REFERENCES users(id) ON DELETE SET NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    expires_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS user_notifications (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    notification_id INTEGER NOT NULL REFERENCES notifications(id) ON DELETE CASCADE,
    is_read BOOLEAN DEFAULT FALSE,
    read_at TIMESTAMP,

    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(user_id, notification_id)
);

-- ===================== DOWNLOADS =====================
CREATE TABLE IF NOT EXISTS downloads (
    id SERIAL PRIMARY KEY,
    title VARCHAR(500) NOT NULL,
    description TEXT,
    category VARCHAR(100) NOT NULL,

    filename VARCHAR(500) NOT NULL,
    original_name VARCHAR(500) NOT NULL,
    file_path VARCHAR(1000) NOT NULL,
    file_type VARCHAR(50),
    file_size INTEGER,

    department_id INTEGER REFERENCES departments(id) ON DELETE SET NULL,
    program_id INTEGER REFERENCES programs(id) ON DELETE SET NULL,
    class_id INTEGER REFERENCES classes(id) ON DELETE SET NULL,
    subject_id INTEGER REFERENCES subjects(id) ON DELETE SET NULL,

    download_count INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    sort_order INTEGER DEFAULT 0,

    uploaded_by INTEGER REFERENCES users(id) ON DELETE SET NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- ===================== GALLERY =====================
CREATE TABLE IF NOT EXISTS gallery_albums (
    id SERIAL PRIMARY KEY,
    title VARCHAR(500) NOT NULL,
    description TEXT,
    cover_image VARCHAR(500),

    department_id INTEGER REFERENCES departments(id) ON DELETE SET NULL,

    is_active BOOLEAN DEFAULT TRUE,
    sort_order INTEGER DEFAULT 0,

    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS gallery_images (
    id SERIAL PRIMARY KEY,
    album_id INTEGER NOT NULL REFERENCES gallery_albums(id) ON DELETE CASCADE,
    title VARCHAR(500),
    image VARCHAR(500) NOT NULL,
    sort_order INTEGER DEFAULT 0,

    created_at TIMESTAMP DEFAULT NOW()
);

-- ===================== CMS =====================
CREATE TABLE IF NOT EXISTS cms_pages (
    id SERIAL PRIMARY KEY,
    title VARCHAR(500) NOT NULL,
    slug VARCHAR(500) UNIQUE NOT NULL,
    content TEXT,
    meta_title VARCHAR(500),
    meta_description TEXT,

    page_type VARCHAR(50) DEFAULT 'custom',
    banner_image VARCHAR(500),
    is_published BOOLEAN DEFAULT TRUE,
    show_in_menu BOOLEAN DEFAULT TRUE,
    menu_order INTEGER DEFAULT 0,
    parent_id INTEGER REFERENCES cms_pages(id) ON DELETE SET NULL,

    created_by INTEGER REFERENCES users(id) ON DELETE SET NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_cms_pages_slug ON cms_pages(slug);

CREATE TABLE IF NOT EXISTS cms_sections (
    id SERIAL PRIMARY KEY,
    page_id INTEGER NOT NULL REFERENCES cms_pages(id) ON DELETE CASCADE,
    section_key VARCHAR(100) NOT NULL,
    title VARCHAR(500),
    content TEXT,
    image VARCHAR(500),
    extra_data TEXT,
    sort_order INTEGER DEFAULT 0,
    is_visible BOOLEAN DEFAULT TRUE,

    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- ===================== EVENTS =====================
CREATE TABLE IF NOT EXISTS events (
    id SERIAL PRIMARY KEY,
    title VARCHAR(500) NOT NULL,
    slug VARCHAR(500) UNIQUE NOT NULL,
    description TEXT,
    content TEXT,
    image VARCHAR(500),

    venue VARCHAR(500),
    event_date TIMESTAMP,
    end_date TIMESTAMP,

    department_id INTEGER REFERENCES departments(id) ON DELETE SET NULL,

    is_active BOOLEAN DEFAULT TRUE,
    is_featured BOOLEAN DEFAULT FALSE,

    created_by INTEGER REFERENCES users(id) ON DELETE SET NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_events_slug ON events(slug);

-- ===================== NEWS =====================
CREATE TABLE IF NOT EXISTS news (
    id SERIAL PRIMARY KEY,
    title VARCHAR(500) NOT NULL,
    slug VARCHAR(500) UNIQUE NOT NULL,
    excerpt TEXT,
    content TEXT,
    image VARCHAR(500),

    category VARCHAR(100),
    department_id INTEGER REFERENCES departments(id) ON DELETE SET NULL,

    is_published BOOLEAN DEFAULT TRUE,
    is_featured BOOLEAN DEFAULT FALSE,
    views INTEGER DEFAULT 0,

    created_by INTEGER REFERENCES users(id) ON DELETE SET NULL,
    published_at TIMESTAMP DEFAULT NOW(),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_news_slug ON news(slug);

-- ===================== FAQS =====================
CREATE TABLE IF NOT EXISTS faqs (
    id SERIAL PRIMARY KEY,
    question VARCHAR(1000) NOT NULL,
    answer TEXT NOT NULL,
    category VARCHAR(100),

    department_id INTEGER REFERENCES departments(id) ON DELETE SET NULL,

    is_active BOOLEAN DEFAULT TRUE,
    sort_order INTEGER DEFAULT 0,

    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- ===================== AUDIT LOGS =====================
CREATE TABLE IF NOT EXISTS audit_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    action VARCHAR(255) NOT NULL,
    resource_type VARCHAR(100),
    resource_id INTEGER,
    details TEXT,

    ip_address VARCHAR(45),
    user_agent VARCHAR(500),

    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_audit_logs_date ON audit_logs(created_at);
CREATE INDEX idx_audit_logs_user ON audit_logs(user_id);

-- ===================== SEED DATA =====================

-- Default institution
INSERT INTO institution (name, institution_type, about, vision, mission, address, email, phone)
VALUES (
    'Government Graduate College Jhang',
    'college',
    'Government Graduate College Jhang is one of the most prestigious educational institutions in the region, committed to providing quality education and producing skilled graduates who contribute to national development.',
    'To be a leading institution of higher education, recognized for academic excellence, research, and community service.',
    'To provide quality education in a stimulating environment that promotes intellectual growth, character building, and professional development.',
    'College Road, Jhang, Punjab, Pakistan',
    'info@ggcjhang.edu.pk',
    '+92-47-7620001'
) ON CONFLICT DO NOTHING;

-- Default super admin
-- Password: Admin@123 (bcrypt hash)
INSERT INTO users (email, password_hash, role, full_name, is_active, email_verified)
VALUES (
    'admin@ggcjhang.edu.pk',
    '$2b$12$LJ3m4ys3Lk0TSwMCfVBXNOJqGx.NpaOQpiCOzCNjBE/ZBkyQSHPeG',
    'super_admin',
    'System Administrator',
    TRUE,
    TRUE
) ON CONFLICT (email) DO NOTHING;

-- Default AI providers (no keys — admin configures from panel)
INSERT INTO ai_providers (name, slug, provider_type, model_name, is_active, is_primary) VALUES
    ('Google Gemini', 'google-gemini', 'gemini', 'gemini-2.0-flash', FALSE, FALSE),
    ('Groq', 'groq', 'groq', 'llama-3.3-70b-versatile', FALSE, FALSE),
    ('OpenRouter', 'openrouter', 'openrouter', 'meta-llama/llama-3.3-70b-instruct', FALSE, FALSE),
    ('HuggingFace', 'huggingface', 'huggingface', 'mistralai/Mistral-7B-Instruct-v0.3', FALSE, FALSE),
    ('DeepSeek', 'deepseek', 'deepseek', 'deepseek-chat', FALSE, FALSE)
ON CONFLICT (slug) DO NOTHING;

-- Default CMS pages
INSERT INTO cms_pages (title, slug, page_type, is_published, show_in_menu, menu_order) VALUES
    ('Home', 'home', 'home', TRUE, TRUE, 1),
    ('About Us', 'about', 'about', TRUE, TRUE, 2),
    ('Departments', 'departments', 'department', TRUE, TRUE, 3),
    ('Admission', 'admission', 'custom', TRUE, TRUE, 4),
    ('Downloads', 'downloads', 'custom', TRUE, TRUE, 5),
    ('Gallery', 'gallery', 'custom', TRUE, TRUE, 6),
    ('News', 'news', 'custom', TRUE, TRUE, 7),
    ('Events', 'events', 'custom', TRUE, TRUE, 8),
    ('FAQ', 'faq', 'custom', TRUE, TRUE, 9),
    ('Contact Us', 'contact', 'contact', TRUE, TRUE, 10),
    ('Privacy Policy', 'privacy-policy', 'custom', TRUE, FALSE, 11),
    ('Terms & Conditions', 'terms', 'custom', TRUE, FALSE, 12)
ON CONFLICT (slug) DO NOTHING;
