from random import randint as rand
from work_with_db import *
import telebot
import os
import time
import config
import utils
import json
import ast


bot = telebot.TeleBot(config.token)


@bot.message_handler(commands=['game'])
def game(message):
    db = MySQLer(config.db_config)
    rows = db.join_select_all()

    # выбираем в качестве правильного ответа
    # рандомную строку из бд (file_id, song_name)
    i = rand(0, db.rows_count('files')-1)
    right_answer = rows[i]

    # выбираем 3 рандомных неправильных ответа
    wrong_answers = []
    indexes = [i]
    while len(wrong_answers) != 3:
        j = rand(0, db.rows_count('files')-1)
        if j not in indexes:
            wrong_answers.append(rows[j][0])
            indexes.append(j)

    print(right_answer, wrong_answers)

    # сохраняем правильный ответ
    # для текущего юзера
    utils.set_user_game(message.chat.id, right_answer[0])
    # генерируем клавиатуру
    markup = utils.generate_markup([right_answer[0]] + wrong_answers)

    bot.send_voice(message.chat.id, right_answer[1], reply_markup=markup)

    db.close_connection()

# выводим кол-во отгаданных к общему кол-ву треков
@bot.message_handler(commands=['getmyscore'])
def get_user_score(message):
    db = MySQLer(config.db_config)
    score = db.get_user_score(message.chat.id)

    username = message.chat.first_name

    bot.send_message(message.chat.id,
                     '%s, your game score(guessed/listen): %s / %s'
                     % (message.chat.first_name, score[0], score[1]))

    db.close_connection()



# для добавления новых песен
@bot.message_handler(commands=['addnewsongs'])
def find_file_ids(message):
    """ Функция отсылает на сервер telegram новые трек,
        добавленные в папку. Затем вносит в базу название песни
        и полученный file_id
    """
    db = MySQLer(config.db_config)
    rows = db.single_table_select_all('songs', 'song_name')
    for file in os.listdir('C:/projects/tst_bot/music'):
        # выбираем все .ogg файл, которых нет в бд
        song_name = file[:-4]
        if file.split('.')[-1] == 'ogg' and song_name not in rows:
            f = open('music/' + file, 'rb')
            res = bot.send_voice(message.chat.id, f, None)
            # приводим JSON к dict
            parsed_string = ast.literal_eval(str(res))
            # получаем id новой записи таблицы files
            new_id = db.insert_data('files', 1, 0, parsed_string["voice"]["file_id"])
            # вставляем название песни в таблицу songs
            db.insert_data('songs', 1, new_id, song_name)
            print(song_name, res)
        time.sleep(1)
    db.close_connection()


@bot.message_handler(func=lambda message: True, content_types=['text'])
def check_answer(message):
    flag = 0
    db = MySQLer(config.db_config)
    user_exists = db.select_one_rec('users', 'WHERE chat_id = %s' % message.chat.id)

    # если в базу текущий польльзователь еще не внесен
    if not user_exists:
        # вносим chat_id в таблицу users
        user_id = db.insert_data('users', 1, 0, message.chat.id)
    else:
        # получаем user_id
        user_id = user_exists[0]

    # считываем правильный ответ
    answer = utils.get_answer_for_user(message.chat.id)

    # если игрок в игре
    if answer:
        keyboard_hider = telebot.types.ReplyKeyboardRemove()
        # получаем id песни по названию
        song_id = db.select_one_rec('songs', 'WHERE song_name = "%s"' % answer)[0]
        track_status = db.select_one_rec('played_tracks',
                                         'WHERE song_id = %s AND user_id = %s' % (song_id, user_id))

        try:
            # слушал до этого и угадал
            if track_status[2] == 1:
                flag = 1
                pass
            # слушал до этого и не угадал и не угадал сейчас
            elif track_status[2] == 0 and message.text != answer:
                pass
            # слушал до этого и не угадал, но угадал сейчас
            elif track_status[2] == 0 and message.text == answer:
                db.update_played_tracks(user_id, song_id, 1)
                flag = 1
        except TypeError:
            # не слушал до этого, но угадал сейчас
            if message.text == answer:
                db.insert_data('played_tracks', 0, song_id, user_id, 1)
                flag = 1
            # не слушал до этого, и не угадал сейчас
            else:
                db.insert_data('played_tracks', 0, song_id, user_id, 0)

        if flag == 1:
            bot.send_message(message.chat.id, 'Верно!', reply_markup=keyboard_hider)
            bot.send_message(message.chat.id, 'Сыграйте еще раз :) /game', reply_markup=keyboard_hider)
        else:
            bot.send_message(message.chat.id,
                             'Эх... Вы не угадали. Попробуйте еще раз! /game',
                             reply_markup=keyboard_hider)

        utils.finish_user_game(message.chat.id)
    else:
        bot.send_message(message.chat.id, 'Чтобы начать игру, введите команду /game')


if __name__ == '__main__':
   bot.polling(none_stop=True)