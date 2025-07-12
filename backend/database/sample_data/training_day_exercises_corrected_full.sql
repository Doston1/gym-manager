-- ==================================================
-- CORRECTED TRAINING MOCK DATA - FULL VERSION
-- ==================================================
-- This file contains corrected mock data that matches your exact table structure
-- with complete training day exercises for all plans
-- ==================================================

-- Temporarily disable safe update mode to allow bulk deletes
SET SQL_SAFE_UPDATES = 0;

-- First, clear existing data (in dependency order)
DELETE FROM training_day_exercises;
DELETE FROM training_plan_days;
DELETE FROM training_plans;
DELETE FROM exercises;

-- Reset auto-increment counters
ALTER TABLE exercises AUTO_INCREMENT = 1;
ALTER TABLE training_plans AUTO_INCREMENT = 1;
ALTER TABLE training_plan_days AUTO_INCREMENT = 1;
ALTER TABLE training_day_exercises AUTO_INCREMENT = 1;

-- Re-enable safe update mode
SET SQL_SAFE_UPDATES = 1;

-- ==================================================
-- EXERCISES TABLE
-- ==================================================

INSERT INTO exercises (name, description, instructions, difficulty_level, primary_muscle_group, secondary_muscle_groups, equipment_needed, image_url, video_url) VALUES

-- CHEST EXERCISES
('Push-ups', 'Classic bodyweight chest exercise', 'Start in plank position. Lower body until chest nearly touches ground, then push back up. Keep core tight and body straight.', 'Beginner', 'Chest', 'Pectorals, Triceps, Anterior Deltoids', 'None', '/images/pushups.jpg', '/videos/pushups.mp4'),
('Bench Press', 'Primary chest building exercise with barbell', 'Lie on bench, grip barbell slightly wider than shoulders. Lower to chest, pause, then press up explosively.', 'Intermediate', 'Chest', 'Pectorals, Triceps, Anterior Deltoids', 'Barbell, Bench', '/images/bench_press.jpg', '/videos/bench_press.mp4'),
('Incline Dumbbell Press', 'Upper chest focused pressing movement', 'Set bench to 30-45 degrees. Press dumbbells up and slightly together at top. Control the descent.', 'Intermediate', 'Chest', 'Upper Pectorals, Triceps, Anterior Deltoids', 'Dumbbells, Incline Bench', '/images/incline_press.jpg', '/videos/incline_press.mp4'),
('Chest Flyes', 'Isolation exercise for chest development', 'Lie on bench with dumbbells. Arc weights out and down, feeling stretch in chest. Bring back together with controlled motion.', 'Intermediate', 'Chest', 'Pectorals, Anterior Deltoids', 'Dumbbells, Bench', '/images/chest_flyes.jpg', '/videos/chest_flyes.mp4'),
('Dips', 'Compound bodyweight chest and tricep exercise', 'Support body on dip bars. Lower until shoulders below elbows, then push back up. Lean forward for more chest activation.', 'Advanced', 'Chest', 'Lower Pectorals, Triceps, Anterior Deltoids', 'Dip Bars', '/images/dips.jpg', '/videos/dips.mp4'),

