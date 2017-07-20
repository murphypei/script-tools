-- Database create script

DROP DATABASE IF EXISTS yaml;

CREATE DATABASE `yaml`;

USE yaml;

GRANT ALL PRIVILEGES ON `yaml`.* to 'root'@'localhost' identified by 'admin';
FLUSH PRIVILEGES;

CREATE TABLE IF NOT EXISTS `project` (
    `id` INT UNSIGNED NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `name` VARCHAR(50) NOT NULL,
    `db_username` VARCHAR(50) NOT NULL,
    `db_password` VARCHAR(50) NOT NULL,
    `db_name` VARCHAR(50) NOT NULL,
    `db_root_passwd` VARCHAR(50) NOT NULL,
    UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

INSERT `project` (`name`, `db_username`, `db_password`, `db_name`, `db_root_passwd`) VALUES ("mobil", "mobile_db_user", "mobile_db_passwd", "mobile_db", "mobile_root_passwd");
