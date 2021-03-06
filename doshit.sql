DROP DATABASE doshit;
CREATE DATABASE doshit DEFAULT CHARACTER SET 'utf8';

GRANT ALL PRIVILEGES ON *.* TO 'dashit'@'%' IDENTIFIED BY 'Password1!';
USE doshit;

CREATE TABLE ashit (
	shit_no int(16) UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY
	,shit_type int(3) NOT NULL
	,shit_time datetime NOT NULL DEFAULT CURRENT_TIMESTAMP
	,shit_length int(64) NOT NULL
	,shit_finished int(1) NOT NULL DEFAULT 0
);

INSERT INTO ashit (shit_type, shit_length) VALUES (2, 5);

CREATE TABLE users (
	user_no int(11) UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY
	,user_name varchar(50) NOT NULL
	,user_passwd char(8) NOT NULL
	,user_type int(1) NOT NULL
);

INSERT INTO users (user_name, user_passwd, user_type) VALUES ('admin', 'password', 1);

CREATE TABLE SHITconfig (
	debounce_timeout int(8) UNSIGNED NOT NULL DEFAULT 1
	,alarm_length int(64) UNSIGNED NOT NULL DEFAULT 5
	,wireless_ssid varchar(31) NOT NULL DEFAULT 'HeartInformationTransmiter'
	,wireless_password varchar(63) NOT NULL DEFAULT 'E6FB1E850C'
	,wireless_encryption varchar(16) NOT NULL DEFAULT 'WEP'
);
/* setup defaults */
INSERT INTO SHITconfig () VALUES ();