-- BACK EXERCISES  
('Pull-ups', 'Ultimate upper body pulling exercise', 'Hang from bar with overhand grip. Pull body up until chin clears bar. Lower with control.', 'Advanced', 'Back', 'Latissimus Dorsi, Rhomboids, Middle Trapezius, Biceps', 'Pull-up Bar', '/images/pullups.jpg', '/videos/pullups.mp4'),
('Bent-over Rows', 'Compound back building exercise', 'Hinge at hips with slight knee bend. Pull bar to lower chest/upper abdomen. Squeeze shoulder blades together.', 'Intermediate', 'Back', 'Latissimus Dorsi, Rhomboids, Middle Trapezius, Rear Deltoids, Biceps', 'Barbell', '/images/bent_rows.jpg', '/videos/bent_rows.mp4'),
('Lat Pulldowns', 'Machine-based latissimus dorsi exercise', 'Sit at machine, lean back slightly. Pull bar to upper chest while squeezing shoulder blades down and back.', 'Beginner', 'Back', 'Latissimus Dorsi, Rhomboids, Middle Trapezius, Biceps', 'Lat Pulldown Machine', '/images/lat_pulldowns.jpg', '/videos/lat_pulldowns.mp4'),
('Deadlifts', 'King of all exercises - posterior chain dominant', 'Stand with bar over mid-foot. Hinge at hips, grab bar, drive through heels to stand tall. Hip hinge movement pattern.', 'Advanced', 'Back', 'Erector Spinae, Latissimus Dorsi, Rhomboids, Trapezius, Glutes, Hamstrings', 'Barbell', '/images/deadlifts.jpg', '/videos/deadlifts.mp4'),
('Seated Cable Rows', 'Horizontal pulling for mid-back development', 'Sit at cable machine, pull handle to torso while squeezing shoulder blades. Control the return.', 'Beginner', 'Back', 'Rhomboids, Middle Trapezius, Latissimus Dorsi, Rear Deltoids, Biceps', 'Cable Machine', '/images/cable_rows.jpg', '/videos/cable_rows.mp4'),

-- SHOULDER EXERCISES
('Overhead Press', 'Primary shoulder building exercise', 'Stand with barbell at shoulder height. Press straight up overhead, lock out arms. Lower with control.', 'Intermediate', 'Shoulders', 'Anterior Deltoids, Medial Deltoids, Triceps, Upper Trapezius', 'Barbell', '/images/overhead_press.jpg', '/videos/overhead_press.mp4'),
('Lateral Raises', 'Isolation for medial deltoids', 'Hold dumbbells at sides. Raise arms out to sides until parallel to floor. Lower with control.', 'Beginner', 'Shoulders', 'Medial Deltoids, Anterior Deltoids', 'Dumbbells', '/images/lateral_raises.jpg', '/videos/lateral_raises.mp4'),
('Face Pulls', 'Rear deltoid and upper back exercise', 'Pull rope to face level, elbows high. Squeeze shoulder blades and posterior deltoids. Great for posture.', 'Beginner', 'Shoulders', 'Posterior Deltoids, Rhomboids, Middle Trapezius', 'Cable Machine, Rope', '/images/face_pulls.jpg', '/videos/face_pulls.mp4'),
('Arnold Press', 'Advanced shoulder exercise with rotation', 'Start with dumbbells at shoulder height, palms facing you. Press up while rotating palms away.', 'Advanced', 'Shoulders', 'Anterior Deltoids, Medial Deltoids, Posterior Deltoids, Triceps', 'Dumbbells', '/images/arnold_press.jpg', '/videos/arnold_press.mp4'),
('Shrugs', 'Trapezius isolation exercise', 'Hold weight at sides or in front. Shrug shoulders straight up, hold briefly, lower slowly.', 'Beginner', 'Shoulders', 'Upper Trapezius, Levator Scapulae', 'Dumbbells or Barbell', '/images/shrugs.jpg', '/videos/shrugs.mp4'),

