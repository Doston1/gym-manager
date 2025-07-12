-- NAME: get_by_id
SELECT plan_id, title, description, difficulty_level, duration_weeks, days_per_week, primary_focus, secondary_focus, target_gender, min_age, max_age, equipment_needed, created_by, is_custom, is_active, created_at, updated_at
FROM training_plans
WHERE plan_id = %s;

-- NAME: get_detailed_by_id
SELECT 
    tp.plan_id, tp.title, tp.description, tp.difficulty_level, tp.duration_weeks, tp.days_per_week, 
    tp.primary_focus, tp.secondary_focus, tp.target_gender, tp.min_age, tp.max_age, tp.equipment_needed, 
    tp.created_by, tp.is_custom, tp.is_active, tp.created_at, tp.updated_at,
    tpd.day_id, tpd.day_number, tpd.name as day_name, tpd.focus as day_focus, 
    tpd.description as day_description, tpd.duration_minutes, tpd.calories_burn_estimate,
    tde.id as exercise_link_id, tde.exercise_id, tde.`order` as exercise_order, 
    tde.sets, tde.reps, tde.rest_seconds, tde.duration_seconds, tde.notes as exercise_notes,
    ex.name as exercise_name, ex.description as exercise_description, ex.instructions as exercise_instructions,
    ex.difficulty_level as exercise_difficulty, ex.primary_muscle_group, ex.secondary_muscle_groups,
    ex.equipment_needed as exercise_equipment, ex.image_url, ex.video_url
FROM training_plans tp
LEFT JOIN training_plan_days tpd ON tp.plan_id = tpd.plan_id
LEFT JOIN training_day_exercises tde ON tpd.day_id = tde.day_id
LEFT JOIN exercises ex ON tde.exercise_id = ex.exercise_id
WHERE tp.plan_id = %s
ORDER BY tpd.day_number, tde.`order`;

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