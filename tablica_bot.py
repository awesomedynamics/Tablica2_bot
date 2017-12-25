import telebot
from telebot import types

no_keyboard = types.ReplyKeyboardRemove()

bot = telebot.TeleBot("456403564:AAFLQjaNSumXGcd9hl_nEbCZyvIFdNmFCHk")

#



#handling start or help command
@bot.message_handler(commands=['start','help'])
def start_command(message: telebot.types.Message):


    #message_dict = message.__dict__
    startText = "Привет! Я - бот таблицы ! \n Выбери интересующий тебя вопрос из меню ниже "
    bot.send_message(message.chat.id, startText)
    commands = ["Офис", "Коворкинг", "Мероприятие", "Перезвони мне"]

    markup = types.ReplyKeyboardMarkup(row_width=2,resize_keyboard=True)

    markup.row(commands[0],commands[1])
    markup.row(commands[2], commands[3])

    bot.send_message(message.chat.id, "Так о чем же тебе рассказать ?",
                     reply_markup=markup)

# билет в черногорию
@bot.message_handler(regexp='Офис')
def  office(message: telebot.types.Message):
    answer = open("ticket.png","rb")
    answer_text = "это должен был быть сюрприз :)"
    bot.send_photo(chat_id=message.chat.id, photo=answer)
    bot.send_message(chat_id=message.chat.id, text = answer_text)

#спа отель
@bot.message_handler(regexp='Коворкинг)
def gift_2(message: telebot.types.Message):
    answer = open("spa.png","rb")
    bot.send_message(chat_id=message.chat.id, text="немножко СПА")
    bot.send_photo(chat_id = message.chat.id, photo = answer)

#колючий коврик
@bot.message_handler(regexp='Мероприятие')
def gift_3(message: telebot.types.Message):
    answer = open("kovplace.jpg","rb")
    bot.send_photo(chat_id = message.chat.id, photo = answer)

#черная икра
@bot.message_handler(regexp='Перезвони мне')
def gift_4(message: telebot.types.Message):
    answer = open("kovplace.jpg","rb")
    bot.send_message(chat_id=message.chat.id, text="а тут нужно будет поискать, вот подсказка:")
    bot.send_photo(chat_id = message.chat.id, photo = answer)


#handling free text message
@bot.message_handler()
def free_text(message: telebot.types.Message):

    answer = "Не еби мою нейросетку! Жми кнопки! "
    bot.send_message(message.chat.id, answer)


bot.polling()