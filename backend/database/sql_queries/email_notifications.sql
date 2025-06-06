-- NAME: get_by_id
SELECT notification_id, user_id, subject, message, sent_at, status, related_type, related_id
FROM email_notifications
WHERE notification_id = %s;

-- NAME: get_by_user_id
SELECT notification_id, user_id, subject, message, sent_at, status, related_type, related_id
FROM email_notifications
WHERE user_id = %s
ORDER BY sent_at DESC;

-- NAME: get_by_status
SELECT notification_id, user_id, subject, message, sent_at, status, related_type, related_id
FROM email_notifications
WHERE status = %s
ORDER BY sent_at DESC;

-- NAME: create
INSERT INTO email_notifications (user_id, subject, message, status, related_type, related_id, sent_at)
VALUES (%(user_id)s, %(subject)s, %(message)s, %(status)s, %(related_type)s, %(related_id)s, %(sent_at)s); -- sent_at can be NOW() or provided

-- NAME: update_status_by_id
UPDATE email_notifications
SET status = %(status)s, sent_at = IF(%(status)s = 'Sent' AND status != 'Sent', NOW(), sent_at) -- Update sent_at only if status changes to 'Sent'
WHERE notification_id = %(notification_id)s;

-- NAME: delete_by_id -- Deleting notifications might be based on age or status
DELETE FROM email_notifications WHERE notification_id = %s;