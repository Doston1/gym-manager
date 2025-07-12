-- NAME: get_by_id
SELECT goal_id, member_id, week_start_date, desired_sessions, priority_level, notes, created_at, updated_at
FROM weekly_training_goals
WHERE goal_id = %s;

-- NAME: get_by_member_and_week
SELECT goal_id, member_id, week_start_date, desired_sessions, priority_level, notes, created_at, updated_at
FROM weekly_training_goals
WHERE member_id = %(member_id)s AND week_start_date = %(week_start_date)s;

-- NAME: get_by_member_id
SELECT goal_id, member_id, week_start_date, desired_sessions, priority_level, notes, created_at, updated_at
FROM weekly_training_goals
WHERE member_id = %s
ORDER BY week_start_date DESC;

-- NAME: get_by_week
SELECT goal_id, member_id, week_start_date, desired_sessions, priority_level, notes, created_at, updated_at
FROM weekly_training_goals
WHERE week_start_date = %s
ORDER BY member_id;

-- NAME: create
INSERT INTO weekly_training_goals (member_id, week_start_date, desired_sessions, priority_level, notes)
VALUES (%(member_id)s, %(week_start_date)s, %(desired_sessions)s, %(priority_level)s, %(notes)s);

-- NAME: update_by_id
UPDATE weekly_training_goals
SET {set_clauses} -- Placeholder
WHERE goal_id = %(goal_id)s;

-- NAME: delete_by_id
DELETE FROM weekly_training_goals WHERE goal_id = %s;

-- NAME: delete_by_member_and_week
DELETE FROM weekly_training_goals
WHERE member_id = %(member_id)s AND week_start_date = %(week_start_date)s;

-- NAME: upsert_by_member_and_week
INSERT INTO weekly_training_goals (member_id, week_start_date, desired_sessions, priority_level, notes)
VALUES (%(member_id)s, %(week_start_date)s, %(desired_sessions)s, %(priority_level)s, %(notes)s)
ON DUPLICATE KEY UPDATE
    desired_sessions = VALUES(desired_sessions),
    priority_level = VALUES(priority_level),
    notes = VALUES(notes),
    updated_at = CURRENT_TIMESTAMP;

-- NAME: check_for_week
SELECT 1 FROM weekly_training_goals WHERE week_start_date = %s LIMIT 1;
