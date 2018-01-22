CREATE DATABASE doshit DEFAULT CHARACTER SET 'utf8'

CREATE TABLE `ashit` (
	`shit_no` int(11) NOT NULL AUTO_INCREMENT,
	`shit_type` int(1) NOT NULL,
	`shit_time` date NOT NULL,
	`shit_length` int(64) NOT NULL,
	PRIMARY KEY (`shit_no`)
) ENGINE=InnoDBs
