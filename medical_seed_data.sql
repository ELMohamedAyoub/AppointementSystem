USE medicalpro;

-- Insert roles
INSERT INTO roles (name, description) VALUES
('admin', 'Administrator with full access'),
('doctor', 'Medical doctor'),
('patient', 'Patient user'),
('receptionist', 'Front desk staff'),
('nurse', 'Nursing staff');

-- Insert permissions
INSERT INTO permissions (name, description) VALUES
('manage_users', 'Create, update, delete users'),
('view_all_patients', 'View all patient data'),
('manage_appointments', 'Create, update, delete appointments'),
('view_own_appointments', 'View own appointments'),
('create_medical_records', 'Create medical records'),
('view_medical_records', 'View medical records'),
('create_prescriptions', 'Create prescriptions'),
('view_prescriptions', 'View prescriptions'),
('manage_doctors', 'Manage doctor profiles and availability'),
('manage_medications', 'Manage medication database'),
('generate_reports', 'Generate system reports');

-- Assign permissions to roles
-- Admin role permissions
INSERT INTO role_permissions (role_id, permission_id) 
SELECT 
    (SELECT id FROM roles WHERE name = 'admin'),
    id
FROM permissions;

-- Doctor role permissions
INSERT INTO role_permissions (role_id, permission_id) 
SELECT 
    (SELECT id FROM roles WHERE name = 'doctor'),
    id
FROM permissions 
WHERE name IN (
    'view_own_appointments',
    'view_medical_records',
    'create_medical_records',
    'create_prescriptions',
    'view_prescriptions',
    'view_all_patients'
);

-- Patient role permissions
INSERT INTO role_permissions (role_id, permission_id) 
SELECT 
    (SELECT id FROM roles WHERE name = 'patient'),
    id
FROM permissions 
WHERE name IN (
    'view_own_appointments',
    'view_prescriptions'
);

-- Receptionist role permissions
INSERT INTO role_permissions (role_id, permission_id) 
SELECT 
    (SELECT id FROM roles WHERE name = 'receptionist'),
    id
FROM permissions 
WHERE name IN (
    'manage_appointments',
    'view_all_patients',
    'view_medical_records'
);

-- Nurse role permissions
INSERT INTO role_permissions (role_id, permission_id) 
SELECT 
    (SELECT id FROM roles WHERE name = 'nurse'),
    id
FROM permissions 
WHERE name IN (
    'view_all_patients',
    'view_medical_records',
    'create_medical_records',
    'view_prescriptions',
    'view_own_appointments'
);

-- Insert appointment statuses
INSERT INTO appointment_status (name, description, color) VALUES
('Scheduled', 'Appointment is scheduled', '#4CAF50'),
('Confirmed', 'Appointment is confirmed', '#2196F3'),
('In Progress', 'Patient is currently with the doctor', '#FF9800'),
('Completed', 'Appointment has been completed', '#9C27B0'),
('Cancelled', 'Appointment was cancelled', '#F44336'),
('No-show', 'Patient did not show up', '#607D8B'),
('Rescheduled', 'Appointment was rescheduled', '#00BCD4'),
('Waiting', 'Patient is in the waiting room', '#FFEB3B'),
('Declined', 'Doctor declined the appointment', '#795548');

-- Insert specialties
INSERT INTO specialties (name, description) VALUES
('Cardiology', 'Deals with disorders of the heart and cardiovascular system'),
('Dermatology', 'Focuses on diseases of the skin'),
('Gastroenterology', 'Focuses on the digestive system and its disorders'),
('Neurology', 'Deals with disorders of the nervous system'),
('Orthopedics', 'Focuses on the musculoskeletal system'),
('Pediatrics', 'Medical care of infants, children, and adolescents'),
('Psychiatry', 'Diagnosis, prevention, and treatment of mental disorders'),
('Ophthalmology', 'Deals with the anatomy and diseases of the eye'),
('Gynecology', 'Deals with the health of the female reproductive system'),
('Urology', 'Focuses on the urinary tract system and male reproductive organs');

-- Insert admin user
INSERT INTO users (email, password, role_id, is_active, email_verified) VALUES
('admin@medicalpro.com', '$2b$12$A2oRmTEXXBg7CHZvnxL27.QZJ8zHALHvzgRHgJqP.n0XMhfULkrPi', (SELECT id FROM roles WHERE name = 'admin'), TRUE, TRUE);

INSERT INTO user_profiles (user_id, first_name, last_name, phone) VALUES
((SELECT id FROM users WHERE email = 'admin@medicalpro.com'), 'System', 'Administrator', '123-456-7890');

-- Insert sample medications
INSERT INTO medications (name, description, manufacturer) VALUES
('Amoxicillin', 'Antibiotic used to treat bacterial infections', 'Generic Pharma'),
('Lisinopril', 'ACE inhibitor used to treat high blood pressure', 'Generic Pharma'),
('Metformin', 'Used to treat type 2 diabetes', 'Generic Pharma'),
('Atorvastatin', 'Statin used to prevent cardiovascular disease', 'Generic Pharma'),
('Albuterol', 'Bronchodilator used to treat asthma', 'Generic Pharma'),
('Omeprazole', 'Proton-pump inhibitor used to treat gastric conditions', 'Generic Pharma'),
('Levothyroxine', 'Used to treat thyroid hormone deficiency', 'Generic Pharma'),
('Ibuprofen', 'NSAID used for pain relief and inflammation', 'Generic Pharma'),
('Sertraline', 'SSRI used to treat depression and anxiety disorders', 'Generic Pharma'),
('Amlodipine', 'Calcium channel blocker used to treat hypertension', 'Generic Pharma');

