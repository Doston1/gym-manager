users = """
CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,  -- Your internal database ID
    firebase_uid VARCHAR(128) UNIQUE NOT NULL,  -- Firebase UID
    email VARCHAR(255) NOT NULL UNIQUE,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    phone VARCHAR(20),
    date_of_birth DATE,
    gender ENUM('Male', 'Female', 'Other', 'Prefer not to say'),
    profile_image_path VARCHAR(255),
    user_type ENUM('member', 'trainer', 'manager') NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);
"""

members = """
CREATE TABLE members (
  member_id int NOT NULL,
  user_id int NOT NULL,
  weight decimal(5,2) DEFAULT NULL,
  height decimal(5,2) DEFAULT NULL,
  fitness_goal enum('Weight Loss','Muscle Gain','Endurance','Flexibility','General Fitness') DEFAULT NULL,
  fitness_level enum('Beginner','Intermediate','Advanced') DEFAULT NULL,
  health_conditions` text,
  PRIMARY KEY (`member_id`),
  UNIQUE KEY `user_id` (`user_id`),
  CONSTRAINT `members_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
"""

trainers = """
CREATE TABLE trainers (
    trainer_id INT PRIMARY KEY,
    user_id INT NOT NULL UNIQUE,
    specialization VARCHAR(255),
    bio TEXT,
    certifications TEXT,
    years_of_experience INT,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);
"""

managers = """
CREATE TABLE managers (
    manager_id INT PRIMARY KEY,
    user_id INT NOT NULL UNIQUE,
    department VARCHAR(100),
    hire_date DATE,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);
"""

membership_types = """
CREATE TABLE membership_types (
    membership_type_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    price_monthly DECIMAL(10,2) NOT NULL,
    price_quarterly DECIMAL(10,2),
    price_yearly DECIMAL(10,2),
    max_classes_per_week INT,
    custom_plans_period INT, -- Number of weeks between allowed custom plans
    unlimited_custom_plans BOOLEAN DEFAULT FALSE,
    class_booking_discount DECIMAL(5,2) DEFAULT 0, -- Percentage discount on class bookings
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
); 
"""

memberships = """
CREATE TABLE memberships (
    membership_id INT AUTO_INCREMENT PRIMARY KEY,
    member_id INT NOT NULL,
    membership_type_id INT NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    payment_status ENUM('Pending', 'Paid', 'Failed', 'Cancelled') DEFAULT 'Pending',
    auto_renew BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (member_id) REFERENCES members(member_id) ON DELETE CASCADE,
    FOREIGN KEY (membership_type_id) REFERENCES membership_types(membership_type_id)
);
"""

halls = """
CREATE TABLE halls (
    hall_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    max_capacity INT NOT NULL,
    location VARCHAR(255),
    equipment_available TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
"""

gym_hours = """
CREATE TABLE gym_hours (
    hours_id INT AUTO_INCREMENT PRIMARY KEY,
    day_of_week ENUM('Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday') NOT NULL,
    opening_time TIME NOT NULL,
    closing_time TIME NOT NULL,
    is_closed BOOLEAN DEFAULT FALSE,
    special_note TEXT,
    is_holiday BOOLEAN DEFAULT FALSE,
    UNIQUE (day_of_week)
);
"""

class_types = """
CREATE TABLE class_types (
    class_type_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    duration_minutes INT NOT NULL,
    difficulty_level ENUM('Beginner', 'Intermediate', 'Advanced', 'All Levels') DEFAULT 'All Levels',
    equipment_needed TEXT,
    default_max_participants INT,
    default_price DECIMAL(10,2) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
"""

classes = """
CREATE TABLE classes (
    class_id INT AUTO_INCREMENT PRIMARY KEY,
    class_type_id INT NOT NULL,
    trainer_id INT NOT NULL,
    hall_id INT NOT NULL,
    date DATE NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    max_participants INT NOT NULL,
    current_participants INT DEFAULT 0,
    price DECIMAL(10,2) NOT NULL,
    status ENUM('Scheduled', 'Cancelled', 'Completed', 'Rescheduled') DEFAULT 'Scheduled',
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (class_type_id) REFERENCES class_types(class_type_id),
    FOREIGN KEY (trainer_id) REFERENCES trainers(trainer_id),
    FOREIGN KEY (hall_id) REFERENCES halls(hall_id),
    INDEX (date, start_time)
);
"""

class_bookings = """
CREATE TABLE class_bookings (
    booking_id INT AUTO_INCREMENT PRIMARY KEY,
    class_id INT NOT NULL,
    member_id INT NOT NULL,
    booking_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    payment_status ENUM('Pending', 'Paid', 'Free', 'Cancelled') NOT NULL,
    amount_paid DECIMAL(10,2),
    attendance_status ENUM('Not Attended', 'Attended', 'Cancelled', 'No Show') DEFAULT 'Not Attended',
    cancellation_date TIMESTAMP NULL,
    cancellation_reason TEXT,
    email_notification_sent BOOLEAN DEFAULT FALSE,
    UNIQUE (class_id, member_id),
    FOREIGN KEY (class_id) REFERENCES classes(class_id),
    FOREIGN KEY (member_id) REFERENCES members(member_id) ON DELETE CASCADE
);
"""

