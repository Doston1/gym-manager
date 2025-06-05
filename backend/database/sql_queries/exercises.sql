-- NAME: exercises_get_by_id
SELECT * FROM exercises WHERE exercise_id = %s;

-- NAME: exercises_get_all
SELECT * FROM exercises ORDER BY name;

-- NAME: exercises_get_by_muscle_group
SELECT * FROM exercises WHERE target_muscles LIKE CONCAT('%', %s, '%') ORDER BY name;

-- NAME: exercises_get_by_equipment
SELECT * FROM exercises WHERE equipment_needed LIKE CONCAT('%', %s, '%') ORDER BY name;

-- NAME: exercises_get_by_difficulty
SELECT * FROM exercises WHERE difficulty_level = %s ORDER BY name;

-- NAME: exercises_create
INSERT INTO exercises (
    name, 
    description, 
    target_muscles, 
    equipment_needed, 
    difficulty_level, 
    video_url, 
    created_by
) VALUES (
    %(name)s, 
    %(description)s, 
    %(target_muscles)s, 
    %(equipment_needed)s, 
    %(difficulty_level)s, 
    %(video_url)s,
    %(created_by)s
);

-- NAME: exercises_update_by_id
UPDATE exercises SET 
    name = %(name)s, 
    description = %(description)s, 
    target_muscles = %(target_muscles)s, 
    equipment_needed = %(equipment_needed)s, 
    difficulty_level = %(difficulty_level)s, 
    video_url = %(video_url)s,
    updated_at = NOW()
WHERE exercise_id = %(exercise_id)s;

-- NAME: exercises_delete_by_id
DELETE FROM exercises WHERE exercise_id = %s;
