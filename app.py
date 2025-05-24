from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_mysqldb import MySQL
import bcrypt
import config

app = Flask(__name__)
app.secret_key = config.Config.SECRET_KEY

# MySQL configuration
app.config['MYSQL_HOST'] = config.Config.DB_HOST
app.config['MYSQL_USER'] = config.Config.DB_USER
app.config['MYSQL_PASSWORD'] = config.Config.DB_PASSWORD
app.config['MYSQL_DB'] = config.Config.DB_NAME
app.config['MYSQL_PORT'] = config.Config.DB_PORT
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
app.config['MYSQL_UNIX_SOCKET'] = None  # Force TCP/IP connection

mysql = MySQL(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

class User(UserMixin):
    def __init__(self, id, email, role):
        self.id = id
        self.email = email
        self.role = role

@login_manager.user_loader
def load_user(user_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT id, email, role FROM users WHERE id = %s", (user_id,))
    user = cur.fetchone()
    cur.close()
    return User(**user) if user else None

# Routes
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = bcrypt.hashpw(request.form['password'].encode(), bcrypt.gensalt())
        role = request.form['role']
        
        try:
            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO users (email, password, role) VALUES (%s, %s, %s)", (email, password, role))
            mysql.connection.commit()
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            flash(str(e), 'danger')
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password'].encode()
        
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cur.fetchone()
        cur.close()
        
        if user and bcrypt.checkpw(password, user['password'].encode()):
            login_user(User(user['id'], user['email'], user['role']))
            return redirect(url_for('dashboard'))
        flash('Invalid credentials', 'danger')
    return render_template('login.html')

@app.route('/dashboard')
@login_required
def dashboard():
    role = current_user.role
    return render_template(f'dashboard/{role}_dashboard.html')

@app.route('/appointments')
@login_required
def appointments():
    cur = mysql.connection.cursor()
    if current_user.role == 'patient':
        cur.execute("""
            SELECT r.date_rdv, m.nom AS doctor, m.specialite 
            FROM rendez_vous r JOIN medecins m ON r.medecin_id = m.id 
            WHERE r.patient_id = %s AND r.date_rdv > NOW()
        """, (current_user.id,))
    elif current_user.role == 'doctor':
        cur.execute("""
            SELECT r.date_rdv, p.nom AS patient, p.email 
            FROM rendez_vous r JOIN patients p ON r.patient_id = p.id 
            WHERE r.medecin_id = %s AND r.date_rdv > NOW()
        """, (current_user.id,))
    appointments = cur.fetchall()
    cur.close()
    return render_template(f'appointments/{current_user.role}_appointments.html', appointments=appointments)

@app.route('/book', methods=['GET', 'POST'])
@login_required
def book():
    if current_user.role != 'patient':
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        try:
            cur = mysql.connection.cursor()
            cur.callproc('CreerRendezVous', (
                current_user.id,
                request.form['doctor_id'],
                request.form['datetime']
            ))
            mysql.connection.commit()
            flash('Appointment booked!', 'success')
        except Exception as e:
            flash(str(e), 'danger')
        finally:
            cur.close()
        return redirect(url_for('appointments'))
    
    cur = mysql.connection.cursor()
    cur.execute("SELECT id, nom, specialite FROM medecins")
    doctors = cur.fetchall()
    cur.close()
    return render_template('appointments/book_appointment.html', doctors=doctors)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
