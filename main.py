import streamlit as st
import psycopg2
import re
import hashlib
import pandas as pd
import datetime
import os
import subprocess

DB_CONFIG = {
    "host": "localhost",
    "database": "postgre",
    "user": "postgre",
    "password": "postgre",
    "port": "5432",
}


# docker run --name kp-container -e POSTGRES_USER=postgre -e POSTGRES_PASSWORD=postgre -e POSTGRES_DB=postgre -p 5432:5432 -d postgres

# Подключение к БД
def get_connection():
    try:
        # conn = psycopg2.connect(**DB_CONFIG)
        # return conn

        return psycopg2.connect(
            dbname=os.getenv("POSTGRES_DB", "postgre"),
            user=os.getenv("POSTGRES_USER", "postgre"),
            password=os.getenv("POSTGRES_PASSWORD", "postgre"),
            host=os.getenv("POSTGRES_HOST", "db"),
            port=os.getenv("POSTGRES_PORT", "5432")
        )
    except Exception as e:
        st.error(f"Ошибка подключения к базе данных: {e}")
        return None


# Функция для выполнения SQL-запросов
def fetch_data(query, params=None):
    conn = get_connection()
    if conn is None:
        return None
    cursor = conn.cursor()
    try:
        if query[:6] == "INSERT" or query[:6] == "UPDATE" or query[:6] == "DELETE":
            cursor.execute(query, params or ())
            conn.commit()  # Принудительное подтверждение транзакции
            return True  # Возвращаем True, если запрос прошел успешно

        else:
            cursor.execute(query, params or ())
            data = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            return data, columns

    except Exception as e:
        st.error(f"Ошибка выполнения запроса: {e}")
        return None, None
    finally:
        cursor.close()
        conn.close()


# Функция для хеширования пароля
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


# Проверка существования логина
def is_login_unique(login):
    conn = get_connection()
    if conn is None:
        return False
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT COUNT(*) FROM Users WHERE login = %s", (login,))
        count = cursor.fetchone()[0]
        return count == 0
    except Exception as e:
        st.error(f"Ошибка при проверке логина: {e}")
        return False
    finally:
        cursor.close()
        conn.close()


# Проверка номера телефона
def validate_phone_number(phone):
    pattern = r"^(\+7|8)\d{10}$"
    return re.match(pattern, phone)


# Проверка сложности пароля
def validate_password(password):
    if len(password) < 8:
        return "Пароль должен быть не менее 8 символов."
    if not re.search(r"[A-Z]", password):
        return "Пароль должен содержать хотя бы одну заглавную букву."
    if not re.search(r"[a-z]", password):
        return "Пароль должен содержать хотя бы одну строчную букву."
    if not re.search(r"\d", password):
        return "Пароль должен содержать хотя бы одну цифру."
    if not re.search(r"[!@#$%^&*_(),.?\":{}|<>]", password):
        return "Пароль должен содержать хотя бы один специальный символ (!@#$%^&* и т.д.)."
    return None


# Регистрация пользователя
def register_user(login, password, role, fio, phone, birth_date, experience=None):
    conn = get_connection()
    if conn is None:
        return
    cursor = conn.cursor()
    try:
        # Определяем роль пользователя
        password = hash_password(password)
        # Вставляем пользователя
        cursor.execute(
            "INSERT INTO Users (login, password, id_role) VALUES (%s, %s, %s) RETURNING id",
            (login, password, role)
        )
        user_id = cursor.fetchone()[0]

        # Вставляем дополнительные данные (например, телефон и дату рождения)
        if role == 1:
            cursor.execute(
                "INSERT INTO Trainers (fullname, phone_number, date_of_birth, experience, id_user) VALUES (%s, %s, %s, %s, %s)",
                (fio, phone, birth_date, experience, user_id)
            )
        elif role == 2:
            cursor.execute(
                "INSERT INTO Fighters (fullname, phone_number, date_of_birth, id_user) VALUES (%s, %s, %s, %s)",
                (fio, phone, birth_date, user_id)
            )


        conn.commit()
        st.success("Пользователь успешно зарегистрирован!")
    except Exception as e:
        st.error(f"Ошибка при регистрации пользователя: {e}")
    finally:
        cursor.close()
        conn.close()


