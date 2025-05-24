USE medicalpro;

-- ========== STORED PROCEDURES ==========

-- Procedure to book a new appointment with validation
DELIMITER $$
CREATE PROCEDURE BookAppointment(
    IN p_patient_id INT, 
    IN p_doctor_id INT, 
    IN p_appointment_date DATE,
    IN p_start_time TIME,
    IN p_end_time TIME,
    IN p_reason TEXT,
    IN p_created_by INT,
    OUT p_appointment_id INT
)
BEGIN
    DECLARE doctor_available BOOLEAN DEFAULT FALSE;
    DECLARE time_slot_available BOOLEAN DEFAULT FALSE;
    DECLARE status_id INT;
    
    -- Transaction to ensure data integrity
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        SIGNAL SQLSTATE '45000' 
        SET MESSAGE_TEXT = 'Error occurred while booking appointment';
    END;
    
    START TRANSACTION;
    
    -- Check if doctor is available on the specified day and time
    SELECT COUNT(*) > 0 INTO doctor_available
    FROM doctor_availability 
    WHERE doctor_id = p_doctor_id 
    AND day_of_week = DAYNAME(p_appointment_date)
    AND start_time <= p_start_time 
    AND end_time >= p_end_time
    AND is_active = TRUE;
    
    -- Check if doctor doesn't have unavailability during this time
    SELECT COUNT(*) = 0 INTO doctor_available
    FROM doctor_unavailability
    WHERE doctor_id = p_doctor_id
    AND (
        (start_datetime <= TIMESTAMP(p_appointment_date, p_start_time) AND end_datetime >= TIMESTAMP(p_appointment_date, p_start_time))
        OR
        (start_datetime <= TIMESTAMP(p_appointment_date, p_end_time) AND end_datetime >= TIMESTAMP(p_appointment_date, p_end_time))
        OR
        (start_datetime >= TIMESTAMP(p_appointment_date, p_start_time) AND end_datetime <= TIMESTAMP(p_appointment_date, p_end_time))
    );
    
    -- Check if time slot is not already booked
    SELECT COUNT(*) = 0 INTO time_slot_available
    FROM appointments
    WHERE doctor_id = p_doctor_id
    AND appointment_date = p_appointment_date
    AND (
        (start_time <= p_start_time AND end_time > p_start_time)
        OR
        (start_time < p_end_time AND end_time >= p_end_time)
        OR
        (start_time >= p_start_time AND end_time <= p_end_time)
    )
    AND status_id NOT IN (SELECT id FROM appointment_status WHERE name IN ('Cancelled', 'Declined', 'No-show'));
    
    -- Get the status ID for 'Scheduled'
    SELECT id INTO status_id FROM appointment_status WHERE name = 'Scheduled' LIMIT 1;
    
    -- Insert appointment if doctor is available and time slot is free
    IF doctor_available AND time_slot_available THEN
        INSERT INTO appointments (
            patient_id, 
            doctor_id, 
            appointment_date, 
            start_time, 
            end_time, 
            status_id, 
            reason, 
            created_by
        ) VALUES (
            p_patient_id,
            p_doctor_id,
            p_appointment_date,
            p_start_time,
            p_end_time,
            status_id,
            p_reason,
            p_created_by
        );
        
        SET p_appointment_id = LAST_INSERT_ID();
        
        -- Create notification for patient
        INSERT INTO notifications (
            user_id,
            title,
            message,
            type,
            related_entity,
            related_id
        )
        SELECT 
            patients.user_id,
            'Appointment Scheduled',
            CONCAT('Your appointment with Dr. ', 
                   (SELECT CONCAT(first_name, ' ', last_name) FROM user_profiles WHERE user_id = doctors.user_id), 
                   ' is scheduled for ', 
                   DATE_FORMAT(p_appointment_date, '%M %d, %Y'), 
                   ' at ', 
                   DATE_FORMAT(p_start_time, '%h:%i %p')),
            'appointment',
            'appointments',
            p_appointment_id
        FROM patients
        JOIN doctors ON doctors.id = p_doctor_id
        WHERE patients.id = p_patient_id;
        
        -- Create notification for doctor
        INSERT INTO notifications (
            user_id,
            title,
            message,
            type,
            related_entity,
            related_id
        )
        SELECT 
            doctors.user_id,
            'New Appointment',
            CONCAT('You have a new appointment with ', 
                   (SELECT CONCAT(first_name, ' ', last_name) FROM user_profiles WHERE user_id = patients.user_id), 
                   ' scheduled for ', 
                   DATE_FORMAT(p_appointment_date, '%M %d, %Y'), 
                   ' at ', 
                   DATE_FORMAT(p_start_time, '%h:%i %p')),
            'appointment',
            'appointments',
            p_appointment_id
        FROM doctors
        JOIN patients ON patients.id = p_patient_id
        WHERE doctors.id = p_doctor_id;
        
        COMMIT;
    ELSE
        IF NOT doctor_available THEN
            SIGNAL SQLSTATE '45000' 
            SET MESSAGE_TEXT = 'Doctor is not available during this time';
        ELSE
            SIGNAL SQLSTATE '45000' 
            SET MESSAGE_TEXT = 'This time slot is already booked';
        END IF;
        
        ROLLBACK;
    END IF;
