-- NAME: training_day_exercises_get_by_id
SELECT * FROM training_day_exercises WHERE day_exercise_id = %s;

-- NAME: training_day_exercises_get_by_day_id
SELECT tde.*, e.name as exercise_name, e.target_muscles, e.equipment_needed, e.difficulty_level, e.video_url
FROM training_day_exercises tde
JOIN exercises e ON tde.exercise_id = e.exercise_id
WHERE tde.day_id = %s
ORDER BY tde.order_in_day;

-- NAME: training_day_exercises_create
INSERT INTO training_day_exercises (
    day_id, 
    exercise_id, 
    sets, 
    reps, 
    rest_seconds, 
    order_in_day, 
    notes
) VALUES (
    %(day_id)s, 
    %(exercise_id)s, 
    %(sets)s, 
    %(reps)s, 
    %(rest_seconds)s, 
    %(order_in_day)s, 
    %(notes)s
);

-- NAME: training_day_exercises_update_by_id
UPDATE training_day_exercises SET 
    exercise_id = %(exercise_id)s, 
    sets = %(sets)s, 
    reps = %(reps)s, 
    rest_seconds = %(rest_seconds)s, 
    order_in_day = %(order_in_day)s, 
    notes = %(notes)s,
    updated_at = NOW()
WHERE day_exercise_id = %(day_exercise_id)s;

-- NAME: training_day_exercises_delete_by_id
DELETE FROM training_day_exercises WHERE day_exercise_id = %s;

-- NAME: training_day_exercises_delete_by_day_id
DELETE FROM training_day_exercises WHERE day_id = %s;

-- NAME: training_day_exercises_get_max_order
SELECT COALESCE(MAX(order_in_day), 0) as max_order FROM training_day_exercises WHERE day_id = %s;
