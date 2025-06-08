-- NAME: get_by_id
SELECT class_id, class_type_id, trainer_id, hall_id, date, start_time, end_time, max_participants, current_participants, price, status, notes, created_at, updated_at
FROM classes
WHERE class_id = %s;

-- NAME: get_all
SELECT class_id, class_type_id, trainer_id, hall_id, date, start_time, end_time, max_participants, current_participants, price, status, notes, created_at, updated_at
FROM classes
ORDER BY date DESC, start_time ASC;

-- NAME: get_detailed_by_id -- New specific query
SELECT 
    c.class_id, c.class_type_id, c.trainer_id, c.hall_id, c.date, c.start_time, c.end_time, 
    c.max_participants, c.current_participants, c.price, c.status, c.notes,
    ct.name AS class_type_name, ct.description AS class_type_description, 
    ct.difficulty_level as class_type_difficulty, ct.duration_minutes as class_type_duration,
    h.name AS hall_name, 
    CONCAT(u.first_name, ' ', u.last_name) AS trainer_name
FROM classes c
LEFT JOIN class_types ct ON c.class_type_id = ct.class_type_id
LEFT JOIN halls h ON c.hall_id = h.hall_id
LEFT JOIN trainers t ON c.trainer_id = t.trainer_id
LEFT JOIN users u ON t.user_id = u.user_id
WHERE c.class_id = %s;

-- NAME: get_all_detailed
SELECT 
    c.class_id, c.class_type_id, c.trainer_id, c.hall_id, c.date, c.start_time, c.end_time, 
    c.max_participants, c.current_participants, c.price, c.status, c.notes,
    ct.name AS class_type_name, 
    h.name AS hall_name, 
    CONCAT(u.first_name, ' ', u.last_name) AS trainer_name
FROM classes c
LEFT JOIN class_types ct ON c.class_type_id = ct.class_type_id
LEFT JOIN halls h ON c.hall_id = h.hall_id
LEFT JOIN trainers t ON c.trainer_id = t.trainer_id
LEFT JOIN users u ON t.user_id = u.user_id
ORDER BY c.date DESC, c.start_time ASC;

-- NAME: create
INSERT INTO classes (class_type_id, trainer_id, hall_id, date, start_time, end_time, max_participants, current_participants, price, status, notes)
VALUES (%(class_type_id)s, %(trainer_id)s, %(hall_id)s, %(date)s, %(start_time)s, %(end_time)s, %(max_participants)s, %(current_participants)s, %(price)s, %(status)s, %(notes)s);

-- NAME: update_by_id
UPDATE classes
SET {set_clauses} -- Placeholder
WHERE class_id = %(class_id)s;

-- NAME: update_current_participants -- Specific update
UPDATE classes
SET current_participants = %(current_participants)s
WHERE class_id = %(class_id)s;

-- NAME: delete_by_id
DELETE FROM classes WHERE class_id = %s;

-- NAME: get_by_trainer_id
SELECT class_id, class_type_id, trainer_id, hall_id, date, start_time, end_time, max_participants, current_participants, price, status, notes
FROM classes WHERE trainer_id = %s ORDER BY date DESC, start_time ASC;

-- NAME: get_by_hall_id
SELECT class_id, class_type_id, trainer_id, hall_id, date, start_time, end_time, max_participants, current_participants, price, status, notes
FROM classes WHERE hall_id = %s ORDER BY date DESC, start_time ASC;

-- NAME: get_by_date_range
SELECT class_id, class_type_id, trainer_id, hall_id, date, start_time, end_time, max_participants, current_participants, price, status, notes
FROM classes 
WHERE date >= %(start_date)s AND date <= %(end_date)s -- Use >= and <= for inclusive range
ORDER BY date ASC, start_time ASC;