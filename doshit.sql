CREATE DATABASE doshit DEFAULT CHARACTER SET 'utf8';

USE doshit;

CREATE TABLE ashit (
	shit_no int(11) UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
	shit_type int(1) NOT NULL,
	shit_time datetime NOT NULL,
	shit_length int(64) NOT NULL
);