# Авторизация пользователя
def enter_user(login, password):
    conn = get_connection()
    if conn is None:
        return None
    cursor = conn.cursor()
    try:
        password = hash_password(password)
        cursor.execute(
            "SELECT id, id_role FROM Users WHERE login = %s AND password = %s",
            (login, password)
        )
        user = cursor.fetchone()
        if user:
            st.session_state["user_id"] = user[0]
            st.session_state["user_role"] = "trainer" if user[1] == 1 else "fighter"
            st.session_state["user_login"] = login
            return True
        else:
            st.error("Неверный логин или пароль.")
            return False
    except Exception as e:
        st.error(f"Ошибка при входе: {e}")
        return False
    finally:
        cursor.close()
        conn.close()


# Окно регистрации
def window_register():
    st.title("Регистрация пользователей")

    fio = st.text_input("ФИО")
    phone = st.text_input("Введите номер телефона (формат: +7XXXXXXXXXX или 8XXXXXXXXXX)")
    birth_date = st.date_input("Дата рождения")
    login = st.text_input("Логин")
    # is_trainer = st.selectbox(["Я боец", "Я тренер", "Я организатор турниров"])
    role = {"Боец": 2, "Тренер": 1}
    role_select = st.selectbox("Я:", list(role.keys()))
    password = st.text_input("Пароль", type="password")
    password_2 = st.text_input("Повторите пароль", type="password")

    experience = None
    if role_select == "Тренер":
        experience = st.number_input("Стаж работы тренером (в годах)", min_value=0, step=1)

    if st.button("Зарегистрироваться"):
        # Проверки на заполнение полей
        if not fio or not phone or not login or not password or not password_2:
            st.error("Все поля должны быть заполнены.")
            return

        # Проверка уникальности логина
        if not is_login_unique(login):
            st.error("Пользователь с таким логином уже существует.")
            return

        # Проверка номера телефона
        if not validate_phone_number(phone):
            st.error("Некорректный номер телефона. Убедитесь, что формат правильный.")
            return

        # Проверка пароля
        password_error = validate_password(password)
        if password_error:
            st.error(password_error)
            return

        if password != password_2:
            st.error("Ваши пароли не совпадают")

        # Регистрация пользователя
        register_user(login, password, role[role_select], fio, phone, birth_date, experience)
        st.balloons()


# Окно авторизации пользователя
def window_authorization():
    st.title("Авторизация пользователей")

    login = st.text_input("Логин")
    password = st.text_input("Пароль", type="password")

    if st.button("Войти"):
        if login == "admin" and password == "admin":
            st.session_state["page"] = "admin"
            st.rerun()
        else:
            success = enter_user(login, password)
            if success:
                st.session_state["page"] = "dashboard"
                st.rerun()


def update_user_data(user_id, fullname, phone_number, date_of_birth, role):
    conn = get_connection()
    if conn is None:
        return False
    cursor = conn.cursor()
    try:
        cursor.execute(
            f"""
            UPDATE {role} 
            SET fullname = %s, phone_number = %s, date_of_birth = %s
            WHERE id_user = %s
            """,
            (fullname, phone_number, date_of_birth, user_id)
        )
        conn.commit()
        return True
    except Exception as e:
        st.error(f"Ошибка обновления данных: {e}")
        return False
    finally:
        cursor.close()
        conn.close()