-- ARM EXERCISES
('Bicep Curls', 'Classic bicep isolation exercise', 'Hold dumbbells at sides. Curl weights up by flexing biceps. Lower slowly, maintain tension.', 'Beginner', 'Arms', 'Biceps Brachii, Brachialis, Brachioradialis', 'Dumbbells', '/images/bicep_curls.jpg', '/videos/bicep_curls.mp4'),
('Tricep Dips', 'Bodyweight tricep exercise', 'Sit on edge of bench, hands beside hips. Lower body by bending elbows, push back up.', 'Beginner', 'Arms', 'Triceps Brachii, Anterior Deltoids', 'Bench', '/images/tricep_dips.jpg', '/videos/tricep_dips.mp4'),
('Hammer Curls', 'Neutral grip bicep exercise', 'Hold dumbbells with neutral grip. Curl up while maintaining neutral wrist position.', 'Beginner', 'Arms', 'Brachialis, Brachioradialis, Biceps Brachii', 'Dumbbells', '/images/hammer_curls.jpg', '/videos/hammer_curls.mp4'),
('Tricep Extensions', 'Isolation exercise for triceps', 'Hold dumbbell overhead with both hands. Lower behind head by bending elbows, extend back up.', 'Intermediate', 'Arms', 'Triceps Brachii', 'Dumbbell', '/images/tricep_extensions.jpg', '/videos/tricep_extensions.mp4'),
('Preacher Curls', 'Strict bicep curl variation', 'Sit at preacher bench. Curl weight up with strict form, lower slowly for maximum bicep activation.', 'Intermediate', 'Arms', 'Biceps Brachii, Brachialis', 'Preacher Bench, Barbell or Dumbbells', '/images/preacher_curls.jpg', '/videos/preacher_curls.mp4'),

-- LEG EXERCISES
('Squats', 'King of leg exercises', 'Stand with feet shoulder-width apart. Lower as if sitting back into chair. Drive through heels to stand.', 'Intermediate', 'Legs', 'Quadriceps, Glutes, Hamstrings, Calves', 'Barbell', '/images/squats.jpg', '/videos/squats.mp4'),
('Lunges', 'Unilateral leg strengthening exercise', 'Step forward into lunge position. Lower back knee toward ground, push back to starting position.', 'Beginner', 'Legs', 'Quadriceps, Glutes, Hamstrings, Calves', 'Dumbbells (optional)', '/images/lunges.jpg', '/videos/lunges.mp4'),
('Romanian Deadlifts', 'Hip-hinge movement targeting posterior chain', 'Hold barbell, hinge at hips keeping knees slightly bent. Lower until feel stretch in hamstrings, return to standing.', 'Intermediate', 'Legs', 'Hamstrings, Glutes, Erector Spinae', 'Barbell', '/images/rdl.jpg', '/videos/rdl.mp4'),
('Leg Press', 'Machine-based quad-dominant exercise', 'Sit in leg press machine. Lower weight by bending knees, press back up through heels.', 'Beginner', 'Legs', 'Quadriceps, Glutes, Hamstrings', 'Leg Press Machine', '/images/leg_press.jpg', '/videos/leg_press.mp4'),
('Calf Raises', 'Isolation exercise for calves', 'Stand on balls of feet. Rise up onto toes as high as possible, lower slowly for stretch.', 'Beginner', 'Legs', 'Gastrocnemius, Soleus', 'None or Dumbbells', '/images/calf_raises.jpg', '/videos/calf_raises.mp4'),

-- CORE EXERCISES
('Planks', 'Isometric core strengthening exercise', 'Hold push-up position with forearms on ground. Keep body straight, engage core muscles.', 'Beginner', 'Core', 'Rectus Abdominis, Transverse Abdominis, Obliques, Erector Spinae', 'None', '/images/planks.jpg', '/videos/planks.mp4'),
('Crunches', 'Basic abdominal exercise', 'Lie on back, knees bent. Lift shoulders off ground by contracting abs. Lower slowly.', 'Beginner', 'Core', 'Rectus Abdominis, Obliques', 'None', '/images/crunches.jpg', '/videos/crunches.mp4'),
('Russian Twists', 'Rotational core exercise', 'Sit with knees bent, lean back slightly. Rotate torso side to side, touching ground beside hips.', 'Intermediate', 'Core', 'Obliques, Rectus Abdominis, Transverse Abdominis', 'Medicine Ball (optional)', '/images/russian_twists.jpg', '/videos/russian_twists.mp4'),
('Mountain Climbers', 'Dynamic core and cardio exercise', 'Start in plank position. Alternate bringing knees to chest in running motion.', 'Intermediate', 'Core', 'Rectus Abdominis, Obliques, Hip Flexors, Shoulders', 'None', '/images/mountain_climbers.jpg', '/videos/mountain_climbers.mp4'),

