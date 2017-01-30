import config
import mysql.connector as mysqldb


class MySQLer:
    def __init__(self, database):
        self.connection = mysqldb.connect(**database)
        self.cursor = self.connection.cursor()

    def select_one_rec(self, tablename, condition):
        """ Выборка одной записи из опр таблицы
            condition - строка вида: WHERE ...
        """
        query = 'SELECT * FROM %s %s' % (tablename, condition)

        self.cursor.execute(query)
        res = self.cursor.fetchall()

        return res[0] if res else None

    def single_table_select_all(self, tablename, columnname):
        """ Выборка всех записей из опр таблицы """
        query = 'SELECT %s FROM %s' % (columnname, tablename)

        self.cursor.execute(query)
        res = self.cursor.fetchall()

        return [x[0] for x in res]

    def join_select_all(self):
        """ Выборка всех записей из двух таблиц (соединение).
            Из таблиц files и songs
        """
        query = ('SELECT s.song_name, f.file_id FROM songs AS s '
                 'INNER JOIN files AS f '
                 'ON f.id = s.song_id;'
        )

        self.cursor.execute(query)
        res = self.cursor.fetchall()

        return res

    def insert_data(self, tablename, return_id, *data):
        """ Вставка данных в опр таблицу.
            Передаем значения в правильном порядке.
            Если return_id = 1:
                то ф-я вернет индекс добавленной записи
        """
        query = 'INSERT INTO %s VALUES(%s)' % (tablename, str(data)[1:-1])

        self.cursor.execute(query)
        self.connection.commit()

        if return_id == 1:
            query = 'SELECT LAST_INSERT_ID();'
            self.cursor.execute(query)
            res = self.cursor.fetchall()

            return res[0][0]

    def update_played_tracks(self, user_id, song_id, new_value):
        query = 'UPDATE played_tracks ' \
                'SET is_guessed = %s ' \
                'WHERE user_id = %s AND song_id = %s;' \
                % (new_value, user_id, song_id)

        self.cursor.execute(query)
        self.connection.commit()

    def rows_count(self, tablename):
        """ Количество записей в опр таблице """
        query = 'SELECT * FROM %s' % tablename

        self.cursor.execute(query)
        res = self.cursor.fetchall()

        return len(res)

    def get_user_score(self, chat_id):
        """ Получаем количество угаданных песен
            и общее количество прослушаных песен
            для конкретного пользователя.
        """

        # запрос возвращает все прослушанные и
        # ОТГАДАННЫЕ пользователем треки
        query1 = 'SELECT COUNT(pt.song_id) ' \
                 'FROM played_tracks AS pt ' \
                 'WHERE pt.user_id = (SELECT user_id FROM users ' \
                 'WHERE chat_id = "%s") ' \
                 'AND pt.is_guessed = 1;' % chat_id

        # запрос возвращает все прослушанные
        # пользователем треки
        query2 = 'SELECT COUNT(*) FROM played_tracks AS pt '\
                 'WHERE pt.user_id = (SELECT user_id FROM users WHERE chat_id = "322530729");'

        self.cursor.execute(query1)
        guessed = self.cursor.fetchall()

        self.cursor.execute(query2)
        played = self.cursor.fetchall()

        return (guessed[0][0], played[0][0])

    def close_connection(self):
        self.connection.close()


if __name__ == '__main__':
    X = MySQLer(config.db_config)
    print('single_table_select_all |',
          X.single_table_select_all('files', 'file_id'))

    print('join_select_all |',
          X.join_select_all())

    print('rows_count |',
          X.rows_count('files'))

    print('select_one_rec |',
          X.select_one_rec('songs', 'WHERE song_id = 13'))

    print('get_user_score |',
          X.get_user_score('322530729'))

    print(X.select_one_rec('played_tracks',
                           'WHERE song_id = %s AND user_id = %s' \
                           % (43, 35)))

    # print('insert_data |',
    #       X.insert_data('users', 1, 0, '98656771'))