END$$
DELIMITER ;

-- Procedure to cancel an appointment
DELIMITER $$
CREATE PROCEDURE CancelAppointment(
    IN p_appointment_id INT,
    IN p_cancelled_by_user_id INT,
    IN p_cancellation_reason TEXT
)
BEGIN
    DECLARE appointment_exists BOOLEAN DEFAULT FALSE;
    DECLARE patient_id_var INT;
    DECLARE doctor_id_var INT;
    DECLARE status_id_cancelled INT;
    DECLARE cancelled_by_role VARCHAR(50);
    
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        SIGNAL SQLSTATE '45000' 
        SET MESSAGE_TEXT = 'Error occurred while cancelling appointment';
    END;
    
    START TRANSACTION;
    
    -- Check if appointment exists
    SELECT COUNT(*) > 0, patient_id, doctor_id INTO appointment_exists, patient_id_var, doctor_id_var
    FROM appointments
    WHERE id = p_appointment_id;
    
    IF NOT appointment_exists THEN
        SIGNAL SQLSTATE '45000' 
        SET MESSAGE_TEXT = 'Appointment not found';
    END IF;
    
    -- Get the status ID for 'Cancelled'
    SELECT id INTO status_id_cancelled FROM appointment_status WHERE name = 'Cancelled' LIMIT 1;
    
    -- Get the role of the user who is cancelling
    SELECT roles.name INTO cancelled_by_role
    FROM users
    JOIN roles ON users.role_id = roles.id
    WHERE users.id = p_cancelled_by_user_id;
    
    -- Update appointment status
    UPDATE appointments
    SET status_id = status_id_cancelled,
        notes = CONCAT(COALESCE(notes, ''), '\nCancelled by ', cancelled_by_role, '. Reason: ', p_cancellation_reason),
        updated_at = NOW()
    WHERE id = p_appointment_id;
    
    -- Create notification for patient
    INSERT INTO notifications (
        user_id,
        title,
        message,
        type,
        related_entity,
        related_id
    )
    SELECT 
        patients.user_id,
        'Appointment Cancelled',
        CONCAT('Your appointment on ', 
               DATE_FORMAT(appointment_date, '%M %d, %Y'), 
               ' at ', 
               DATE_FORMAT(start_time, '%h:%i %p'),
               ' has been cancelled.'),
        'appointment',
        'appointments',
        p_appointment_id
    FROM appointments
    JOIN patients ON patients.id = patient_id_var
    WHERE appointments.id = p_appointment_id;
    
    -- Create notification for doctor
    INSERT INTO notifications (
        user_id,
        title,
        message,
        type,
        related_entity,
        related_id
    )
    SELECT 
        doctors.user_id,
        'Appointment Cancelled',
        CONCAT('Your appointment with ', 
               (SELECT CONCAT(first_name, ' ', last_name) FROM user_profiles WHERE user_id = patients.user_id), 
               ' on ', 
               DATE_FORMAT(appointment_date, '%M %d, %Y'), 
               ' at ', 
               DATE_FORMAT(start_time, '%h:%i %p'),
               ' has been cancelled.'),
        'appointment',
        'appointments',
        p_appointment_id
    FROM appointments
    JOIN doctors ON doctors.id = doctor_id_var
    JOIN patients ON patients.id = patient_id_var
    WHERE appointments.id = p_appointment_id;
    
    COMMIT;
