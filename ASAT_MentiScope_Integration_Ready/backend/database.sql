-- ASAT MentiScope Database Schema
-- Translated to PostgreSQL from original MySQL

CREATE TABLE faculty (
    faculty_id SERIAL PRIMARY KEY,
    username VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    email VARCHAR(255) UNIQUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE students (
    student_id SERIAL PRIMARY KEY,
    faculty_id INTEGER REFERENCES faculty(faculty_id) ON DELETE SET NULL,
    full_name VARCHAR(255) NOT NULL,
    student_id_number VARCHAR(100) UNIQUE,
    age INTEGER,
    grade VARCHAR(50),
    school VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE sessions (
    session_id SERIAL PRIMARY KEY,
    student_id INTEGER NOT NULL REFERENCES students(student_id) ON DELETE CASCADE,
    session_uuid VARCHAR(255) UNIQUE NOT NULL,
    status VARCHAR(50) DEFAULT 'pending',
    start_time TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    end_time TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE events (
    event_id SERIAL PRIMARY KEY,
    student_id INTEGER NOT NULL REFERENCES students(student_id) ON DELETE CASCADE,
    session_id INTEGER NOT NULL REFERENCES sessions(session_id) ON DELETE CASCADE,
    construct VARCHAR(100),
    task_id VARCHAR(100),
    item_id INTEGER,
    stimulus VARCHAR(255),
    event_type VARCHAR(50),
    response VARCHAR(255),
    correct BOOLEAN,
    reaction_time_ms INTEGER,
    error_type VARCHAR(100),
    difficulty_level INTEGER,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE scores (
    score_id SERIAL PRIMARY KEY,
    student_id INTEGER NOT NULL REFERENCES students(student_id) ON DELETE CASCADE,
    session_uuid VARCHAR(255),
    
    -- Per-module scores
    sustained_score FLOAT,
    selective_score FLOAT,
    divided_score FLOAT,
    executive_score FLOAT,
    
    -- SDK-compliant outputs
    raw_score FLOAT,
    normalized_score FLOAT,
    percentile INTEGER,
    sub_scores JSONB,
    confidence_score FLOAT,
    
    -- Composite
    overall_score FLOAT,
    module_results JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE reports (
    report_id SERIAL PRIMARY KEY,
    student_id INTEGER NOT NULL REFERENCES students(student_id) ON DELETE CASCADE,
    session_id INTEGER NOT NULL REFERENCES sessions(session_id) ON DELETE CASCADE,
    behavioral_metrics JSONB,
    recommendations JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
