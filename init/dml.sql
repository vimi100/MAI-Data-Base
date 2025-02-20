INSERT INTO Roles (name)
VALUES ('Trainer'), ('Fighter');


INSERT INTO Users (login, password, id_role)
VALUES ('vimi', '03ac674216f3e15c761ee1a5e255f067953623c8b388b4459e13f978d7c846f4', 2),
       ('vim', '03ac674216f3e15c761ee1a5e255f067953623c8b388b4459e13f978d7c846f4', 2),
       ('dude', '03ac674216f3e15c761ee1a5e255f067953623c8b388b4459e13f978d7c846f4', 2),
       ('ss', '03ac674216f3e15c761ee1a5e255f067953623c8b388b4459e13f978d7c846f4', 2),
       ('gut', '03ac674216f3e15c761ee1a5e255f067953623c8b388b4459e13f978d7c846f4', 2),
        ('mate', '03ac674216f3e15c761ee1a5e255f067953623c8b388b4459e13f978d7c846f4', 1),
        ('god', '03ac674216f3e15c761ee1a5e255f067953623c8b388b4459e13f978d7c846f4', 1),
        ('evil', '03ac674216f3e15c761ee1a5e255f067953623c8b388b4459e13f978d7c846f4', 1),
        ('boy', '03ac674216f3e15c761ee1a5e255f067953623c8b388b4459e13f978d7c846f4', 2),
        ('boy2', '03ac674216f3e15c761ee1a5e255f067953623c8b388b4459e13f978d7c846f4', 2),
        ('boy3', '03ac674216f3e15c761ee1a5e255f067953623c8b388b4459e13f978d7c846f4', 2),
        ('boy4', '03ac674216f3e15c761ee1a5e255f067953623c8b388b4459e13f978d7c846f4', 2),
        ('fly', '03ac674216f3e15c761ee1a5e255f067953623c8b388b4459e13f978d7c846f4', 1),
        ('fly2', '03ac674216f3e15c761ee1a5e255f067953623c8b388b4459e13f978d7c846f4', 2);

INSERT INTO Fighters (fullname, date_of_birth, phone_number, id_user)
VALUES ('Бурунов Михаил Андреевич', '2004-09-10', '+79875033684', 1),
        ('Фазонов Михаил Андреевич', '2004-09-10', '+79875033684', 2),
        ('Герасимов Михаил Андреевич', '2004-09-10', '+79875033684', 3),
        ('Химмлер Михаил Андреевич', '2004-09-10', '+79875033684', 4),
        ('Смирнов Михаил Андреевич', '2004-09-10', '+79875033684', 5),
        ('Губнов Михаил Андреевич', '2004-09-10', '+79875033684', 9),
        ('Тварь Михаил Андреевич', '2004-09-10', '+79875033684', 10),
        ('Непобеждённый Михаил Андреевич', '2004-09-10', '+79875033684', 11),
        ('Станиславов Михаил Андреевич', '2004-09-10', '+79875033684', 12),
        ('Почестнев Михаил Андреевич', '2004-09-10', '+79875033684', 14);

INSERT INTO Trainers (fullname, date_of_birth, phone_number, experience, id_user)
VALUES
    ('Акульбек Сидорович', '2004-09-10', '+79875033684', 10, 6),
    ('Курт Кобейн Дональдович', '1967-02-20', '+79875033684', 15, 7),
    ('Том Харди', '1985-09-10', '+79875033684', 20, 8),
    ('Сталоне Сильвестер', '1965-09-10', '+79875033684', 30, 13);


INSERT INTO Clubs (name_club, address, tournament_place, training_place)
VALUES
    ('Звезда', 'Метро Сокол, Новопесчанный переулок 5', True, True),
    ('Восток', 'Метро Аэропорт, Новопесчанный переулок 5', True, True),
    ('Космос', 'Метро Динамо, Новопесчанный переулок 5', False, True),
    ('Металл', 'Метро Маяковская, Новопесчанный переулок 5', False, True);

INSERT INTO Teams (name, id_trainer)
VALUES
    ('Металлисты', 1),
    ('Нирвана', 2),
    ('Рембо', 4);

INSERT INTO Teams_Composition (id_team, id_fighter)
VALUES
    (1, 1),
    (1, 2),
    (2, 3),
    (2, 4),
    (3, 5),
    (3, 6);

INSERT INTO Tournaments (name, id_team_red, id_team_blue, id_club, date)
VALUES
    ('Турнир за первенство Москвы 1 этап', 1, 2, 1, '2024-09-10'),
    ('Турнир за первенство Москвы 2 этап', 2, 3, 2, '2024-10-13'),
    ('Турнир за первенство Москвы 3 этап', 1, 3, 1, '2024-11-17'),
    ('Турнир за первенство России', 2, 1, 3, '2025-02-17');

INSERT INTO Winners (id_team, id_tournament)
VALUES
    (1, 1),
    (2, 2),
    (3, 3);


SELECT * FROM Users;
