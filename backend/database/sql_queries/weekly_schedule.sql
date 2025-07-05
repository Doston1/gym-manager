-- NAME: get_by_id
SELECT schedule_id, week_start_date, day_of_week, start_time, end_time, hall_id, trainer_id, max_capacity, status, created_by, created_at, updated_at
FROM weekly_schedule
WHERE schedule_id = %s;

-- NAME: get_by_week
SELECT ws.schedule_id, ws.week_start_date, ws.day_of_week, ws.start_time, ws.end_time, 
       ws.hall_id, h.name as hall_name, 
       ws.trainer_id, CONCAT(u_trainer.first_name, ' ', u_trainer.last_name) as trainer_name,
       ws.max_capacity, 
       (SELECT COUNT(*) FROM schedule_members sm WHERE sm.schedule_id = ws.schedule_id AND sm.status NOT IN ('Cancelled', 'No Show')) as current_participants,
       ws.status, ws.created_by
FROM weekly_schedule ws
JOIN halls h ON ws.hall_id = h.hall_id
JOIN trainers t ON ws.trainer_id = t.trainer_id
JOIN users u_trainer ON t.user_id = u_trainer.user_id
WHERE ws.week_start_date = %s
ORDER BY ws.day_of_week, ws.start_time;

-- NAME: get_by_trainer_and_week
SELECT ws.schedule_id, ws.week_start_date, ws.day_of_week, ws.start_time, ws.end_time, 
       ws.hall_id, h.name as hall_name, 
       ws.trainer_id, CONCAT(u_trainer.first_name, ' ', u_trainer.last_name) as trainer_name,
       ws.max_capacity, 
       (SELECT COUNT(*) FROM schedule_members sm WHERE sm.schedule_id = ws.schedule_id AND sm.status NOT IN ('Cancelled', 'No Show')) as current_participants,
       ws.status
FROM weekly_schedule ws
JOIN halls h ON ws.hall_id = h.hall_id
JOIN trainers t ON ws.trainer_id = t.trainer_id
JOIN users u_trainer ON t.user_id = u_trainer.user_id
WHERE ws.trainer_id = %(trainer_id)s AND ws.week_start_date = %(week_start_date)s
ORDER BY ws.day_of_week, ws.start_time;

-- NAME: get_by_hall_and_week 
SELECT ws.schedule_id, ws.week_start_date, ws.day_of_week, ws.start_time, ws.end_time, 
       ws.hall_id, h.name as hall_name, 
       ws.trainer_id, CONCAT(u_trainer.first_name, ' ', u_trainer.last_name) as trainer_name,
       ws.max_capacity, 
       (SELECT COUNT(*) FROM schedule_members sm WHERE sm.schedule_id = ws.schedule_id AND sm.status NOT IN ('Cancelled', 'No Show')) as current_participants,
       ws.status
FROM weekly_schedule ws
JOIN halls h ON ws.hall_id = h.hall_id
JOIN trainers t ON ws.trainer_id = t.trainer_id
JOIN users u_trainer ON t.user_id = u_trainer.user_id
WHERE ws.hall_id = %(hall_id)s AND ws.week_start_date = %(week_start_date)s
ORDER BY ws.day_of_week, ws.start_time;

-- NAME: create
INSERT INTO weekly_schedule (week_start_date, day_of_week, start_time, end_time, hall_id, trainer_id, max_capacity, status, created_by)
VALUES (%(week_start_date)s, %(day_of_week)s, %(start_time)s, %(end_time)s, %(hall_id)s, %(trainer_id)s, %(max_capacity)s, %(status)s, %(created_by)s);

-- NAME: update_by_id
UPDATE weekly_schedule
SET {set_clauses} -- Placeholder
WHERE schedule_id = %(schedule_id)s;

-- NAME: delete_by_id
DELETE FROM weekly_schedule WHERE schedule_id = %s;

-- NAME: check_overlap -- For validating new schedule slots
SELECT schedule_id FROM weekly_schedule
WHERE day_of_week = %(day_of_week)s
  AND week_start_date = %(week_start_date)s
  AND (trainer_id = %(trainer_id)s OR hall_id = %(hall_id)s)
  AND (
    (%(start_time)s < end_time AND %(end_time)s > start_time)
  )
  AND status != 'Cancelled'
  AND (%(schedule_id_to_exclude)s IS NULL OR schedule_id != %(schedule_id_to_exclude)s); -- For updates