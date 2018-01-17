import telebot
from telebot import types
from pymongo import MongoClient
import datetime
from flask import Flask, request
from flask_sslify import SSLify
import os
from mongodb_api import update_booking, update_log, register_user
from telegramcalendar import create_calendar
import mongodb_api

#подключаемся к монго
client = MongoClient(os.environ["MONGODB_URL"], username = os.environ["MONGODB_USERNAME"], password = os.environ["MONGODB_PASSWORD"], authSource = os.environ["MONGODB_AUTHSOURCE"])
db = client[os.environ["MONGODB_AUTHSOURCE"]]
bookings_coll = db.bookings
office_coll = db.office_links
log_coll = db.log


no_keyboard = types.ReplyKeyboardRemove()

bot = telebot.TeleBot(os.environ["TOKEN"])
server = Flask(__name__)
sslify=SSLify(server)

#handling start or help command
@bot.message_handler(commands=['start','help'])
def start_command(message: telebot.types.Message):

    startText = "Привет! Я - бот таблицы ! \n Выбери интересующий тебя вопрос из меню ниже "
    bot.send_message(message.chat.id, startText)
    commands = ["Офис", "Коворкинг", "Мероприятие", "Перезвони мне"]

    markup = types.ReplyKeyboardMarkup(row_width=2,resize_keyboard=True)

    markup.row(commands[0],commands[1])
    markup.row(commands[2], commands[3])

    bot.send_message(message.chat.id, "Так о чем же тебе рассказать ?",
                     reply_markup=markup)

    #Регистрируем юзера
    register_user(message)

# Обрабатываем кнопку офис
@bot.message_handler(func = lambda message: message.text is not None and message.text == "Офис")
def  office(message: telebot.types.Message):
    reply_markup = types.ForceReply()
    bot.send_message(chat_id=message.chat.id, text="количество сотрудников:", reply_markup=reply_markup)


# Обрабатываем ответ о кол-ве людей в офисе
@bot.message_handler(func = lambda message: message.reply_to_message is not None and message.reply_to_message.text == "количество сотрудников:")
def  office_options(message: telebot.types.Message):

    # убедимся что нам дали число сотрудников. Если там текст то заставим повторить и запустим функцию заново
    try:
        number_of_empl = int(message.text)
    except ValueError:
        number_of_empl = message.text
        bot.send_message(chat_id=message.chat.id, text="что-то не так, введи, пожалуйста, ЧИСЛО сотрудников")
        reply_markup = types.ForceReply()
        bot.send_message(chat_id=message.chat.id, text="количество сотрудников:", reply_markup=reply_markup)
        return None

    if number_of_empl < 4:

        markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
        buttons_office_or_cowork = ["Офис на четверых", "Коворкинг"]
        markup.row(buttons_office_or_cowork[0], buttons_office_or_cowork [1])
        bot.send_message(chat_id=message.chat.id, text="у нас офисы от четырех человек, может вам лучше коворкинг?",reply_markup=markup)

#тут будет говнокод, надо будет нормально написать. Показываем ссылки на офисы


    if number_of_empl >= 4 and number_of_empl <= 23:

        office_url_record = office_coll.find_one({"size": number_of_empl})
        office_url = office_url_record["url"]


        markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
        buttons_office_book = ["Хочу этот офис!", "В главное меню"]
        markup.row(buttons_office_book[0], buttons_office_book[1])

        bot.send_message(chat_id=message.chat.id, text="вот что у нас есть")
        bot.send_message(chat_id=message.chat.id, text=office_url, reply_markup=markup)
        # апдейтим состояние клиента в монго
        update_booking(chat_id=message.chat.id, product="office", people=number_of_empl)

    if number_of_empl > 23:

        reply_markup = types.ForceReply()
        bot.send_message(chat_id=message.chat.id, text="у нас готовые решения до 23 человек, но мы можем больше! оставь нам свой телефон и мы перезвоним")
        bot.send_message(chat_id=message.chat.id, text="мой телефон:", reply_markup=reply_markup)
        # апдейтим состояние клиента в монго
        update_booking(chat_id=message.chat.id, product="office", people=number_of_empl)

#  обрабатываем кнопку Хочу этот офис!