-- CARDIO EXERCISES
('Running', 'Cardiovascular endurance exercise', 'Maintain steady pace for prescribed duration. Focus on breathing and form.', 'Beginner', 'Cardio', 'Heart, Lungs, Legs, Core', 'None or Treadmill', '/images/running.jpg', '/videos/running.mp4'),
('Cycling', 'Low-impact cardiovascular exercise', 'Maintain steady cadence and resistance. Great for active recovery or high-intensity intervals.', 'Beginner', 'Cardio', 'Heart, Lungs, Quadriceps, Glutes, Calves', 'Bike or Stationary Bike', '/images/cycling.jpg', '/videos/cycling.mp4'),
('Jump Rope', 'High-intensity cardiovascular exercise', 'Jump over rope with feet together or alternating. Great for coordination and cardio fitness.', 'Intermediate', 'Cardio', 'Heart, Lungs, Calves, Shoulders, Core', 'Jump Rope', '/images/jump_rope.jpg', '/videos/jump_rope.mp4'),
('Burpees', 'Full-body high-intensity exercise', 'Squat down, jump back to plank, do push-up, jump feet to hands, jump up with arms overhead.', 'Advanced', 'Cardio', 'Heart, Lungs, Full Body', 'None', '/images/burpees.jpg', '/videos/burpees.mp4'),

-- FULL BODY EXERCISES
('Thrusters', 'Squat to overhead press combination', 'Hold dumbbells at shoulders. Squat down, drive up explosively while pressing weights overhead.', 'Advanced', 'Full Body', 'Legs, Shoulders, Core, Arms', 'Dumbbells', '/images/thrusters.jpg', '/videos/thrusters.mp4'),
('Bear Crawl', 'Primal movement pattern', 'Crawl forward on hands and feet, keeping knees just off ground. Engage core throughout.', 'Intermediate', 'Full Body', 'Core, Shoulders, Legs, Arms', 'None', '/images/bear_crawl.jpg', '/videos/bear_crawl.mp4');

-- ==================================================
-- TRAINING PLANS
-- ==================================================

INSERT INTO training_plans (title, description, difficulty_level, duration_weeks, days_per_week, primary_focus, secondary_focus, target_gender, min_age, max_age, equipment_needed, created_by, is_custom, is_active) VALUES
('Beginner Full Body Transformation', 'Perfect starting program for gym newcomers focusing on building strength, learning proper form, and establishing consistent exercise habits.', 'Beginner', 12, 3, 'General Fitness', 'Strength', 'Any', 16, 65, 'Dumbbells, Bench', NULL, FALSE, TRUE),
('Upper/Lower Split - Muscle Building', 'Intermediate program alternating between upper and lower body workouts. Designed for muscle growth and strength development.', 'Intermediate', 8, 4, 'Muscle Gain', 'Strength', 'Any', 18, 45, 'Full Gym Equipment', NULL, FALSE, TRUE),
('Fat Loss Accelerator', 'High-intensity program combining strength training and cardio for maximum fat burning and body composition improvement.', 'Intermediate', 10, 4, 'Weight Loss', 'Endurance', 'Any', 18, 55, 'Minimal Equipment', NULL, FALSE, TRUE),
('Senior Fitness & Mobility', 'Gentle but effective program designed for older adults focusing on maintaining strength, balance, and flexibility.', 'Beginner', 8, 3, 'General Fitness', 'Flexibility', 'Any', 55, 85, 'Light Weights, Chair', NULL, FALSE, TRUE),
('Home Workout Essentials', 'No equipment needed! Perfect for training at home with bodyweight exercises and minimal space requirements.', 'Beginner', 6, 4, 'General Fitness', 'Endurance', 'Any', 14, 65, 'None', NULL, FALSE, TRUE);

