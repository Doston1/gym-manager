-- NAME: get_by_auth_id
SELECT user_id, auth_id, email, first_name, last_name, phone, date_of_birth, gender, profile_image_path, user_type, created_at, updated_at, is_active
FROM users
WHERE auth_id = %s;

-- NAME: get_by_email
SELECT user_id, auth_id, email, first_name, last_name, phone, date_of_birth, gender, profile_image_path, user_type, created_at, updated_at, is_active
FROM users
WHERE email = %s;

-- NAME: get_by_id_pk
SELECT user_id, auth_id, email, first_name, last_name, phone, date_of_birth, gender, profile_image_path, user_type, created_at, updated_at, is_active
FROM users
WHERE user_id = %s;

-- NAME: get_all
SELECT user_id, auth_id, email, first_name, last_name, phone, date_of_birth, gender, profile_image_path, user_type, created_at, updated_at, is_active
FROM users
ORDER BY user_id
LIMIT %s OFFSET %s;

-- NAME: create
INSERT INTO users (auth_id, email, first_name, last_name, phone, date_of_birth, gender, profile_image_path, user_type, is_active)
VALUES (%(auth_id)s, %(email)s, %(first_name)s, %(last_name)s, %(phone)s, %(date_of_birth)s, %(gender)s, %(profile_image_path)s, %(user_type)s, %(is_active)s);

-- NAME: update_by_auth_id
UPDATE users
SET {set_clauses} -- This placeholder will be replaced by Python code
WHERE auth_id = %(auth_id)s;

-- NAME: delete_by_auth_id
DELETE FROM users WHERE auth_id = %s;