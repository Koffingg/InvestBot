from main import Database
import telebot
from telebot import types
import matplotlib.pyplot as plt
import tinvest


# То что касается бота
TOKEN = "5259140715:AAGHkZ42Ty1UPd5ate3NUURr4MP3c_1o6MU"
bot = telebot.TeleBot(TOKEN)

counter_for_create_table = 1


@bot.message_handler(commands=['start'])
def start_bot(message):
    global counter_for_create_table
    db = Database('users.db')
    if counter_for_create_table == 1:
        db.create_table()
        counter_for_create_table += 1
    keyboards_start = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1_stock = types.KeyboardButton(text='Акции')
    btn2_etf = types.KeyboardButton(text='Фонды')
    btn3_currency = types.KeyboardButton(text='Валюты')
    keyboards_start.add(btn1_stock, btn2_etf, btn3_currency)
    bot.send_message(message.chat.id, f"Привет {message.from_user.first_name} \nДля того чтобы "
                                      f"начать отслеживать свои инвестиции, вам нужно будет передать свой токен.",
                     reply_markup=keyboards_start)
    help_user(message)


# Это функция, которая выводит как пользователю получить токен, то есть инструкция
@bot.message_handler(commands=['token'])
def help_user(message):
    keyboard_under_msg = types.InlineKeyboardMarkup()
    keyboard_under_msg.add(types.InlineKeyboardButton("Тинькофф токен",
                                                      url="https://www.tinkoff.ru/invest/"))
    msg = bot.send_message(message.chat.id, 'Необходимо:\n1) Авторизоваться на сайте Тинькофф Инвестиции\n2) Перейти в '
                                            'раздел "Настройки"\n3) Пролистать вниз до раздела "Токены Tinkoff Invest '
                                            'API" и нажать "Создать токен"\n4) В управлении токенами выбрать токен для '
                                            'всех счетов и поставить галочку в поле "Полный доступ" и нажать '
                                            '"Выпустить токен"\n5) Полученный токен скопировать и ввести в чат-бот',
                           reply_markup=keyboard_under_msg)
    bot.register_next_step_handler(msg, setter_token_users)


"""Тут функция, которая записывает пользователя в базу данных"""


def setter_token_users(message):
    db = Database('users.db')
    if message.text[:2] != 't.':
        bot.send_message(message.chat.id, 'Вы где-то ошиблись!\nДанная запись не является токеном\nПопробуйте ещё раз '
                                          '\"/token\"')
    else:
        counter = db.add_user(message.from_user.id, message.from_user.first_name, message.text)
        if counter:
            bot.send_message(message.chat.id, 'Ваш токен был сохранён👍')
        else:
            bot.send_message(message.chat.id, 'Такой пользователь уже существует!🚫')


# Команда, которая удаляет пользователя предварительно спрашивая его хочет он этого или нет
@bot.message_handler(commands=['delete'], content_types=['text'])
def delete_user(message):
    msg = bot.send_message(message.chat.id, "Вы уверены, что хотите удалить свой токен?")
    bot.register_next_step_handler(msg, text_for_delete_user)  # переправляет нас на функцию где мы получим ответ
    # пользователя


"""Вывод только акций"""


def print_stock(message):
    db = Database('users.db')
    user_token = db.get_token(message.from_user.id)

    person = tinvest.SyncClient(user_token)
    positions = person.get_portfolio()

    labels = []
    values = []

    for pos in positions.payload.positions:
        if pos.instrument_type == 'Stock':
            labels.append(pos.name)
            values.append(pos.balance)
            bot.send_message(message.chat.id,
                             f'Акция: {pos.name}\nСколько куплено: {pos.balance}\nВ какой валюте хранится '
                             f'акция:'
                             f' {pos.average_position_price.currency}\nЦена последней покупки акции: '
                             f'{pos.average_position_price.value}')

    if len(labels) != 0 and len(values) != 0:
        plt.title('Акции в портфеле')
        plt.pie(values, labels=labels, shadow=True, autopct='%1.1f%%', startangle=180)
        plt.axis('equal')
        plt.savefig(f'plot{message.chat.id}.png')
        plt.clf()
        plt.close()
        bot.send_photo(message.chat.id, photo=open(f'plot{message.chat.id}.png', 'rb'))
        os.remove(f'plot{message.chat.id}.png')
    else:
        bot.send_message(message.chat.id, 'У вас отсутствуют акции!')


"""Вывод валют"""


def print_currency(message):
    db = Database('users.db')
    user_token = db.get_token(message.from_user.id)

    person = tinvest.SyncClient(user_token)
    positions = person.get_portfolio()

    labels = []
    values = []

    for pos in positions.payload.positions:
        if pos.instrument_type == 'Currency':
            values.append(pos.balance)
            labels.append(pos.name)
            bot.send_message(message.chat.id,
                             f'Валюта: {pos.name}\nБаланс в этой валюте: {pos.balance}\nВ чём хранится '
                             f'валюта:'
                             f' {pos.average_position_price.currency}\nЦена последней покупки валюты: '
                             f'{pos.average_position_price.value}')

    if len(labels) != 0 and len(values) != 0:
        plt.title('Валюты в портфеле')
        plt.pie(values, labels=labels, shadow=True, autopct='%1.1f%%', startangle=180)
        plt.axis('equal')
        plt.savefig(f'plot{message.chat.id}.png')
        plt.clf()
        plt.close()
        bot.send_photo(message.chat.id, photo=open(f'plot{message.chat.id}.png', 'rb'))
        os.remove(f'plot{message.chat.id}.png')
    else:
        bot.send_message(message.chat.id, 'У вас отсутствует валюта!')