-- ==================================================
-- TRAINING PLAN DAYS
-- ==================================================

INSERT INTO training_plan_days (plan_id, day_number, name, focus, description, duration_minutes, calories_burn_estimate) VALUES
-- Plan 1: Beginner Full Body (3 days) - day_id 1-3
(1, 1, 'Full Body A', 'Full body strength and movement patterns', 'Introduction to basic movements with focus on proper form', 45, 300),
(1, 2, 'Full Body B', 'Full body with different exercise variations', 'Building strength with alternative exercises', 40, 280),
(1, 3, 'Full Body C', 'Full body with emphasis on core and stability', 'Core strength and stability focus', 35, 250),

-- Plan 2: Upper/Lower Split (4 days) - day_id 4-7
(2, 1, 'Upper Body Power', 'Chest, shoulders, arms, and back', 'Heavy upper body strength training', 75, 450),
(2, 2, 'Lower Body Strength', 'Legs and glutes with heavy compounds', 'Compound leg movements for strength', 70, 420),
(2, 3, 'Upper Body Volume', 'Higher volume upper body training', 'Volume focused upper body training', 65, 380),
(2, 4, 'Lower Body Volume', 'Higher volume lower body training', 'High volume leg training', 60, 360),

-- Plan 3: Fat Loss Accelerator (4 days) - day_id 8-11
(3, 1, 'Upper Body Circuit', 'Upper body with minimal rest', 'Circuit training for fat loss', 40, 400),
(3, 2, 'HIIT Cardio', 'High-intensity cardiovascular training', 'High intensity interval training', 35, 420),
(3, 3, 'Lower Body Circuit', 'Lower body with minimal rest', 'Lower body circuit training', 45, 380),
(3, 4, 'Full Body Finisher', 'Full body metabolic conditioning', 'Metabolic conditioning workout', 30, 350),

-- Plan 4: Senior Fitness (3 days) - day_id 12-14
(4, 1, 'Strength & Balance', 'Safe strength training with balance work', 'Strength and balance for seniors', 35, 150),
(4, 2, 'Flexibility & Mobility', 'Joint mobility and stretching', 'Mobility and flexibility work', 30, 120),
(4, 3, 'Functional Movement', 'Daily living movement patterns', 'Functional movements for daily life', 40, 180),

-- Plan 5: Home Workout (4 days) - day_id 15-18
(5, 1, 'Upper Body Focus', 'Bodyweight upper body exercises', 'Upper body bodyweight training', 40, 280),
(5, 2, 'Lower Body Focus', 'Bodyweight lower body exercises', 'Lower body bodyweight training', 45, 320),
(5, 3, 'Core & Cardio', 'Core strengthening and cardio', 'Core and cardiovascular training', 35, 300),
(5, 4, 'Full Body Integration', 'Combined movement patterns', 'Full body integration workout', 50, 380);

-- ==================================================
-- TRAINING DAY EXERCISES
-- ==================================================

INSERT INTO training_day_exercises (day_id, exercise_id, `order`, sets, reps, rest_seconds, duration_seconds, notes) VALUES

-- ===== PLAN 1: BEGINNER FULL BODY =====
-- Day 1: Full Body A (day_id = 1)
(1, 1, 1, 3, '8-12', 90, NULL, 'Start with knee push-ups if needed'),
(1, 21, 2, 3, '8-10', 90, NULL, 'Focus on form over weight'),
(1, 16, 3, 3, '10-12', 90, NULL, 'Control the weight throughout'),
(1, 22, 4, 3, '12-15', 90, NULL, 'Step forward into lunge'),
(1, 26, 5, 3, '30 seconds', 90, 30, 'Hold plank position steady'),
(1, 30, 6, 2, '15 minutes', 60, 900, 'Moderate pace'),

