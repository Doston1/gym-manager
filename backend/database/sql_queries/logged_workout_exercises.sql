-- NAME: get_by_id
SELECT log_exercise_id, logged_workout_id, exercise_id, training_day_exercise_id, `order_in_workout`,
       sets_prescribed, reps_prescribed, weight_prescribed, rest_prescribed_seconds, duration_prescribed_seconds,
       sets_completed, reps_actual_per_set, weight_actual_per_set, rest_actual_seconds_per_set, duration_actual_seconds,
       notes_exercise_specific, completed_at
FROM logged_workout_exercises
WHERE log_exercise_id = %s;

-- NAME: get_by_logged_workout_id
SELECT lwe.log_exercise_id, lwe.logged_workout_id, lwe.exercise_id, ex.name as exercise_name, 
       lwe.training_day_exercise_id, lwe.`order_in_workout`,
       lwe.sets_prescribed, lwe.reps_prescribed, lwe.weight_prescribed, lwe.rest_prescribed_seconds, lwe.duration_prescribed_seconds,
       lwe.sets_completed, lwe.reps_actual_per_set, lwe.weight_actual_per_set, lwe.rest_actual_seconds_per_set, lwe.duration_actual_seconds,
       lwe.notes_exercise_specific, lwe.completed_at
FROM logged_workout_exercises lwe
JOIN exercises ex ON lwe.exercise_id = ex.exercise_id
WHERE lwe.logged_workout_id = %s
ORDER BY lwe.`order_in_workout`;

-- NAME: create_batch -- For inserting multiple exercises for a workout
-- This is a template; actual execution will loop through items in Python
-- INSERT INTO logged_workout_exercises (logged_workout_id, exercise_id, training_day_exercise_id, `order_in_workout`, sets_prescribed, reps_prescribed, weight_prescribed, rest_prescribed_seconds, duration_prescribed_seconds, sets_completed, reps_actual_per_set, weight_actual_per_set, rest_actual_seconds_per_set, duration_actual_seconds, notes_exercise_specific, completed_at) VALUES (...);

-- NAME: create_single
INSERT INTO logged_workout_exercises (
    logged_workout_id, exercise_id, training_day_exercise_id, `order_in_workout`,
    sets_prescribed, reps_prescribed, weight_prescribed, rest_prescribed_seconds, duration_prescribed_seconds,
    sets_completed, reps_actual_per_set, weight_actual_per_set, rest_actual_seconds_per_set, duration_actual_seconds,
    notes_exercise_specific, completed_at
) VALUES (
    %(logged_workout_id)s, %(exercise_id)s, %(training_day_exercise_id)s, %(order_in_workout)s,
    %(sets_prescribed)s, %(reps_prescribed)s, %(weight_prescribed)s, %(rest_prescribed_seconds)s, %(duration_prescribed_seconds)s,
    %(sets_completed)s, %(reps_actual_per_set)s, %(weight_actual_per_set)s, %(rest_actual_seconds_per_set)s, %(duration_actual_seconds)s,
    %(notes_exercise_specific)s, %(completed_at)s
);


-- NAME: update_by_id
UPDATE logged_workout_exercises
SET {set_clauses} -- Placeholder
WHERE log_exercise_id = %(log_exercise_id)s;

-- NAME: delete_by_id
DELETE FROM logged_workout_exercises WHERE log_exercise_id = %s;

-- NAME: delete_by_logged_workout_id
DELETE FROM logged_workout_exercises WHERE logged_workout_id = %s;