# Страница "Профиль"
def profile_page(user_id, role):
    st.title("Профиль")
    query = f"""
        SELECT fullname, phone_number, date_of_birth 
        FROM {role}
        WHERE id_user = %s
    """
    data, _ = fetch_data(query, (user_id,))
    if data:
        fullname, phone_number, date_of_birth = data[0]
        fullname = st.text_input("ФИО", value=fullname)
        phone_number = st.text_input("Телефон", value=phone_number)
        date_of_birth = st.date_input("Дата рождения", value=date_of_birth)

        if st.button("Обновить"):
            if update_user_data(user_id, fullname, phone_number, date_of_birth, role):
                st.success("Данные успешно обновлены!")
    else:
        st.error("Не удалось загрузить данные профиля.")


# Страница "Команда" для бойца
def team_page(user_id):
    st.title("Команда и расписание")
    query = """
        SELECT id_team
        FROM Teams_Composition
        JOIN Fighters ON Teams_Composition.id_fighter = Fighters.id
        WHERE Fighters.id_user = %s
    """
    data, columns = fetch_data(query, (user_id,))
    if data:
        team_id = data[0][0]
        query1 = """Select name, id_trainer from Teams where id = %s"""
        data1, _ = fetch_data(query1, (team_id,))
        st.subheader(f"Вы в команде: {data1[0][0]}")

        query_trainer = "SELECT fullname, phone_number FROM Trainers WHERE id = %s"
        data_trainer, _ = fetch_data(query_trainer, (data1[0][1],))
        st.subheader(f"Ваш тренер: {data_trainer[0][0]}. {data_trainer[0][1]}")

        # Получение расписания тренировок
        query_schedule = """
                SELECT TS.date, TS.time_start, TS.time_end, C.name_club AS club_name
                FROM Training_Schedule TS
                JOIN Clubs C ON TS.id_club = C.id
                WHERE TS.id_team = %s
                ORDER BY TS.date, TS.time_start
            """
        schedule_data, schedule_columns = fetch_data(query_schedule, (team_id,))
        if schedule_data:
            st.write("Текущее расписание тренировок:")
            st.dataframe(
                pd.DataFrame(schedule_data, columns=["Дата", "Начало", "Конец", "Клуб"]),
                use_container_width=True, hide_index=True
            )
        else:
            st.write("Пока нет тренировок в расписании.")

    else:
        st.write("Вы пока не в команде")


def team_page_trainer(user_id):
    query3 = f"""SELECT id FROM Trainers WHERE id_user={user_id}"""
    data3, columns3 = fetch_data(query3)
    trainer_id = data3[0][0]

    query = """
        SELECT *
        FROM Teams
        WHERE id_trainer = %s
    """
    data, columns = fetch_data(query, (trainer_id,))
    if data:
        team_id = data[0][0]
        st.title(f"Команда: {data[0][1]}")  # Название команды

        query_team_members = """
            SELECT Fighters.id, Fighters.fullname, Fighters.phone_number, Fighters.date_of_birth 
            FROM Teams_Composition
            JOIN Fighters ON Teams_Composition.id_fighter = Fighters.id
            WHERE Teams_Composition.id_team = %s
        """
        members, _ = fetch_data(query_team_members, (team_id,))
        if members:
            st.write("Состав команды:")
            for member in members:
                st.write(f"- {member[1]} - {member[3]} ({member[2]}) ")

            # Выбор бойца для удаления
            member_options = {member[1]: member[0] for member in members}  # {Имя: ID}
            selected_member = st.selectbox("Удалить бойца из команды:", list(member_options.keys()))

            if st.button("Удалить бойца"):
                selected_member_id = member_options[selected_member]
                query_remove_fighter = "DELETE FROM Teams_Composition WHERE id_team = %s AND id_fighter = %s"
                if fetch_data(query_remove_fighter, (team_id, selected_member_id)):
                    st.success(f"Боец {selected_member} успешно удалён из команды!")
                    st.rerun()  # Обновляем страницу
                else:
                    st.error("Ошибка удаления бойца из команды.")
        else:
            st.write("Команда пока не имеет участников.")

        # Получаем список бойцов, которые не в командах
        query_available_fighters = """
            SELECT Fighters.id, Fighters.fullname 
            FROM Fighters
            WHERE Fighters.id NOT IN (
                SELECT id_fighter FROM Teams_Composition
            )
        """
        available_fighters, _ = fetch_data(query_available_fighters)

        if available_fighters:
            fighter_options = {fighter[1]: fighter[0] for fighter in available_fighters}  # {Имя: ID}
            selected_fighter = st.selectbox("Выберите бойца для добавления в команду:",
                                            list(fighter_options.keys()))

            if st.button("Добавить бойца"):
                selected_fighter_id = fighter_options[selected_fighter]
                query_add_fighter = "INSERT INTO Teams_Composition (id_team, id_fighter) VALUES (%s, %s)"
                if fetch_data(query_add_fighter, (team_id, selected_fighter_id)):
                    st.success(f"Боец {selected_fighter} успешно добавлен в команду!")
                    st.rerun()  # Обновляем страницу
                else:
                    st.error("Ошибка добавления бойца в команду.")
        else:
            st.write("Нет доступных бойцов для добавления.")
    else:
        st.write("У вас пока нет команды, но вы можете её создать!")
        naming = st.text_input("Название команды")
        if st.button("Создать команду"):
            query2 = """INSERT INTO Teams (name, id_trainer) VALUES (%s, %s)"""
            params = (naming, trainer_id)
            # Вызов функции для выполнения запроса
            if fetch_data(query2, params):
                st.success("Данные успешно обновлены!")
                st.rerun()
            else:
                st.error("Ошибка добавления команды")


