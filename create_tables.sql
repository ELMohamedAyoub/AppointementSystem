CREATE DATABASE IF NOT EXISTS medical_appointments;
USE medical_appointments;

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    role ENUM('patient', 'doctor', 'admin') NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE patients (
    id INT PRIMARY KEY,
    nom VARCHAR(255) NOT NULL,
    prenom VARCHAR(255) NOT NULL,
    FOREIGN KEY (id) REFERENCES users(id)
);

CREATE TABLE medecins (
    id INT PRIMARY KEY,
    nom VARCHAR(255) NOT NULL,
    specialite VARCHAR(255) NOT NULL,
    FOREIGN KEY (id) REFERENCES users(id)
);

CREATE TABLE rendez_vous (
    id INT AUTO_INCREMENT PRIMARY KEY,
    patient_id INT NOT NULL,
    medecin_id INT NOT NULL,
    date_rdv DATETIME NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES patients(id),
    FOREIGN KEY (medecin_id) REFERENCES medecins(id)
);

DELIMITER //
CREATE PROCEDURE CreerRendezVous(
    IN patient_id INT,
    IN medecin_id INT,
    IN date_rdv DATETIME
)
BEGIN
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Appointment creation failed';
    END;
    
    START TRANSACTION;
    IF (SELECT COUNT(*) FROM rendez_vous WHERE medecin_id = medecin_id AND date_rdv = date_rdv) > 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Time slot occupied';
    END IF;
    
    INSERT INTO rendez_vous (patient_id, medecin_id, date_rdv) 
    VALUES (patient_id, medecin_id, date_rdv);
    COMMIT;
END//
DELIMITER ;