-- Day 2: Full Body B (day_id = 2)
(2, 7, 1, 3, '6-8', 120, NULL, 'Full range of motion'),
(2, 11, 2, 3, '10-12', 90, NULL, 'Pull to chest level'),
(2, 16, 3, 3, '10-12', 90, NULL, 'Keep elbows close to body'),
(2, 25, 4, 3, '12-15', 90, NULL, 'Full range of motion'),
(2, 28, 5, 3, '20 reps', 60, NULL, 'Touch ground each side'),
(2, 31, 6, 2, '10 minutes', 60, 600, 'Steady rhythm'),

-- Day 3: Full Body C (day_id = 3)
(3, 6, 1, 3, '5-8', 120, NULL, 'Use assistance if needed'),
(3, 21, 2, 3, '10-12', 90, NULL, 'Drive through heels'),
(3, 16, 3, 3, '8-10', 90, NULL, 'Full range of motion'),
(3, 25, 4, 3, '15 reps', 60, NULL, 'Controlled movement'),
(3, 29, 5, 3, '15 reps', 60, NULL, 'Keep core engaged'),
(3, 27, 6, 3, '12-15', 60, NULL, 'Lift shoulders off ground'),

-- ===== PLAN 2: UPPER/LOWER SPLIT =====
-- Day 4: Upper Body Power (day_id = 4)
(4, 2, 1, 5, '3-5', 180, NULL, 'Heavy weight, explosive concentric'),
(4, 5, 2, 4, '6-8', 150, NULL, 'Lean forward for chest focus'),
(4, 11, 3, 4, '6-8', 120, NULL, 'Strict overhead press'),
(4, 7, 4, 4, '6-8', 120, NULL, 'Focus on squeezing back'),
(4, 16, 5, 3, '8-10', 90, NULL, 'Control the weight'),

-- Day 5: Lower Body Strength (day_id = 5)
(5, 21, 1, 5, '3-5', 180, NULL, 'Heavy back squats'),
(5, 23, 2, 4, '5-6', 180, NULL, 'Romanian deadlifts'),
(5, 22, 3, 4, '8-10', 120, NULL, 'Each leg'),
(5, 25, 4, 3, '12-15', 90, NULL, 'Full range of motion'),
(5, 26, 5, 3, '45 seconds', 90, 45, 'Core stability'),

-- Day 6: Upper Body Volume (day_id = 6)
(6, 3, 1, 4, '8-12', 90, NULL, 'Upper chest focus'),
(6, 8, 2, 4, '8-12', 90, NULL, 'Machine-based exercise'),
(6, 12, 3, 4, '10-12', 75, NULL, 'Slow controlled movement'),
(6, 4, 4, 3, '12-15', 75, NULL, 'Feel the stretch'),
(6, 16, 5, 3, '12-15', 60, NULL, 'Slow and controlled'),

-- Day 7: Lower Body Volume (day_id = 7)
(7, 22, 1, 4, '12-15', 90, NULL, 'Each leg alternating'),
(7, 24, 2, 4, '12-15', 90, NULL, 'Controlled tempo'),
(7, 25, 3, 4, '15-20', 60, NULL, 'Full range of motion'),
(7, 30, 4, 3, '20 minutes', 60, 1200, 'Moderate intensity'),
(7, 28, 5, 3, '20 reps', 45, NULL, 'Core rotation'),

-- ===== PLAN 3: FAT LOSS ACCELERATOR =====
-- Day 8: Upper Body Circuit (day_id = 8)
(8, 1, 1, 3, '12-15', 45, NULL, 'Fast tempo, minimal rest'),
(8, 5, 2, 3, '10-12', 45, NULL, 'Circuit style training'),
(8, 12, 3, 3, '12-15', 45, NULL, 'Keep moving between exercises'),
(8, 17, 4, 3, '10-12', 45, NULL, 'Bodyweight tricep dips'),
(8, 29, 5, 3, '30 seconds', 30, 30, 'High intensity cardio burst'),
(8, 26, 6, 2, '30 seconds', 60, 30, 'Core stability hold'),

