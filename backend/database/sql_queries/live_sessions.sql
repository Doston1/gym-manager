-- NAME: get_by_id
SELECT ls.live_session_id, ls.schedule_id, ls.start_time, ls.end_time, ls.status, ls.notes,
       ws.week_start_date, ws.day_of_week, ws.start_time as scheduled_start_time, ws.end_time as scheduled_end_time,
       h.name as hall_name, CONCAT(u_trainer.first_name, ' ', u_trainer.last_name) as trainer_name
FROM live_sessions ls
JOIN weekly_schedule ws ON ls.schedule_id = ws.schedule_id
JOIN halls h ON ws.hall_id = h.hall_id
JOIN trainers t ON ws.trainer_id = t.trainer_id
JOIN users u_trainer ON t.user_id = u_trainer.user_id
WHERE ls.live_session_id = %s;

-- NAME: get_by_schedule_id
SELECT live_session_id, schedule_id, start_time, end_time, status, notes
FROM live_sessions
WHERE schedule_id = %s
ORDER BY start_time DESC; -- A schedule might have multiple (e.g., cancelled then restarted) live sessions

-- NAME: get_active_for_trainer -- status IN ('Started', 'In Progress')
SELECT ls.live_session_id, ls.schedule_id, ls.start_time, ls.status,
       ws.week_start_date, ws.day_of_week, ws.start_time as scheduled_start_time,
       h.name as hall_name
FROM live_sessions ls
JOIN weekly_schedule ws ON ls.schedule_id = ws.schedule_id
JOIN halls h ON ws.hall_id = h.hall_id
WHERE ws.trainer_id = %s AND ls.status IN ('Started', 'In Progress')
ORDER BY ls.start_time DESC;

-- NAME: get_active_for_member -- based on their attendance
SELECT ls.live_session_id, ls.schedule_id, ls.start_time, ls.status,
       ws.week_start_date, ws.day_of_week, ws.start_time as scheduled_start_time,
       h.name as hall_name, CONCAT(u_trainer.first_name, ' ', u_trainer.last_name) as trainer_name
FROM live_sessions ls
JOIN weekly_schedule ws ON ls.schedule_id = ws.schedule_id
JOIN halls h ON ws.hall_id = h.hall_id
JOIN trainers t ON ws.trainer_id = t.trainer_id
JOIN users u_trainer ON t.user_id = u_trainer.user_id
JOIN live_session_attendance lsa ON ls.live_session_id = lsa.live_session_id
WHERE lsa.member_id = %s AND ls.status IN ('Started', 'In Progress') AND lsa.status = 'Checked In'
ORDER BY ls.start_time DESC;

-- NAME: create
INSERT INTO live_sessions (schedule_id, start_time, status, notes)
VALUES (%(schedule_id)s, %(start_time)s, %(status)s, %(notes)s);

-- NAME: update_status_and_end_time
UPDATE live_sessions
SET status = %(status)s, end_time = %(end_time)s, notes = %(notes)s, updated_at = NOW()
WHERE live_session_id = %(live_session_id)s;

-- NAME: update_notes -- Example of a more specific update
UPDATE live_sessions
SET notes = %(notes)s, updated_at = NOW()
WHERE live_session_id = %(live_session_id)s;