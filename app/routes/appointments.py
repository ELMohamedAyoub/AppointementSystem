from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models import Appointment
from datetime import datetime
import logging

bp = Blueprint('appointments', __name__)
logger = logging.getLogger(__name__)

@bp.route('/appointments')
@login_required
def list_appointments():
    appointments = Appointment.query.filter_by(user_id=current_user.id).order_by(Appointment.start_time).all()
    return render_template('appointments/list.html', title='My Appointments', appointments=appointments)

@bp.route('/appointments/create', methods=['GET', 'POST'])
@login_required
def create_appointment():
    if request.method == 'POST':
        try:
            # Get form data
            title = request.form.get('title')
            description = request.form.get('description')
            start_time = datetime.strptime(request.form.get('start_time'), '%Y-%m-%dT%H:%M')
            end_time = datetime.strptime(request.form.get('end_time'), '%Y-%m-%dT%H:%M')
            
            # Validate times
            if end_time <= start_time:
                flash('End time must be after start time', 'error')
                return redirect(url_for('appointments.create_appointment'))
            
            # Create new appointment
            appointment = Appointment(
                title=title,
                description=description,
                start_time=start_time,
                end_time=end_time,
                user_id=current_user.id,
                status='pending'
            )
            
            # Save to database
            db.session.add(appointment)
            db.session.commit()
            
            flash('Appointment created successfully!', 'success')
            logger.info(f'Appointment created: {appointment.id} by user {current_user.id}')
            return redirect(url_for('appointments.list_appointments'))
            
        except Exception as e:
            db.session.rollback()
            logger.error(f'Error creating appointment: {str(e)}')
            flash('Error creating appointment. Please try again.', 'error')
            return redirect(url_for('appointments.create_appointment'))
    
    return render_template('appointments/create.html', title='Create Appointment')

@bp.route('/appointments/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_appointment(id):
    appointment = Appointment.query.get_or_404(id)
    if appointment.user_id != current_user.id:
        flash('You do not have permission to edit this appointment.', 'error')
        return redirect(url_for('appointments.list_appointments'))
    
    if request.method == 'POST':
        try:
            appointment.title = request.form.get('title')
            appointment.description = request.form.get('description')
            appointment.start_time = datetime.strptime(request.form.get('start_time'), '%Y-%m-%dT%H:%M')
            appointment.end_time = datetime.strptime(request.form.get('end_time'), '%Y-%m-%dT%H:%M')
            
            db.session.commit()
            flash('Appointment updated successfully!', 'success')
            logger.info(f'Appointment updated: {appointment.id} by user {current_user.id}')
            return redirect(url_for('appointments.list_appointments'))
            
        except Exception as e:
            db.session.rollback()
            logger.error(f'Error updating appointment: {str(e)}')
            flash('Error updating appointment. Please try again.', 'error')
            return redirect(url_for('appointments.edit_appointment', id=id))
    
    return render_template('appointments/edit.html', title='Edit Appointment', appointment=appointment)

@bp.route('/appointments/<int:id>/delete', methods=['POST'])
@login_required
def delete_appointment(id):
    appointment = Appointment.query.get_or_404(id)
    if appointment.user_id != current_user.id:
        flash('You do not have permission to delete this appointment.', 'error')
        return redirect(url_for('appointments.list_appointments'))
    
    try:
        db.session.delete(appointment)
        db.session.commit()
        flash('Appointment deleted successfully!', 'success')
        logger.info(f'Appointment deleted: {id} by user {current_user.id}')
    except Exception as e:
        db.session.rollback()
        logger.error(f'Error deleting appointment: {str(e)}')
        flash('Error deleting appointment. Please try again.', 'error')
    
    return redirect(url_for('appointments.list_appointments')) 