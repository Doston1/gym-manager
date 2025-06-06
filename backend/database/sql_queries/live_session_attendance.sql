-- NAME: get_by_id
SELECT id, live_session_id, member_id, check_in_time, check_out_time, status, notes
FROM live_session_attendance
WHERE id = %s;

-- NAME: get_by_live_session_id
SELECT lsa.id, lsa.live_session_id, lsa.member_id, CONCAT(u.first_name, ' ', u.last_name) as member_name,
       lsa.check_in_time, lsa.check_out_time, lsa.status, lsa.notes
FROM live_session_attendance lsa
JOIN members m ON lsa.member_id = m.member_id
JOIN users u ON m.user_id = u.user_id
WHERE lsa.live_session_id = %s;

-- NAME: get_by_live_session_and_member
SELECT id, live_session_id, member_id, check_in_time, check_out_time, status, notes
FROM live_session_attendance
WHERE live_session_id = %(live_session_id)s AND member_id = %(member_id)s;

-- NAME: create_check_in -- Assumes status 'Checked In' on creation
INSERT INTO live_session_attendance (live_session_id, member_id, check_in_time, status, notes)
VALUES (%(live_session_id)s, %(member_id)s, %(check_in_time)s, 'Checked In', %(notes)s);

-- NAME: update_check_out_or_status
UPDATE live_session_attendance
SET status = %(status)s, check_out_time = %(check_out_time)s, notes = %(notes)s, updated_at = NOW()
WHERE id = %(id)s;