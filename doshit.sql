CREATE DATABASE doshit DEFAULT CHARACTER SET 'utf8';

USE doshit;

CREATE TABLE ashit (
	shit_no int(11) UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
	shit_type int(3) NOT NULL,
	shit_time datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
	shit_length float(64) NOT NULL
);
