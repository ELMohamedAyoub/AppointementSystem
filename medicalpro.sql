-- Database Creation
CREATE DATABASE IF NOT EXISTS medicalpro_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE medicalpro_db;

-- Drop tables in reverse order of foreign key dependencies
DROP TABLE IF EXISTS medical_records;
DROP TABLE IF EXISTS appointments;
DROP TABLE IF EXISTS prescriptions;
DROP TABLE IF EXISTS medications;
DROP TABLE IF EXISTS insurance_info;
DROP TABLE IF EXISTS patient_emergency_contacts;
DROP TABLE IF EXISTS doctor_specialties;
DROP TABLE IF EXISTS specialties;
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS audit_log;

-- Create Users Table with enhanced security
CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL COMMENT 'Stores securely hashed passwords using bcrypt',
    email VARCHAR(100) UNIQUE NOT NULL,
    role ENUM('patient', 'doctor', 'secretary', 'admin') NOT NULL,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    phone_number VARCHAR(20),
    date_of_birth DATE,
    gender ENUM('M', 'F', 'O', 'P') COMMENT 'M: Male, F: Female, O: Other, P: Prefer not to say',
    address TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    last_login TIMESTAMP NULL,
    failed_login_attempts INT DEFAULT 0,
    password_reset_token VARCHAR(100),
    password_reset_expires TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_users_role (role),
    INDEX idx_users_email (email),
    INDEX idx_users_username (username)
);

