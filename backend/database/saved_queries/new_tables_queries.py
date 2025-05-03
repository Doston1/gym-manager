# file for copilot to generate the new necessary tables for the database

# New and modified tables for the gym scheduling and training dashboard functionality

# Table to store member's weekly training preferences
training_preferences = """
CREATE TABLE training_preferences (
    preference_id INT AUTO_INCREMENT PRIMARY KEY,
    member_id INT NOT NULL,
    week_start_date DATE NOT NULL,
    day_of_week ENUM('Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday') NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    preference_type ENUM('Preferred', 'Available', 'Not Available') NOT NULL,
    trainer_id INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (member_id) REFERENCES members(member_id) ON DELETE CASCADE,
    FOREIGN KEY (trainer_id) REFERENCES trainers(trainer_id) ON DELETE SET NULL,
    UNIQUE KEY (member_id, week_start_date, day_of_week, start_time, end_time)
);
"""

# Table to store the generated weekly training schedule
weekly_schedule = """
CREATE TABLE weekly_schedule (
    schedule_id INT AUTO_INCREMENT PRIMARY KEY,
    week_start_date DATE NOT NULL,
    day_of_week ENUM('Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday') NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    hall_id INT NOT NULL,
    trainer_id INT NOT NULL,
    max_capacity INT NOT NULL,
    status ENUM('Scheduled', 'In Progress', 'Completed', 'Cancelled') DEFAULT 'Scheduled',
    created_by INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (hall_id) REFERENCES halls(hall_id) ON DELETE CASCADE,
    FOREIGN KEY (trainer_id) REFERENCES trainers(trainer_id) ON DELETE CASCADE,
    FOREIGN KEY (created_by) REFERENCES users(user_id) ON DELETE CASCADE
);
"""

# Table to store member assignments to the weekly training schedule
schedule_members = """
CREATE TABLE schedule_members (
    id INT AUTO_INCREMENT PRIMARY KEY,
    schedule_id INT NOT NULL,
    member_id INT NOT NULL,
    status ENUM('Assigned', 'Confirmed', 'Cancelled', 'Attended', 'No Show') DEFAULT 'Assigned',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (schedule_id) REFERENCES weekly_schedule(schedule_id) ON DELETE CASCADE,
    FOREIGN KEY (member_id) REFERENCES members(member_id) ON DELETE CASCADE,
    UNIQUE KEY (schedule_id, member_id)
);
"""

# Table to track live training sessions
live_sessions = """
CREATE TABLE live_sessions (
    live_session_id INT AUTO_INCREMENT PRIMARY KEY,
    schedule_id INT NOT NULL,
    start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    end_time TIMESTAMP NULL,
    status ENUM('Started', 'In Progress', 'Completed', 'Cancelled') DEFAULT 'Started',
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (schedule_id) REFERENCES weekly_schedule(schedule_id) ON DELETE CASCADE
);
"""

# Table to track individual member progress during live sessions
live_session_exercises = """
CREATE TABLE live_session_exercises (
    id INT AUTO_INCREMENT PRIMARY KEY,
    live_session_id INT NOT NULL,
    member_id INT NOT NULL,
    exercise_id INT NOT NULL,
    sets_completed INT,
    actual_reps VARCHAR(100),
    weight_used VARCHAR(100),
    comments TEXT,
    completed BOOLEAN DEFAULT FALSE,
    completed_at TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (live_session_id) REFERENCES live_sessions(live_session_id) ON DELETE CASCADE,
    FOREIGN KEY (member_id) REFERENCES members(member_id) ON DELETE CASCADE,
    FOREIGN KEY (exercise_id) REFERENCES exercises(exercise_id) ON DELETE CASCADE
);
"""

# Table to track member attendance in live sessions
live_session_attendance = """
CREATE TABLE live_session_attendance (
    id INT AUTO_INCREMENT PRIMARY KEY,
    live_session_id INT NOT NULL,
    member_id INT NOT NULL,
    check_in_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    check_out_time TIMESTAMP NULL,
    status ENUM('Checked In', 'Checked Out', 'No Show') DEFAULT 'Checked In',
    notes TEXT,
    FOREIGN KEY (live_session_id) REFERENCES live_sessions(live_session_id) ON DELETE CASCADE,
    FOREIGN KEY (member_id) REFERENCES members(member_id) ON DELETE CASCADE,
    UNIQUE KEY (live_session_id, member_id)
);
"""

