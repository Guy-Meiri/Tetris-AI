import sqlite3
import os
import sys
from os.path import dirname
from datetime import datetime
sys.path.append(r'C:\Users\Guy\Desktop\CS\AI-workshop\tetris-java')

class DB:
    __instance = None

    @staticmethod
    def clearDB(location="agentResults.db"):
        if DB.__instance != None:
            DB.__instance.connection.close()
            DB.__instance = None
        full_location = os.path.join(os.getenv('APPDATA'), location)
        print(full_location)
        os.remove(full_location)

    @staticmethod
    def get_instance(location="agentResults.db"):
        if DB.__instance == None:
            full_location = os.path.join(os.getenv('APPDATA'), location)
            DB.__instance = DB(full_location)
        return DB.__instance

    def __init__(self, db_location):
        self.connection = sqlite3.connect(db_location)

    def saveGameToDataBase(self, agent_name, score, time_played, level, game_date):
        c = self.connection.cursor()
    
        # TODO: add if database file does not exist then crate it!
        createTableScript = """
         CREATE TABLE IF NOT EXISTS tetris_games(
            game_id integer primary key AUTOINCREMENT,
            agent_name text,
            score integer,
            time_played integer,
            level integer,
            game_date datetime
        )"""
    
        #now = datetime.now()  #(now - game_param_extractor.game_start_time).seconds
        c.executescript(createTableScript)
        c.execute("""INSERT INTO tetris_games(agent_name, score, time_played, level, game_date)
             VALUES(?, ?, ?, ?, ?)""", (agent_name, score, time_played, level, game_date))
        self.connection.commit()
        #insertScript = f"INSERT INTO tetris_games(agent_name, score, time_played, game_date) VALUES('{agent_name}', {score}, {(now - game_param_extractor.game_start_time).seconds}, '{now}')"
        #print(insertScript)
        #c.executescript(insertScript)
        #c.execute("INSERT INTO tetris_games VALUES(:agent_name, :score, :time_played)", {'agent_name': "moshe", 'score': 43, 'time_played':100})
        #c.execute("SELECT * FROM tetris_games")
        # print("---------")
        #print(c.fetchall())
    
    def print_rows(self):
        c = self.connection.cursor()
        c.execute("SELECT * FROM tetris_games")
        print(c.fetchall())



if __name__ == "__main__":    
    #DB.clearDB()
    db = DB.get_instance()
    db.print_rows()
    #DB.clearDB()