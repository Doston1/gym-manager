-- NAME: get_by_id
SELECT active_plan_id, member_id, plan_id, start_date, end_date, status, created_at, updated_at
FROM member_active_plans
WHERE active_plan_id = %s;

-- NAME: get_by_member_id
SELECT map.active_plan_id, map.member_id, map.plan_id, tp.title as plan_title, map.start_date, map.end_date, map.status
FROM member_active_plans map
JOIN training_plans tp ON map.plan_id = tp.plan_id
WHERE map.member_id = %s
ORDER BY map.start_date DESC;

-- NAME: get_active_by_member_id -- Get only currently active plan(s) for a member
SELECT map.active_plan_id, map.member_id, map.plan_id, tp.title as plan_title, map.start_date, map.end_date, map.status
FROM member_active_plans map
JOIN training_plans tp ON map.plan_id = tp.plan_id
WHERE map.member_id = %s AND map.status = 'Active'
ORDER BY map.start_date DESC;

-- NAME: create
INSERT INTO member_active_plans (member_id, plan_id, start_date, end_date, status)
VALUES (%(member_id)s, %(plan_id)s, %(start_date)s, %(end_date)s, %(status)s);

-- NAME: update_by_id
UPDATE member_active_plans
SET {set_clauses} -- Placeholder
WHERE active_plan_id = %(active_plan_id)s;

-- NAME: delete_by_id -- Usually, status is changed to 'Cancelled' rather than hard delete
DELETE FROM member_active_plans WHERE active_plan_id = %s;