-- Note: In a real system, you would not add sample doctors and patients in the seed file
-- These would be created through the application UI
-- This is just for demonstration and testing purposes

-- Sample script to add test users (commented out for production use)
/*
-- Add sample doctors
INSERT INTO users (email, password, role_id, is_active, email_verified) VALUES
('doctor1@medicalpro.com', '$2b$12$A2oRmTEXXBg7CHZvnxL27.QZJ8zHALHvzgRHgJqP.n0XMhfULkrPi', (SELECT id FROM roles WHERE name = 'doctor'), TRUE, TRUE),
('doctor2@medicalpro.com', '$2b$12$A2oRmTEXXBg7CHZvnxL27.QZJ8zHALHvzgRHgJqP.n0XMhfULkrPi', (SELECT id FROM roles WHERE name = 'doctor'), TRUE, TRUE);

INSERT INTO user_profiles (user_id, first_name, last_name, phone, gender) VALUES
((SELECT id FROM users WHERE email = 'doctor1@medicalpro.com'), 'John', 'Smith', '123-555-1111', 'Male'),
((SELECT id FROM users WHERE email = 'doctor2@medicalpro.com'), 'Sarah', 'Johnson', '123-555-2222', 'Female');

INSERT INTO doctors (user_id, specialty_id, license_number, biography, years_of_experience, consultation_fee) VALUES
((SELECT id FROM users WHERE email = 'doctor1@medicalpro.com'), 
 (SELECT id FROM specialties WHERE name = 'Cardiology'), 
 'DOC12345', 
 'Dr. Smith is a board-certified cardiologist with extensive experience in heart disease management and prevention.', 
 15, 
 150.00),
((SELECT id FROM users WHERE email = 'doctor2@medicalpro.com'), 
 (SELECT id FROM specialties WHERE name = 'Pediatrics'), 
 'DOC67890', 
 'Dr. Johnson specializes in pediatric care and has a passion for working with children of all ages.', 
 10, 
 120.00);

-- Add doctor availability
INSERT INTO doctor_availability (doctor_id, day_of_week, start_time, end_time) VALUES
((SELECT id FROM doctors WHERE license_number = 'DOC12345'), 'Monday', '09:00:00', '17:00:00'),
((SELECT id FROM doctors WHERE license_number = 'DOC12345'), 'Wednesday', '09:00:00', '17:00:00'),
((SELECT id FROM doctors WHERE license_number = 'DOC12345'), 'Friday', '09:00:00', '17:00:00'),
((SELECT id FROM doctors WHERE license_number = 'DOC67890'), 'Tuesday', '08:00:00', '16:00:00'),
((SELECT id FROM doctors WHERE license_number = 'DOC67890'), 'Thursday', '08:00:00', '16:00:00');

-- Add sample patients
INSERT INTO users (email, password, role_id, is_active, email_verified) VALUES
('patient1@example.com', '$2b$12$A2oRmTEXXBg7CHZvnxL27.QZJ8zHALHvzgRHgJqP.n0XMhfULkrPi', (SELECT id FROM roles WHERE name = 'patient'), TRUE, TRUE),
('patient2@example.com', '$2b$12$A2oRmTEXXBg7CHZvnxL27.QZJ8zHALHvzgRHgJqP.n0XMhfULkrPi', (SELECT id FROM roles WHERE name = 'patient'), TRUE, TRUE);

INSERT INTO user_profiles (user_id, first_name, last_name, phone, date_of_birth, gender, address, city, state, postal_code, country) VALUES
((SELECT id FROM users WHERE email = 'patient1@example.com'), 
 'Michael', 'Brown', 
 '123-555-3333', 
 '1985-04-12', 
 'Male', 
 '123 Main St', 
 'Springfield', 
 'IL', 
 '62704', 
 'USA'),
((SELECT id FROM users WHERE email = 'patient2@example.com'), 
 'Jessica', 'Davis', 
 '123-555-4444', 
 '1990-08-23', 
 'Female', 
 '456 Oak Ave', 
 'Springfield', 
 'IL', 
 '62704', 
 'USA');

INSERT INTO patients (user_id, blood_group, height, weight, allergies, emergency_contact_name, emergency_contact_phone, emergency_contact_relation) VALUES
((SELECT id FROM users WHERE email = 'patient1@example.com'), 
 'A+', 
 180.5, 
 82.3, 
 'Penicillin', 
 'Emily Brown', 
 '123-555-5555', 
 'Spouse'),
((SELECT id FROM users WHERE email = 'patient2@example.com'), 
 'O-', 
 165.0, 
 60.5, 
 'Peanuts, Shellfish', 
 'Robert Davis', 
 '123-555-6666', 
 'Spouse');
*/ 