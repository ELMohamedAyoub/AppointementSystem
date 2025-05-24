-- Initialize the Medical Pro database
-- This file combines all SQL scripts for easy initialization

-- First create schema
SOURCE medical_schema.sql;

-- Create stored procedures, functions, and triggers
SOURCE medical_procedures_functions.sql;

-- Insert seed data
SOURCE medical_seed_data.sql;

-- Display successful initialization message
SELECT 'Database initialization completed successfully!' AS 'Status'; 