# Table to store active training plans for members
member_active_plans = """
CREATE TABLE member_active_plans (
    active_plan_id INT AUTO_INCREMENT PRIMARY KEY,
    member_id INT NOT NULL,
    plan_id INT NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE,
    status ENUM('Active', 'Completed', 'Cancelled') DEFAULT 'Active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY `unique_active_member_plan` (`member_id`, `status`) -- Only one active plan per member
        WHERE `status` = 'Active',
    FOREIGN KEY (member_id) REFERENCES members(member_id) ON DELETE CASCADE,
    FOREIGN KEY (plan_id) REFERENCES training_plans(plan_id)
);
"""

# Table to store muscle group training cycles (3 sessions per week focusing on different muscle groups)
training_cycles = """
CREATE TABLE training_cycles (
    cycle_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

# Table to store training sessions within a cycle
training_cycle_sessions = """
CREATE TABLE training_cycle_sessions (
    session_id INT AUTO_INCREMENT PRIMARY KEY,
    cycle_id INT NOT NULL,
    session_number INT NOT NULL, -- 1, 2, or 3 for the three sessions in a week
    muscle_focus ENUM('Upper Body', 'Lower Body', 'Core', 'Push', 'Pull', 'Legs', 'Full Body', 'Cardio', 'Other') NOT NULL,
    duration_minutes INT DEFAULT 90,
    description TEXT,
    UNIQUE KEY `unique_cycle_session` (`cycle_id`, `session_number`),
    FOREIGN KEY (cycle_id) REFERENCES training_cycles(cycle_id) ON DELETE CASCADE
);
"""

# Table to link exercises to training cycle sessions
session_exercises = """
CREATE TABLE session_exercises (
    id INT AUTO_INCREMENT PRIMARY KEY,
    session_id INT NOT NULL,
    exercise_id INT NOT NULL,
    `order` INT NOT NULL,
    sets INT NOT NULL,
    reps VARCHAR(50) NOT NULL,
    rest_seconds INT,
    notes TEXT,
    FOREIGN KEY (session_id) REFERENCES training_cycle_sessions(session_id) ON DELETE CASCADE,
    FOREIGN KEY (exercise_id) REFERENCES exercises(exercise_id)
);
"""

# Stored procedure for auto-scheduling based on preferences
schedule_generation_procedure = """
DELIMITER //