def training_schedule_page(user_id):
    query3 = f"""SELECT id FROM Trainers WHERE id_user={user_id}"""
    data3, columns3 = fetch_data(query3)
    trainer_id = data3[0][0]

    # Получение команды тренера
    query_team = "SELECT id, name FROM Teams WHERE id_trainer = %s"
    data_team, _ = fetch_data(query_team, (trainer_id,))
    if not data_team:
        st.error("У вас нет команды. Создайте команду, чтобы управлять расписанием тренировок.")
        return

    team_id, team_name = data_team[0]
    st.title(f"Расписание тренировок для команды '{team_name}'")

    # Получение расписания тренировок
    query_schedule = """
        SELECT TS.id, TS.date, TS.time_start, TS.time_end, C.name_club AS club_name
        FROM Training_Schedule TS
        JOIN Clubs C ON TS.id_club = C.id
        WHERE TS.id_team = %s
        ORDER BY TS.date, TS.time_start
    """
    schedule_data, schedule_columns = fetch_data(query_schedule, (team_id,))
    if schedule_data:
        st.write("Текущее расписание тренировок:")
        st.dataframe(
            pd.DataFrame([row[1:] for row in schedule_data], columns=["Дата", "Начало", "Конец", "Клуб"]),
            use_container_width=True, hide_index=True
        )
    else:
        st.write("Пока нет тренировок в расписании.")

    # Добавление новой тренировки
    st.subheader("Добавить новую тренировку")
    club_query = "SELECT id, name_club FROM Clubs"
    clubs, _ = fetch_data(club_query)
    if clubs:
        club_options = {club[1]: club[0] for club in clubs}
        selected_club = st.selectbox("Выберите клуб", list(club_options.keys()))
        date = st.date_input("Дата тренировки")
        time_start = st.time_input("Время начала")
        time_end = st.time_input("Время окончания")

        if st.button("Добавить тренировку"):
            if time_start >= time_end:
                st.error("Время начала должно быть раньше времени окончания.")
            else:
                query_add_training = """INSERT INTO Training_Schedule (id_club, date, time_start, time_end, id_team)
                    VALUES (%s, %s, %s, %s, %s)
                """
                if fetch_data(query_add_training, (club_options[selected_club], date, time_start, time_end, team_id)):
                    st.success("Тренировка успешно добавлена!")
                    st.rerun()
                else:
                    st.error("Ошибка добавления тренировки.")

    # Редактирование расписания
    if schedule_data:
        st.subheader("Редактировать существующую тренировку")
        training_ids = {f"Тренировка: {row[1]} {row[2]}-{row[3]} ({row[4]})": row[0] for row in schedule_data}
        selected_training = st.selectbox("Выберите тренировку для редактирования", list(training_ids.keys()))
        training_id = training_ids[selected_training]

        new_club = st.selectbox("Изменить клуб", list(club_options.keys()),
                                index=0)
        new_date = st.date_input("Изменить дату", schedule_data[0][1])
        new_time_start = st.time_input("Изменить время начала", schedule_data[0][2])
        new_time_end = st.time_input("Изменить время окончания", schedule_data[0][3])

        if st.button("Сохранить изменения"):
            if new_time_start >= new_time_end:
                st.error("Время начала должно быть раньше времени окончания.")
            else:
                query_update_training = """UPDATE Training_Schedule
                    SET id_club = %s, date = %s, time_start = %s, time_end = %s
                    WHERE id = %s
                """
                if fetch_data(query_update_training,
                              (club_options[new_club], new_date, new_time_start, new_time_end, training_id)):
                    st.success("Изменения успешно сохранены!")
                    st.rerun()
                else:
                    st.error("Ошибка обновления тренировки.")
    # Удаление тренировки

    if schedule_data:
        st.subheader("Удалить тренировку")
        selected_training_delete = st.selectbox(
            "Выберите тренировку для удаления",
            list(training_ids.keys()),
            key="delete_training"
        )
        training_id_delete = training_ids[selected_training_delete]
        if st.button("Удалить тренировку"):
            query_delete_training = "DELETE FROM Training_Schedule WHERE id = %s"
            if fetch_data(query_delete_training, (training_id_delete,)):
                st.success("Тренировка успешно удалена!")
                st.rerun()
            else:
                st.error("Ошибка удаления тренировки.")


