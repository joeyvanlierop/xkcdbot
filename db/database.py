import os
import sqlite3
from sqlite3 import Error


blacklisted_table = "blacklisted"
statistics_table = "statistics"
create_blacklisted_table =  f"""
                            CREATE TABLE IF NOT EXISTS {blacklisted_table} (
                                username VARCHAR (40) PRIMARY KEY
                            );
                            """
create_statistics_table =   f"""
                            CREATE TABLE IF NOT EXISTS {statistics_table} (
                                id      VARCHAR  PRIMARY KEY,
                                count   INT      DEFAULT 1,
                                updated DATETIME DEFAULT (DATETIME('now'))
                            );
                            """


class Database():
    def __init__(self, database_name):
        if database_name == ":memory:":
            self.connection = self.__create_connection(":memory:")
        else:
            dirname = os.path.dirname(os.path.abspath(__file__))
            database_path = os.path.join(dirname, database_name)
            self.connection = self.__create_connection(database_path)

        self.cursor = self.connection.cursor()

        if self.connection:
            self.__create_table(create_blacklisted_table)
            self.__create_table(create_statistics_table)

    def __create_connection(self, database_path):
        """
        Returns a database connection object from the database at the given path

        :param database_path: The path to the database file
        :return:
        """
        connection = None

        try:
            connection = sqlite3.connect(database_path)
            return connection
        except Error as e:
            print(e)

    def __create_table(self, create_table_sql):
        """
        Create a table from the create_table_sql statement

        :param conn: Connection object
        :param create_table_sql: A CREATE TABLE statement
        :return:
        """
        try:
            self.cursor.execute(create_table_sql)
        except Error as e:
            print(e)

    def add_blacklist(self, username):
        """
        Adds a user to the blacklisted user database
        Will not add if the user is already present in the database
        """
        sql =   f"""
                INSERT INTO {blacklisted_table}
                    (username)
                VALUES
                    (?)
                """

        if not self.is_blacklisted(username):
            self.cursor.execute(sql, (username,))
            self.connection.commit()

    def is_blacklisted(self, username):
        """Returns true if the given username exists in the blacklisted user database"""
        sql =   f"""
                SELECT *
                FROM {blacklisted_table}
                WHERE username = ?
                """
        
        self.cursor.execute(sql, (username,))
        return self.cursor.fetchone() is not None

    def increment_id(self, id):
        """
        Increments the count of the given id by 1
        Updates the updated value to the current time

        Adds the given id if it does not exist
        """
        sql =   f"""
                INSERT INTO {statistics_table}
                    (id)
                VALUES
                    (?)
                ON CONFLICT(id) DO UPDATE SET
                    count = count + 1,
                    updated = DATETIME('now')
                """

        self.cursor.execute(sql, (id,))
        self.connection.commit()

    def get_id_statistics(self, id):
        """
        Returns statistics of the given id
        
        The first value is the amount of times the given id has been referenced
        The second value is the last time the the given id was been referenced
        """
        sql =   f"""
                SELECT count, updated
                FROM {statistics_table}
                WHERE id = ?
                """
        
        self.cursor.execute(sql, (id,))
        return self.cursor.fetchone()