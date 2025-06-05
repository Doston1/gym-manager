-- NAME: get_by_user_id_pk
SELECT m.manager_id, m.user_id, m.department, m.hire_date, u.first_name, u.last_name, u.email
FROM managers m
JOIN users u ON m.user_id = u.user_id
WHERE m.user_id = %s;

-- NAME: get_by_manager_id_pk
SELECT m.manager_id, m.user_id, m.department, m.hire_date, u.first_name, u.last_name, u.email
FROM managers m
JOIN users u ON m.user_id = u.user_id
WHERE m.manager_id = %s;

-- NAME: create
INSERT INTO managers (manager_id, user_id, department, hire_date)
VALUES (%(manager_id)s, %(user_id)s, %(department)s, %(hire_date)s);

-- NAME: update_by_manager_id_pk
UPDATE managers
SET {set_clauses} -- Placeholder
WHERE manager_id = %(manager_id)s;

-- Note: Delete for managers is typically handled by ON DELETE CASCADE from the users table.