-- Create Specialties Table
CREATE TABLE specialties (
    specialty_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create Doctor Specialties Table (Many-to-Many relationship)
CREATE TABLE doctor_specialties (
    doctor_id INT NOT NULL,
    specialty_id INT NOT NULL,
    years_experience INT,
    certification_number VARCHAR(50),
    certification_expiry DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (doctor_id, specialty_id),
    FOREIGN KEY (doctor_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (specialty_id) REFERENCES specialties(specialty_id) ON DELETE CASCADE
);

-- Create Insurance Information Table
CREATE TABLE insurance_info (
    insurance_id INT AUTO_INCREMENT PRIMARY KEY,
    patient_id INT NOT NULL,
    provider_name VARCHAR(100) NOT NULL,
    policy_number VARCHAR(50) NOT NULL,
    group_number VARCHAR(50),
    coverage_start_date DATE NOT NULL,
    coverage_end_date DATE,
    is_primary BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES users(user_id) ON DELETE CASCADE,
    INDEX idx_insurance_patient (patient_id)
);

-- Create Emergency Contacts Table
CREATE TABLE patient_emergency_contacts (
    contact_id INT AUTO_INCREMENT PRIMARY KEY,
    patient_id INT NOT NULL,
    contact_name VARCHAR(100) NOT NULL,
    relationship VARCHAR(50) NOT NULL,
    phone_number VARCHAR(20) NOT NULL,
    is_primary BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES users(user_id) ON DELETE CASCADE,
    INDEX idx_emergency_patient (patient_id)
);

-- Create Medications Table
CREATE TABLE medications (
    medication_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    generic_name VARCHAR(100),
    manufacturer VARCHAR(100),
    dosage_form VARCHAR(50),
    strength VARCHAR(50),
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_medication_name (name)
);

-- Create Prescriptions Table
CREATE TABLE prescriptions (
    prescription_id INT AUTO_INCREMENT PRIMARY KEY,
    patient_id INT NOT NULL,
    doctor_id INT NOT NULL,
    medication_id INT NOT NULL,
    dosage VARCHAR(50) NOT NULL,
    frequency VARCHAR(50) NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE,
    refills_remaining INT DEFAULT 0,
    status ENUM('active', 'completed', 'cancelled') DEFAULT 'active',
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES users(user_id) ON DELETE RESTRICT,
    FOREIGN KEY (doctor_id) REFERENCES users(user_id) ON DELETE RESTRICT,
    FOREIGN KEY (medication_id) REFERENCES medications(medication_id) ON DELETE RESTRICT,
    INDEX idx_prescription_patient (patient_id),
    INDEX idx_prescription_doctor (doctor_id)
);

-- Create Appointments Table with enhanced features
CREATE TABLE appointments (
    appointment_id INT AUTO_INCREMENT PRIMARY KEY,
    patient_id INT NOT NULL,
    doctor_id INT NOT NULL,
    appointment_date DATE NOT NULL,
    appointment_time TIME NOT NULL,
    duration INT DEFAULT 30 COMMENT 'Duration in minutes',
    type ENUM('checkup', 'consultation', 'follow-up', 'emergency', 'procedure') NOT NULL,
    status ENUM('pending', 'confirmed', 'canceled', 'completed', 'no-show') DEFAULT 'pending',
    reason TEXT,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES users(user_id) ON DELETE RESTRICT ON UPDATE CASCADE,
    FOREIGN KEY (doctor_id) REFERENCES users(user_id) ON DELETE RESTRICT ON UPDATE CASCADE,
    INDEX idx_appointments_doctor_date (doctor_id, appointment_date),
    INDEX idx_appointments_patient (patient_id),
    INDEX idx_appointments_date (appointment_date),
    INDEX idx_appointments_status (status)
);

-- Create Medical Records Table with enhanced features
CREATE TABLE medical_records (
    record_id INT AUTO_INCREMENT PRIMARY KEY,
    patient_id INT NOT NULL,
    doctor_id INT NOT NULL,
    record_date DATE NOT NULL,
    visit_type ENUM('initial', 'follow-up', 'emergency', 'routine') NOT NULL,
    chief_complaint TEXT,
    diagnosis VARCHAR(255) NOT NULL,
    diagnosis_code VARCHAR(20) COMMENT 'ICD-10 code',
    treatment_plan TEXT,
    follow_up_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES users(user_id) ON DELETE RESTRICT ON UPDATE CASCADE,
    FOREIGN KEY (doctor_id) REFERENCES users(user_id) ON DELETE RESTRICT ON UPDATE CASCADE,
    INDEX idx_medical_records_patient (patient_id),
    INDEX idx_medical_records_date (record_date),
    INDEX idx_medical_records_doctor (doctor_id)
);

-- Create Audit Log table with enhanced tracking
CREATE TABLE audit_log (
    log_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT COMMENT 'User who performed the action',
    action_type VARCHAR(50) NOT NULL,
    table_name VARCHAR(50) NOT NULL,
    record_id INT COMMENT 'ID of the record affected',
    old_values JSON COMMENT 'Previous values before change',
    new_values JSON COMMENT 'New values after change',
    ip_address VARCHAR(45),
    user_agent TEXT,
    action_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE SET NULL ON UPDATE CASCADE,
    INDEX idx_audit_user (user_id),
    INDEX idx_audit_timestamp (action_timestamp)
);

-- Insert Specialties
INSERT INTO specialties (name, description) VALUES
('Cardiology', 'Heart and cardiovascular system specialist'),
('Dermatology', 'Skin, hair, and nail conditions specialist'),
('Neurology', 'Nervous system and brain disorders specialist'),
('Pediatrics', 'Child and adolescent health specialist'),
('Orthopedics', 'Bone and joint conditions specialist'),
('Ophthalmology', 'Eye and vision care specialist'),
('ENT', 'Ear, nose, and throat specialist'),
('Internal Medicine', 'Adult disease prevention and treatment specialist');

-- Insert Medications
INSERT INTO medications (name, generic_name, manufacturer, dosage_form, strength, description) VALUES
('Lipitor', 'Atorvastatin', 'Pfizer', 'Tablet', '20mg', 'Cholesterol-lowering medication'),
('Ventolin', 'Albuterol', 'GlaxoSmithKline', 'Inhaler', '90mcg', 'Bronchodilator for asthma'),
('Zoloft', 'Sertraline', 'Pfizer', 'Tablet', '50mg', 'Antidepressant medication'),
('Amoxicillin', 'Amoxicillin', 'Various', 'Capsule', '500mg', 'Antibiotic for bacterial infections'),
('Metformin', 'Metformin', 'Various', 'Tablet', '850mg', 'Diabetes medication');

-- Insert Sample Users with more realistic data
INSERT INTO users (username, password, email, role, first_name, last_name, phone_number, date_of_birth, gender, address) VALUES
('admin', '$2a$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBAQH/8.5JQKHy', 'admin@medicalpro.com', 'admin', 'Admin', 'User', '555-0001', '1980-01-01', 'M', '123 Admin St, Medical City'),
('dr.smith', '$2a$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBAQH/8.5JQKHy', 'smith@medicalpro.com', 'doctor', 'John', 'Smith', '555-0002', '1975-05-15', 'M', '456 Doctor Ave, Medical City'),
('dr.johnson', '$2a$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBAQH/8.5JQKHy', 'johnson@medicalpro.com', 'doctor', 'Sarah', 'Johnson', '555-0003', '1982-08-20', 'F', '789 Doctor Blvd, Medical City'),
('secretary', '$2a$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBAQH/8.5JQKHy', 'secretary@medicalpro.com', 'secretary', 'Mary', 'Williams', '555-0004', '1990-03-10', 'F', '321 Office Rd, Medical City'),
('patient1', '$2a$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBAQH/8.5JQKHy', 'patient1@email.com', 'patient', 'James', 'Wilson', '555-0005', '1988-11-25', 'M', '654 Patient St, Medical City'),
('patient2', '$2a$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBAQH/8.5JQKHy', 'patient2@email.com', 'patient', 'Emma', 'Brown', '555-0006', '1992-07-15', 'F', '987 Patient Ave, Medical City');

-- Get User IDs for relationships
SET @admin_id = (SELECT user_id FROM users WHERE username = 'admin');
SET @secretary_id = (SELECT user_id FROM users WHERE username = 'secretary');
SET @dr_smith_id = (SELECT user_id FROM users WHERE username = 'dr.smith');
SET @dr_johnson_id = (SELECT user_id FROM users WHERE username = 'dr.johnson');
SET @patient1_id = (SELECT user_id FROM users WHERE username = 'patient1');
SET @patient2_id = (SELECT user_id FROM users WHERE username = 'patient2');

-- Assign Doctor Specialties
INSERT INTO doctor_specialties (doctor_id, specialty_id, years_experience, certification_number) VALUES
(@dr_smith_id, 1, 15, 'CARD-12345'), -- Cardiology
(@dr_smith_id, 3, 15, 'NEURO-12345'), -- Neurology
(@dr_johnson_id, 2, 10, 'DERM-67890'), -- Dermatology
(@dr_johnson_id, 5, 10, 'ORTHO-67890'); -- Orthopedics

-- Insert Insurance Information
INSERT INTO insurance_info (patient_id, provider_name, policy_number, group_number, coverage_start_date, coverage_end_date) VALUES
(@patient1_id, 'Blue Cross Blue Shield', 'BCBS123456', 'GRP789', '2023-01-01', '2024-12-31'),
(@patient2_id, 'Aetna', 'AET789012', 'GRP456', '2023-01-01', '2024-12-31');

-- Insert Emergency Contacts
INSERT INTO patient_emergency_contacts (patient_id, contact_name, relationship, phone_number, is_primary) VALUES
(@patient1_id, 'Jane Wilson', 'Spouse', '555-0007', TRUE),
(@patient2_id, 'Michael Brown', 'Parent', '555-0008', TRUE);

-- Insert Sample Appointments with more realistic data
INSERT INTO appointments (patient_id, doctor_id, appointment_date, appointment_time, duration, type, status, reason) VALUES
(@patient1_id, @dr_smith_id, CURDATE() + INTERVAL 1 DAY, '09:00:00', 30, 'checkup', 'confirmed', 'Annual physical examination'),
(@patient2_id, @dr_smith_id, CURDATE() + INTERVAL 1 DAY, '09:30:00', 45, 'consultation', 'pending', 'Chest pain evaluation'),
(@patient1_id, @dr_johnson_id, CURDATE() + INTERVAL 2 DAY, '14:00:00', 30, 'follow-up', 'pending', 'Skin condition follow-up'),
(@patient2_id, @dr_johnson_id, CURDATE() + INTERVAL 3 DAY, '10:00:00', 60, 'procedure', 'canceled', 'Joint injection'),
(@patient1_id, @dr_smith_id, CURDATE() - INTERVAL 7 DAY, '11:00:00', 30, 'checkup', 'completed', 'Blood work review');

-- Insert Sample Medical Records with more detailed information
INSERT INTO medical_records (patient_id, doctor_id, record_date, visit_type, chief_complaint, diagnosis, diagnosis_code, treatment_plan, follow_up_date) VALUES
(@patient1_id, @dr_smith_id, CURDATE() - INTERVAL 10 DAY, 'initial', 'Fever and cough for 3 days', 'Influenza', 'J11.1', 'Rest, fluids, symptomatic treatment', CURDATE() + INTERVAL 7 DAY),
(@patient1_id, @dr_smith_id, CURDATE() - INTERVAL 5 DAY, 'follow-up', 'Follow-up for influenza', 'Influenza - Resolving', 'J11.1', 'Continue rest, monitor symptoms', NULL),
(@patient2_id, @dr_johnson_id, CURDATE() - INTERVAL 14 DAY, 'initial', 'Rash on forearm', 'Contact Dermatitis', 'L25.9', 'Topical corticosteroid cream', CURDATE() + INTERVAL 14 DAY),
(@patient2_id, @dr_johnson_id, CURDATE() - INTERVAL 3 DAY, 'follow-up', 'Follow-up for dermatitis', 'Contact Dermatitis - Improving', 'L25.9', 'Continue cream, avoid irritants', NULL);

-- Insert Sample Prescriptions
INSERT INTO prescriptions (patient_id, doctor_id, medication_id, dosage, frequency, start_date, end_date, refills_remaining, status) VALUES
(@patient1_id, @dr_smith_id, 1, '20mg', 'Once daily', CURDATE() - INTERVAL 10 DAY, CURDATE() + INTERVAL 20 DAY, 2, 'active'),
(@patient2_id, @dr_johnson_id, 4, '500mg', 'Three times daily', CURDATE() - INTERVAL 14 DAY, CURDATE() + INTERVAL 7 DAY, 0, 'active');

-- Create enhanced stored procedures
DELIMITER //

-- Procedure to check doctor availability
CREATE PROCEDURE CheckDoctorAvailability(
    IN p_doctor_id INT,
    IN p_date DATE,
    IN p_time TIME,
    IN p_duration INT
)
BEGIN
    DECLARE is_available BOOLEAN DEFAULT TRUE;
    
    -- Check if there are any overlapping appointments
    SELECT EXISTS (
        SELECT 1 FROM appointments 
        WHERE doctor_id = p_doctor_id 
        AND appointment_date = p_date
        AND (
            (appointment_time <= p_time AND appointment_time + INTERVAL duration MINUTE > p_time)
            OR (appointment_time < p_time + INTERVAL p_duration MINUTE AND appointment_time + INTERVAL duration MINUTE >= p_time + INTERVAL p_duration MINUTE)
        )
    ) INTO is_available;
    
    SELECT is_available AS available;
END //

-- Procedure to get patient's complete medical history
CREATE PROCEDURE GetPatientCompleteHistory(IN p_patient_id INT)
BEGIN
    -- Get basic patient information
    SELECT 
        u.first_name, u.last_name, u.date_of_birth, u.gender,
        i.provider_name, i.policy_number
    FROM users u
    LEFT JOIN insurance_info i ON u.user_id = i.patient_id
    WHERE u.user_id = p_patient_id;
    
    -- Get medical records
    SELECT 
        mr.record_date, mr.visit_type, mr.chief_complaint, 
        mr.diagnosis, mr.diagnosis_code, mr.treatment_plan,
        CONCAT(d.first_name, ' ', d.last_name) AS doctor_name
    FROM medical_records mr
    JOIN users d ON mr.doctor_id = d.user_id
    WHERE mr.patient_id = p_patient_id
    ORDER BY mr.record_date DESC;
    
    -- Get active prescriptions
    SELECT 
        m.name, p.dosage, p.frequency, p.start_date, p.end_date,
        p.refills_remaining, CONCAT(d.first_name, ' ', d.last_name) AS prescribed_by
    FROM prescriptions p
    JOIN medications m ON p.medication_id = m.medication_id
    JOIN users d ON p.doctor_id = d.user_id
    WHERE p.patient_id = p_patient_id AND p.status = 'active';
    
    -- Get upcoming appointments
    SELECT 
        a.appointment_date, a.appointment_time, a.type, a.status,
        CONCAT(d.first_name, ' ', d.last_name) AS doctor_name
    FROM appointments a
    JOIN users d ON a.doctor_id = d.user_id
    WHERE a.patient_id = p_patient_id
    AND a.appointment_date >= CURDATE()
    ORDER BY a.appointment_date, a.appointment_time;
END //

-- Procedure to get doctor's schedule
CREATE PROCEDURE GetDoctorSchedule(
    IN p_doctor_id INT,
    IN p_start_date DATE,
    IN p_end_date DATE
)
BEGIN
    SELECT 
        a.appointment_date,
        a.appointment_time,
        a.duration,
        a.type,
        a.status,
        CONCAT(p.first_name, ' ', p.last_name) AS patient_name,
        a.reason
    FROM appointments a
    JOIN users p ON a.patient_id = p.user_id
    WHERE a.doctor_id = p_doctor_id
    AND a.appointment_date BETWEEN p_start_date AND p_end_date
    ORDER BY a.appointment_date, a.appointment_time;
END //

-- Procedure to search patients
CREATE PROCEDURE SearchPatients(
    IN p_search_term VARCHAR(100)
)
BEGIN
    SELECT 
        u.user_id,
        u.first_name,
        u.last_name,
        u.date_of_birth,
        u.phone_number,
        i.provider_name,
        i.policy_number
    FROM users u
    LEFT JOIN insurance_info i ON u.user_id = i.patient_id
    WHERE u.role = 'patient'
    AND (
        u.first_name LIKE CONCAT('%', p_search_term, '%')
        OR u.last_name LIKE CONCAT('%', p_search_term, '%')
        OR u.phone_number LIKE CONCAT('%', p_search_term, '%')
        OR i.policy_number LIKE CONCAT('%', p_search_term, '%')
    );
END //

DELIMITER ;

-- Create enhanced views
CREATE VIEW doctor_schedule_view AS
SELECT 
    a.appointment_id,
    a.appointment_date,
    a.appointment_time,
    a.duration,
    a.type,
    a.status,
    CONCAT(p.first_name, ' ', p.last_name) AS patient_name,
    p.phone_number AS patient_phone,
    a.reason
FROM appointments a
JOIN users p ON a.patient_id = p.user_id
WHERE a.appointment_date >= CURDATE()
ORDER BY a.appointment_date, a.appointment_time;

CREATE VIEW patient_medical_summary_view AS
SELECT 
    u.user_id,
    CONCAT(u.first_name, ' ', u.last_name) AS patient_name,
    u.date_of_birth,
    u.gender,
    i.provider_name,
    i.policy_number,
    COUNT(DISTINCT mr.record_id) AS total_visits,
    COUNT(DISTINCT p.prescription_id) AS active_prescriptions,
    MAX(a.appointment_date) AS last_appointment
FROM users u
LEFT JOIN insurance_info i ON u.user_id = i.patient_id
LEFT JOIN medical_records mr ON u.user_id = mr.patient_id
LEFT JOIN prescriptions p ON u.user_id = p.patient_id AND p.status = 'active'
LEFT JOIN appointments a ON u.user_id = a.patient_id
WHERE u.role = 'patient'
GROUP BY u.user_id;

-- Create triggers for enhanced auditing
DELIMITER //

CREATE TRIGGER after_appointment_status_change
AFTER UPDATE ON appointments
FOR EACH ROW
BEGIN
    IF OLD.status != NEW.status THEN
        INSERT INTO audit_log (user_id, action_type, table_name, record_id, old_values, new_values)
        VALUES (
            @admin_id, -- This should be replaced with the actual user ID in the application
            'UPDATE',
            'appointments',
            NEW.appointment_id,
            JSON_OBJECT('status', OLD.status),
            JSON_OBJECT('status', NEW.status)
        );
    END IF;
END //

CREATE TRIGGER after_medical_record_insert
AFTER INSERT ON medical_records
FOR EACH ROW
BEGIN
    INSERT INTO audit_log (user_id, action_type, table_name, record_id, new_values)
    VALUES (
        NEW.doctor_id,
        'INSERT',
        'medical_records',
        NEW.record_id,
        JSON_OBJECT(
            'patient_id', NEW.patient_id,
            'diagnosis', NEW.diagnosis,
            'record_date', NEW.record_date
        )
    );
END //

DELIMITER ;
