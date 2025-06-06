-- NAME: get_by_id
SELECT hall_id, name, description, max_capacity, location, equipment_available, is_active, created_at, updated_at
FROM halls
WHERE hall_id = %s;

-- NAME: get_all
SELECT hall_id, name, description, max_capacity, location, equipment_available, is_active, created_at, updated_at
FROM halls
ORDER BY name;

-- NAME: get_all_active
SELECT hall_id, name, description, max_capacity, location, equipment_available, is_active, created_at, updated_at
FROM halls
WHERE is_active = TRUE
ORDER BY name;

-- NAME: create
INSERT INTO halls (name, description, max_capacity, location, equipment_available, is_active)
VALUES (%(name)s, %(description)s, %(max_capacity)s, %(location)s, %(equipment_available)s, %(is_active)s);

-- NAME: update_by_id
UPDATE halls
SET {set_clauses} -- Placeholder
WHERE hall_id = %(hall_id)s;

-- NAME: delete_by_id
DELETE FROM halls WHERE hall_id = %s;