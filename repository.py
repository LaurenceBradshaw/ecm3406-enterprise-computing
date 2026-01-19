import sqlite3

class Repository:
    def __init__(self,table):
        self.table = table 
        self.database = self.table + ".db" 
        self.make()
  
    def make(self):
        connection = sqlite3.connect(self.database)
        try:
            cursor = connection.cursor()
            cursor.execute(
                f"CREATE TABLE IF NOT EXISTS {self.table} " +
                "(id TEXT PRIMARY KEY, regx TEXT, sub TEXT)"
            )
            connection.commit()
        finally:
            connection.close()
  
    def clear(self):
        connection = sqlite3.connect(self.database)
        try:
            cursor = connection.cursor()
            cursor.execute(
                f"DELETE FROM {self.table}" 
            )
            connection.commit()
        finally:
            connection.close()

    def insert(self,js):
        connection = sqlite3.connect(self.database)
        try:
            cursor = connection.cursor()
            cursor.execute(
                f"INSERT INTO {self.table} (id,regx,sub) VALUES (?,?,?)",
                (js["id"],js["regx"],js["sub"])
            )
            connection.commit()
            return cursor.rowcount
        finally:
            connection.close()

    def update(self,js):
        connection = sqlite3.connect(self.database)
        try:
            cursor = connection.cursor()
            cursor.execute(
              f"UPDATE {self.table} SET regx=?, sub=? WHERE id=?",
              (js["regx"],js["sub"],js["id"])
            )
            connection.commit()
            return cursor.rowcount
        finally:
            connection.close()

    def lookup(self,id):
        connection = sqlite3.connect(self.database)
        try:
            cursor = connection.cursor()
            cursor.execute(
                f"SELECT id, regx, sub FROM {self.table} WHERE id=?",
                (id,)
            )
            row = cursor.fetchone()
            if row:
                return {"id":row[0],"regx":row[1],"sub":row[2]}
            else:
                return None
        finally:
            connection.close()

    def delete(self, id):
        connection = sqlite3.connect(self.database)
        try:
            cursor = connection.cursor()
            cursor.execute(
                f"DELETE FROM {self.table} WHERE id=?",
                (id,)
            )
            connection.commit()
            return cursor.rowcount > 0
        finally:
            connection.close()

    def get_ids(self):
        connection = sqlite3.connect(self.database)
        try:
            cursor = connection.cursor()
            cursor.execute(
                f"SELECT id FROM {self.table}"
            )
            rows = cursor.fetchall()
            return [row[0] for row in rows]
        finally:
            connection.close()