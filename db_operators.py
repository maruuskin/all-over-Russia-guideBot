import sqlite3


# БД для хранения информации о пользователях и городах, про достопримечательности в которых он спрашивали
def create_database():
    conn = sqlite3.connect('cities.db')
    cursor = conn.cursor()

    cursor.execute("""CREATE TABLE IF NOT EXISTS users_cities (
                        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_name TEXT,
                        city_id INTEGER,
                        FOREIGN KEY(city_id) REFERENCES cities(city_id)
                    )""")

    cursor.execute("""CREATE TABLE IF NOT EXISTS cities (
                        city_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        city_name TEXT,
                        UNIQUE(city_id)
                    )""")

    cursor.execute("""CREATE TABLE IF NOT EXISTS sights (
                            sight_id INTEGER PRIMARY KEY AUTOINCREMENT,
                            sight_name TEXT, 
                            city_id INTEGER,
                            coords1 DOUBLE,
                            coords2 DOUBLE
                        )""")

    conn.commit()
    conn.close()


# Добавление информации в БД
def add_sights_to_db(name, city, sights_names, sights_coords):
    try:
        conn = sqlite3.connect('cities.db')
        cursor = conn.cursor()

        cursor.execute("SELECT city_id FROM cities WHERE city_name=?",
                       (city,))
        city_id = cursor.fetchone()

        if not city_id:
            cursor.execute("INSERT INTO cities (city_name) VALUES (?)",
                           (city.lower().capitalize(),))
            conn.commit()

            cursor.execute("SELECT city_id FROM cities WHERE city_name=?",
                           (city,))
            city_id = cursor.fetchone()

        cursor.execute("SELECT user_name FROM users_cities WHERE user_name=?", (name,))
        all_names = cursor.fetchall()

        if not all_names:
            cursor.execute("INSERT INTO users_cities (user_name, city_id) VALUES (?, ?)",
                           (name, city_id[0]))
            conn.commit()
        else:
            cursor.execute("UPDATE users_cities SET city_id=? WHERE user_name=?",
                           (city_id[0], name))
            conn.commit()

        for numb in range(len(sights_names)):
            cursor.execute("SELECT sight_id FROM sights WHERE sight_name=? AND city_id=? AND coords1=? AND coords2=?",
                           (sights_names[numb], city_id[0], sights_coords[numb][0], sights_coords[numb][1]))
            same_sights = cursor.fetchall()
            if not same_sights:
                cursor.execute("INSERT INTO sights (sight_name, city_id, coords1, coords2) VALUES (?, ?, ?, ?)",
                               (sights_names[numb], city_id[0], sights_coords[numb][0], sights_coords[numb][1]))
                conn.commit()

    except Exception as ex:
        print(ex)

