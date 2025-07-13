-- ==================================================
-- CLASS SYSTEM MOCK DATA
-- ==================================================
-- This file contains sample data for class types and scheduled classes
-- ==================================================

-- Temporarily disable safe update mode to allow bulk deletes
SET SQL_SAFE_UPDATES = 0;

-- First, clear existing data (in dependency order)
DELETE FROM class_bookings; -- Delete bookings first to maintain referential integrity
DELETE FROM classes;
DELETE FROM class_types;

-- Reset auto-increment counters
ALTER TABLE class_types AUTO_INCREMENT = 1;
ALTER TABLE classes AUTO_INCREMENT = 1;

-- Re-enable safe update mode
SET SQL_SAFE_UPDATES = 1;

-- ==================================================
-- CLASS TYPES TABLE
-- ==================================================

INSERT INTO class_types (name, description, duration_minutes, difficulty_level, equipment_needed, default_max_participants, default_price, is_active) VALUES
-- Cardio Classes
('HIIT Workout', 'High-Intensity Interval Training to maximize calorie burn and improve cardiovascular fitness', 45, 'Advanced', 'Exercise mats, dumbbells, kettlebells', 20, 15.99, TRUE),
('Spinning', 'Indoor cycling workout with high-energy music and instructor-led routines', 60, 'Intermediate', 'Stationary bikes', 15, 12.99, TRUE),
('Zumba', 'Dance fitness program featuring Latin and international music with dance movements', 55, 'All Levels', 'None', 25, 10.99, TRUE),
('Cardio Kickboxing', 'High-energy workout combining martial arts techniques with cardio', 50, 'Intermediate', 'Boxing gloves (optional), exercise mats', 20, 14.99, TRUE),

-- Mind & Body Classes
('Yoga Flow', 'Dynamic yoga practice connecting breath with movement through flowing sequences', 75, 'All Levels', 'Yoga mats, blocks, straps', 18, 12.99, TRUE),
('Pilates', 'Exercise system focused on improving flexibility, strength and body awareness', 60, 'Intermediate', 'Exercise mats, Pilates rings', 15, 13.99, TRUE),
('Meditation & Mindfulness', 'Guided meditation sessions for stress reduction and mental clarity', 45, 'Beginner', 'Meditation cushions, yoga mats', 20, 9.99, TRUE),
('Tai Chi', 'Ancient Chinese martial art practiced for defense and health benefits', 60, 'All Levels', 'None', 15, 11.99, TRUE),

-- Strength & Conditioning Classes
('BodyPump', 'Barbell workout designed to strengthen and tone your entire body', 55, 'Intermediate', 'Barbells, weight plates, steps', 20, 14.99, TRUE),
('CrossFit Style', 'High-intensity functional movements combining gymnastics, weightlifting, and cardio', 60, 'Advanced', 'Various equipment: barbells, kettlebells, pull-up bars', 12, 16.99, TRUE),
('Core & Abs', 'Focused core workout to strengthen abdominal and back muscles', 30, 'All Levels', 'Exercise mats, stability balls', 25, 9.99, TRUE),
('Circuit Training', 'Fast-paced workout alternating between different exercise stations', 45, 'Intermediate', 'Various equipment: dumbbells, medicine balls, TRX', 18, 13.99, TRUE),

-- Specialty Classes
('Senior Fitness', 'Low-impact exercises designed specifically for older adults', 45, 'Beginner', 'Chairs, light dumbbells, resistance bands', 15, 8.99, TRUE),
('Prenatal Yoga', 'Safe yoga practice modified for expectant mothers', 60, 'Beginner', 'Yoga mats, bolsters, blocks', 12, 14.99, TRUE),
('Aqua Fitness', 'Water-based workout providing resistance with reduced joint impact', 45, 'All Levels', 'Pool noodles, water dumbbells', 20, 11.99, TRUE);

-- ==================================================
-- CLASSES TABLE
-- ==================================================

-- Calculate dates relative to current date for realistic scheduling
SET @today = CURRENT_DATE();
SET @next_monday = @today + INTERVAL (7 - WEEKDAY(@today)) % 7 DAY;
SET @next_tuesday = @next_monday + INTERVAL 1 DAY;
SET @next_wednesday = @next_monday + INTERVAL 2 DAY;
SET @next_thursday = @next_monday + INTERVAL 3 DAY;
SET @next_friday = @next_monday + INTERVAL 4 DAY;
SET @next_saturday = @next_monday + INTERVAL 5 DAY;
SET @next_sunday = @next_monday + INTERVAL 6 DAY;

