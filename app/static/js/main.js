// Main JavaScript file for the appointment system

// Flash message auto-dismiss
document.addEventListener('DOMContentLoaded', function() {
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            alert.style.opacity = '0';
            setTimeout(function() {
                alert.remove();
            }, 300);
        }, 3000);
    });
});

// Form validation
function validateAppointmentForm() {
    const startTime = document.getElementById('start_time');
    const endTime = document.getElementById('end_time');
    
    if (startTime && endTime) {
        if (new Date(endTime.value) <= new Date(startTime.value)) {
            alert('End time must be after start time');
            return false;
        }
    }
    return true;
}

// Add form validation to appointment forms
document.addEventListener('DOMContentLoaded', function() {
    const appointmentForms = document.querySelectorAll('form[action*="appointments"]');
    appointmentForms.forEach(function(form) {
        form.addEventListener('submit', function(e) {
            if (!validateAppointmentForm()) {
                e.preventDefault();
            }
        });
    });
});

// Confirm delete actions
document.addEventListener('DOMContentLoaded', function() {
    const deleteButtons = document.querySelectorAll('button[type="submit"]');
    deleteButtons.forEach(function(button) {
        if (button.textContent.toLowerCase().includes('delete')) {
            button.addEventListener('click', function(e) {
                if (!confirm('Are you sure you want to delete this item?')) {
                    e.preventDefault();
                }
            });
        }
    });
}); 