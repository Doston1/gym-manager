-- NAME: class_types_get_by_id
SELECT * FROM class_types WHERE class_type_id = %s;

-- NAME: class_types_get_all
SELECT * FROM class_types ORDER BY name;

-- NAME: class_types_create
INSERT INTO class_types (
    name, 
    description, 
    difficulty_level, 
    equipment_needed, 
    default_max_participants, 
    default_price,
    duration_minutes
) VALUES (
    %(name)s, 
    %(description)s, 
    %(difficulty_level)s, 
    %(equipment_needed)s, 
    %(default_max_participants)s, 
    %(default_price)s,
    %(duration_minutes)s
);

-- NAME: class_types_update_by_id
UPDATE class_types 
SET 
    name = %(name)s, 
    description = %(description)s, 
    difficulty_level = %(difficulty_level)s, 
    equipment_needed = %(equipment_needed)s, 
    default_max_participants = %(default_max_participants)s, 
    default_price = %(default_price)s,
    duration_minutes = %(duration_minutes)s,
    updated_at = NOW(),
    is_active = %(is_active)s
WHERE class_type_id = %(class_type_id)s;

-- NAME: class_types_delete_by_id
DELETE FROM class_types WHERE class_type_id = %s;

-- NAME: classes_get_by_id
SELECT * FROM classes WHERE class_id = %s;

-- NAME: classes_get_all
SELECT * FROM classes ORDER BY date DESC, start_time ASC;

-- NAME: classes_get_all_detailed
SELECT 
    c.class_id, 
    c.class_type_id, 
    c.trainer_id, 
    c.hall_id,
    c.date,
    c.start_time, 
    c.end_time, 
    c.max_participants, 
    c.current_participants,
    c.price,
    c.status,
    c.notes,
    c.created_at,
    c.updated_at,
    ct.name AS class_type_name, 
    ct.description AS class_type_description, 
    ct.difficulty_level,
    ct.equipment_needed,
    h.name AS hall_name, 
    h.max_capacity AS hall_capacity,
    h.location AS hall_location,
    CONCAT(u.first_name, ' ', u.last_name) AS trainer_name,
    u.profile_image_path AS trainer_image,
    t.specialization AS trainer_specialization
FROM classes c
LEFT JOIN class_types ct ON c.class_type_id = ct.class_type_id
LEFT JOIN halls h ON c.hall_id = h.hall_id
LEFT JOIN trainers t ON c.trainer_id = t.trainer_id
LEFT JOIN users u ON t.user_id = u.user_id
ORDER BY c.date DESC, c.start_time ASC;

-- NAME: classes_create
INSERT INTO classes (
    class_type_id, 
    trainer_id, 
    hall_id, 
    date,
    start_time, 
    end_time, 
    max_participants, 
    current_participants,
    price,
    status,
    notes
) VALUES (
    %(class_type_id)s, 
    %(trainer_id)s, 
    %(hall_id)s, 
    %(date)s,
    %(start_time)s, 
    %(end_time)s, 
    %(max_participants)s, 
    %(current_participants)s,
    %(price)s,
    %(status)s,
    %(notes)s
);

-- NAME: classes_update_by_id
UPDATE classes 
SET 
    class_type_id = %(class_type_id)s, 
    trainer_id = %(trainer_id)s, 
    hall_id = %(hall_id)s, 
    date = %(date)s,
    start_time = %(start_time)s, 
    end_time = %(end_time)s, 
    max_participants = %(max_participants)s, 
    price = %(price)s,
    status = %(status)s,
    notes = %(notes)s,
    updated_at = NOW()
WHERE class_id = %(class_id)s;

-- NAME: classes_delete_by_id
DELETE FROM classes WHERE class_id = %s;

-- NAME: classes_get_by_trainer_id
SELECT * FROM classes WHERE trainer_id = %s ORDER BY date DESC, start_time ASC;

-- NAME: classes_get_by_hall_id
SELECT * FROM classes WHERE hall_id = %s ORDER BY date DESC, start_time ASC;

-- NAME: classes_get_by_date_range
SELECT * FROM classes 
WHERE date BETWEEN %(start_date)s AND %(end_date)s 
ORDER BY date ASC, start_time ASC;

-- NAME: class_bookings_get_by_id
SELECT * FROM class_bookings WHERE booking_id = %s;

-- NAME: class_bookings_get_by_class_id
SELECT 
    cb.*,
    u.first_name,
    u.last_name,
    u.email,
    u.profile_image_path
FROM class_bookings cb
JOIN members m ON cb.member_id = m.member_id
JOIN users u ON m.user_id = u.user_id
WHERE cb.class_id = %s
ORDER BY cb.booking_date DESC;

-- NAME: class_bookings_get_by_member_id
SELECT 
    cb.*,
    c.date AS class_date,
    c.start_time,
    c.end_time,
    ct.name AS class_type_name,
    h.name AS hall_name,
    CONCAT(u.first_name, ' ', u.last_name) AS trainer_name
FROM class_bookings cb
JOIN classes c ON cb.class_id = c.class_id
JOIN class_types ct ON c.class_type_id = ct.class_type_id
JOIN halls h ON c.hall_id = h.hall_id
JOIN trainers t ON c.trainer_id = t.trainer_id
JOIN users u ON t.user_id = u.user_id
WHERE cb.member_id = %s
ORDER BY c.date DESC, c.start_time DESC;

-- NAME: class_bookings_create
INSERT INTO class_bookings (
    class_id,
    member_id,
    payment_status,
    amount_paid
) VALUES (
    %(class_id)s,
    %(member_id)s,
    %(payment_status)s,
    %(amount_paid)s
);

-- NAME: class_bookings_update_by_id
UPDATE class_bookings
SET
    attendance_status = %(attendance_status)s,
    payment_status = %(payment_status)s,
    amount_paid = %(amount_paid)s,
    email_notification_sent = %(email_notification_sent)s
WHERE booking_id = %(booking_id)s;

-- NAME: class_bookings_delete_by_id
DELETE FROM class_bookings WHERE booking_id = %s;

-- NAME: class_bookings_cancel_by_id
UPDATE class_bookings
SET
    attendance_status = 'Cancelled',
    payment_status = %(payment_status)s,
    cancellation_date = NOW(),
    cancellation_reason = %(cancellation_reason)s
WHERE booking_id = %(booking_id)s;

-- NAME: update_class_current_participants
UPDATE classes
SET current_participants = (
    SELECT COUNT(*) 
    FROM class_bookings 
    WHERE class_id = %(class_id)s 
    AND attendance_status != 'Cancelled'
)
WHERE class_id = %(class_id)s;
