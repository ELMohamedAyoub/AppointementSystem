# Système de Gestion des Rendez-vous Médicaux
## 1. Contexte et Objectifs
### 1.1 Contexte
Les centres médicaux et les cabinets de consultation ont besoin d'un système simple et efficace pour gérer les rendez-vous entre patients et médecins. Actuellement, la prise de rendez-vous se fait souvent par téléphone ou en personne, ce qui peut entraîner des erreurs et un manque d'efficacité.
### 1.2 Objectifs
- Développer un système permettant aux patients de prendre, modifier et annuler leurs rendez-vous.
- Assurer un suivi efficace des disponibilités des médecins.
- Simplifier l'accès aux informations pour les patients et les professionnels de santé.
---
## 2. Périmètre du Projet
Le projet inclut les fonctionnalités suivantes :
- Inscription et gestion des utilisateurs (patients et médecins).
- Prise, modification et annulation des rendez-vous.
- Consultation des disponibilités en temps réel.
- Accès restreint selon les rôles (patients et médecins et secretariat).
---
## 3. Exigences Fonctionnelles
### 3.1 Gestion des Rendez-vous
- Le patient peut consulter les disponibilités des médecins.
- Il peut réserver un créneau et recevoir une confirmation.
- Le patient peut annuler ou modifier son rendez-vous.
- Le médecin peut voir ses rendez-vous planifiés.
### 3.2 Gestion des Utilisateurs
- *Patient* : Inscription, connexion, prise et gestion de rendez-vous.
- *Médecin* : Connexion, consultation et gestion de disponibilités.
---
## 4. Exigences Techniques
### 4.1 Base de Données SQL (Avancé)
La base de données utilisera *SQL avancé, incluant des **procédures stockées, des **fonctions SQL, des **jointures complexes, ainsi qu'une **gestion des rôles* et un *plan de gestion des erreurs**.
#### 4.1.1 Procédures Stockées
Les procédures stockées permettront d'automatiser la gestion des rendez-vous et d'assurer l'intégrité des données.
*Exemple : Création d'un rendez-vous avec transaction et gestion d'erreur*
````SQL
DELIMITER 
CREATE PROCEDURE CreerRendezVous(
    IN patient_id INT, 
    IN medecin_id INT, 
    IN date_rdv DATETIME
)
BEGIN
    DECLARE dispo INT;
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        SIGNAL SQLSTATE '45000' 
        SET MESSAGE_TEXT = 'Erreur lors de la création du rendez-vous';
    END;
    
    START TRANSACTION;
    
    -- Vérifier la disponibilité du médecin
    SELECT COUNT(*) INTO dispo FROM rendez_vous 
    WHERE medecin_id = medecin_id AND date_rdv = date_rdv;
    
    IF dispo = 0 THEN
        INSERT INTO rendez_vous (patient_id, medecin_id, date_rdv) 
        VALUES (patient_id, medecin_id, date_rdv);
        COMMIT;
    ELSE
        ROLLBACK;
        SIGNAL SQLSTATE '45000' 
        SET MESSAGE_TEXT = 'Ce créneau est déjà pris';
    END IF;
END
DELIMITER ;
````
Cette procédure utilise *les transactions et la gestion des erreurs* pour garantir l'intégrité des données.
#### 4.1.2 Jointures Avancées
Les jointures complexes permettront d'extraire efficacement les données nécessaires aux utilisateurs.
*Exemple : Récupérer la liste des rendez-vous avec les détails des patients et médecins*
````SQL
SELECT r.id, r.date_rdv, 
       p.nom AS patient_nom, p.prenom AS patient_prenom, 
       m.nom AS medecin_nom, m.specialite
FROM rendez_vous r
INNER JOIN patients p ON r.patient_id = p.id
INNER JOIN medecins m ON r.medecin_id = m.id
WHERE r.date_rdv > NOW()
ORDER BY r.date_rdv;
````
Cette requête combine plusieurs tables pour afficher toutes les informations pertinentes.
#### 4.1.3 Fonctions SQL
Les fonctions SQL permettront d'effectuer des calculs et d'extraire des données précises.
*Exemple : Nombre de rendez-vous d'un patient*
````SQL
CREATE FUNCTION NbRendezVous(patient_id INT) RETURNS INT
DETERMINISTIC
BEGIN
    DECLARE total INT;
    SELECT COUNT(*) INTO total FROM rendez_vous WHERE patient_id = patient_id;
    RETURN total;
END;
````
Cette fonction retourne le nombre de rendez-vous d'un patient donné.
#### 4.1.4 Rôles et Permissions
Pour assurer la sécurité, des rôles SQL seront mis en place :
- *Patient* : Peut prendre et annuler ses propres rendez-vous.
- *Médecin* : Peut consulter ses propres rendez-vous.
- *Admin* : Peut gérer tous les rendez-vous et utilisateurs.
*Exemple : Création d'un rôle Patient*
````SQL
CREATE ROLE patient_role;
GRANT SELECT, INSERT, DELETE ON rendez_vous TO patient_role;
````
Chaque utilisateur se verra assigner un rôle selon son statut.
#### 4.1.5 Gestion des Erreurs
Un système de gestion des erreurs sera implémenté pour capturer et journaliser les erreurs SQL.
*Exemple : Capture des erreurs dans un log*
````SQL
CREATE TABLE log_erreurs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    message TEXT,
    date_erreur TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE PROCEDURE LogErreur(IN message TEXT)
BEGIN
    INSERT INTO log_erreurs (message) VALUES (message);
END;
````
Toutes les erreurs critiques seront enregistrées pour analyse.
### 4.2 Architecture Applicative
- *Back-end* : Python avec Flask ou Django.
- *Connexion à la base de données* avec SQLAlchemy.
- *Interface* : Application en ligne simple (CLI ou interface basique).
---
## 5. Contraintes
- L'application doit être simple à utiliser et intuitive.
- La gestion des accès doit être bien définie (patients et médecins).
- La base de données doit assurer une bonne intégrité des informations.
---
## 6. Livrables
- Base de données SQL avec tables, procédures stockées, jointures complexes et rôles.
- Code source Python structurant l'application.
- Documentation technique et guide d'utilisation.
---
## 7. Conclusion
Ce système repose sur l'utilisation de *SQL avancé* pour gérer les rendez-vous de manière efficace et sécurisée. Les procédures stockées, fonctions SQL, jointures complexes et rôles permettent d'assurer une gestion fluide et robuste des données. En intégrant Python pour le traitement des données, cette solution sera simple à utiliser et rapide à déployer.