def tournaments_page():

    today = datetime.date.today()

    st.title("Турниры")
    st.subheader("Предстоящие турниры")

    # Получение предстоящих турниров
    query_upcoming = """
        SELECT T.name, T.date, CR.name AS red_team, CB.name AS blue_team, C.name_club AS club
        FROM Tournaments T
        JOIN Teams CR ON T.id_team_red = CR.id
        JOIN Teams CB ON T.id_team_blue = CB.id
        JOIN Clubs C ON T.id_club = C.id
        WHERE T.date >= %s
        ORDER BY T.date
    """
    upcoming_data, upcoming_columns = fetch_data(query_upcoming, (today,))
    if upcoming_data:
        upcoming_df = pd.DataFrame(
            upcoming_data, columns=["Название", "Дата", "Команда 1", "Команда 2", "Клуб"]
        )
        st.dataframe(upcoming_df, use_container_width=True, hide_index=True)
    else:
        st.write("Нет предстоящих турниров.")

    st.subheader("Прошедшие турниры")

    # Получение прошедших турниров
    query_past = """
        SELECT T.id, T.name, T.date, CR.name AS red_team, CB.name AS blue_team, C.name_club AS club, W.id_team AS winner_id
        FROM Tournaments T
        JOIN Teams CR ON T.id_team_red = CR.id
        JOIN Teams CB ON T.id_team_blue = CB.id
        JOIN Clubs C ON T.id_club = C.id
        LEFT JOIN Winners W ON T.id = W.id_tournament
        WHERE T.date < %s
        ORDER BY T.date DESC
    """
    past_data, past_columns = fetch_data(query_past, (today,))
    if past_data:
        # Получаем словарь сопоставления ID команд с их названиями
        query_teams = "SELECT id, name FROM Teams"
        teams_data, _ = fetch_data(query_teams)
        id_to_name = {team[0]: team[1] for team in teams_data}

        # Преобразуем данные прошедших турниров
        past_df = pd.DataFrame(
            past_data, columns=["ID", "Название", "Дата", "Команда 1", "Команда 2", "Клуб", "ID Победителя"]
        )

        # Сопоставляем ID победителя с его названием
        past_df["Победитель"] = past_df["ID Победителя"].apply(
            lambda team_id: f'🏆 {id_to_name.get(team_id, "Не определён")}')

        # Удаляем лишние технические колонки для отображения
        display_df = past_df.drop(columns=["ID Победителя", "ID"])
        st.dataframe(display_df, hide_index=True, use_container_width=True)

    else:
        st.write("Нет прошедших турниров.")


