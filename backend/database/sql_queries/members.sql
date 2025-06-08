-- NAME: get_by_user_id_pk
SELECT member_id, user_id, weight, height, fitness_goal, fitness_level, health_conditions
FROM members
WHERE user_id = %s;

-- NAME: get_by_member_id_pk
SELECT member_id, user_id, weight, height, fitness_goal, fitness_level, health_conditions
FROM members
WHERE member_id = %s;

-- NAME: create
INSERT INTO members (user_id, weight, height, fitness_goal, fitness_level, health_conditions)
VALUES (%(user_id)s, %(weight)s, %(height)s, %(fitness_goal)s, %(fitness_level)s, %(health_conditions)s);

-- NAME: update_by_user_id_pk
UPDATE members
SET {set_clauses} -- Placeholder for dynamic SET clauses
WHERE user_id = %(user_id)s;

-- NAME: update_by_member_id_pk
UPDATE members
SET {set_clauses} -- Placeholder for dynamic SET clauses
WHERE member_id = %(member_id)s;

-- Note: Delete for members is typically handled by ON DELETE CASCADE from the users table.
-- If direct deletion is needed:
-- NAME: delete_by_member_id_pk
-- DELETE FROM members WHERE member_id = %s;