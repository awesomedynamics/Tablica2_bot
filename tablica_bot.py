import telebot
from telebot import types

no_keyboard = types.ReplyKeyboardRemove()

bot = telebot.TeleBot("456403564:AAFLQjaNSumXGcd9hl_nEbCZyvIFdNmFCHk")

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

# Обрабатываем кнопку офис
@bot.message_handler(func = lambda message: message.text is not None and message.text == "Офис")
def  office(message: telebot.types.Message):
    reply_markup = types.ForceReply()
    bot.send_message(chat_id=message.chat.id, text="Number of people in office:", reply_markup=reply_markup)

# Обрабатываем ответ о кол-ве людей в офисе
@bot.message_handler(func = lambda message: message.reply_to_message is not None and message.reply_to_message.text == "Number of people in office:")
def  office(message: telebot.types.Message):

    # убедимся что нам дали число сотрудников. Если там текст то заставим повторить и запустим функцию заново
    try:
        number_of_empl = int(message.text)
    except ValueError:
        number_of_empl = message.text
        bot.send_message(chat_id=message.chat.id, text="что-то не так, введи, пожалуйста, ЧИСЛО сотрудников")
        reply_markup = types.ForceReply()
        bot.send_message(chat_id=message.chat.id, text="Number of people in office:", reply_markup=reply_markup)
        return None

    if number_of_empl < 4:

        markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
        buttons_office_or_cowork = ["Офис на четверых", "Коворкинг"]
        markup.row(buttons_office_or_cowork[0], buttons_office_or_cowork [1])
        bot.send_message(chat_id=message.chat.id, text="у нас офисы от четырех человек, может вам лучше коворкинг?",reply_markup=markup)

#тут будет говнокод, надо будет нормально написать. Показываем ссылки на офисы

    if number_of_empl == 4:
        markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
        buttons_office_book = ["Хочу этот офис!", "В главное меню"]
        markup.row(buttons_office_book[0], buttons_office_book[1])

        bot.send_message(chat_id=message.chat.id, text="вот что у нас есть на четверых")
        bot.send_message(chat_id=message.chat.id, text="http://tablica.work/#!/tproduct/34756154-1507644732627",reply_markup=markup)

    if number_of_empl == 5:
        markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
        buttons_office_book = ["Хочу этот офис!", "В главное меню"]
        markup.row(buttons_office_book[0], buttons_office_book[1])
        bot.send_message(chat_id=message.chat.id, text="вот что у нас есть на пятерых")
        bot.send_message(chat_id=message.chat.id, text="http://tablica.work/#!/tproduct/34756154-1498486301712",reply_markup=markup)


    if number_of_empl == 6:
        markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
        buttons_office_book = ["Хочу этот офис!", "В главное меню"]
        markup.row(buttons_office_book[0], buttons_office_book[1])
        bot.send_message(chat_id=message.chat.id, text="вот что у нас есть на шестерых")
        bot.send_message(chat_id=message.chat.id, text="http://tablica.work/#!/tproduct/34756154-1507644678469",reply_markup=markup)


    if number_of_empl > 6:
        bot.send_message(chat_id=message.chat.id, text="это еще не доделано")

#  обрабатываем кнопку Коворкинг
@bot.message_handler(func=lambda message: message.text is not None and message.text == "Коворкинг")
def coworking(message: telebot.types.Message):
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    buttons_cowork_book = ["Хочу в коворкинг!", "В главное меню"]
    markup.row(buttons_cowork_book[0], buttons_cowork_book[1])
    bot.send_message(chat_id=message.chat.id, text="У нас рабочее место от 500 рублей в день, хочешь забронировать ?", reply_markup=markup)

#  обрабатываем кнопку В главное меню
@bot.message_handler(func=lambda message: message.text is not None and message.text == "В главное меню")
def main_menu(message: telebot.types.Message):
    commands = ["Офис", "Коворкинг", "Мероприятие", "Перезвони мне"]
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.row(commands[0], commands[1])
    markup.row(commands[2], commands[3])
    bot.send_message(message.chat.id, "Так о чем же тебе рассказать ?",
                     reply_markup=markup)


#handling free text message
@bot.message_handler()
def free_text(message: telebot.types.Message):

    answer = "Не еби мою нейросетку! Жми кнопки! "
    bot.send_message(message.chat.id, answer)


bot.polling()