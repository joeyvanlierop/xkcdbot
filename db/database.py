import os
import sqlite3
from sqlite3 import Error
from datetime import datetime
from contextlib import closing


blacklisted_table = "blacklisted"
statistics_table = "statistics"
create_blacklisted_table = f"""
                            CREATE TABLE IF NOT EXISTS {blacklisted_table} (
                                username VARCHAR (40) NOT NULL PRIMARY KEY
                            );
                            """
create_statistics_table = f"""
                            CREATE TABLE IF NOT EXISTS {statistics_table} (
                                id         INTEGER      PRIMARY KEY,
                                comment_id VARCHAR (10) NOT NULL,
                                comic_id   VARCHAR      NOT NULL,
                                date       DATETIME     DEFAULT (DATETIME('now'))
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
        with closing(self.connection.cursor()) as cursor:
            try:
                cursor.execute(create_table_sql)
            except Error as e:
                print(e)

    def add_blacklist(self, username):
        """
        Adds a user to the blacklisted user database
        Will not add if the user is already present in the database
        """
        sql = f"""
                INSERT INTO {blacklisted_table}
                    (username)
                VALUES
                    (?)
                """

        if not self.is_blacklisted(username):
            with closing(self.connection.cursor()) as cursor:
                cursor.execute(sql, (username,))
                self.connection.commit()

    def is_blacklisted(self, username):
        """Returns true if the given username exists in the blacklisted user database"""
        sql = f"""
                SELECT *
                FROM {blacklisted_table}
                WHERE username = ?
                """

        with closing(self.connection.cursor()) as cursor:
            cursor.execute(sql, (username,))
            return cursor.fetchone() is not None

    def add_id(self, comment_id, comic_id):
        """
        Adds the given id to the table with the given datetime
        If no datetime is given, the current datetime (in UTC) is used

        :param comment_id: The id of the comment to add
        :param comment_id: The id of the comic to add
        :param comment_id: The datetime of the comment to add - Temporarily removed
        """
        # if not date:
        #     date = datetime.utcnow()
        # date.strftime('%Y-%m-%d %H:%M:%S')
        sql = f"""
                INSERT INTO {statistics_table}
                    (comment_id, comic_id)
                VALUES
                    (?, ?)
                """
        
        with closing(self.connection.cursor()) as cursor:
            cursor.execute(sql, (comment_id, comic_id))
            self.connection.commit()

    def total_reference_count(self):
        """
        Returns the total amount of comics that have been referenced
        """
        sql = f"""
                SELECT COUNT(*)
                FROM {statistics_table}
                """

        with closing(self.connection.cursor()) as cursor:
            cursor.execute(sql)
            return cursor.fetchone()[0]

    def comic_id_count(self, comic_id):
        """
        Returns the total amount of times the given id has been referenced
        """
        sql = f"""
                SELECT COUNT(*)
                FROM {statistics_table}
                WHERE comic_id = ?
                """

        with closing(self.connection.cursor()) as cursor:
            cursor.execute(sql, (comic_id,))
            return cursor.fetchone()[0]