CREATE PROCEDURE generate_weekly_schedule(IN week_start_date_param DATE)
BEGIN
    DECLARE done INT DEFAULT FALSE;
    DECLARE v_hall_id, v_trainer_id, v_member_id, v_schedule_id INT;
    DECLARE v_day VARCHAR(20);
    DECLARE v_start_time, v_end_time TIME;
    DECLARE v_max_capacity INT;
    
    -- Cursor for finding halls and times where members have preferences
    DECLARE halls_times_cur CURSOR FOR
        SELECT DISTINCT
            h.hall_id,
            h.max_capacity,
            tp.day_of_week,
            tp.start_time,
            tp.end_time
        FROM
            halls h
        CROSS JOIN (
            SELECT 
                day_of_week, 
                start_time, 
                end_time
            FROM 
                training_preferences
            WHERE 
                week_start_date = week_start_date_param
            GROUP BY 
                day_of_week, start_time, end_time
            HAVING 
                COUNT(*) >= 5 -- Minimum number of members to schedule a session
        ) tp
        WHERE
            h.is_active = TRUE
            AND NOT EXISTS (
                SELECT 1 
                FROM weekly_training_schedule ws
                WHERE 
                    ws.hall_id = h.hall_id
                    AND ws.day_of_week = tp.day_of_week
                    AND ws.start_time = tp.start_time
                    AND ws.end_time = tp.end_time
                    AND ws.week_start_date = week_start_date_param
            )
        ORDER BY 
            COUNT(*) DESC; -- Prioritize time slots with more member preferences
            
    DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = TRUE;
    
    -- Open cursor
    OPEN halls_times_cur;
    
    read_loop: LOOP
        FETCH halls_times_cur INTO v_hall_id, v_max_capacity, v_day, v_start_time, v_end_time;
        IF done THEN
            LEAVE read_loop;
        END IF;
        
        -- Find an available trainer for this time slot
        SELECT trainer_id INTO v_trainer_id
        FROM trainers tr
        WHERE NOT EXISTS (
            SELECT 1
            FROM weekly_training_schedule ws
            WHERE 
                ws.trainer_id = tr.trainer_id
                AND ws.day_of_week = v_day
                AND ws.start_time = v_start_time
                AND ws.end_time = v_end_time
                AND ws.week_start_date = week_start_date_param
        )
        LIMIT 1;
        
        -- If we found a trainer, create a schedule entry
        IF v_trainer_id IS NOT NULL THEN
            INSERT INTO weekly_training_schedule (
                hall_id, 
                trainer_id, 
                day_of_week, 
                start_time, 
                end_time, 
                week_start_date, 
                max_capacity
            ) VALUES (
                v_hall_id, 
                v_trainer_id, 
                v_day, 
                v_start_time, 
                v_end_time, 
                week_start_date_param, 
                v_max_capacity
            );
            
            SET v_schedule_id = LAST_INSERT_ID();
            
            -- Assign members who preferred this slot to the schedule
            INSERT INTO member_schedule_assignments (schedule_id, member_id)
            SELECT 
                v_schedule_id, 
                tp.member_id
            FROM 
                training_preferences tp
            WHERE 
                tp.day_of_week = v_day
                AND tp.start_time = v_start_time
                AND tp.end_time = v_end_time
                AND tp.week_start_date = week_start_date_param
                AND tp.preference_type = 'Preferred'
            LIMIT v_max_capacity;
            
            -- Update the current_capacity of the schedule
            UPDATE weekly_training_schedule
            SET current_capacity = (
                SELECT COUNT(*) 
                FROM member_schedule_assignments 
                WHERE schedule_id = v_schedule_id
            )
            WHERE schedule_id = v_schedule_id;
        END IF;
    END LOOP;
    
    CLOSE halls_times_cur;
END //

DELIMITER ;
"""

# Event to automatically run schedule generation after preference window closes
schedule_generation_event = """
DELIMITER //

CREATE EVENT generate_next_week_schedule
ON SCHEDULE EVERY 1 WEEK
STARTS (SELECT TIMESTAMP(CONCAT(
    DATE_ADD(CURDATE(), INTERVAL (4 - WEEKDAY(CURDATE())) DAY), -- Next Thursday
    ' 23:59:59'
)))
DO
BEGIN
    -- Calculate the upcoming Sunday (start of next week)
    SET @next_week_start = DATE_ADD(CURDATE(), INTERVAL (7 - WEEKDAY(CURDATE())) DAY);
    
    -- Generate the schedule for next week
    CALL generate_weekly_schedule(@next_week_start);
END //

