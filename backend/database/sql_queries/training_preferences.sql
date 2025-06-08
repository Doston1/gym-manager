-- NAME: get_by_id
SELECT preference_id, member_id, week_start_date, day_of_week, start_time, end_time, preference_type, trainer_id, created_at
FROM training_preferences
WHERE preference_id = %s;

-- NAME: get_by_member_and_week
SELECT preference_id, member_id, week_start_date, day_of_week, start_time, end_time, preference_type, trainer_id, created_at
FROM training_preferences
WHERE member_id = %(member_id)s AND week_start_date = %(week_start_date)s
ORDER BY day_of_week, start_time;

-- NAME: get_by_member_id
SELECT preference_id, member_id, week_start_date, day_of_week, start_time, end_time, preference_type, trainer_id, created_at
FROM training_preferences
WHERE member_id = %s
ORDER BY week_start_date, day_of_week, start_time;

-- NAME: create
INSERT INTO training_preferences (member_id, week_start_date, day_of_week, start_time, end_time, preference_type, trainer_id)
VALUES (%(member_id)s, %(week_start_date)s, %(day_of_week)s, %(start_time)s, %(end_time)s, %(preference_type)s, %(trainer_id)s);

-- NAME: update_by_id
UPDATE training_preferences
SET {set_clauses} -- Placeholder
WHERE preference_id = %(preference_id)s;

-- NAME: delete_by_id
DELETE FROM training_preferences WHERE preference_id = %s;

-- NAME: delete_by_member_and_week
DELETE FROM training_preferences
WHERE member_id = %(member_id)s AND week_start_date = %(week_start_date)s;


-- NAME: check_for_week
SELECT 1 FROM training_preferences WHERE week_start_date = %s LIMIT 1;