END$$
DELIMITER ;

-- Procedure to reschedule an appointment
DELIMITER $$
CREATE PROCEDURE RescheduleAppointment(
    IN p_appointment_id INT,
    IN p_new_date DATE,
    IN p_new_start_time TIME,
    IN p_new_end_time TIME,
    IN p_rescheduled_by_user_id INT,
    IN p_reschedule_reason TEXT
)
BEGIN
    DECLARE appointment_exists BOOLEAN DEFAULT FALSE;
    DECLARE doctor_id_var INT;
    DECLARE doctor_available BOOLEAN DEFAULT FALSE;
    DECLARE time_slot_available BOOLEAN DEFAULT FALSE;
    DECLARE rescheduled_by_role VARCHAR(50);
    
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        SIGNAL SQLSTATE '45000' 
        SET MESSAGE_TEXT = 'Error occurred while rescheduling appointment';
    END;
    
    START TRANSACTION;
    
    -- Check if appointment exists
    SELECT COUNT(*) > 0, doctor_id INTO appointment_exists, doctor_id_var
    FROM appointments
    WHERE id = p_appointment_id;
    
    IF NOT appointment_exists THEN
        SIGNAL SQLSTATE '45000' 
        SET MESSAGE_TEXT = 'Appointment not found';
    END IF;
    
    -- Check if doctor is available on the new day and time
    SELECT COUNT(*) > 0 INTO doctor_available
    FROM doctor_availability 
    WHERE doctor_id = doctor_id_var 
    AND day_of_week = DAYNAME(p_new_date)
    AND start_time <= p_new_start_time 
    AND end_time >= p_new_end_time
    AND is_active = TRUE;
    
    -- Check if doctor doesn't have unavailability during this time
    SELECT COUNT(*) = 0 INTO doctor_available
    FROM doctor_unavailability
    WHERE doctor_id = doctor_id_var
    AND (
        (start_datetime <= TIMESTAMP(p_new_date, p_new_start_time) AND end_datetime >= TIMESTAMP(p_new_date, p_new_start_time))
        OR
        (start_datetime <= TIMESTAMP(p_new_date, p_new_end_time) AND end_datetime >= TIMESTAMP(p_new_date, p_new_end_time))
        OR
        (start_datetime >= TIMESTAMP(p_new_date, p_new_start_time) AND end_datetime <= TIMESTAMP(p_new_date, p_new_end_time))
    );
    
    -- Check if new time slot is not already booked
    SELECT COUNT(*) = 0 INTO time_slot_available
    FROM appointments
    WHERE doctor_id = doctor_id_var
    AND appointment_date = p_new_date
    AND id != p_appointment_id  -- Exclude current appointment
    AND (
        (start_time <= p_new_start_time AND end_time > p_new_start_time)
        OR
        (start_time < p_new_end_time AND end_time >= p_new_end_time)
        OR
        (start_time >= p_new_start_time AND end_time <= p_new_end_time)
    )
    AND status_id NOT IN (SELECT id FROM appointment_status WHERE name IN ('Cancelled', 'Declined', 'No-show'));
    
    -- Get the role of the user who is rescheduling
    SELECT roles.name INTO rescheduled_by_role
    FROM users
    JOIN roles ON users.role_id = roles.id
    WHERE users.id = p_rescheduled_by_user_id;
    
    -- Reschedule appointment if doctor is available and time slot is free
    IF doctor_available AND time_slot_available THEN
        UPDATE appointments
        SET appointment_date = p_new_date,
            start_time = p_new_start_time,
            end_time = p_new_end_time,
            notes = CONCAT(COALESCE(notes, ''), '\nRescheduled by ', rescheduled_by_role, '. Reason: ', p_reschedule_reason),
            updated_at = NOW()
        WHERE id = p_appointment_id;
        
        -- Create notifications for patient and doctor about rescheduling
        INSERT INTO notifications (
            user_id,
            title,
            message,
            type,
            related_entity,
            related_id
        )
        SELECT 
            user_id,
            'Appointment Rescheduled',
            CONCAT('Your appointment has been rescheduled to ', 
                   DATE_FORMAT(p_new_date, '%M %d, %Y'), 
                   ' at ', 
                   DATE_FORMAT(p_new_start_time, '%h:%i %p')),
            'appointment',
            'appointments',
            p_appointment_id
        FROM (
            -- Get patient's user_id
            SELECT patients.user_id 
            FROM appointments
            JOIN patients ON appointments.patient_id = patients.id
            WHERE appointments.id = p_appointment_id
            
            UNION
            
            -- Get doctor's user_id
            SELECT doctors.user_id 
            FROM appointments
            JOIN doctors ON appointments.doctor_id = doctors.id
            WHERE appointments.id = p_appointment_id
        ) AS users_to_notify;
        
        COMMIT;
    ELSE
        IF NOT doctor_available THEN
            SIGNAL SQLSTATE '45000' 
            SET MESSAGE_TEXT = 'Doctor is not available during this time';
        ELSE
            SIGNAL SQLSTATE '45000' 
            SET MESSAGE_TEXT = 'This time slot is already booked';
        END IF;
        
        ROLLBACK;
    END IF;
