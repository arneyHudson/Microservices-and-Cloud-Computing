import sqlite3

class PlayerModel:
    TABLENAME = "Player"

    def __init__(self):
        self.conn = sqlite3.connect('sports.db', check_same_thread=False)
        self.conn.row_factory = sqlite3.Row

    def __del__(self):
        self.conn.commit()
        self.conn.close()

    def create(self, params):
        query = f'''
            INSERT INTO {self.TABLENAME} 
            (name, team_id, position, avg, home_runs, ops_plus, war, owar, dwar, drs) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        '''
        values = (
            params.get("name"), 
            params.get("team_id"),
            params.get("position"), 
            params.get("avg"), 
            params.get("home_runs"),
            params.get("ops_plus"), 
            params.get("war"),
            params.get("owar"), 
            params.get("dwar"), 
            params.get("drs")
        )
        self.conn.execute(query, values)

    def list(self):
        query = f'SELECT * FROM {self.TABLENAME}'
        result_set = self.conn.execute(query).fetchall()
        return [dict(row) for row in result_set]

    def get_by_id(self, player_id):
        query = f'SELECT * FROM {self.TABLENAME} WHERE id = ?'
        result = self.conn.execute(query, (player_id,)).fetchone()
        return dict(result) if result else None
    
    def get_stats(self, player_id):
        # Pulling stats directly from the Player table
        query = 'SELECT avg, home_runs, ops_plus, war, owar, dwar, drs FROM Player WHERE id = ?'
        result = self.conn.execute(query, (player_id,)).fetchone()
        return dict(result) if result else {}
    
    def get_all(self):
        """Fetch all players from the database."""
        query = f'SELECT * FROM {self.TABLENAME}'
        result_set = self.conn.execute(query).fetchall()
        return [dict(row) for row in result_set]
    
    def update(self, params):
        query = f'''
            UPDATE {self.TABLENAME} 
            SET name = ?, home_runs = ?, ops_plus = ?, war = ?, owar = ?, dwar = ?, drs = ?
            WHERE id = ?
        '''
        values = (
            params.get("name"),
            params.get("home_runs"),
            params.get("ops_plus"),
            params.get("war"),
            params.get("owar"),
            params.get("dwar"),
            params.get("drs"),
            params.get("id")
        )
        self.conn.execute(query, values)

    def delete(self, player_id):
        """Delete a player by ID."""
        query = f'DELETE FROM {self.TABLENAME} WHERE id = ?'
        self.conn.execute(query, (player_id,))