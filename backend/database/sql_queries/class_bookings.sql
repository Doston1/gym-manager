-- NAME: get_by_id
SELECT booking_id, class_id, member_id, booking_date, payment_status, amount_paid, attendance_status, cancellation_date, cancellation_reason, email_notification_sent
FROM class_bookings
WHERE booking_id = %s;

-- NAME: get_by_class_id
SELECT cb.booking_id, cb.class_id, cb.member_id, cb.booking_date, cb.payment_status, cb.amount_paid, cb.attendance_status,
       u.first_name, u.last_name, u.email, u.profile_image_path
FROM class_bookings cb
JOIN members m ON cb.member_id = m.member_id
JOIN users u ON m.user_id = u.user_id
WHERE cb.class_id = %s
ORDER BY cb.booking_date DESC;

-- NAME: get_by_member_id
SELECT cb.booking_id, cb.class_id, cb.member_id, cb.booking_date, cb.payment_status, cb.amount_paid, cb.attendance_status,
       c.date AS class_date, c.start_time AS class_start_time, c.end_time AS class_end_time,
       ct.name AS class_type_name,
       h.name AS hall_name,
       CONCAT(u_trainer.first_name, ' ', u_trainer.last_name) AS trainer_name
FROM class_bookings cb
JOIN classes c ON cb.class_id = c.class_id
JOIN class_types ct ON c.class_type_id = ct.class_type_id
JOIN halls h ON c.hall_id = h.hall_id
JOIN trainers t ON c.trainer_id = t.trainer_id
JOIN users u_trainer ON t.user_id = u_trainer.user_id
WHERE cb.member_id = %s
ORDER BY c.date DESC, c.start_time DESC;

-- NAME: create
INSERT INTO class_bookings (class_id, member_id, payment_status, amount_paid, attendance_status, email_notification_sent)
VALUES (%(class_id)s, %(member_id)s, %(payment_status)s, %(amount_paid)s, %(attendance_status)s, %(email_notification_sent)s);

-- NAME: update_by_id
UPDATE class_bookings
SET {set_clauses} -- Placeholder
WHERE booking_id = %(booking_id)s;

-- NAME: delete_by_id
DELETE FROM class_bookings WHERE booking_id = %s;

-- NAME: get_count_by_class_id_active_booking -- Count confirmed/paid bookings towards capacity
SELECT COUNT(*) as booking_count 
FROM class_bookings 
WHERE class_id = %s AND payment_status IN ('Paid', 'Free') AND attendance_status != 'Cancelled'; 
-- Adjust statuses based on your business logic for who counts towards capacity