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
	FOREIGN KEY (user_id) REFERENCES users(id)
) ENGINE=InnoDB CHARSET=utf8mb4;

INSERT INTO types (name, label) VALUES
	('weekly', 'co tydzien'),
	('monthly', 'co miesiac'),
	('yearly', 'co rok');