END$$
DELIMITER ;

-- Procedure to add prescription with medications
DELIMITER $$
CREATE PROCEDURE CreatePrescription(
    IN p_appointment_id INT,
    IN p_diagnosis TEXT,
    IN p_notes TEXT
)
BEGIN
    DECLARE v_patient_id INT;
    DECLARE v_doctor_id INT;
    DECLARE prescription_id INT;
    
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        SIGNAL SQLSTATE '45000' 
        SET MESSAGE_TEXT = 'Error occurred while creating prescription';
    END;
    
    START TRANSACTION;
    
    -- Get patient and doctor IDs from appointment
    SELECT patient_id, doctor_id INTO v_patient_id, v_doctor_id
    FROM appointments
    WHERE id = p_appointment_id;
    
    -- Insert prescription
    INSERT INTO prescriptions (
        appointment_id,
        patient_id,
        doctor_id,
        prescription_date,
        diagnosis,
        notes
    ) VALUES (
        p_appointment_id,
        v_patient_id,
        v_doctor_id,
        CURDATE(),
        p_diagnosis,
        p_notes
    );
    
    SET prescription_id = LAST_INSERT_ID();
    
    -- Create notification for patient
    INSERT INTO notifications (
        user_id,
        title,
        message,
        type,
        related_entity,
        related_id
    )
    SELECT 
        patients.user_id,
        'New Prescription',
        CONCAT('Dr. ', 
               (SELECT CONCAT(first_name, ' ', last_name) FROM user_profiles WHERE user_id = doctors.user_id), 
               ' has created a new prescription for you.'),
        'prescription',
        'prescriptions',
        prescription_id
    FROM patients
    JOIN doctors ON doctors.id = v_doctor_id
    WHERE patients.id = v_patient_id;
    
    COMMIT;
    
    -- Return the created prescription ID
    SELECT prescription_id AS new_prescription_id;
END$$
DELIMITER ;

-- Procedure to add medication to a prescription
DELIMITER $$
CREATE PROCEDURE AddMedicationToPrescription(
    IN p_prescription_id INT,
    IN p_medication_id INT,
    IN p_dosage VARCHAR(100),
    IN p_frequency VARCHAR(100),
    IN p_duration VARCHAR(100),
    IN p_instructions TEXT
)
BEGIN
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        SIGNAL SQLSTATE '45000' 
        SET MESSAGE_TEXT = 'Error occurred while adding medication to prescription';
    END;
    
    START TRANSACTION;
    
    -- Insert medication to prescription
    INSERT INTO prescription_medications (
        prescription_id,
        medication_id,
        dosage,
        frequency,
        duration,
        instructions
    ) VALUES (
        p_prescription_id,
        p_medication_id,
        p_dosage,
        p_frequency,
        p_duration,
        p_instructions
    );
    
    COMMIT;
END$$
DELIMITER ;

-- ========== SQL FUNCTIONS ==========

