-- NAME: get_by_id
SELECT lw.logged_workout_id, lw.member_id, lw.member_active_plan_id, lw.training_plan_day_id,
       lw.workout_date, lw.duration_minutes_actual, lw.notes_overall_session, lw.source, lw.live_session_id,
       tp.title as active_plan_title, tpd.name as plan_day_name
FROM logged_workouts lw
LEFT JOIN member_active_plans map ON lw.member_active_plan_id = map.active_plan_id
LEFT JOIN training_plans tp ON map.plan_id = tp.plan_id
LEFT JOIN training_plan_days tpd ON lw.training_plan_day_id = tpd.day_id
WHERE lw.logged_workout_id = %s;

-- NAME: get_by_member_id
SELECT lw.logged_workout_id, lw.member_id, lw.member_active_plan_id, lw.training_plan_day_id,
       lw.workout_date, lw.duration_minutes_actual, lw.notes_overall_session, lw.source, lw.live_session_id,
       tp.title as active_plan_title, tpd.name as plan_day_name
FROM logged_workouts lw
LEFT JOIN member_active_plans map ON lw.member_active_plan_id = map.active_plan_id
LEFT JOIN training_plans tp ON map.plan_id = tp.plan_id
LEFT JOIN training_plan_days tpd ON lw.training_plan_day_id = tpd.day_id
WHERE lw.member_id = %s
ORDER BY lw.workout_date DESC;

-- NAME: create
INSERT INTO logged_workouts (member_id, member_active_plan_id, training_plan_day_id, workout_date, duration_minutes_actual, notes_overall_session, source, live_session_id)
VALUES (%(member_id)s, %(member_active_plan_id)s, %(training_plan_day_id)s, %(workout_date)s, %(duration_minutes_actual)s, %(notes_overall_session)s, %(source)s, %(live_session_id)s);

-- NAME: update_by_id
UPDATE logged_workouts
SET {set_clauses} -- Placeholder
WHERE logged_workout_id = %(logged_workout_id)s;

-- NAME: delete_by_id
DELETE FROM logged_workouts WHERE logged_workout_id = %s;