# Навигация для бойца
def fighter_dashboard():
    st.sidebar.title(f"Привет, боец, {st.session_state['user_login']}!")
    page = st.sidebar.radio("Навигация", ["Команда", "Турниры", "Профиль"])

    if st.button("Выйти из аккаунта"):
        st.session_state["user_id"] = None
        st.session_state["user_role"] = None
        st.session_state["user_login"] = None
        st.session_state["page"] = "login"
        st.rerun()
    if page == "Команда":
        team_page(st.session_state["user_id"])
    elif page == "Турниры":
        tournaments_page()
    elif page == "Профиль":
        profile_page(st.session_state["user_id"], 'Fighters')


# Навигация для тренера
def trainer_dashboard():
    st.sidebar.title(f"Здравствуй, тренер, {st.session_state['user_login']}!")
    page = st.sidebar.radio("Навигация", ["Команда", "Тренировки", "Турниры", "Профиль"])
    if st.button("Выйти из аккаунта"):
        st.session_state["user_id"] = None
        st.session_state["user_role"] = None
        st.session_state["user_login"] = None
        st.session_state["page"] = "login"
        st.rerun()
    if page == "Команда":
        team_page_trainer(st.session_state["user_id"])
    elif page == "Тренировки":
        training_schedule_page(st.session_state["user_id"])
    elif page == "Турниры":
        tournaments_page()
    elif page == "Профиль":
        profile_page(st.session_state["user_id"], 'Trainers')


# Функция отображения таблиц с возможностью редактирования и удаления
def edit_table(table_name):
    st.subheader(f"Таблица: {table_name}")

    # Отображение данных
    data_query = f"SELECT * FROM {table_name}"
    data, columns = fetch_data(data_query)

    if data:
        df = pd.DataFrame(data, columns=columns)
        st.dataframe(df, use_container_width=True)

        # Удаление записи
        with st.expander("Удалить запись"):
            record_id = st.number_input("Введите ID записи для удаления", min_value=1, step=1)
            if st.button("Удалить запись"):
                delete_query = f"DELETE FROM {table_name} WHERE id = %s"
                fetch_data(delete_query, (record_id,))
                st.success(f"Запись с ID {record_id} удалена из таблицы {table_name}")

        # Добавление новой записи
        with st.expander("Добавить запись"):
            new_record = {}
            for col in columns:
                if col != "id":
                    new_record[col] = st.text_input(f"{col}")
            if st.button("Добавить запись"):
                columns_str = ", ".join([col for col in new_record.keys()])
                placeholders = ", ".join(["%s"] * len(new_record))
                insert_query = f"INSERT INTO {table_name} ({columns_str}) VALUES ({placeholders})"
                fetch_data(insert_query, tuple(new_record.values()))
                st.success(f"Новая запись добавлена в таблицу {table_name}")

        # Редактирование записи
        with st.expander("Редактировать запись"):
            record_id = st.number_input("Введите ID записи для редактирования", min_value=1, step=1)
            updated_record = {}
            for col in columns:
                if col != "id":
                    updated_record[col] = st.text_input(f"Новое значение для {col}")
            if st.button("Сохранить изменения"):
                set_clause = ", ".join([f"{col} = %s" for col in updated_record.keys()])
                update_query = f"UPDATE {table_name} SET {set_clause} WHERE id = %s"
                fetch_data(update_query, tuple(updated_record.values()) + (record_id,))
                st.success(f"Запись с ID {record_id} обновлена в таблице {table_name}")
    else:
        st.warning(f"Таблица {table_name} пуста или не существует.")


