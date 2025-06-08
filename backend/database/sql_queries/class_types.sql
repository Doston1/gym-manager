-- NAME: get_by_id
SELECT class_type_id, name, description, duration_minutes, difficulty_level, equipment_needed, default_max_participants, default_price, is_active, created_at, updated_at
FROM class_types
WHERE class_type_id = %s;

-- NAME: get_all
SELECT class_type_id, name, description, duration_minutes, difficulty_level, equipment_needed, default_max_participants, default_price, is_active, created_at, updated_at
FROM class_types
ORDER BY name;

-- NAME: create
INSERT INTO class_types (name, description, duration_minutes, difficulty_level, equipment_needed, default_max_participants, default_price, is_active)
VALUES (%(name)s, %(description)s, %(duration_minutes)s, %(difficulty_level)s, %(equipment_needed)s, %(default_max_participants)s, %(default_price)s, %(is_active)s);

-- NAME: update_by_id
UPDATE class_types
SET {set_clauses} -- Placeholder: name=%(name)s, description=%(description)s, etc.
WHERE class_type_id = %(class_type_id)s;

-- NAME: delete_by_id
DELETE FROM class_types WHERE class_type_id = %s;