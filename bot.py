from random import randint as rand
from work_with_db import *
import telebot
import os
import time
import config
import utils


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


# для добавления новых песен
@bot.message_handler(commands=['test'])
def find_file_ids(message):
    db = MySQLer(config.db_config)
    rows = db.single_table_select_all('songs', 'song_name')
    for file in os.listdir('C:/projects/tst_bot/music'):
        # выбираем все .ogg файл,
        # которых нет в бд
        if file.split('.')[-1] == 'ogg' and file[:-4] not in rows:
            f = open('music/' + file, 'rb')
            res = bot.send_voice(message.chat.id, f, None)
            print(file, res)
        time.sleep(1)
    db.close_connection()


@bot.message_handler(func=lambda message: True, content_types=['text'])
def check_answer(message):
    answer = utils.get_answer_for_user(message.chat.id)

    if answer: # если игрок в игре
        keyboard_hider = telebot.types.ReplyKeyboardRemove()

        if message.text == answer:
            bot.send_message(message.chat.id, 'Верно!', reply_markup=keyboard_hider)
            bot.send_message(message.chat.id, 'Сыграйте еще раз :) /game', reply_markup=keyboard_hider)
        else:
            bot.send_message(message.chat.id, 'Эх... Вы не угадали. Попробуйте еще раз! /game', reply_markup=keyboard_hider)

        utils.finish_user_game(message.chat.id)
    else:
        bot.send_message(message.chat.id, 'Чтобы начать игру, введите команду /game')


if __name__ == '__main__':
   bot.polling(none_stop=True)