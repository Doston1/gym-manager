-- NAME: get_by_id
SELECT plan_id, title, description, difficulty_level, duration_weeks, days_per_week, primary_focus, secondary_focus, target_gender, min_age, max_age, equipment_needed, created_by, is_custom, is_active, created_at, updated_at
FROM training_plans
WHERE plan_id = %s;

-- NAME: get_all
SELECT plan_id, title, description, difficulty_level, duration_weeks, days_per_week, primary_focus, secondary_focus, target_gender, min_age, max_age, equipment_needed, created_by, is_custom, is_active, created_at, updated_at
FROM training_plans
ORDER BY title;

-- NAME: get_all_by_active_status
SELECT plan_id, title, description, difficulty_level, duration_weeks, days_per_week, primary_focus, secondary_focus, target_gender, min_age, max_age, equipment_needed, created_by, is_custom, is_active, created_at, updated_at
FROM training_plans
WHERE is_active = %s
ORDER BY title;

-- NAME: get_by_trainer_id
SELECT plan_id, title, description, difficulty_level, duration_weeks, days_per_week, primary_focus, secondary_focus, target_gender, min_age, max_age, equipment_needed, created_by, is_custom, is_active, created_at, updated_at
FROM training_plans
WHERE created_by = %s
ORDER BY title;

-- NAME: create
INSERT INTO training_plans (title, description, difficulty_level, duration_weeks, days_per_week, primary_focus, secondary_focus, target_gender, min_age, max_age, equipment_needed, created_by, is_custom, is_active)
VALUES (%(title)s, %(description)s, %(difficulty_level)s, %(duration_weeks)s, %(days_per_week)s, %(primary_focus)s, %(secondary_focus)s, %(target_gender)s, %(min_age)s, %(max_age)s, %(equipment_needed)s, %(created_by)s, %(is_custom)s, %(is_active)s);

-- NAME: update_by_id
UPDATE training_plans
SET {set_clauses} -- Placeholder
WHERE plan_id = %(plan_id)s;

-- NAME: delete_by_id
DELETE FROM training_plans WHERE plan_id = %s;