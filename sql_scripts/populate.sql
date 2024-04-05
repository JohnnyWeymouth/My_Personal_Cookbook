USE cooking;

--          user VALUES (user_id(default),   username,   user_email,   first_name,   last_name,   password_hash,   date_joined );
INSERT INTO user VALUES (1, 'kkartch3', 'kevin@kevin.com', 'Kevin', 'Kartchner', '5baa61e4c9b93f3f0682250b6cf8331b7ee68fd8', '2024-03-01');
INSERT INTO user VALUES (2, 'johnnyboi', 'johnny@johnny.com', 'Johnny', 'Weymouth', '5baa61e4c9b93f3f0682250b6cf8331b7ee68fd8', '2024-03-01');
INSERT INTO user VALUES (3, 'kobywashere', 'koby@koby.com', 'Koby', 'Moulton', '5baa61e4c9b93f3f0682250b6cf8331b7ee68fd8', '2024-03-01');

--          login_attempt VALUES (login_id(default),   user_exists,   date_time,   attempt_num,   ip_address,   user_id(FK) );
INSERT INTO login_attempt VALUES (80, true, '3-1-2024 8:45 AM', 5, '192.168.255.255', 1);
INSERT INTO login_attempt VALUES (81, false, '3-1-2024 8:48 AM', 1, '192.168.246.255', 2);
INSERT INTO login_attempt VALUES (82, true, '3-1-2024 8:50 AM', 3, '192.168.245.255', 3);

--          login_session VALUES (session_id(default),   date_time,   cookie,   active,   user_id(FK) );
INSERT INTO login_session VALUES (9, '3-1-2024 8:45 AM', 'hsfksfdsfsdlfldsj', true, 1);
INSERT INTO login_session VALUES (10, '3-1-2024 8:48 AM', 'fjdkjfkajsfiewkf', false, 2);
INSERT INTO login_session VALUES (11, '3-1-2024 8:50 AM', 'luerhjnndeurf', true, 3);

--          recipe VALUES (recipe_id(default),   recipe_name,   date_created,   recipe_image,   recipe_description,   instructions,   tags,   user_id(FK) );
INSERT INTO recipe VALUES (70, 'Pasta', '2024-03-01', NULL, 'It is so good with parm.', 'Boil the pasta', '["Spicy", "Italian"]', 1);
INSERT INTO recipe VALUES (71, 'Omlete', '2024-03-01', NULL, 'Eggman does not approve', 'Crack the eggs', '["Breakfast", "Romantic"]', 2);
INSERT INTO recipe VALUES (72, 'Cake', '2024-03-01', NULL, 'Square cake from minecraft', 'Mix the flour and egg', '["Sweet", "Dessert", "Baking"]', 3);

--          ingredient VALUES (ingredient_id(default),   ingredient_name );
INSERT INTO ingredient VALUES (20, 'egg');
INSERT INTO ingredient VALUES (21, 'flour');
INSERT INTO ingredient VALUES (22, 'butter');

--          recipe_ingredient VALUES (quantity,   recipe_id(FK),   ingredient_id(FK) );
INSERT INTO recipe_ingredient VALUES ('2 cups', 70, 21);
INSERT INTO recipe_ingredient VALUES ('1', 70, 20);
INSERT INTO recipe_ingredient VALUES ('4', 71, 20);
INSERT INTO recipe_ingredient VALUES ('1 gallon', 72, 22);
INSERT INTO recipe_ingredient VALUES ('2', 72, 20);

--          personal_cookbook_entry VALUES (user_id(FK),   recipe_id(FK) );
INSERT INTO personal_cookbook_entry VALUES (1, 70);
INSERT INTO personal_cookbook_entry VALUES (2, 70);
INSERT INTO personal_cookbook_entry VALUES (3, 71);

--          to_try_entry VALUES (user_id(FK),   recipe_id(FK) );
INSERT INTO to_try_entry VALUES (1, 71);
INSERT INTO to_try_entry VALUES (2, 71);
INSERT INTO to_try_entry VALUES (3, 72);