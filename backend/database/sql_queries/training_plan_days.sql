-- NAME: training_plan_days_get_by_id
SELECT * FROM training_plan_days WHERE day_id = %s;

-- NAME: training_plan_days_get_by_plan_id
SELECT * FROM training_plan_days WHERE plan_id = %s ORDER BY day_number;

-- NAME: training_plan_days_create
INSERT INTO training_plan_days (
    plan_id, 
    day_number, 
    name, 
    description, 
    target_muscles, 
    duration_minutes, 
    difficulty_level
) VALUES (
    %(plan_id)s, 
    %(day_number)s, 
    %(name)s, 
    %(description)s, 
    %(target_muscles)s, 
    %(duration_minutes)s, 
    %(difficulty_level)s
);

-- NAME: training_plan_days_update_by_id
UPDATE training_plan_days SET 
    day_number = %(day_number)s,
    name = %(name)s, 
    description = %(description)s, 
    target_muscles = %(target_muscles)s, 
    duration_minutes = %(duration_minutes)s, 
    difficulty_level = %(difficulty_level)s,
    updated_at = NOW()
WHERE day_id = %(day_id)s;

-- NAME: training_plan_days_delete_by_id
DELETE FROM training_plan_days WHERE day_id = %s;

-- NAME: training_plan_days_delete_by_plan_id
DELETE FROM training_plan_days WHERE plan_id = %s;