-- Day 9: HIIT Cardio (day_id = 9)
(9, 30, 1, 6, '2 minutes high intensity', 60, 120, 'Interval training'),
(9, 33, 2, 4, '30 seconds max effort', 90, 30, 'All-out effort'),
(9, 32, 3, 5, '45 seconds', 75, 45, 'Maintain intensity'),
(9, 29, 4, 4, '20 seconds', 40, 20, 'Explosive movement'),
(9, 31, 5, 3, '5 minutes steady', 120, 300, 'Active recovery pace'),

-- Day 10: Lower Body Circuit (day_id = 10)
(10, 21, 1, 4, '15-20', 45, NULL, 'Bodyweight or light weight'),
(10, 22, 2, 4, '12 per leg', 45, NULL, 'Alternate legs quickly'),
(10, 25, 3, 4, '15-20', 45, NULL, 'Single leg focus'),
(10, 33, 4, 3, '10 reps', 45, NULL, 'Full body explosive'),
(10, 28, 5, 3, '25 reps', 30, NULL, 'Core circuit'),
(10, 26, 6, 2, '45 seconds', 60, 45, 'Plank variations'),

-- Day 11: Full Body Finisher (day_id = 11)
(11, 34, 1, 3, '8-10', 60, NULL, 'Squat to press combo'),
(11, 33, 2, 3, '8-12', 60, NULL, 'Full body burpees'),
(11, 29, 3, 3, '30 seconds', 45, 30, 'Mountain climber intervals'),
(11, 21, 4, 3, '15 reps', 45, NULL, 'Bodyweight squats'),
(11, 1, 5, 3, '10-15', 45, NULL, 'Push-up variations'),
(11, 26, 6, 2, '60 seconds', 90, 60, 'Final plank hold'),

-- ===== PLAN 4: SENIOR FITNESS & MOBILITY =====
-- Day 12: Strength & Balance (day_id = 12)
(12, 21, 1, 3, '8-12', 120, NULL, 'Chair squats if needed'),
(12, 16, 2, 3, '8-10', 90, NULL, 'Light weights, seated if needed'),
(12, 25, 3, 3, '10-12', 90, NULL, 'Hold wall for balance'),
(12, 12, 4, 3, '8-10', 90, NULL, 'Very light weights'),
(12, 26, 5, 2, '15-30 seconds', 60, 30, 'Modified plank or wall plank'),
(12, 30, 6, 1, '10-15 minutes', 60, 900, 'Gentle walking pace'),

-- Day 13: Flexibility & Mobility (day_id = 13)
(13, 26, 1, 3, '20 seconds', 90, 20, 'Wall plank or modified'),
(13, 27, 2, 3, '8-10', 60, NULL, 'Gentle crunches or seated'),
(13, 28, 3, 3, '10 reps', 60, NULL, 'Seated or standing'),
(13, 25, 4, 3, '8-10', 90, NULL, 'Wall support for balance'),
(13, 30, 5, 1, '20 minutes', 60, 1200, 'Gentle pace with rest'),

-- Day 14: Functional Movement (day_id = 14)
(14, 21, 1, 3, '6-10', 120, NULL, 'Chair assisted squats'),
(14, 22, 2, 3, '6-8 per leg', 90, NULL, 'Step-ups or modified lunges'),
(14, 16, 3, 3, '6-8', 90, NULL, 'Seated or very light weights'),
(14, 25, 4, 3, '8-10', 90, NULL, 'Wall or chair support'),
(14, 26, 5, 2, '20 seconds', 90, 20, 'Wall plank'),
(14, 31, 6, 1, '10 minutes', 60, 600, 'Gentle stationary bike'),

