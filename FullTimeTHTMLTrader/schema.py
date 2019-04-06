import os
import sqlite3

DBFILENAME = os.path.join(os.path.dirname(__file__), "app", 'termtrader.db')
# DBFILENAME = 'termtrader.db'

def create_db(dbfilename=DBFILENAME):
    with sqlite3.connect(dbfilename) as conn:
        cur = conn.cursor()

        SQL = """ DROP TABLE IF EXISTS accounts;"""
        cur.execute(SQL)

        SQL = """
        CREATE TABLE accounts (
            pk INTEGER PRIMARY KEY AUTOINCREMENT,
            username VARCHAR(255),
            password_hash VARCHAR(128),
            balance REAL,
            api_key INTEGER
        );
        """
        cur.execute(SQL)

        SQL = """ DROP TABLE IF EXISTS positions;"""
        cur.execute(SQL)

        SQL = """
        CREATE TABLE positions (
            pk INTEGER PRIMARY KEY AUTOINCREMENT,
            account_pk INTEGER, 
            ticker VARCHAR(10),
            shares INTEGER,
            FOREIGN KEY(account_pk) REFERENCES account(pk)
        );
        """
        cur.execute(SQL)

        SQL = """ DROP TABLE IF EXISTS trades;"""
        cur.execute(SQL)

        SQL = """
        CREATE TABLE trades (
            pk INTEGER PRIMARY KEY AUTOINCREMENT,
            account_pk INTEGER, 
            ticker VARCHAR(10),
            volume INTEGER,
            price REAL,
            time FLOAT,
            FOREIGN KEY(account_pk) REFERENCES account(pk)
        );
        """
        cur.execute(SQL)


if __name__ == "__main__":
    create_db(DBFILENAME)
