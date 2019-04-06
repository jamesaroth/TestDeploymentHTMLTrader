import sqlite3

with sqlite3.connect("example.db") as conn:
    cur = conn.cursor()
    SQL = "DROP TABLE IF EXISTS testtable;"
    cur.execute(SQL)
    SQL = """ CREATE TABLE testtable (
        pk INTEGER PRIMARY KEY AUTOINCREMENT,
        field1 VARCHAR(128),
        field2 VARCHAR(128)); """
    cur.execute(SQL)
