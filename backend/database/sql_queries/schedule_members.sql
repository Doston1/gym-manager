-- NAME: get_by_id
SELECT id, schedule_id, member_id, status, training_plan_day_id, created_at, updated_at
FROM schedule_members
WHERE id = %s;

-- NAME: get_by_schedule_id
SELECT sm.id, sm.schedule_id, sm.member_id, CONCAT(u.first_name, ' ', u.last_name) as member_name, u.email as member_email,
       sm.status, sm.training_plan_day_id, tpd.name as plan_day_name
FROM schedule_members sm
JOIN members m ON sm.member_id = m.member_id
JOIN users u ON m.user_id = u.user_id
LEFT JOIN training_plan_days tpd ON sm.training_plan_day_id = tpd.day_id
WHERE sm.schedule_id = %s;

-- NAME: get_by_member_id_and_week
SELECT sm.id, sm.schedule_id, 
       ws.week_start_date, ws.day_of_week, ws.start_time, ws.end_time, 
       h.name as hall_name, CONCAT(u_trainer.first_name, ' ', u_trainer.last_name) as trainer_name,
       sm.status, sm.training_plan_day_id, tpd.name as plan_day_name
FROM schedule_members sm
JOIN weekly_schedule ws ON sm.schedule_id = ws.schedule_id
JOIN halls h ON ws.hall_id = h.hall_id
JOIN trainers t ON ws.trainer_id = t.trainer_id
JOIN users u_trainer ON t.user_id = u_trainer.user_id
LEFT JOIN training_plan_days tpd ON sm.training_plan_day_id = tpd.day_id
WHERE sm.member_id = %(member_id)s AND ws.week_start_date = %(week_start_date)s
ORDER BY ws.day_of_week, ws.start_time;

-- NAME: get_count_by_schedule_id_active_status
SELECT COUNT(*) as member_count
FROM schedule_members
WHERE schedule_id = %s AND status NOT IN ('Cancelled', 'No Show'); -- Consider which statuses count towards capacity

-- NAME: create
INSERT INTO schedule_members (schedule_id, member_id, status, training_plan_day_id)
VALUES (%(schedule_id)s, %(member_id)s, %(status)s, %(training_plan_day_id)s);

-- NAME: update_by_id
UPDATE schedule_members
SET {set_clauses} -- Placeholder
WHERE id = %(id)s;

-- NAME: delete_by_id
DELETE FROM schedule_members WHERE id = %s;

-- NAME: delete_by_schedule_and_member
DELETE FROM schedule_members WHERE schedule_id = %(schedule_id)s AND member_id = %(member_id)s;