-- Insert classes for the upcoming week
INSERT INTO classes (class_type_id, trainer_id, hall_id, date, start_time, end_time, max_participants, current_participants, price, status, notes) VALUES
-- Monday Classes
(1, 1, 1, @next_monday, '07:00:00', '07:45:00', 20, 5, 15.99, 'Scheduled', 'Morning HIIT to start your week!'),
(5, 2, 2, @next_monday, '09:00:00', '10:15:00', 18, 12, 12.99, 'Scheduled', 'Morning yoga to reduce stress'),
(10, 3, 3, @next_monday, '12:00:00', '13:00:00', 12, 8, 16.99, 'Scheduled', 'Lunch CrossFit session'),
(3, 4, 1, @next_monday, '17:30:00', '18:25:00', 25, 20, 10.99, 'Scheduled', 'After-work Zumba party'),
(11, 5, 2, @next_monday, '19:00:00', '19:30:00', 25, 15, 9.99, 'Scheduled', 'Evening core workout'),

-- Tuesday Classes
(2, 3, 3, @next_tuesday, '06:30:00', '07:30:00', 15, 7, 12.99, 'Scheduled', 'Early morning spinning class'),
(6, 1, 2, @next_tuesday, '10:00:00', '11:00:00', 15, 10, 13.99, 'Scheduled', 'Mid-morning Pilates'),
(9, 5, 1, @next_tuesday, '12:30:00', '13:25:00', 20, 12, 14.99, 'Scheduled', 'Lunch BodyPump session'),
(7, 2, 2, @next_tuesday, '16:00:00', '16:45:00', 20, 5, 9.99, 'Scheduled', 'Afternoon meditation'),
(4, 4, 1, @next_tuesday, '18:30:00', '19:20:00', 20, 18, 14.99, 'Scheduled', 'Evening kickboxing'),

-- Wednesday Classes
(1, 1, 1, @next_wednesday, '07:00:00', '07:45:00', 20, 0, 15.99, 'Cancelled', 'Class cancelled due to instructor illness'),
(8, 3, 2, @next_wednesday, '09:30:00', '10:30:00', 15, 8, 11.99, 'Scheduled', 'Morning Tai Chi'),
(12, 5, 3, @next_wednesday, '12:00:00', '12:45:00', 18, 18, 13.99, 'Scheduled', 'Lunch circuit training - FULL'),
(5, 2, 2, @next_wednesday, '17:00:00', '18:15:00', 18, 15, 12.99, 'Scheduled', 'Evening yoga flow'),
(3, 4, 1, @next_wednesday, '19:00:00', '19:55:00', 25, 10, 10.99, 'Scheduled', 'Evening Zumba'),

-- Thursday Classes
(2, 3, 3, @next_thursday, '06:30:00', '07:30:00', 15, 15, 12.99, 'Scheduled', 'Early morning spinning - FULL'),
(13, 1, 2, @next_thursday, '10:00:00', '10:45:00', 15, 7, 8.99, 'Scheduled', 'Senior fitness class'),
(10, 5, 1, @next_thursday, '12:30:00', '13:30:00', 12, 9, 16.99, 'Scheduled', 'Lunch CrossFit session'),
(14, 2, 2, @next_thursday, '16:00:00', '17:00:00', 12, 4, 14.99, 'Scheduled', 'Prenatal yoga'),
(4, 4, 1, @next_thursday, '18:30:00', '19:20:00', 20, 0, 14.99, 'Cancelled', 'Class cancelled due to low enrollment'),

-- Friday Classes
(1, 1, 1, @next_friday, '07:00:00', '07:45:00', 20, 10, 15.99, 'Scheduled', 'Morning HIIT'),
(6, 2, 2, @next_friday, '09:00:00', '10:00:00', 15, 12, 13.99, 'Scheduled', 'Morning Pilates'),
(9, 3, 3, @next_friday, '12:00:00', '12:55:00', 20, 18, 14.99, 'Scheduled', 'Lunch BodyPump session'),
(11, 5, 1, @next_friday, '17:30:00', '18:00:00', 25, 23, 9.99, 'Scheduled', 'Evening core workout'),
(5, 4, 2, @next_friday, '19:00:00', '20:15:00', 18, 16, 12.99, 'Scheduled', 'End-of-week relaxation yoga'),