-- Function to check if a doctor is available at a specific time
DELIMITER $$
CREATE FUNCTION IsDoctorAvailable(
    p_doctor_id INT,
    p_date DATE,
    p_start_time TIME,
    p_end_time TIME
) RETURNS BOOLEAN
DETERMINISTIC
BEGIN
    DECLARE is_scheduled BOOLEAN;
    DECLARE is_available BOOLEAN;
    DECLARE is_unavailable BOOLEAN;
    
    -- Check regular schedule
    SELECT COUNT(*) > 0 INTO is_available
    FROM doctor_availability
    WHERE doctor_id = p_doctor_id
    AND day_of_week = DAYNAME(p_date)
    AND start_time <= p_start_time
    AND end_time >= p_end_time
    AND is_active = TRUE;
    
    IF NOT is_available THEN
        RETURN FALSE;
    END IF;
    
    -- Check unavailability
    SELECT COUNT(*) > 0 INTO is_unavailable
    FROM doctor_unavailability
    WHERE doctor_id = p_doctor_id
    AND (
        (start_datetime <= TIMESTAMP(p_date, p_start_time) AND end_datetime >= TIMESTAMP(p_date, p_start_time))
        OR
        (start_datetime <= TIMESTAMP(p_date, p_end_time) AND end_datetime >= TIMESTAMP(p_date, p_end_time))
        OR
        (start_datetime >= TIMESTAMP(p_date, p_start_time) AND end_datetime <= TIMESTAMP(p_date, p_end_time))
    );
    
    IF is_unavailable THEN
        RETURN FALSE;
    END IF;
    
    -- Check existing appointments
    SELECT COUNT(*) > 0 INTO is_scheduled
    FROM appointments
    WHERE doctor_id = p_doctor_id
    AND appointment_date = p_date
    AND (
        (start_time <= p_start_time AND end_time > p_start_time)
        OR
        (start_time < p_end_time AND end_time >= p_end_time)
        OR
        (start_time >= p_start_time AND end_time <= p_end_time)
    )
    AND status_id NOT IN (SELECT id FROM appointment_status WHERE name IN ('Cancelled', 'Declined', 'No-show'));
    
    IF is_scheduled THEN
        RETURN FALSE;
    END IF;
    
    RETURN TRUE;
END$$
DELIMITER ;

-- Function to count appointments for a doctor in date range
DELIMITER $$
CREATE FUNCTION CountDoctorAppointments(
    p_doctor_id INT,
    p_start_date DATE,
    p_end_date DATE
) RETURNS INT
DETERMINISTIC
BEGIN
    DECLARE appointment_count INT;
    
    SELECT COUNT(*) INTO appointment_count
    FROM appointments
    WHERE doctor_id = p_doctor_id
    AND appointment_date BETWEEN p_start_date AND p_end_date
    AND status_id NOT IN (SELECT id FROM appointment_status WHERE name IN ('Cancelled', 'Declined', 'No-show'));
    
    RETURN appointment_count;
END$$
DELIMITER ;

-- Function to count appointments for a patient in date range
DELIMITER $$
CREATE FUNCTION CountPatientAppointments(
    p_patient_id INT,
    p_start_date DATE,
    p_end_date DATE
) RETURNS INT
DETERMINISTIC
BEGIN
    DECLARE appointment_count INT;
    
    SELECT COUNT(*) INTO appointment_count
    FROM appointments
    WHERE patient_id = p_patient_id
    AND appointment_date BETWEEN p_start_date AND p_end_date
    AND status_id NOT IN (SELECT id FROM appointment_status WHERE name IN ('Cancelled', 'Declined', 'No-show'));
    
    RETURN appointment_count;
END$$
DELIMITER ;

-- Function to get doctor's current workload (appointments in next 7 days)
DELIMITER $$
CREATE FUNCTION GetDoctorWorkload(
    p_doctor_id INT
) RETURNS INT
DETERMINISTIC
BEGIN
    RETURN CountDoctorAppointments(p_doctor_id, CURDATE(), DATE_ADD(CURDATE(), INTERVAL 7 DAY));
END$$
DELIMITER ;

-- ========== TRIGGERS ==========

-- Trigger to log user creation
DELIMITER $$
CREATE TRIGGER after_user_create
AFTER INSERT ON users
FOR EACH ROW
BEGIN
    INSERT INTO audit_logs (
        user_id,
        action,
        entity_type,
        entity_id,
        new_values
    ) VALUES (
        NULL, -- System action as there's no user yet for self-creation
        'CREATE',
        'users',
        NEW.id,
        JSON_OBJECT(
            'id', NEW.id,
            'email', NEW.email,
            'role_id', NEW.role_id,
            'is_active', NEW.is_active,
            'created_at', NEW.created_at
        )
    );