@bot.message_handler(func = lambda message: message.text is not None and message.text == "Хочу этот офис!")
def book_office(message: telebot.types.Message):
    reply_markup = types.ForceReply()
    bot.send_message(chat_id=message.chat.id, text="оставь нам свой телефон и мы перезвоним")
    bot.send_message(chat_id=message.chat.id, text="мой телефон:", reply_markup=reply_markup)

#  обрабатываем кнопку Коворкинг
@bot.message_handler(func=lambda message: message.text is not None and message.text == "Коворкинг")
def coworking(message: telebot.types.Message):
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    buttons_cowork_book = ["Хочу в коворкинг!", "В главное меню"]
    markup.row(buttons_cowork_book[0], buttons_cowork_book[1])
    bot.send_message(chat_id=message.chat.id, text="У нас рабочее место от 500 рублей в день, хочешь забронировать ?", reply_markup=markup)


#  обрабатываем кнопку Хочу в коворкинг!

@bot.message_handler(func = lambda message: message.text is not None and message.text == "Хочу в коворкинг!")
def book_coworking(message: telebot.types.Message):
    reply_markup = types.ForceReply()
    bot.send_message(chat_id=message.chat.id, text="оставь нам свой телефон и мы перезвоним")
    bot.send_message(chat_id=message.chat.id, text="мой телефон:", reply_markup=reply_markup)

    #апдейтим состояние клиента в монго
    update_booking(chat_id=message.chat.id, product="coworking")


# Обрабатываем кнопку Мероприятие
@bot.message_handler(func = lambda message: message.text is not None and message.text == "Мероприятие")
def event(message: telebot.types.Message):
    reply_markup = types.ForceReply()
    bot.send_message(chat_id=message.chat.id, text="количество гостей:", reply_markup=reply_markup)
    update_booking(chat_id=message.chat.id, product="event")


# Обрабатываем ответ о кол-ве людей на Мероприятие
@bot.message_handler(func = lambda message: message.reply_to_message is not None and message.reply_to_message.text == "количество гостей:")
def event_size(message: telebot.types.Message):

    # убедимся что нам дали число сотрудников. Если там текст то заставим повторить и запустим функцию заново
    try:
        number_of_ppl = int(message.text)
    except ValueError:
        number_of_ppl = message.text
        bot.send_message(chat_id=message.chat.id, text="что-то не так, введи, пожалуйста, ЧИСЛО людей на мероприятии")
        reply_markup = types.ForceReply()
        bot.send_message(chat_id=message.chat.id, text="количество гостей:", reply_markup=reply_markup)
        return None

    get_calendar(message)

    update_booking(chat_id=message.chat.id, people=message.text)

# Обрабатываем ответ о продолжительности мероприятия
@bot.message_handler(func = lambda message: message.reply_to_message is not None and message.reply_to_message.text == "продолжительность мероприятия (в часах):")
def event_length(message: telebot.types.Message):

    # убедимся что нам дали число сотрудников. Если там текст то заставим повторить и запустим функцию заново
    try:
        number_of_hrs = int(message.text)
    except ValueError:
        number_of_hrs = message.text
        bot.send_message(chat_id=message.chat.id, text="что-то не так, введи, пожалуйста, продолжительность в часах")
        reply_markup = types.ForceReply()
        bot.send_message(chat_id=message.chat.id, text="продолжительность мероприятия (в часах):", reply_markup=reply_markup)
        return None


    update_booking(chat_id=message.chat.id, length=message.text)

    reply_markup = types.ForceReply()
    bot.send_message(chat_id=message.chat.id, text="Все получилось! Оставь нам свой телефон и мы перезвоним")
    bot.send_message(chat_id=message.chat.id, text="мой телефон:", reply_markup=reply_markup)




#  обрабатываем кнопку Перезвони мне!

@bot.message_handler(func = lambda message: message.text is not None and message.text == "Перезвони мне")
def  book_callback(message: telebot.types.Message):
    reply_markup = types.ForceReply()
    bot.send_message(chat_id=message.chat.id, text="оставь нам свой телефон и мы перезвоним")
    bot.send_message(chat_id=message.chat.id, text="мой телефон:", reply_markup=reply_markup)