DELIMITER ;
"""

# These changes to members table fix the existing syntax issue in the members table definition
# and adds an active_cycle_id field to track which training cycle a member is currently following
fixed_members_table = """
CREATE TABLE members (
    member_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    weight DECIMAL(5,2) DEFAULT NULL,
    height DECIMAL(5,2) DEFAULT NULL,
    fitness_goal ENUM('Weight Loss','Muscle Gain','Endurance','Flexibility','General Fitness') DEFAULT NULL,
    fitness_level ENUM('Beginner','Intermediate','Advanced') DEFAULT NULL,
    health_conditions TEXT,
    active_cycle_id INT NULL,
    UNIQUE KEY user_id (user_id),
    CONSTRAINT members_ibfk_1 FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE CASCADE,
    CONSTRAINT members_ibfk_2 FOREIGN KEY (active_cycle_id) REFERENCES training_cycles (cycle_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
"""

# Initial configuration data
initial_system_config = """
INSERT INTO system_configuration (config_key, config_value, description) VALUES
('preference_day', 'Thursday', 'Day of the week when members can set preferences'),
('preference_start_time', '00:00:00', 'Start time when members can set preferences'),
('preference_end_time', '23:59:59', 'End time when members can set preferences'),
('training_duration_minutes', '90', 'Default duration of training sessions in minutes'),
('schedule_generation_time', '00:00:00', 'Time when the system generates the schedule for next week'),
('max_members_per_trainer', '10', 'Maximum number of members a trainer can handle in a training session');
"""

# View to help with schedule generation - available halls at given times
available_halls_view = """
CREATE VIEW available_halls_view AS
SELECT
    h.hall_id,
    h.name,
    h.max_capacity,
    d.day_of_week,
    t.start_time,
    t.end_time,
    w.week_start_date
FROM
    halls h
CROSS JOIN
    (SELECT DISTINCT day_of_week FROM training_preferences) d
CROSS JOIN
    (SELECT DISTINCT start_time, end_time FROM training_preferences) t
CROSS JOIN
    (SELECT DISTINCT week_start_date FROM training_preferences) w
LEFT JOIN
    weekly_training_schedule s ON
        h.hall_id = s.hall_id AND
        d.day_of_week = s.day_of_week AND
        t.start_time = s.start_time AND
        t.end_time = s.end_time AND
        w.week_start_date = s.week_start_date
WHERE
    s.schedule_id IS NULL AND
    h.is_active = TRUE;
"""

# View to help with schedule generation - available trainers at given times
available_trainers_view = """
CREATE VIEW available_trainers_view AS
SELECT
    tr.trainer_id,
    u.first_name,
    u.last_name,
    d.day_of_week,
    t.start_time,
    t.end_time,
    w.week_start_date
FROM
    trainers tr
JOIN
    users u ON tr.user_id = u.user_id
CROSS JOIN
    (SELECT DISTINCT day_of_week FROM training_preferences) d
CROSS JOIN
    (SELECT DISTINCT start_time, end_time FROM training_preferences) t
CROSS JOIN
    (SELECT DISTINCT week_start_date FROM training_preferences) w
LEFT JOIN
    weekly_training_schedule s ON
        tr.trainer_id = s.trainer_id AND
        d.day_of_week = s.day_of_week AND
        t.start_time = s.start_time AND
        t.end_time = s.end_time AND
        w.week_start_date = s.week_start_date
WHERE
    s.schedule_id IS NULL;
"""

# Training-related tables for preferences, scheduling, and live session tracking

training_preferences = """
CREATE TABLE training_preferences (
    preference_id INT AUTO_INCREMENT PRIMARY KEY,
    member_id INT NOT NULL,
    week_start_date DATE NOT NULL,
    day_of_week ENUM('Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday') NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    preference_type ENUM('Preferred', 'Available', 'Not Available') NOT NULL,
    trainer_id INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (member_id) REFERENCES members(member_id) ON DELETE CASCADE,
    FOREIGN KEY (trainer_id) REFERENCES trainers(trainer_id) ON DELETE SET NULL,
    UNIQUE KEY (member_id, week_start_date, day_of_week, start_time, end_time)
);
"""

weekly_schedule = """
CREATE TABLE weekly_schedule (
    schedule_id INT AUTO_INCREMENT PRIMARY KEY,
    week_start_date DATE NOT NULL,
    day_of_week ENUM('Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday') NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    hall_id INT NOT NULL,
    trainer_id INT NOT NULL,
    max_capacity INT NOT NULL,
    status ENUM('Scheduled', 'In Progress', 'Completed', 'Cancelled') DEFAULT 'Scheduled',
    created_by INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (hall_id) REFERENCES halls(hall_id) ON DELETE CASCADE,
    FOREIGN KEY (trainer_id) REFERENCES trainers(trainer_id) ON DELETE CASCADE,
    FOREIGN KEY (created_by) REFERENCES users(user_id) ON DELETE CASCADE
);
"""

schedule_members = """
CREATE TABLE schedule_members (
    id INT AUTO_INCREMENT PRIMARY KEY,
    schedule_id INT NOT NULL,
    member_id INT NOT NULL,
    status ENUM('Assigned', 'Confirmed', 'Cancelled', 'Attended', 'No Show') DEFAULT 'Assigned',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (schedule_id) REFERENCES weekly_schedule(schedule_id) ON DELETE CASCADE,
    FOREIGN KEY (member_id) REFERENCES members(member_id) ON DELETE CASCADE,
    UNIQUE KEY (schedule_id, member_id)
);
"""

live_sessions = """
CREATE TABLE live_sessions (
    live_session_id INT AUTO_INCREMENT PRIMARY KEY,
    schedule_id INT NOT NULL,
    start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    end_time TIMESTAMP NULL,
    status ENUM('Started', 'In Progress', 'Completed', 'Cancelled') DEFAULT 'Started',
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (schedule_id) REFERENCES weekly_schedule(schedule_id) ON DELETE CASCADE
);
"""

live_session_exercises = """
CREATE TABLE live_session_exercises (
    id INT AUTO_INCREMENT PRIMARY KEY,
    live_session_id INT NOT NULL,
    member_id INT NOT NULL,
    exercise_id INT NOT NULL,
    sets_completed INT,
    actual_reps VARCHAR(100),
    weight_used VARCHAR(100),
    comments TEXT,
    completed BOOLEAN DEFAULT FALSE,
    completed_at TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (live_session_id) REFERENCES live_sessions(live_session_id) ON DELETE CASCADE,
    FOREIGN KEY (member_id) REFERENCES members(member_id) ON DELETE CASCADE,
    FOREIGN KEY (exercise_id) REFERENCES exercises(exercise_id) ON DELETE CASCADE
);
"""

live_session_attendance = """
CREATE TABLE live_session_attendance (
    id INT AUTO_INCREMENT PRIMARY KEY,
    live_session_id INT NOT NULL,
    member_id INT NOT NULL,
    check_in_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    check_out_time TIMESTAMP NULL,
    status ENUM('Checked In', 'Checked Out', 'No Show') DEFAULT 'Checked In',
    notes TEXT,
    FOREIGN KEY (live_session_id) REFERENCES live_sessions(live_session_id) ON DELETE CASCADE,
    FOREIGN KEY (member_id) REFERENCES members(member_id) ON DELETE CASCADE,
    UNIQUE KEY (live_session_id, member_id)
);
"""

member_active_plans = """
CREATE TABLE member_active_plans (
    active_plan_id INT AUTO_INCREMENT PRIMARY KEY,
    member_id INT NOT NULL,
    plan_id INT NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE,
    status ENUM('Active', 'Completed', 'Cancelled') DEFAULT 'Active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY `unique_active_member_plan` (`member_id`, `status`) -- Only one active plan per member
        WHERE `status` = 'Active',
    FOREIGN KEY (member_id) REFERENCES members(member_id) ON DELETE CASCADE,
    FOREIGN KEY (plan_id) REFERENCES training_plans(plan_id)
);
"""

training_cycles = """
CREATE TABLE training_cycles (
    cycle_id INT AUTO_INCREMENT PRIMARY KEY,
    member_id INT NOT NULL,
    plan_id INT NOT NULL, 
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    status ENUM('Planned', 'In Progress', 'Completed', 'Cancelled') DEFAULT 'Planned',
    created_by INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (member_id) REFERENCES members(member_id) ON DELETE CASCADE,
    FOREIGN KEY (plan_id) REFERENCES training_plans(plan_id) ON DELETE CASCADE,
    FOREIGN KEY (created_by) REFERENCES users(user_id) ON DELETE CASCADE
);
"""

# Stored procedure for automatic schedule generation based on preferences
schedule_generation_procedure = """
DELIMITER //

CREATE PROCEDURE GenerateWeeklySchedule(IN p_week_start_date DATE, IN p_manager_id INT)
BEGIN
    -- Variables for hall allocation
    DECLARE v_hall_id INT;
    DECLARE v_max_capacity INT;
    
    -- Variables for time slot tracking
    DECLARE v_day VARCHAR(10);
    DECLARE v_start_time TIME;
    DECLARE v_end_time TIME;
    
    -- Variables for trainer assignment
    DECLARE v_trainer_id INT;
    DECLARE v_trainer_preference_count INT;
    
    -- Main cursor to go through each time slot and day
    DECLARE done BOOLEAN DEFAULT FALSE;
    DECLARE time_slots CURSOR FOR
        SELECT 
            day_of_week,
            start_time,
            end_time
        FROM (
            SELECT DISTINCT
                day_of_week,
                start_time,
                end_time
            FROM training_preferences
            WHERE week_start_date = p_week_start_date
            AND preference_type IN ('Preferred', 'Available')
            GROUP BY day_of_week, start_time, end_time
            HAVING COUNT(DISTINCT member_id) >= 3  -- Only consider slots with at least 3 interested members
        ) AS available_slots;
    
    DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = TRUE;
    
    -- Start by cleaning up any existing schedule for this week
    DELETE FROM weekly_schedule WHERE week_start_date = p_week_start_date;
    
    -- Open the cursor to go through time slots
    OPEN time_slots;
    
    time_slot_loop: LOOP
        -- Get next time slot 
        FETCH time_slots INTO v_day, v_start_time, v_end_time;
        IF done THEN
            LEAVE time_slot_loop;
        END IF;
        
        -- Choose a hall (simple round-robin for this example)
        SELECT hall_id, max_capacity 
        INTO v_hall_id, v_max_capacity 
        FROM halls 
        WHERE is_active = TRUE 
        ORDER BY RAND() LIMIT 1;
        
        -- Find the best trainer for this slot (one with most preferences)
        SELECT 
            tp.trainer_id,
            COUNT(tp.member_id) AS preference_count
        INTO 
            v_trainer_id,
            v_trainer_preference_count
        FROM training_preferences tp
        WHERE tp.week_start_date = p_week_start_date
        AND tp.day_of_week = v_day
        AND tp.start_time = v_start_time
        AND tp.end_time = v_end_time
        AND tp.trainer_id IS NOT NULL
        GROUP BY tp.trainer_id
        ORDER BY preference_count DESC
        LIMIT 1;
        
        -- If no trainer preference, assign one randomly
        IF v_trainer_id IS NULL THEN
            SELECT trainer_id INTO v_trainer_id FROM trainers ORDER BY RAND() LIMIT 1;
        END IF;
        
        -- Create the schedule entry
        INSERT INTO weekly_schedule (
            week_start_date, 
            day_of_week, 
            start_time, 
            end_time, 
            hall_id, 
            trainer_id, 
            max_capacity, 
            created_by
        ) VALUES (
            p_week_start_date,
            v_day,
            v_start_time,
            v_end_time,
            v_hall_id,
            v_trainer_id,
            v_max_capacity,
            p_manager_id
        );
        
        -- Assign members who marked this slot as preferred
        INSERT INTO schedule_members (schedule_id, member_id)
        SELECT 
            LAST_INSERT_ID(),
            tp.member_id
        FROM training_preferences tp
        WHERE tp.week_start_date = p_week_start_date
        AND tp.day_of_week = v_day
        AND tp.start_time = v_start_time
        AND tp.end_time = v_end_time
        AND tp.preference_type = 'Preferred'
        ORDER BY RAND()
        LIMIT v_max_capacity;
        
        -- If there's still capacity, add members who marked as available
        INSERT INTO schedule_members (schedule_id, member_id)
        SELECT 
            LAST_INSERT_ID(),
            tp.member_id
        FROM training_preferences tp
        LEFT JOIN schedule_members sm ON sm.member_id = tp.member_id AND sm.schedule_id = LAST_INSERT_ID()
        WHERE tp.week_start_date = p_week_start_date
        AND tp.day_of_week = v_day
        AND tp.start_time = v_start_time
        AND tp.end_time = v_end_time
        AND tp.preference_type = 'Available'
        AND sm.id IS NULL  -- Only members not already assigned
        ORDER BY RAND()
        LIMIT (v_max_capacity - (SELECT COUNT(*) FROM schedule_members WHERE schedule_id = LAST_INSERT_ID()));
        
    END LOOP;
    
    CLOSE time_slots;
    
END //

DELIMITER ;
"""