END$$
DELIMITER ;

-- Trigger to log user updates
DELIMITER $$
CREATE TRIGGER after_user_update
AFTER UPDATE ON users
FOR EACH ROW
BEGIN
    INSERT INTO audit_logs (
        user_id,
        action,
        entity_type,
        entity_id,
        old_values,
        new_values
    ) VALUES (
        NULL, -- We don't know who made the change from this context
        'UPDATE',
        'users',
        NEW.id,
        JSON_OBJECT(
            'email', OLD.email,
            'role_id', OLD.role_id,
            'is_active', OLD.is_active,
            'last_login', OLD.last_login
        ),
        JSON_OBJECT(
            'email', NEW.email,
            'role_id', NEW.role_id,
            'is_active', NEW.is_active,
            'last_login', NEW.last_login
        )
    );
END$$
DELIMITER ;

-- Trigger to log appointment creation
DELIMITER $$
CREATE TRIGGER after_appointment_create
AFTER INSERT ON appointments
FOR EACH ROW
BEGIN
    INSERT INTO audit_logs (
        user_id,
        action,
        entity_type,
        entity_id,
        new_values
    ) VALUES (
        NEW.created_by,
        'CREATE',
        'appointments',
        NEW.id,
        JSON_OBJECT(
            'id', NEW.id,
            'patient_id', NEW.patient_id,
            'doctor_id', NEW.doctor_id,
            'appointment_date', NEW.appointment_date,
            'start_time', NEW.start_time,
            'end_time', NEW.end_time,
            'status_id', NEW.status_id
        )
    );
END$$
DELIMITER ;

-- Trigger to log appointment updates
DELIMITER $$
CREATE TRIGGER after_appointment_update
AFTER UPDATE ON appointments
FOR EACH ROW
BEGIN
    INSERT INTO audit_logs (
        user_id,
        action,
        entity_type,
        entity_id,
        old_values,
        new_values
    ) VALUES (
        NULL, -- Unknown from this context
        'UPDATE',
        'appointments',
        NEW.id,
        JSON_OBJECT(
            'patient_id', OLD.patient_id,
            'doctor_id', OLD.doctor_id,
            'appointment_date', OLD.appointment_date,
            'start_time', OLD.start_time,
            'end_time', OLD.end_time,
            'status_id', OLD.status_id
        ),
        JSON_OBJECT(
            'patient_id', NEW.patient_id,
            'doctor_id', NEW.doctor_id,
            'appointment_date', NEW.appointment_date,
            'start_time', NEW.start_time,
            'end_time', NEW.end_time,
            'status_id', NEW.status_id
        )
    );
END$$
DELIMITER ;

-- Trigger to log prescription creation
DELIMITER $$
CREATE TRIGGER after_prescription_create
AFTER INSERT ON prescriptions
FOR EACH ROW
BEGIN
    INSERT INTO audit_logs (
        user_id,
        action,
        entity_type,
        entity_id,
        new_values
    ) VALUES (
        (SELECT user_id FROM doctors WHERE id = NEW.doctor_id),
        'CREATE',
        'prescriptions',
        NEW.id,
        JSON_OBJECT(
            'id', NEW.id,
            'patient_id', NEW.patient_id,
            'doctor_id', NEW.doctor_id,
            'appointment_id', NEW.appointment_id,
            'prescription_date', NEW.prescription_date
        )
    );
END$$
DELIMITER ;

-- Trigger to automatically update appointment status to 'Completed' after adding prescription
DELIMITER $$
CREATE TRIGGER after_prescription_create_update_appointment
AFTER INSERT ON prescriptions
FOR EACH ROW
BEGIN
    DECLARE completed_status_id INT;
    
    -- Get the 'Completed' status ID
    SELECT id INTO completed_status_id 
    FROM appointment_status 
    WHERE name = 'Completed' 
    LIMIT 1;
    
    -- Update the appointment status to 'Completed'
    UPDATE appointments
    SET status_id = completed_status_id,
        updated_at = NOW()
    WHERE id = NEW.appointment_id;
END$$
DELIMITER ; 