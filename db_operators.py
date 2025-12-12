import sqlite3


def create_database():

    conn = sqlite3.connect('cities.db')
    cursor = conn.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS users_cities (
                        user_id INTEGER,
                        city_id INTEGER,
                        FOREIGN KEY(city_id) REFERENCES cities(city_id)
                    )""")
    cursor.execute("""CREATE TABLE IF NOT EXISTS cities (
                        city_id INTEGER PRIMARY KEY,
                        city_name TEXT,
                        sights TEXT,
                        UNIQUE(city_id)
                    )""")
    conn.commit()
    conn.close()

