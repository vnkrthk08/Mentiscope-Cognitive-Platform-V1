-- ==========================================================
-- PostgreSQL Database Schema for MentiScope Gq Engine
-- ==========================================================

-- 1. Assessment Sessions Table
CREATE TABLE assessment_sessions (
    id VARCHAR(36) PRIMARY KEY,
    student_id VARCHAR(100) NOT NULL,
    session_id VARCHAR(100) NOT NULL,
    module_id VARCHAR(50) NOT NULL,
    construct VARCHAR(50) NOT NULL,
    status VARCHAR(20) DEFAULT 'IN_PROGRESS',
    current_level INTEGER DEFAULT 1,
    started_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    ended_at TIMESTAMP WITH TIME ZONE
);
CREATE INDEX idx_assessment_sessions_student_id ON assessment_sessions(student_id);
CREATE INDEX idx_assessment_sessions_session_id ON assessment_sessions(session_id);

-- 2. Question Instances (The generated variants shown to user)
CREATE TABLE question_instances (
    id VARCHAR(36) PRIMARY KEY,
    session_id VARCHAR(36) NOT NULL REFERENCES assessment_sessions(id) ON DELETE CASCADE,
    question_id VARCHAR(100) NOT NULL,
    template_id VARCHAR(100) NOT NULL,
    module VARCHAR(50) NOT NULL,
    difficulty INTEGER DEFAULT 1,
    question_json JSONB NOT NULL,
    correct_answer VARCHAR(200) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_question_instances_session_id ON question_instances(session_id);

-- 3. Student Responses (Includes rich behavioral telemetry)
CREATE TABLE student_responses (
    id VARCHAR(36) PRIMARY KEY,
    session_id VARCHAR(36) NOT NULL REFERENCES assessment_sessions(id) ON DELETE CASCADE,
    question_id VARCHAR(100) NOT NULL,
    module_name VARCHAR(50) DEFAULT 'GQ',
    difficulty_level INTEGER DEFAULT 1,
    response TEXT NOT NULL,
    correct BOOLEAN NOT NULL,
    reaction_time_ms INTEGER NOT NULL,
    hover_duration_ms INTEGER DEFAULT 0,
    idle_time_ms INTEGER DEFAULT 0,
    drag_distance DOUBLE PRECISION DEFAULT 0.0,
    answer_changes INTEGER DEFAULT 0,
    confidence_score INTEGER DEFAULT 3,
    attempt_number INTEGER DEFAULT 1,
    hint_used BOOLEAN DEFAULT FALSE,
    answered_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_student_responses_session_id ON student_responses(session_id);
CREATE INDEX idx_student_responses_question_id ON student_responses(question_id);

-- 4. Assessment Events (Granular frontend telemetry logs)
CREATE TABLE assessment_events (
    id VARCHAR(36) PRIMARY KEY,
    session_id VARCHAR(100) NOT NULL,
    event_type VARCHAR(50) NOT NULL,
    task_id VARCHAR(100),
    item_id VARCHAR(100),
    correct BOOLEAN,
    reaction_time_ms INTEGER,
    difficulty_level INTEGER,
    event_metadata JSONB,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_assessment_events_session_id ON assessment_events(session_id);