"""Вывод фондов"""


def print_etf(message):
    db = Database('users.db')
    user_token = db.get_token(message.from_user.id)

    person = tinvest.SyncClient(user_token)
    positions = person.get_portfolio()

    labels = []
    values = []

    for pos in positions.payload.positions:
        if pos.instrument_type == 'Etf':
            labels.append(pos.name)
            values.append(pos.balance)
            bot.send_message(message.chat.id,
                             f'Название фонда: {pos.name}\nСколько куплено фондов: {pos.balance}\nВ какой валюте хранится '
                             f'фонд:'
                             f' {pos.average_position_price.currency}\nЦена последней покупки фонда: '
                             f'{pos.average_position_price.value}')

    if len(labels) != 0 and len(values) != 0:
        plt.title('Фонды в портфеле')
        plt.pie(values, labels=labels, shadow=True, autopct='%1.1f%%', startangle=180)
        plt.axis('equal')
        plt.savefig(f'plot{message.chat.id}.png')
        plt.clf()
        plt.close()
        bot.send_photo(message.chat.id, photo=open(f'plot{message.chat.id}.png', 'rb'))
        os.remove(f'plot{message.chat.id}.png')

    else:
        bot.send_message(message.chat.id, 'У вас отсутствуют фонды!')


"""Тут функции которые выводят курс валют"""


def check_currency_dollar():
    url_dollar = "https://clck.ru/pLS2o"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)"
                             " Chrome/101.0.4951.67 Safari/537.36"}
    response = requests.get(url=url_dollar, headers=headers)
    soup = BeautifulSoup(response.text, "lxml")  # приводим код странички в нормальное состояние
    data = soup.find("div", class_="dDoNo ikb4Bb gsrt")  # поиск по тегу и классу
    course_dollar = data.find("span", class_="DFlfde SwHCTb").text
    return course_dollar


def check_currency_euro():
    url_euro = "https://clck.ru/pLxdN"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)"
                             " Chrome/101.0.4951.67 Safari/537.36"}
    response = requests.get(url=url_euro, headers=headers)
    soup = BeautifulSoup(response.text, "lxml")
    data = soup.find("div", class_="dDoNo ikb4Bb gsrt")
    course_euro = data.find("span", class_="DFlfde SwHCTb").text
    return course_euro


# Здесь непосредственно ответы пользователя, которые как-то вызывают функции
@bot.message_handler(content_types=['text'])
def user_responses(message):
    db = Database('users.db')
    if db.user_presence(message.from_user.id):
        if message.text.lower() == 'курсы валют':
            keyboards_under_text = types.InlineKeyboardMarkup()
            btn1_under_text = types.InlineKeyboardButton("Доллар", callback_data='Доллар')
            btn2_under_text = types.InlineKeyboardButton("Евро", callback_data='Евро')
            keyboards_under_text.add(btn1_under_text, btn2_under_text)
            bot.send_message(message.chat.id, 'Курс какой из валют вы хотите узнать?',
                             reply_markup=keyboards_under_text)
        if message.text.lower() == 'акции':
            print_stock(message)
        if message.text.lower() == 'валюты':
            print_currency(message)
        if message.text.lower() == 'фонды':
            print_etf(message)
    else:
        bot.send_message(message.chat.id, 'Извините, но вы не можете использовать бота пока не передадите ему свой '
                                          'токен\nВоспользуйтесь функцией - /token')


counter_for_alert = 0


# Это кнопки, которые расположены под текстом
@bot.callback_query_handler(func=lambda call: True)  # ответ на кнопки, которые пользователь нажмёт
def response_to_buttons(call):
    global counter_for_alert
    db = Database('users.db')
    if call.data == "Доллар":
        bot.send_message(call.message.chat.id, f'В данный момент - {check_currency_dollar()} руб.')
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f"{call.data}",
                              reply_markup=None)  # удаление кнопки после её выбора
    if call.data == "Евро":
        bot.send_message(call.message.chat.id, f'В данный момент - {check_currency_euro()} руб.')
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f"{call.data}",
                              reply_markup=None)  # удаление кнопки после её выбора
    if call.data == "Вы включили уведомления!":
        token_user = db.get_token(call.message.chat.id)
        if db.check_alert_user(token_user):
            bot.send_message(call.message.chat.id, "Вы уже подключили уведомления!")
            bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                          reply_markup=None)
        else:
            db.enable_alert_for_user(token_user)
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f"{call.data}",
                                  reply_markup=None)  # удаление кнопки после её выбора
            counter_for_alert += 1
            if counter_for_alert == 1:
                while True:
                    schedule.run_pending()
                    time.sleep(30)
    if call.data == "Уведомления не будут включены!":
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f"{call.data}",
                              reply_markup=None)  # удаление кнопки после её выбора
    if call.data == "Уведомления выключены!":
        user_token = db.get_token(call.message.chat.id)
        db.turn_off_alert(user_token)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f"{call.data}",
                              reply_markup=None)
    # bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=None)


try:
    bot.infinity_polling()
except tinvest.exceptions.UnexpectedError:
    print('Пользователь передал не тот токен')
"""Это для удаления в дальнейшем может пригодиться"""
# sql.execute('DELETE FROM name_and_token WHERE name = ?', ('Gleb',))