# Обрабатываем ответ с номером телефона
@bot.message_handler(func = lambda message: message.reply_to_message is not None and message.reply_to_message.text == "мой телефон:")
def  get_contact(message: telebot.types.Message):

    # апдейтим контакт в монго
    update_booking(chat_id=message.chat.id, contact=message.text)


    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    buttons_final = ["В главное меню"]
    markup.row(buttons_final[0])


    bot.send_message(chat_id=message.chat.id, text="круто! мы перезвоним в ближайшее время !", reply_markup=markup)

#  обрабатываем кнопку В главное меню
@bot.message_handler(func=lambda message: message.text is not None and message.text == "В главное меню")
def main_menu(message: telebot.types.Message):
    commands = ["Офис", "Коворкинг", "Мероприятие", "Перезвони мне"]
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.row(commands[0], commands[1])
    markup.row(commands[2], commands[3])
    bot.send_message(message.chat.id, "Так о чем же тебе рассказать ?",
                     reply_markup=markup)

#календарь
current_shown_dates={}

def get_calendar(message):
    now = datetime.datetime.now() #Current date
    chat_id = message.chat.id
    date = (now.year,now.month)
    current_shown_dates[chat_id] = date #Saving the current date in a dict
    markup= create_calendar(now.year,now.month)
    bot.send_message(message.chat.id, "легко! Выбери дату твоего события", reply_markup=markup)


#функции передвижения по календарю
@bot.callback_query_handler(func=lambda call: call.data == 'next-month')
def next_month(call):
    chat_id = call.message.chat.id
    saved_date = current_shown_dates.get(chat_id)
    if(saved_date is not None):
        year,month = saved_date
        month+=1
        if month>12:
            month=1
            year+=1
        date = (year,month)
        current_shown_dates[chat_id] = date
        markup= create_calendar(year,month)
        bot.edit_message_text("легко! Выбери дату твоего события", call.from_user.id, call.message.message_id, reply_markup=markup)
        bot.answer_callback_query(call.id, text="")
    else:
        #Do something to inform of the error
        pass

@bot.callback_query_handler(func=lambda call: call.data == 'previous-month')
def previous_month(call):
    chat_id = call.message.chat.id
    saved_date = current_shown_dates.get(chat_id)
    if(saved_date is not None):
        year,month = saved_date
        month-=1
        if month<1:
            month=12
            year-=1
        date = (year,month)
        current_shown_dates[chat_id] = date
        markup= create_calendar(year,month)
        bot.edit_message_text("легко! Выбери дату твоего события", call.from_user.id, call.message.message_id, reply_markup=markup)
        bot.answer_callback_query(call.id, text="")
    else:
        #Do something to inform of the error
        pass

#процессим клик по календарю
@bot.callback_query_handler(func=lambda call: call.data[0:13] == 'calendar-day-')
def get_day(call):
    chat_id = call.message.chat.id
    saved_date = current_shown_dates.get(chat_id)
    if(saved_date is not None):
        day=call.data[13:]
        date = datetime.datetime(int(saved_date[0]),int(saved_date[1]),int(day),0,0,0)
        bot.send_message(chat_id, str(date))
        bot.answer_callback_query(call.id, text="")

    else:
        #Do something to inform of the error
        pass

    update_booking(chat_id=chat_id, date = date)

    reply_markup = types.ForceReply()
    bot.send_message(chat_id=call.message.chat.id, text="осталось чуть-чуть... сколько часов продлится мероприятие ? ")
    bot.send_message(chat_id=call.message.chat.id, text="продолжительность мероприятия (в часах):", reply_markup=reply_markup)


#handling free text message
@bot.message_handler()
def free_text(message: telebot.types.Message):

    answer = "Я пока ничего об этом не знаю, но ты точно найдешь желанное на нашем сайте! http://tablica.work/ "
    update_log(chat_id=message.chat.id, message=message)
    bot.send_message(message.chat.id, answer)


@server.route("/bot", methods=['POST','GET'])
def getMessage():
    if request.method == 'POST':
        bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
        return "!",200
    return '<h1>Hello bot</h1>'

@server.route("/")
def webhook():
     bot.remove_webhook()
     bot.set_webhook(url="https://tablicabot.herokuapp.com/bot")
     return "!", 200