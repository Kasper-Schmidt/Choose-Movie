import sqlite3

DATABASE_NAME = "film_roulette.db"

def get_connection():
    connection = sqlite3.connect(DATABASE_NAME)
    connection.row_factory = sqlite3.Row
    return connection

def create_database():
    connection = get_connection()

    connection.execute("""
        CREATE TABLE IF NOT EXISTS saved_movies (
            tmdb_id INTEGER PRIMARY KEY,
            title TEXT NOT NULL,
            release_date TEXT,
            vote_average REAL,
            status TEXT NOT NULL CHECK(status IN ('watch_later', 'watched')),
            added_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    connection.commit()
    connection.close()


def save_movie(movie, status):
    connection = get_connection()

    connection.execute("""
        INSERT INTO saved_movies (
            tmdb_id,
            title,
            release_date,
            vote_average,
            status
            )     
            VALUES (?, ?, ?, ?, ?, ?)

        ON CONFLICT(tmdb_id) DO UPDATE SET
            title = excluded.title,
            release_date = excluded.release_date,
            vote_average = excluded.vote_average,
            status = excluded.status,
            added_at = CURRENT_TIMESTAMP                  
        """, (
                movie["id"],
                movie["title"],
                movie.get("release_date"),
                movie.get("vote_average"),
                status,
            ))
        
    connection.commit()
    connection.close()
