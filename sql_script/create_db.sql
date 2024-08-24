-- Drop the database if it exists
DROP DATABASE IF EXISTS nrb_db;

-- Drop the user if it exists
DROP USER IF EXISTS 'jama'@'localhost';

-- Create the database
CREATE DATABASE nrb_db;

-- Create the user with password
CREATE USER 'jama'@'localhost' IDENTIFIED BY 'jb';

-- Grant all privileges on the database to the user
GRANT ALL PRIVILEGES ON nrb_db.* TO 'jama'@'localhost';

-- Apply the changes
FLUSH PRIVILEGES;