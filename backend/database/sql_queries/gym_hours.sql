-- NAME: get_by_id
SELECT hours_id, day_of_week, opening_time, closing_time, is_closed, special_note, is_holiday
FROM gym_hours
WHERE hours_id = %s;

-- NAME: get_by_day_of_week
SELECT hours_id, day_of_week, opening_time, closing_time, is_closed, special_note, is_holiday
FROM gym_hours
WHERE day_of_week = %s;

-- NAME: get_all
SELECT hours_id, day_of_week, opening_time, closing_time, is_closed, special_note, is_holiday
FROM gym_hours
ORDER BY FIELD(day_of_week, 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday');

-- NAME: create
INSERT INTO gym_hours (day_of_week, opening_time, closing_time, is_closed, special_note, is_holiday)
VALUES (%(day_of_week)s, %(opening_time)s, %(closing_time)s, %(is_closed)s, %(special_note)s, %(is_holiday)s);

-- NAME: update_by_day_of_week -- More common to update by day than by ID for this table
UPDATE gym_hours
SET opening_time = %(opening_time)s, 
    closing_time = %(closing_time)s, 
    is_closed = %(is_closed)s, 
    special_note = %(special_note)s,
    is_holiday = %(is_holiday)s
WHERE day_of_week = %(day_of_week)s;

-- NAME: update_by_id
UPDATE gym_hours
SET {set_clauses} -- Placeholder
WHERE hours_id = %(hours_id)s;

-- NAME: delete_by_id -- Deleting a gym hour record might be rare; usually updated.
DELETE FROM gym_hours WHERE hours_id = %s;

-- NAME: delete_by_day_of_week
DELETE FROM gym_hours WHERE day_of_week = %s;