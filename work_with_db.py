import config
import mysql.connector as mysqldb


class MySQLer:
    def __init__(self, database):
        self.connection = mysqldb.connect(**database)
        self.cursor = self.connection.cursor()

    def single_table_select_all(self, tablename, columnname):
        """ Выборка всех записей из опр таблицы """
        query = 'SELECT %s FROM %s' % (columnname, tablename)

        self.cursor.execute(query)
        res = self.cursor.fetchall()

        return [x[0] for x in res]

    def join_select_all(self):
        """ Выборка всех записей из двух таблиц (соединение)"""
        query = ('SELECT s.song_name, f.file_id FROM songs AS s '
                 'INNER JOIN files AS f '
                 'ON f.id = s.song_id;'
        )

        self.cursor.execute(query)
        res = self.cursor.fetchall()

        return res

    def rows_count(self, tablename):
        """ Количество записей в опр таблице """
        query = 'SELECT * FROM %s' % tablename

        self.cursor.execute(query)
        res = self.cursor.fetchall()

        return len(res)

    def close_connection(self):
        self.connection.close()


if __name__ == '__main__':
    X = MySQLer(config.db_config)
    print(X.single_table_select_all('files'))
    print(X.single_table_select_all('songs'))
    print(X.join_select_all())
    print(X.rows_count('files'))
    print(X.rows_count('songs'))