-- Weekend Classes
(15, 3, 3, @next_saturday, '09:00:00', '09:45:00', 20, 12, 11.99, 'Scheduled', 'Morning aqua fitness'),
(10, 5, 1, @next_saturday, '10:30:00', '11:30:00', 12, 12, 16.99, 'Scheduled', 'Weekend CrossFit - FULL'),
(3, 4, 2, @next_saturday, '12:00:00', '12:55:00', 25, 20, 10.99, 'Scheduled', 'Saturday Zumba party'),
(12, 1, 3, @next_saturday, '15:00:00', '15:45:00', 18, 10, 13.99, 'Scheduled', 'Afternoon circuit training'),
(5, 2, 2, @next_saturday, '17:00:00', '18:15:00', 18, 18, 12.99, 'Scheduled', 'Weekend yoga flow - FULL'),

(8, 3, 2, @next_sunday, '09:30:00', '10:30:00', 15, 7, 11.99, 'Scheduled', 'Sunday morning Tai Chi'),
(7, 2, 3, @next_sunday, '11:00:00', '11:45:00', 20, 15, 9.99, 'Scheduled', 'Mindfulness meditation'),
(11, 5, 1, @next_sunday, '13:00:00', '13:30:00', 25, 16, 9.99, 'Scheduled', 'Quick core workout'),
(4, 4, 2, @next_sunday, '15:00:00', '15:50:00', 20, 14, 14.99, 'Scheduled', 'Sunday kickboxing'),
(5, 1, 3, @next_sunday, '17:30:00', '18:45:00', 18, 5, 12.99, 'Scheduled', 'Evening relaxation yoga');

-- Add some historical classes (completed/rescheduled)
SET @last_monday = @today - INTERVAL DAYOFWEEK(@today) + 1 DAY;
SET @last_tuesday = @last_monday + INTERVAL 1 DAY;
SET @last_wednesday = @last_monday + INTERVAL 2 DAY;

INSERT INTO classes (class_type_id, trainer_id, hall_id, date, start_time, end_time, max_participants, current_participants, price, status, notes) VALUES
-- Last Week's Classes (Completed)
(1, 1, 1, @last_monday, '07:00:00', '07:45:00', 20, 12, 15.99, 'Completed', 'Morning HIIT'),
(5, 2, 2, @last_tuesday, '09:00:00', '10:15:00', 18, 16, 12.99, 'Completed', 'Morning yoga session'),
(3, 4, 1, @last_wednesday, '17:30:00', '18:25:00', 25, 22, 10.99, 'Completed', 'Very popular Zumba class'),
(2, 3, 3, @last_monday, '06:30:00', '07:30:00', 15, 10, 12.99, 'Rescheduled', 'Rescheduled to Tuesday due to trainer illness');

-- ==================================================
-- VERIFICATION QUERIES
-- ==================================================

SELECT 'Class types inserted:' as status, COUNT(*) as count FROM class_types;
SELECT 'Classes inserted:' as status, COUNT(*) as count FROM classes;
SELECT 'Scheduled classes:' as status, COUNT(*) as count FROM classes WHERE status = 'Scheduled';
SELECT 'Completed classes:' as status, COUNT(*) as count FROM classes WHERE status = 'Completed';

-- Show upcoming week's schedule
SELECT 
    c.class_id,
    ct.name as class_type,
    DATE_FORMAT(c.date, '%W, %M %e') as class_date,
    TIME_FORMAT(c.start_time, '%h:%i %p') as start_time,
    TIME_FORMAT(c.end_time, '%h:%i %p') as end_time,
    CONCAT(c.current_participants, '/', c.max_participants) as attendance,
    c.status,
    c.price
FROM classes c
JOIN class_types ct ON c.class_type_id = ct.class_type_id
WHERE c.date BETWEEN @today AND @today + INTERVAL 7 DAY
ORDER BY c.date, c.start_time;

-- Popularity analysis
SELECT 
    ct.name as class_type,
    COUNT(c.class_id) as total_classes,
    AVG(c.current_participants) as avg_attendance,
    SUM(c.price * c.current_participants) as estimated_revenue
FROM class_types ct
JOIN classes c ON ct.class_type_id = c.class_type_id
GROUP BY ct.class_type_id
ORDER BY avg_attendance DESC;