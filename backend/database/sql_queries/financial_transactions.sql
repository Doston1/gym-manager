-- NAME: get_by_id
SELECT ft.transaction_id, ft.member_id, CONCAT(u.first_name, ' ', u.last_name) as member_name,
       ft.transaction_type, ft.amount, ft.payment_method, ft.transaction_date, ft.status,
       ft.reference_id, ft.notes
FROM financial_transactions ft
LEFT JOIN members m ON ft.member_id = m.member_id
LEFT JOIN users u ON m.user_id = u.user_id
WHERE ft.transaction_id = %s;

-- NAME: get_by_member_id
SELECT transaction_id, member_id, transaction_type, amount, payment_method, transaction_date, status, reference_id, notes
FROM financial_transactions
WHERE member_id = %s
ORDER BY transaction_date DESC;

-- NAME: get_by_type
SELECT transaction_id, member_id, transaction_type, amount, payment_method, transaction_date, status, reference_id, notes
FROM financial_transactions
WHERE transaction_type = %s
ORDER BY transaction_date DESC;

-- NAME: get_by_status
SELECT transaction_id, member_id, transaction_type, amount, payment_method, transaction_date, status, reference_id, notes
FROM financial_transactions
WHERE status = %s
ORDER BY transaction_date DESC;

-- NAME: get_by_date_range
SELECT transaction_id, member_id, transaction_type, amount, payment_method, transaction_date, status, reference_id, notes
FROM financial_transactions
WHERE transaction_date >= %(start_date)s AND transaction_date <= %(end_date)s
ORDER BY transaction_date DESC;

-- NAME: create
INSERT INTO financial_transactions (member_id, transaction_type, amount, payment_method, transaction_date, status, reference_id, notes)
VALUES (%(member_id)s, %(transaction_type)s, %(amount)s, %(payment_method)s, %(transaction_date)s, %(status)s, %(reference_id)s, %(notes)s);

-- NAME: update_status_by_id
UPDATE financial_transactions
SET status = %(status)s, reference_id = %(reference_id)s, notes = %(notes)s -- Example update
WHERE transaction_id = %(transaction_id)s;

-- NAME: update_by_id
UPDATE financial_transactions
SET {set_clauses} -- Placeholder
WHERE transaction_id = %(transaction_id)s;

-- Delete is usually not done for financial transactions, rather they are voided/refunded (new transaction)
-- NAME: delete_by_id
-- DELETE FROM financial_transactions WHERE transaction_id = %s;