# def backup_database():
#     st.subheader("Бэкап базы данных")
#
#     backup_dir = "backups"
#     os.makedirs(backup_dir, exist_ok=True)  # Создаем папку для бэкапов, если она не существует
#
#     backup_file = os.path.join(backup_dir, "backup_" + pd.Timestamp.now().strftime("%Y%m%d_%H%M%S") + ".sql")
#
#     db_name = "postgre"  # Замените на имя вашей базы данных
#     db_user = "postgre"  # Замените на имя пользователя базы данных
#     db_host = "localhost"  # Хост базы данных
#     db_password = "postgre"  # Пароль пользователя базы данных
#
#     # Выполняем pg_dump через subprocess
#     try:
#         os.environ["PGPASSWORD"] = db_password  # Устанавливаем пароль в переменную окружения
#         subprocess.run(
#             ["pg_dump.exe", "-U", db_user, "-h", db_host, "-F", "c", "-b", "-v", "-f", backup_file, db_name],
#             check=True
#         )
#         st.success(f"Бэкап успешно создан: {backup_file}")
#     except Exception as e:
#         st.error(f"Ошибка при создании бэкапа: {e}")
#     finally:
#         if "PGPASSWORD" in os.environ:
#             del os.environ["PGPASSWORD"]  # Удаляем переменную окружения для безопасности


def backup_database_via_docker():
    container_name = "fight_club"  # Название контейнера PostgreSQL
    db_user = "postgre"
    db_name = "postgre"
    backup_file = "backup.sql"

    try:
        subprocess.run(
            ["docker", "exec", container_name, "pg_dump", "-U", db_user, "-F", "c", "-b", "-v", "-f", f"/tmp/{backup_file}", db_name],
            check=True
        )
        # Копируем файл из контейнера на хост
        subprocess.run(
            ["docker", "cp", f"{container_name}:/tmp/{backup_file}", backup_file],
            check=True
        )
        print(f"Бэкап сохранён как {backup_file}")
    except Exception as e:
        print(f"Ошибка создания бэкапа: {e}")


def admin_panel():
    st.title("Панель администратора")
    st.write("Управляйте всеми данными из одной панели.")

    # Выбор таблицы
    tables = [
        "Roles", "Users", "Fighters", "Trainers", "Teams", "Teams_Composition", "Clubs",
        "Training_Schedule", "Tournaments", "Winners"
    ]
    selected_table = st.selectbox("Выберите таблицу для управления", tables)

    if selected_table:
        edit_table(selected_table)

    # Добавление функциональности бэкапа
    st.subheader("Бэкап базы данных")
    if st.button("Создать бэкап"):
        backup_database_via_docker()

    if st.button("Выйти из аккаунта"):
        st.session_state["page"] = "login"
        st.rerun()


# Главная логика приложения
def main():
    if "page" not in st.session_state:
        st.session_state["page"] = "login"  # По умолчанию авторизация

    if st.session_state["page"] == "dashboard":
        if "user_role" in st.session_state:
            if st.session_state["user_role"] == "fighter":
                fighter_dashboard()
            elif st.session_state["user_role"] == "trainer":
                trainer_dashboard()
        else:
            st.error("Ошибка: роль пользователя не определена.")
    elif st.session_state["page"] == "admin":
        admin_panel()
    else:
        st.title("БОКСЕРСКИЙ КЛУБ")
        st.sidebar.title("Навигация")
        page = st.sidebar.radio("Перейти к странице", ["Авторизация", "Регистрация"])
        if page == "Регистрация":
            window_register()
        elif page == "Авторизация":
            window_authorization()


if __name__ == "__main__":
    main()
