from app import create_app, db
from app.models import User, Appointment

app = create_app()

with app.app_context():
    # Create all tables
    db.create_all()
    
    # Create a test user if none exists
    if not User.query.filter_by(username='test').first():
        user = User(username='test', email='test@example.com')
        user.set_password('password')
        db.session.add(user)
        db.session.commit()
        print("Test user created!")
    
    print("Database initialized successfully!") 