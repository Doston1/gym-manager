-- NAME: get_by_user_id_pk
SELECT t.trainer_id, t.user_id, t.specialization, t.bio, t.certifications, t.years_of_experience, u.first_name, u.last_name, u.email
FROM trainers t
JOIN users u ON t.user_id = u.user_id
WHERE t.user_id = %s;

-- NAME: get_by_trainer_id_pk
SELECT t.trainer_id, t.user_id, t.specialization, t.bio, t.certifications, t.years_of_experience, u.first_name, u.last_name, u.email
FROM trainers t
JOIN users u ON t.user_id = u.user_id
WHERE t.trainer_id = %s;

-- NAME: create
INSERT INTO trainers (trainer_id, user_id, specialization, bio, certifications, years_of_experience)
VALUES (%(trainer_id)s, %(user_id)s, %(specialization)s, %(bio)s, %(certifications)s, %(years_of_experience)s);

-- NAME: update_by_trainer_id_pk
UPDATE trainers
SET {set_clauses} -- Placeholder
WHERE trainer_id = %(trainer_id)s;

-- NAME: get_all_active
SELECT t.trainer_id, t.user_id, t.specialization, t.bio, t.certifications, t.years_of_experience, u.first_name, u.last_name, u.email, u.is_active
FROM trainers t
JOIN users u ON t.user_id = u.user_id
WHERE u.is_active = TRUE;

-- Note: Delete for trainers is typically handled by ON DELETE CASCADE from the users table.