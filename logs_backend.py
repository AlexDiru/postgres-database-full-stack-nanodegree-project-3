#! /usr/bin/env python3
import psycopg2


class LogDatabase():
    """ Manage the connection to the database, closing and also the reporting.
        An easy-to-use class for an external user to use without worrying about
        the database

    """

    def __init__(self):
        """ Initialise the class with the database name

        """

        self.__DBNAME = 'news'

    def __connect(self):
        """ Connects to the database

        """
        try:
            self.__connection = psycopg2.connect(database=self.__DBNAME)
            self.__cursor = self.__connection.cursor()
        except:
            print("Failed to connect to database")

    def commit(self):
        """ This commits the connection

        """

        self.__connection.commit()

    def __close(self):
        """ This closes the cursor and the connection

        """

        self.__cursor.close()
        self.__connection.close()

    def __execute_query(self, query):
        self.__connect()
        self.__cursor.execute(query)

    def most_popular_articles(self):
        """ This function prints a text-based report of the most popular articles

        """

        # This query gets all of the articles listed by popularity
        # (highest popularity first)
        # It works by first looking at the URL in log i.e.:
        # /article/balloon-goons-doomed
        # The output needs to be text after the right most /
        # balloon-goons-doomed
        # Since split_part has a limit where you can't split starting
        # from the right hand side
        # The string is reversed, string split performed, then reversed back
        # This is stored in 'filename'
        # Then this is joined with the articles table on slug
        # Empty filenames are discard
        # Filenames are grouped then counted
        query = """WITH filenames AS (select reverse(split_part(reverse(path),'/',1))
                    AS filename FROM log)
                SELECT articles.title, COUNT(filename) FROM filenames
                JOIN articles ON articles.slug = filenames.filename
                WHERE filename <> ''
                GROUP BY articles.title
                ORDER BY count
                DESC
                LIMIT 3;"""

        self.__execute_query(query)

        # Iterate through the cursor
        print("Most Popular 3 Articles:")
        for (title, views) in self.__cursor:
            print("\"{}\" had {} views".format(title, views))

        self.__close()

    def most_popular_authors(self):
        """ This function prints a text-based report of the most popular authors

        """

        # This query works similar to finding the most popular articles
        # Except it joins the authors table as well and groups by the author
        # name rather than the article title
        query = """WITH filenames AS (select reverse(split_part(reverse(path),'/',1))
                AS filename FROM log)
                SELECT name, COUNT(filename) FROM filenames
                JOIN articles ON articles.slug = filenames.filename
                JOIN authors ON authors.id = articles.author
                WHERE filename <> ''
                GROUP BY name
                ORDER BY count
                DESC;"""

        self.__execute_query(query)

        # Iterate through the cursor
        print("Most Popular Authors:")
        for (name, views) in self.__cursor:
            print("{} had {} views".format(name, views))

        self.__close()

    def errored_requests(self):
        """ This function shows the dates which more than 1% of the requests were
            errors

        """

        # Counts the number of successes and errors for each day
        # Computes the ratio
        # Filters where the ratio is higher than 1 percent

        query = """WITH
                    noterrors AS
                        (SELECT time::date AS date, status, COUNT(status)
                         AS successcount FROM log
                         WHERE status = '200 OK'
                         GROUP BY time::date, status),
                    errors AS
                        (SELECT time::date AS date, status, COUNT(status)
                         AS errorcount FROM log
                         WHERE status <> '200 OK' GROUP BY time::date, status)
                SELECT noterrors.date,
                       errorcount::float/(successcount+errorcount)
                AS ratio
                FROM noterrors JOIN errors ON errors.date = noterrors.date
                WHERE errorcount::float/(successcount+errorcount) > 0.01;"""

        self.__execute_query(query)

        # Iterate through cursor
        print("Days which had errors > 1%:")
        for (date, ratio) in self.__cursor:
            print("{}: Error Ratio of {}%".format(date, ratio*100))

        self.__close()

# Don't run the following code if this file is imported
if __name__ == "__main__":
    logdb = LogDatabase()

    # Reports
    logdb.most_popular_articles()
    logdb.most_popular_authors()
    logdb.errored_requests()
