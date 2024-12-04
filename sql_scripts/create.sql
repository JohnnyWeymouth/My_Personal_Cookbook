CREATE DATABASE cooking;

USE cooking;

CREATE TABLE user (
  user_id SERIAL,
  username VARCHAR (255) NOT NULL,
  user_email VARCHAR (255) NOT NULL,
  first_name VARCHAR (255) NOT NULL,
  last_name VARCHAR (255) NOT NULL,
  password_hash VARCHAR (255) NOT NULL,
  date_joined DATE NOT NULL,
  PRIMARY KEY (user_id),
  UNIQUE (username),
  UNIQUE (user_email)
);

CREATE TABLE login_attempt (
  login_id SERIAL,
  user_exists BOOLEAN NOT NULL,
  date_time VARCHAR (255) NOT NULL,
  attempt_num INT NOT NULL,
  ip_address VARCHAR (255) NOT NULL,
  user_id BIGINT UNSIGNED,
  PRIMARY KEY (login_id),
  FOREIGN KEY (user_id) REFERENCES user(user_id)
);

CREATE TABLE login_session (
  session_id SERIAL,
  date_time VARCHAR (255) NOT NULL,
  cookie VARCHAR (255) NOT NULL,
  active BOOLEAN NOT NULL,
  user_id BIGINT UNSIGNED,
  PRIMARY KEY (session_id),
  FOREIGN KEY (user_id) REFERENCES user(user_id),
  UNIQUE (cookie)
);

CREATE TABLE recipe (
  recipe_id SERIAL,
  recipe_name VARCHAR (255) NOT NULL,
  date_created DATE NOT NULL,
  recipe_image MEDIUMBLOB,
  recipe_description VARCHAR (3000) NOT NULL,
  instructions VARCHAR (3000) NOT NULL,
  tags JSON NOT NULL,
  user_id BIGINT UNSIGNED,
  PRIMARY KEY (recipe_id),
  FOREIGN KEY (user_id) REFERENCES user(user_id)
);

CREATE TABLE personal_cookbook_entry (
  user_id BIGINT UNSIGNED,
  recipe_id BIGINT UNSIGNED,
  PRIMARY KEY (user_id, recipe_id),
  FOREIGN KEY (user_id) REFERENCES user(user_id),
  FOREIGN KEY (recipe_id) REFERENCES recipe(recipe_id)
);

CREATE TABLE to_try_entry (
  user_id BIGINT UNSIGNED,
  recipe_id BIGINT UNSIGNED,
  PRIMARY KEY (user_id, recipe_id),
  FOREIGN KEY (user_id) REFERENCES user(user_id),
  FOREIGN KEY (recipe_id) REFERENCES recipe(recipe_id)
);