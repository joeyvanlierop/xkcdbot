import os
import logging
import sqlite3
from sqlite3 import Error
from datetime import datetime
from contextlib import closing


blacklisted_table = "blacklisted"
statistics_table = "statistics"
comic_titles_table = "comic_titles"

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
create_comic_titles_table = f"""
                            CREATE TABLE IF NOT EXISTS {comic_titles_table} (
                                title       VARCHAR     NOT NULL,
                                number      INTEGER     NOT NULL
                            );
                            """

logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


class Database():
    def __init__(self, database_name):
        if database_name == ":memory:":
            self.connection = self.__create_connection(":memory:")
        else:
            database_path = os.path.abspath(database_name)
            self.connection = self.__create_connection(database_path)

        if self.connection:
            self.__create_table(create_blacklisted_table)
            self.__create_table(create_statistics_table)
            self.__create_table(create_comic_titles_table)

    def __create_connection(self, database_path):
        """
        Returns a database connection object from the database at the given path

        :param database_path: The path to the database file
        :return:
        """
        connection = None

        try:
            logger.info(f"Opening database at: {database_path}")
            connection = sqlite3.connect(database_path)
            return connection
        except Error as e:
            logger.error(e)

    def __create_table(self, create_table_sql):
        """
        Create a table from the create_table_sql statement

        :param conn: Connection object
        :param create_table_sql: A CREATE TABLE statement
        :return:
        """
        with closing(self.connection.cursor()) as cursor:
            try:
                logger.info("Creating sql table")
                cursor.execute(create_table_sql)
            except Error as e:
                logger.log(e)

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
            logger.info(f"Adding {username} to blacklist")
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

        logger.info(f"Checking if {username} is blacklisted")
        with closing(self.connection.cursor()) as cursor:
            cursor.execute(sql, (username,))
            return cursor.fetchone() is not None

    def add_id(self, comment_id, comic_id):
        """
        Adds the given id to the table with the given datetime
        If no datetime is given, the current datetime (in UTC) is used

        :param comment_id: The id of the comment to add
        :param comic_id: The id of the comic to add
        :param date: The datetime of the comment to add - Temporarily removed
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
            logger.info(
                f"Adding comment {comment_id} with comic {comic_id} to database")
            cursor.execute(sql, (comment_id, comic_id))
            self.connection.commit()

    def comic_title_relations_count(self):
        """Returns the total count of comic titles stored in the database"""
        sql = f"""
                SELECT COUNT(*)
                FROM {comic_titles_table}
                """

        with closing(self.connection.cursor()) as cursor:
            logger.info(
                "Returning total count of comic titles stored in the database")
            cursor.execute(sql)
            return cursor.fetchone()[0]

    def add_comic_title(self, comic_title, comic_number):
        """Adds new entry <comic_title> : <comic_number> to the comic titles table."""
        sql = f"""
                INSERT INTO {comic_titles_table}
                    (title, number)
                VALUES
                    (?, ?)
                """

        with closing(self.connection.cursor()) as cursor:
            cursor.execute(sql, (comic_title, comic_number))
            self.connection.commit()

    def get_comic_number(self, comic_title):
        """Returns number (int) of comic with given title if it exists, otherwise returns None."""
        sql = f"""
                SELECT number
                FROM {comic_titles_table}
                WHERE title = ?
                """

        logger.info(
            f"Attempting to return number of comic with title: '{comic_title}'")
        with closing(self.connection.cursor()) as cursor:
            cursor.execute(sql, (comic_title,))

            res = cursor.fetchone()
            if res is not None:
                return res[0]

    def total_reference_count(self):
        """
        Returns the total amount of comics that have been referenced
        """
        sql = f"""
                SELECT COUNT(*)
                FROM {statistics_table}
                """

        with closing(self.connection.cursor()) as cursor:
            logger.info("Returning total count of all comic references")
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
            logger.info(f"Returning reference count of comic {comic_id}")
            cursor.execute(sql, (comic_id,))
            return cursor.fetchone()[0]
