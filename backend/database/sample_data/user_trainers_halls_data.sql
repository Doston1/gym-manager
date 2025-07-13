-- ==================================================
-- USERS, TRAINERS, AND HALLS SAMPLE DATA
-- ==================================================
-- This file contains sample data for users, trainers, and halls tables
-- ==================================================

-- Temporarily disable safe update mode to allow bulk deletes
SET SQL_SAFE_UPDATES = 0;

-- First, clear existing data (in dependency order)
DELETE FROM trainers;
DELETE FROM users WHERE user_type = 'trainer';
DELETE FROM halls;

-- Reset auto-increment counters for halls only (users already has data)
ALTER TABLE halls AUTO_INCREMENT = 1;

-- Re-enable safe update mode
SET SQL_SAFE_UPDATES = 1;

-- ==================================================
-- USERS TABLE - TRAINERS
-- ==================================================

INSERT INTO users (auth_id, email, first_name, last_name, gender, date_of_birth, phone, profile_image_path, user_type, is_active) VALUES
('auth0|tr76512', 'john.smith@fitgym.com', 'John', 'Smith', 'Male', '1985-06-12', '+1234567890', '/images/trainers/john_smith.jpg', 'trainer', TRUE),
('auth0|tr85263', 'sarah.johnson@fitgym.com', 'Sarah', 'Johnson', 'Female', '1990-03-25', '+1987654321', '/images/trainers/sarah_johnson.jpg', 'trainer', TRUE),
('auth0|tr19753', 'michael.lee@fitgym.com', 'Michael', 'Lee', 'Male', '1988-11-08', '+1122334455', '/images/trainers/michael_lee.jpg', 'trainer', TRUE),
('auth0|tr62938', 'amanda.patel@fitgym.com', 'Amanda', 'Patel', 'Female', '1992-07-15', '+1555666777', '/images/trainers/amanda_patel.jpg', 'trainer', TRUE),
('auth0|tr53748', 'david.garcia@fitgym.com', 'David', 'Garcia', 'Male', '1983-09-30', '+1777888999', '/images/trainers/david_garcia.jpg', 'trainer', TRUE);

-- ==================================================
-- TRAINERS TABLE
-- ==================================================

-- Get the user_id values for inserted trainers
SET @john_user_id = (SELECT user_id FROM users WHERE email = 'john.smith@fitgym.com');
SET @sarah_user_id = (SELECT user_id FROM users WHERE email = 'sarah.johnson@fitgym.com');
SET @michael_user_id = (SELECT user_id FROM users WHERE email = 'michael.lee@fitgym.com');
SET @amanda_user_id = (SELECT user_id FROM users WHERE email = 'amanda.patel@fitgym.com');
SET @david_user_id = (SELECT user_id FROM users WHERE email = 'david.garcia@fitgym.com');

INSERT INTO trainers (user_id, specialization, bio, certifications, years_of_experience) VALUES
(@john_user_id, 'Strength Training, Bodybuilding', 'ACE Certified Personal Trainer with over 10 years of experience in strength and conditioning. Specializes in transforming physiques and competitive bodybuilding preparation.', 'ACE Certified Personal Trainer, NASM Performance Enhancement', 10),
(@sarah_user_id, 'Yoga, Pilates, Meditation', 'RYT-500 Yoga Instructor who combines traditional yoga with modern fitness approaches. Creates holistic programs focusing on mind-body connection and flexibility.', 'RYT-500 Yoga Alliance, Pilates Method Alliance Certified', 8),
(@michael_user_id, 'CrossFit, Functional Training', 'CrossFit Level 3 Trainer who believes in the power of functional movement. Former collegiate athlete who specializes in high-intensity workouts and athletic performance.', 'CrossFit Level 3 Trainer, NSCA CSCS', 6),
(@amanda_user_id, 'Dance Fitness, Cardio, Group Exercise', 'Energetic and motivational instructor certified in multiple group fitness formats. Known for creating high-energy workouts that feel like a party rather than exercise.', 'AFAA Group Fitness, Zumba Certified, Les Mills Instructor', 5),
(@david_user_id, 'Senior Fitness, Rehabilitation', 'Specializes in working with seniors and individuals requiring special accommodations. Focuses on functional movement, pain reduction, and quality of life improvement.', 'NASM Corrective Exercise Specialist, ACE Senior Fitness Specialist', 12);

-- ==================================================
-- HALLS TABLE
-- ==================================================

INSERT INTO halls (name, description, max_capacity, location, equipment_available, is_active) VALUES
('Main Studio', 'Our largest multi-purpose studio featuring a sprung floor and wall-to-wall mirrors. Perfect for group classes and dance-based workouts.', 30, 'Ground Floor, West Wing', 'Sound system, projector, yoga mats, exercise balls, resistance bands', TRUE),
('Zen Room', 'A tranquil space designed for mind-body classes. Features dimmable lighting and a serene atmosphere for yoga, pilates and meditation.', 20, 'Second Floor, East Wing', 'Yoga mats, blocks, straps, bolsters, meditation cushions, sound healing instruments', TRUE),
('Strength Lab', 'Dedicated strength training space featuring free weights and functional training equipment. Ideal for smaller group strength classes.', 15, 'Ground Floor, East Wing', 'Dumbbells (2-50lbs), kettlebells, barbells, squat racks, benches, suspension trainers', TRUE),
('Cycling Studio', 'Specialized studio for indoor cycling featuring stadium seating and immersive lighting. High-energy environment for intense cardio workouts.', 25, 'Second Floor, West Wing', 'Stationary bikes, sound system, performance metrics displays, atmospheric lighting', TRUE),
('Aqua Center', 'Indoor heated pool area for water-based fitness classes and rehabilitation sessions.', 20, 'Lower Level', 'Pool noodles, aqua dumbbells, resistance equipment, kickboards', TRUE);

-- ==================================================
-- VERIFICATION QUERIES
-- ==================================================

SELECT 'Users (trainers) inserted:' as status, COUNT(*) as count FROM users WHERE user_type = 'trainer';
SELECT 'Trainers inserted:' as status, COUNT(*) as count FROM trainers;
SELECT 'Halls inserted:' as status, COUNT(*) as count FROM halls;

-- Show trainers with their specializations
SELECT 
    CONCAT(u.first_name, ' ', u.last_name) as trainer_name,
    t.specialization,
    t.years_of_experience as experience_years,
    u.user_id,
    t.trainer_id
FROM trainers t
JOIN users u ON t.user_id = u.user_id
ORDER BY t.years_of_experience DESC;

-- Show halls with capacity
SELECT 
    h.name as hall_name,
    h.max_capacity,
    h.location,
    h.description
FROM halls h
ORDER BY h.max_capacity DESC;