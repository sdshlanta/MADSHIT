CREATE DATABASE doshit DEFAULT CHARACTER SET 'utf8';

GRANT ALL PRIVILEGES ON *.* TO 'dashit'@'%' IDENTIFIED BY 'Password1!';
USE doshit;

CREATE TABLE ashit (
	shit_no int(11) UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
	shit_type int(3) NOT NULL,
	shit_time datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
	shit_length int(64) NOT NULL
);

CREATE TABLE users (
	user_no int(11) UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
	user_name varchar(50) NOT NULL,
	user_passwd char(8) NOT NULL,
	user_type int(1) NOT NULL
);

INSERT INTO users (user_name, user_passwd, user_type) VALUES ('admin', 'password', 1);