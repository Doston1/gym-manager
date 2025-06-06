-- NAME: get_by_id
SELECT cpr.request_id, cpr.member_id, CONCAT(u_member.first_name, ' ', u_member.last_name) as member_name,
       cpr.goal, cpr.days_per_week, cpr.focus_areas, cpr.equipment_available, cpr.health_limitations,
       cpr.request_date, cpr.assigned_trainer_id, CONCAT(u_trainer.first_name, ' ', u_trainer.last_name) as trainer_name,
       cpr.status, cpr.completed_plan_id, tp.title as completed_plan_title, cpr.notes
FROM custom_plan_requests cpr
JOIN members m ON cpr.member_id = m.member_id
JOIN users u_member ON m.user_id = u_member.user_id
LEFT JOIN trainers t ON cpr.assigned_trainer_id = t.trainer_id
LEFT JOIN users u_trainer ON t.user_id = u_trainer.user_id
LEFT JOIN training_plans tp ON cpr.completed_plan_id = tp.plan_id
WHERE cpr.request_id = %s;

-- NAME: get_by_member_id
SELECT cpr.request_id, cpr.member_id, cpr.goal, cpr.days_per_week, cpr.request_date, 
       cpr.assigned_trainer_id, CONCAT(u_trainer.first_name, ' ', u_trainer.last_name) as trainer_name,
       cpr.status, cpr.completed_plan_id, tp.title as completed_plan_title
FROM custom_plan_requests cpr
LEFT JOIN trainers t ON cpr.assigned_trainer_id = t.trainer_id
LEFT JOIN users u_trainer ON t.user_id = u_trainer.user_id
LEFT JOIN training_plans tp ON cpr.completed_plan_id = tp.plan_id
WHERE cpr.member_id = %s
ORDER BY cpr.request_date DESC;

-- NAME: get_by_trainer_id
SELECT cpr.request_id, cpr.member_id, CONCAT(u_member.first_name, ' ', u_member.last_name) as member_name,
       cpr.goal, cpr.days_per_week, cpr.request_date, cpr.status
FROM custom_plan_requests cpr
JOIN members m ON cpr.member_id = m.member_id
JOIN users u_member ON m.user_id = u_member.user_id
WHERE cpr.assigned_trainer_id = %s
ORDER BY cpr.request_date DESC;

-- NAME: get_by_status
SELECT cpr.request_id, cpr.member_id, CONCAT(u_member.first_name, ' ', u_member.last_name) as member_name,
       cpr.goal, cpr.days_per_week, cpr.request_date, 
       cpr.assigned_trainer_id, CONCAT(u_trainer.first_name, ' ', u_trainer.last_name) as trainer_name,
       cpr.status
FROM custom_plan_requests cpr
JOIN members m ON cpr.member_id = m.member_id
JOIN users u_member ON m.user_id = u_member.user_id
LEFT JOIN trainers t ON cpr.assigned_trainer_id = t.trainer_id
LEFT JOIN users u_trainer ON t.user_id = u_trainer.user_id
WHERE cpr.status = %s
ORDER BY cpr.request_date DESC;

-- NAME: create
INSERT INTO custom_plan_requests (member_id, goal, days_per_week, focus_areas, equipment_available, health_limitations, assigned_trainer_id, status, notes)
VALUES (%(member_id)s, %(goal)s, %(days_per_week)s, %(focus_areas)s, %(equipment_available)s, %(health_limitations)s, %(assigned_trainer_id)s, %(status)s, %(notes)s);

-- NAME: update_by_id
UPDATE custom_plan_requests
SET {set_clauses} -- Placeholder
WHERE request_id = %(request_id)s;

-- NAME: delete_by_id -- Usually status changes to 'Cancelled' instead
DELETE FROM custom_plan_requests WHERE request_id = %s;