from flask import Blueprint, render_template
from flask_login import login_required, current_user

bp = Blueprint('main', __name__)

@bp.route('/')
@bp.route('/index')
def index():
    return render_template('index.html', title='Home')

@bp.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', title='Dashboard') 