from flask import Flask, render_template, request, redirect, url_for, flash, session
from datetime import datetime, timedelta
import logging
from models import db, User, Appointment, MedicalRecord, Prescription, Medication
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        role = request.form['role']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists!', 'danger')
            return redirect(url_for('register'))
            
        user = User(
            username=username,
            email=email,
            role=role,
            first_name=first_name,
            last_name=last_name
        )
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()

        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            session['user'] = {
                'user_id': user.user_id,
                'username': user.username,
                'role': user.role
            }
            user.last_login = datetime.utcnow()
            db.session.commit()
            return redirect(url_for('dashboard'))
            
        flash('Invalid username or password', 'danger')
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))

    current_user = session['user']
    user = User.query.get(current_user['user_id'])
    
    if not user:
        session.clear()
        return redirect(url_for('login'))

    # Get today's date for the dashboard
    today_date = datetime.now().strftime('%Y-%m-%d')

    # Get appointments based on role
    if user.role == 'patient':
        appointments = Appointment.query.filter_by(patient_id=user.user_id).all()
    elif user.role == 'doctor':
        appointments = Appointment.query.filter_by(doctor_id=user.user_id).all()
    else:  # secretary or admin
        appointments = Appointment.query.all()

    # Get medical records based on role
    if user.role == 'patient':
        medical_records = MedicalRecord.query.filter_by(patient_id=user.user_id).all()
    elif user.role == 'doctor':
        medical_records = MedicalRecord.query.filter_by(doctor_id=user.user_id).all()
    else:  # secretary or admin
        medical_records = MedicalRecord.query.all()

    return render_template(f'dashboard/{user.role}_dashboard.html',
                         user=user,
                         appointments=appointments,
                         medical_records=medical_records,
                         today_date=today_date)

@app.route('/appointments', methods=['GET', 'POST'])
def manage_appointments():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    current_user = session['user']
    user = User.query.get(current_user['user_id'])
    
    if request.method == 'POST':
        patient_id = user.user_id if user.role == 'patient' else request.form.get('patient_id')
        doctor_id = request.form.get('doctor_id')
        
        new_appointment = Appointment(
            patient_id=patient_id,
            doctor_id=doctor_id,
            appointment_date=datetime.strptime(request.form.get('date'), '%Y-%m-%d').date(),
            appointment_time=datetime.strptime(request.form.get('time'), '%H:%M').time(),
            type=request.form.get('type'),
            reason=request.form.get('reason'),
            notes=request.form.get('notes')
        )
        
        db.session.add(new_appointment)
        db.session.commit()
        
        flash('Appointment created successfully!', 'success')
        return redirect(url_for('manage_appointments'))

    # Get appointments based on role
    if user.role == 'patient':
        appointments = Appointment.query.filter_by(patient_id=user.user_id).all()
    elif user.role == 'doctor':
        appointments = Appointment.query.filter_by(doctor_id=user.user_id).all()
    else:  # secretary or admin
        appointments = Appointment.query.all()

    # Get list of doctors for appointment creation
    doctors = User.query.filter_by(role='doctor').all()
    patients = User.query.filter_by(role='patient').all()

    return render_template('appointments.html',
                         appointments=appointments,
                         doctors=doctors,
                         patients=patients,
                         user=user)

@app.route('/appointments/confirm/<int:appointment_id>', methods=['POST'])
def confirm_appointment(appointment_id):
    if 'user' not in session:
        return redirect(url_for('login'))
        
    appointment = Appointment.query.get_or_404(appointment_id)
    appointment.status = 'confirmed'
    db.session.commit()
    
    flash('Appointment confirmed!', 'success')
    return redirect(url_for('manage_appointments'))

@app.route('/appointments/cancel/<int:appointment_id>', methods=['POST'])
def cancel_appointment(appointment_id):
    if 'user' not in session:
        return redirect(url_for('login'))
        
    appointment = Appointment.query.get_or_404(appointment_id)
    appointment.status = 'canceled'
    db.session.commit()
    
    flash('Appointment canceled!', 'success')
    return redirect(url_for('manage_appointments'))

@app.route('/medical-records')
def view_medical_records():
    if 'user' not in session:
        return redirect(url_for('login'))
        
    current_user = session['user']
    user = User.query.get(current_user['user_id'])
    
    if user.role == 'patient':
        records = MedicalRecord.query.filter_by(patient_id=user.user_id).all()
    elif user.role == 'doctor':
        records = MedicalRecord.query.filter_by(doctor_id=user.user_id).all()
    else:  # secretary or admin
        records = MedicalRecord.query.all()
        
    return render_template('medical_records.html', records=records, user=user)

@app.route('/profile')
def view_profile():
    if 'user' not in session:
        return redirect(url_for('login'))
        
    current_user = session['user']
    user = User.query.get(current_user['user_id'])
    
    return render_template('profile.html', user=user)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

# Create database tables
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
