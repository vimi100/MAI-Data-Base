CREATE TABLE Roles (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(15) NOT NULL
);

CREATE TABLE Users (
    id BIGSERIAL PRIMARY KEY,
    login VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    id_role BIGINT REFERENCES Roles(id)
);

CREATE TABLE Fighters (
    id BIGSERIAL PRIMARY KEY,
    fullname VARCHAR(100) NOT NULL,
    date_of_birth DATE,
    phone_number VARCHAR(15),
    id_user BIGINT REFERENCES Users(id) ON DELETE CASCADE
);

CREATE TABLE Trainers (
    id BIGSERIAL PRIMARY KEY,
    fullname VARCHAR(100) NOT NULL,
    date_of_birth DATE,
    phone_number VARCHAR(15),
    experience INT,
    id_user BIGINT REFERENCES Users(id)
);

CREATE TABLE Teams (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    id_trainer BIGINT REFERENCES Trainers(id)
);

CREATE TABLE Teams_Composition (
    id BIGSERIAL PRIMARY KEY,
    id_team BIGINT REFERENCES Teams(id),
    id_fighter BIGINT REFERENCES Fighters(id) ON DELETE CASCADE
);

CREATE TABLE Clubs (
    id BIGSERIAL PRIMARY KEY,
    name_club VARCHAR(50) NOT NULL,
    address VARCHAR(100),
    tournament_place BOOLEAN,
    training_place BOOLEAN
);

CREATE TABLE Training_Schedule (
    id BIGSERIAL PRIMARY KEY,
    id_club BIGINT REFERENCES Clubs(id) ON DELETE CASCADE,
    date DATE,
    time_start TIME,
    time_end TIME,
    id_team BIGINT REFERENCES Teams(id) ON DELETE CASCADE
);

CREATE TABLE Tournaments (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    id_team_red BIGINT REFERENCES Teams(id) ON DELETE CASCADE,
    id_team_blue BIGINT REFERENCES Teams(id) ON DELETE CASCADE,
    id_club BIGINT REFERENCES Clubs(id) ON DELETE CASCADE,
    date DATE
);

CREATE TABLE Winners (
    id BIGSERIAL PRIMARY KEY,
    id_team BIGINT REFERENCES Teams(id) ON DELETE CASCADE,
    id_tournament BIGINT REFERENCES Tournaments(id) ON DELETE CASCADE
);

CREATE OR REPLACE FUNCTION update_club_tournament_place()
RETURNS TRIGGER AS $$
BEGIN
    -- Обновляем значение tournament_place для клуба, выбранного в турнире
    UPDATE Clubs
    SET tournament_place = TRUE
    WHERE id = NEW.id_club;

    RETURN NEW; -- Возвращаем добавленную запись в таблицу Tournaments
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER after_tournament_insert
AFTER INSERT ON Tournaments
FOR EACH ROW
EXECUTE FUNCTION update_club_tournament_place();