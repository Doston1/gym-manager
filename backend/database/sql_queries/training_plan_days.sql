-- NAME: get_by_id
SELECT day_id, plan_id, day_number, name, focus, description, duration_minutes, calories_burn_estimate
FROM training_plan_days
WHERE day_id = %s;

-- NAME: get_by_plan_id
SELECT day_id, plan_id, day_number, name, focus, description, duration_minutes, calories_burn_estimate
FROM training_plan_days
WHERE plan_id = %s
ORDER BY day_number;

-- NAME: create
INSERT INTO training_plan_days (plan_id, day_number, name, focus, description, duration_minutes, calories_burn_estimate)
VALUES (%(plan_id)s, %(day_number)s, %(name)s, %(focus)s, %(description)s, %(duration_minutes)s, %(calories_burn_estimate)s);

-- NAME: update_by_id
UPDATE training_plan_days
SET {set_clauses} -- Placeholder
WHERE day_id = %(day_id)s;

-- NAME: delete_by_id
DELETE FROM training_plan_days WHERE day_id = %s;

-- NAME: delete_by_plan_id
DELETE FROM training_plan_days WHERE plan_id = %s;