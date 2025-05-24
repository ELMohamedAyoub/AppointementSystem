# Modern Appointment System

A modern, user-friendly appointment management system built with Flask.

## Features

- User authentication and authorization
- Appointment scheduling and management
- Calendar view
- Email notifications
- Admin dashboard
- Responsive design

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
Create a `.env` file in the root directory with:
```
FLASK_APP=app
FLASK_ENV=development
SECRET_KEY=your-secret-key
DATABASE_URL=sqlite:///appointments.db
```

4. Initialize the database:
```bash
flask db init
flask db migrate
flask db upgrade
```

5. Run the application:
```bash
flask run
```

## Project Structure

```
appointment_system/
├── app/
│   ├── __init__.py
│   ├── models/
│   ├── routes/
│   ├── templates/
│   └── static/
├── migrations/
├── tests/
├── .env
├── .gitignore
├── config.py
├── requirements.txt
└── README.md
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License.