-- ===== PLAN 5: HOME WORKOUT ESSENTIALS =====
-- Day 15: Upper Body Focus (day_id = 15)
(15, 1, 1, 4, '10-15', 60, NULL, 'Various hand positions'),
(15, 16, 2, 4, '8-10', 60, NULL, 'Use water bottles if no weights'),
(15, 17, 3, 3, '10-12', 60, NULL, 'Chair or bench dips'),
(15, 26, 4, 3, '30 seconds', 60, 30, 'Forearm plank'),
(15, 29, 5, 3, '30 seconds', 45, 30, 'Get heart rate up'),
(15, 27, 6, 3, '15 reps', 45, NULL, 'Floor crunches'),

-- Day 16: Lower Body Focus (day_id = 16)
(16, 21, 1, 4, '15-20', 60, NULL, 'Bodyweight squats'),
(16, 22, 2, 4, '12 per leg', 60, NULL, 'Stationary lunges'),
(16, 25, 3, 4, '15-20', 60, NULL, 'Single leg for difficulty'),
(16, 28, 4, 3, '25 reps', 45, NULL, 'Core rotation'),
(16, 30, 5, 1, '5 minutes', 45, 300, 'March in place if no space'),

-- Day 17: Core & Cardio (day_id = 17)
(17, 26, 1, 4, '45 seconds', 45, 45, 'Various plank positions'),
(17, 27, 2, 4, '20 reps', 45, NULL, 'Basic crunches'),
(17, 28, 3, 4, '30 reps', 45, NULL, 'Seated or standing'),
(17, 29, 4, 4, '45 seconds', 30, 45, 'High intensity'),
(17, 33, 5, 3, '8-10 reps', 60, NULL, 'Modified as needed'),

-- Day 18: Full Body Integration (day_id = 18)
(18, 34, 1, 3, '8-10', 75, NULL, 'Use water bottles as weights'),
(18, 21, 2, 3, '12-15', 60, NULL, 'Bodyweight squats'),
(18, 1, 3, 3, '8-12', 60, NULL, 'Push-up variations'),
(18, 29, 4, 3, '20 seconds', 45, 20, 'Quick cardio burst'),
(18, 26, 5, 3, '30 seconds', 60, 30, 'Core stability'),
(18, 35, 6, 2, '30 seconds', 90, 30, 'Full body movement');

-- ==================================================
-- VERIFICATION QUERIES
-- ==================================================

SELECT 'Exercises inserted:' as status, COUNT(*) as count FROM exercises;
SELECT 'Training plans inserted:' as status, COUNT(*) as count FROM training_plans;
SELECT 'Training plan days inserted:' as status, COUNT(*) as count FROM training_plan_days;
SELECT 'Training day exercises inserted:' as status, COUNT(*) as count FROM training_day_exercises;

-- Show sample plan structure with muscle groups
SELECT 
    tp.title as plan_name,
    tpd.name as day_name,
    e.name as exercise_name,
    e.primary_muscle_group,
    e.secondary_muscle_groups,
    tde.sets,
    tde.reps,
    tde.notes
FROM training_plans tp
JOIN training_plan_days tpd ON tp.plan_id = tpd.plan_id
JOIN training_day_exercises tde ON tpd.day_id = tde.day_id
JOIN exercises e ON tde.exercise_id = e.exercise_id
WHERE tp.plan_id = 1
ORDER BY tpd.day_number, tde.`order`;

-- Verify all plans have training day exercises
SELECT 
    tp.plan_id,
    tp.title,
    COUNT(DISTINCT tpd.day_id) as total_days,
    COUNT(tde.day_id) as exercises_count
FROM training_plans tp
LEFT JOIN training_plan_days tpd ON tp.plan_id = tpd.plan_id
LEFT JOIN training_day_exercises tde ON tpd.day_id = tde.day_id
GROUP BY tp.plan_id, tp.title
ORDER BY tp.plan_id;
