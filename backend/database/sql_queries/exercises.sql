-- NAME: get_by_id
SELECT exercise_id, name, description, instructions, difficulty_level, primary_muscle_group, secondary_muscle_groups, equipment_needed, image_url, video_url, is_active, created_at, updated_at
FROM exercises
WHERE exercise_id = %s;

-- NAME: get_all
SELECT exercise_id, name, description, instructions, difficulty_level, primary_muscle_group, secondary_muscle_groups, equipment_needed, image_url, video_url, is_active, created_at, updated_at
FROM exercises
ORDER BY name;

-- NAME: get_all_by_active_status
SELECT exercise_id, name, description, instructions, difficulty_level, primary_muscle_group, secondary_muscle_groups, equipment_needed, image_url, video_url, is_active, created_at, updated_at
FROM exercises
WHERE is_active = %s
ORDER BY name;

-- NAME: create
INSERT INTO exercises (name, description, instructions, difficulty_level, primary_muscle_group, secondary_muscle_groups, equipment_needed, image_url, video_url, is_active)
VALUES (%(name)s, %(description)s, %(instructions)s, %(difficulty_level)s, %(primary_muscle_group)s, %(secondary_muscle_groups)s, %(equipment_needed)s, %(image_url)s, %(video_url)s, %(is_active)s);

-- NAME: update_by_id
UPDATE exercises
SET {set_clauses} -- Placeholder for dynamic SET clauses
WHERE exercise_id = %(exercise_id)s;

-- NAME: delete_by_id
DELETE FROM exercises WHERE exercise_id = %s;