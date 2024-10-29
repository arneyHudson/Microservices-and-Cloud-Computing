import sqlite3

class Schema:
    def __init__(self):
        self.conn = sqlite3.connect('sports.db')
        self.create_player_table()

    def __del__(self):
        self.conn.commit()
        self.conn.close()

    def create_player_table(self):
        query = """
        CREATE TABLE IF NOT EXISTS "Player" (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            team_id INTEGER,
            position TEXT,
            avg REAL,
            home_runs INTEGER,
            ops_plus INTEGER,
            war REAL,
            owar REAL,
            dwar REAL,
            drs INTEGER
        );
        """
        self.conn.execute(query)