training_plans = """
CREATE TABLE training_plans (
    plan_id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    difficulty_level ENUM('Beginner', 'Intermediate', 'Advanced', 'All Levels') DEFAULT 'All Levels',
    duration_weeks INT NOT NULL,
    days_per_week INT NOT NULL,
    primary_focus ENUM('Weight Loss', 'Muscle Gain', 'Endurance', 'Flexibility', 'Strength', 'General Fitness') NOT NULL,
    secondary_focus ENUM('Weight Loss', 'Muscle Gain', 'Endurance', 'Flexibility', 'Strength', 'General Fitness'),
    target_gender ENUM('Any', 'Male', 'Female') DEFAULT 'Any',
    min_age INT,
    max_age INT,
    equipment_needed TEXT,
    created_by INT, -- Reference to trainers.trainer_id
    is_custom BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (created_by) REFERENCES trainers(trainer_id)
);
"""

training_plan_days = """
CREATE TABLE training_plan_days (
    day_id INT AUTO_INCREMENT PRIMARY KEY,
    plan_id INT NOT NULL,
    day_number INT NOT NULL, -- 1 for day 1, 2 for day 2, etc.
    name VARCHAR(255),
    focus VARCHAR(255), -- E.g., "Chest and Triceps", "Lower Body", etc.
    description TEXT,
    duration_minutes INT,
    calories_burn_estimate INT,
    UNIQUE (plan_id, day_number),
    FOREIGN KEY (plan_id) REFERENCES training_plans(plan_id) ON DELETE CASCADE
);
"""

exercises = """
CREATE TABLE exercises (
    exercise_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    instructions TEXT,
    difficulty_level ENUM('Beginner', 'Intermediate', 'Advanced') DEFAULT 'Beginner',
    primary_muscle_group ENUM('Chest', 'Back', 'Shoulders', 'Arms', 'Legs', 'Core', 'Full Body', 'Cardio') NOT NULL,
    secondary_muscle_groups TEXT,
    equipment_needed TEXT,
    image_url VARCHAR(255),
    video_url VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
"""
training_day_exercisese = """
CREATE TABLE training_day_exercises (
    id INT AUTO_INCREMENT PRIMARY KEY,
    day_id INT NOT NULL,
    exercise_id INT NOT NULL,
    `order` INT NOT NULL, -- Sequence of exercises within the day
    sets INT,
    reps VARCHAR(50), -- Could be a range like "8-12" or specific like "10"
    rest_seconds INT,
    duration_seconds INT, -- For timed exercises
    notes TEXT,
    FOREIGN KEY (day_id) REFERENCES training_plan_days(day_id) ON DELETE CASCADE,
    FOREIGN KEY (exercise_id) REFERENCES exercises(exercise_id)
);
"""

member_saved_plans = """
CREATE TABLE member_saved_plans (
    id INT AUTO_INCREMENT PRIMARY KEY,
    member_id INT NOT NULL,
    plan_id INT NOT NULL,
    saved_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    notes TEXT,
    UNIQUE (member_id, plan_id),
    FOREIGN KEY (member_id) REFERENCES members(member_id) ON DELETE CASCADE,
    FOREIGN KEY (plan_id) REFERENCES training_plans(plan_id)
);
"""

custom_plan_requests = """
CREATE TABLE custom_plan_requests (
    request_id INT AUTO_INCREMENT PRIMARY KEY,
    member_id INT NOT NULL,
    goal TEXT NOT NULL,
    days_per_week INT NOT NULL,
    focus_areas TEXT,
    equipment_available TEXT,
    health_limitations TEXT,
    request_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    assigned_trainer_id INT,
    status ENUM('Pending', 'Assigned', 'In Progress', 'Completed', 'Cancelled') DEFAULT 'Pending',
    completed_plan_id INT, -- References training_plans.plan_id when complete
    notes TEXT,
    FOREIGN KEY (member_id) REFERENCES members(member_id) ON DELETE CASCADE,
    FOREIGN KEY (assigned_trainer_id) REFERENCES trainers(trainer_id),
    FOREIGN KEY (completed_plan_id) REFERENCES training_plans(plan_id)
);
"""

financial_transactions = """
CREATE TABLE financial_transactions (
    transaction_id INT AUTO_INCREMENT PRIMARY KEY,
    member_id INT,
    transaction_type ENUM('Membership Fee', 'Class Booking', 'Cancellation Fee', 'Refund', 'Other') NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    payment_method ENUM('Credit Card', 'Debit Card', 'Cash', 'Bank Transfer', 'Other') NOT NULL,
    transaction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status ENUM('Pending', 'Completed', 'Failed', 'Refunded') DEFAULT 'Pending',
    reference_id VARCHAR(255), -- Can reference membership_id or booking_id depending on transaction_type
    notes TEXT,
    FOREIGN KEY (member_id) REFERENCES members(member_id)
);
"""

email_notifications = """
CREATE TABLE email_notifications (
    notification_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    subject VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status ENUM('Sent', 'Failed', 'Pending') DEFAULT 'Pending',
    related_type ENUM('Class Booking', 'Class Cancellation', 'Membership', 'Custom Plan', 'General') NOT NULL,
    related_id INT, -- Can be booking_id, membership_id, etc. depending on related_type
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);
"""

initial_data_setup = """
INSERT INTO membership_types (name, description, price_monthly, max_classes_per_week, custom_plans_period, unlimited_custom_plans) VALUES
('Basic', 'Access to pre-built training programs and ability to book classes separately', 29.99, 0, NULL, FALSE),
('Premium', 'Everything in Basic plus booking of up to 2 classes per week and a custom training plan every 3 weeks', 59.99, 2, 3, FALSE),
('Pro', 'Unlimited class bookings and custom training plans', 99.99, NULL, NULL, TRUE);
"""
