from random import shuffle
from telebot import types
import config
import shelve


def generate_markup(answers):
    """ Создаем кастмную клавиатуру для выбора ответов"""
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)

    shuffle(answers)
    for answer in answers:
        markup.add(answer)

    return markup


def set_user_game(chat_id, right_answer):
    """ Записываем юзера в игроки и правильный ответ в текущей игре"""
    with shelve.open(config.shelve_name) as storage:
        storage[str(chat_id)] = right_answer


def finish_user_game(chat_id):
    """ Заканчиваем текущую игру и удаляем запись юзера"""
    with shelve.open(config.shelve_name) as storage:
        del storage[str(chat_id)]


def get_answer_for_user(chat_id):
    with shelve.open(config.shelve_name) as storage:
        try:
            answer = storage[str(chat_id)]
            return answer
        except (KeyError, EOFError):
            return None