import os
import sqlite3

class ORM:
    # list of the column names in the table, except for pk
    fields = []

    # name of the table in database
    table = "example"

    # name of the database
    database = os.path.join(os.path.dirname(__file__), 'termtrader.db')

    def __init__(self):
        """ initialize properties for each column in the table """
        self.pk = None

    def save(self):
        """ if a pk exists, update the row to the current values, if it does
        not insert a new row """
        if self.pk:
            self._update()
        else:
            self._insert()

    def _field_value_list(self):
        """ returns a tuple of the values of the columns in the same order as
        the field list """
        values = []
        for fieldname in self.fields:
            values.append(self.__dict__.get(fieldname))
        return tuple(values)

    def _insert(self):
        """ insert a new row into the database """
        with sqlite3.connect(self.database) as conn:
            cur = conn.cursor()
            SQLPATTERN = "INSERT INTO {tablename}({fieldnames}) VALUES({qmarks});"
            fieldnames = ", ".join(self.fields)
            qmarks = ", ".join(["?" for _ in self.fields])
            SQL = SQLPATTERN.format(
                tablename=self.table, fieldnames=fieldnames, qmarks=qmarks)

            values = self._field_value_list()

            cur.execute(SQL, values)
            """ cur.lastrowid = pk that was created in the most recent insert """
            self.pk = cur.lastrowid

    def _update(self):
        with sqlite3.connect(self.database) as conn:
            cur = conn.cursor()
            SQLPATTERN = "UPDATE {table} SET {pairs} WHERE pk = ?;"
            # fieldname=value, fieldname=value
            """ list comprehension generating field1=?, field2=?, field3=? etc. """
            pairstrings = [
                "{}=?".format(fieldname) for fieldname in self.fields
            ]
            pairs = ", ".join(pairstrings)
            SQL = SQLPATTERN.format(table=self.table, pairs=pairs)

            """ tuple with all field values as well as pk """
            values = (*self._field_value_list(), self.pk)
            
            cur.execute(SQL, values)

    def delete(self):
        """ remove the row corresponding to this object from the table """
        if not self.pk:
            raise ValueError("pk not set for delete operation")

        with sqlite3.connect(self.database) as conn:
            cur = conn.cursor()
            SQLPATTERN = "DELETE FROM {table} WHERE pk = ?;"
            SQL = SQLPATTERN.format(table=self.table)
            cur.execute(SQL, (self.pk, ))

    @classmethod
    def _from_row(cls, row):
        """ return a new instance of this class with properties set from a
        dictionary-like object (such as a sqlite3.Row object) """
        row = dict(row)
        new_obj = cls()
        for column in row:
            """ object.__dict__ contains all of its self.property values as
            a key: value dictionary """
            new_obj.__dict__[column] = row.get(column)
        return new_obj

    @classmethod
    def select_many(cls, where_clause="", values=tuple()):
        """ provide a WHERE clause to a SELECT statement and return objects
        representing each matched row """
        with sqlite3.connect(cls.database) as conn:
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            SQLPATTERN = "SELECT * FROM {table} {where_clause};"
            SQL = SQLPATTERN.format(table=cls.table, where_clause=where_clause)
            cur.execute(SQL, values)
            result = []
            for row in cur.fetchall():
                result.append(cls._from_row(row))
            return result

    @classmethod
    def select_one(cls, where_clause="", values=tuple()):
        """ provide a WHERE clause and return one object that corresponds to
        the row SELECTED or None if no results matched """
        with sqlite3.connect(cls.database) as conn:
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            SQLPATTERN = "SELECT * FROM {table} {where_clause}"
            SQL = SQLPATTERN.format(table=cls.table, where_clause=where_clause)
            cur.execute(SQL, values)
            row = cur.fetchone()

            if row is None:
                return None
            return cls._from_row(row)

    @classmethod
    def from_pk(cls, pk):
        """ grab the row with the given pk """
        return cls.select_one("WHERE pk = ?", (pk, ))

# INSERT INTO testtable(field1, field2) VALUES (?, ?);
# cur.execute(SQL, (self.field1, self.field2))

class Test(ORM):
    fields = ["field1", "field2"]
    table = "testtable"
    database = "example.db"

    def __init__(self):
        self.pk = None
        self.field1 = None
        self.field2 = None

if __name__ == "__main__":
    t = Test()
    t.field1 = "something"
    t.field2 = "silly"
    t.save()
    t.field2 = "different"
    t.save()

    objects = Test.select_many()
    for obj in objects:
        print("pk = ", obj.pk, obj.field1, obj.field2)
