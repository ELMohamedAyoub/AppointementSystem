from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    role = db.Column(db.Enum('patient', 'doctor', 'secretary', 'admin'), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    phone_number = db.Column(db.String(20))
    date_of_birth = db.Column(db.Date)
    gender = db.Column(db.Enum('M', 'F', 'O', 'P'))
    address = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    last_login = db.Column(db.DateTime)
    failed_login_attempts = db.Column(db.Integer, default=0)
    password_reset_token = db.Column(db.String(100))
    password_reset_expires = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    appointments_as_patient = db.relationship('Appointment', foreign_keys='Appointment.patient_id', backref='patient', lazy=True)
    appointments_as_doctor = db.relationship('Appointment', foreign_keys='Appointment.doctor_id', backref='doctor', lazy=True)
    medical_records_as_patient = db.relationship('MedicalRecord', foreign_keys='MedicalRecord.patient_id', backref='patient', lazy=True)
    medical_records_as_doctor = db.relationship('MedicalRecord', foreign_keys='MedicalRecord.doctor_id', backref='doctor', lazy=True)
    prescriptions_as_patient = db.relationship('Prescription', foreign_keys='Prescription.patient_id', backref='patient', lazy=True)
    prescriptions_as_doctor = db.relationship('Prescription', foreign_keys='Prescription.doctor_id', backref='doctor', lazy=True)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def __repr__(self):
        return f'<User {self.username}>'

class Appointment(db.Model):
    __tablename__ = 'appointments'
    
    appointment_id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    appointment_date = db.Column(db.Date, nullable=False)
    appointment_time = db.Column(db.Time, nullable=False)
    duration = db.Column(db.Integer, default=30)
    type = db.Column(db.Enum('checkup', 'consultation', 'follow-up', 'emergency', 'procedure'), nullable=False)
    status = db.Column(db.Enum('pending', 'confirmed', 'canceled', 'completed', 'no-show'), default='pending')
    reason = db.Column(db.Text)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<Appointment {self.appointment_id}>'

class MedicalRecord(db.Model):
    __tablename__ = 'medical_records'
    
    record_id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    record_date = db.Column(db.Date, nullable=False)
    visit_type = db.Column(db.Enum('initial', 'follow-up', 'emergency', 'routine'), nullable=False)
    chief_complaint = db.Column(db.Text)
    diagnosis = db.Column(db.String(255), nullable=False)
    diagnosis_code = db.Column(db.String(20))
    treatment_plan = db.Column(db.Text)
    follow_up_date = db.Column(db.Date)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<MedicalRecord {self.record_id}>'

class Prescription(db.Model):
    __tablename__ = 'prescriptions'
    
    prescription_id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    medication_id = db.Column(db.Integer, db.ForeignKey('medications.medication_id'), nullable=False)
    dosage = db.Column(db.String(50), nullable=False)
    frequency = db.Column(db.String(50), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date)
    refills_remaining = db.Column(db.Integer, default=0)
    status = db.Column(db.Enum('active', 'completed', 'cancelled'), default='active')
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<Prescription {self.prescription_id}>'

class Medication(db.Model):
    __tablename__ = 'medications'
    
    medication_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    generic_name = db.Column(db.String(100))
    manufacturer = db.Column(db.String(100))
    dosage_form = db.Column(db.String(50))
    strength = db.Column(db.String(50))
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Medication {self.name}>' 