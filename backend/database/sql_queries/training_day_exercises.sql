-- NAME: get_by_id
SELECT id, day_id, exercise_id, `order`, sets, reps, rest_seconds, duration_seconds, notes
FROM training_day_exercises
WHERE id = %s;

-- NAME: get_by_day_id
SELECT tde.id, tde.day_id, tde.exercise_id, tde.`order`, tde.sets, tde.reps, tde.rest_seconds, tde.duration_seconds, tde.notes, ex.name as exercise_name
FROM training_day_exercises tde
JOIN exercises ex ON tde.exercise_id = ex.exercise_id
WHERE tde.day_id = %s
ORDER BY tde.`order`;

-- NAME: create
INSERT INTO training_day_exercises (day_id, exercise_id, `order`, sets, reps, rest_seconds, duration_seconds, notes)
VALUES (%(day_id)s, %(exercise_id)s, %(order)s, %(sets)s, %(reps)s, %(rest_seconds)s, %(duration_seconds)s, %(notes)s);

-- NAME: update_by_id
UPDATE training_day_exercises
SET {set_clauses} -- Placeholder
WHERE id = %(id)s;

-- NAME: delete_by_id
DELETE FROM training_day_exercises WHERE id = %s;

-- NAME: delete_by_day_id
DELETE FROM training_day_exercises WHERE day_id = %s;