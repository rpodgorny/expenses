DROP TABLE IF EXISTS expenses;
DROP TABLE IF EXISTS users;

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
);
CREATE INDEX ON users(name);

CREATE TABLE expenses (
    id SERIAL PRIMARY KEY,
    date DATE NOT NULL,
    category TEXT NOT NULL,
    note TEXT NOT NULL,
    amount DECIMAL NOT NULL,
    user_id INTEGER NOT NULL REFERENCES users(id),
	date_until DATE,
	CHECK (date_until = NULL OR date_until > date)
);
CREATE INDEX ON expenses(date);
CREATE INDEX ON expenses(category);
CREATE INDEX ON expenses(date_until);

