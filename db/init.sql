USE 'subapka';

CREATE TABLE IF NOT EXISTS users (
	id 		INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
	name		VARCHAR(100) UNIQUE NOT NULL,
	email		VARCHAR(255) UNIQUE NOT NULL,
	password	VARCHAR(255) NOT NULL,
	created_at	TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS types (
	name 		VARCHAR(50) NOT NULL PRIMARY KEY,
	label 		VARCHAR(255)
) ENGINE=InnoDB CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS subscriptions (
	id 		INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
	name		VARCHAR(255) NOT NULL,
	price		DECIMAL(10,2) NOT NULL CHECK (price > 0),
	currency 	CHAR(3) NOT NULL DEFAULT 'PLN',
	type		VARCHAR(50) NOT NULL,
	renewal_date	DATE NOT NULL,
	user_id		INT UNSIGNED NOT NULL,
	status		VARCHAR(20) NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'cancelled')),
	created_at 	TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
	FOREIGN KEY (type) REFERENCES types(name),
	FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE RESTRICT
) ENGINE=InnoDB CHARSET=utf8mb4;

INSERT INTO types (name, label) VALUES
	('weekly', 'co tydzien'),
	('monthly', 'co miesiac'),
	('yearly', 'co rok');

INSERT INTO users (name, email, password) VALUES
	('jan', 'jan@example.com', 'haslo1234');

SET @jan_id = (SELECT id FROM users WHERE email = 'jan@example.com');

INSERT INTO subscriptions (name, price, currency, type, renewal_date, user_id, status) VALUES
	('Netflix', 43.00, 'PLN', 'monthly', '2026-12-01', @jan_id, 'active'),
	('Spotify', 23.99, 'PLN', 'monthly', '2026-11-20', @jan_id, 'active'),
	('Amazon Prime', 49.00, 'PLN', 'yearly', '2027-03-15', @jan_id, 'active'),
	('Tygodnik', 12.00, 'PLN', 'weekly', '2026-11-18', @jan_id, 'cancelled');
