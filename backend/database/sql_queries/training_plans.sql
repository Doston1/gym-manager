-- NAME: training_plans_get_by_id
SELECT * FROM training_plans WHERE plan_id = %s;

-- NAME: training_plans_get_all
SELECT * FROM training_plans ORDER BY name;

-- NAME: training_plans_get_by_focus
SELECT * FROM training_plans WHERE focus = %s ORDER BY name;

-- NAME: training_plans_get_by_trainer
SELECT * 
FROM training_plans 
WHERE created_by = %s 
ORDER BY created_at DESC;

-- NAME: training_plans_create
INSERT INTO training_plans (
    name, 
    description, 
    focus, 
    difficulty_level, 
    duration_weeks, 
    created_by, 
    is_public
) VALUES (
    %(name)s, 
    %(description)s, 
    %(focus)s, 
    %(difficulty_level)s, 
    %(duration_weeks)s, 
    %(created_by)s, 
    %(is_public)s
);

-- NAME: training_plans_update_by_id
UPDATE training_plans SET 
    name = %(name)s, 
    description = %(description)s, 
    focus = %(focus)s, 
    difficulty_level = %(difficulty_level)s, 
    duration_weeks = %(duration_weeks)s, 
    is_public = %(is_public)s,
    updated_at = NOW()
WHERE plan_id = %(plan_id)s;

-- NAME: training_plans_delete_by_id
DELETE FROM training_plans WHERE plan_id = %s;

-- NAME: training_plans_get_detailed_by_id
SELECT 
    tp.*,
    CONCAT(u.first_name, ' ', u.last_name) as trainer_name,
    u.profile_image_path as trainer_image,
    (SELECT COUNT(*) FROM training_plan_days WHERE plan_id = tp.plan_id) as day_count,
    (SELECT COUNT(*) FROM member_saved_plans WHERE plan_id = tp.plan_id) as usage_count
FROM 
    training_plans tp
JOIN 
    trainers t ON tp.created_by = t.trainer_id
JOIN 
    users u ON t.user_id = u.user_id
WHERE 
    tp.plan_id = %s;
