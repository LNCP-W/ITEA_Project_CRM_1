from telebot import TeleBot, types
if __name__ == "__main__":
    import main


x = "1772461411:AAGpWy5vDHgvw0lOpqegfV0tY7BUu-XIgQs"
bot = TeleBot(token=x)


@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(
        chat_id=message.chat.id,
        text=f"Привет, {message.chat.first_name} {message.chat.last_name}. "
             f"Это бот сервисного центра 'Очень крутой сервисный центр'")
    markup = types.ReplyKeyboardMarkup(row_width=2)
    button1 = types.KeyboardButton('Сотрудник')
    button2 = types.KeyboardButton('Клиент')
    markup.add(button1, button2)
    bot.send_message(chat_id=message.chat.id, text="Вы сотрудник или клиент?", reply_markup=markup)
    bot.register_next_step_handler(message, select)

def select(message):
    x=message
    if message.text == 'Клиент':
        markup = types.ReplyKeyboardMarkup()
        button1 = types.KeyboardButton('Отправить контакт', request_contact=True)
        markup.add(button1)
        bot.send_message(chat_id=message.chat.id, text="Отправить номер телефона?", reply_markup=markup)
        bot.register_next_step_handler(message, subscribe_phone)
    if message.text == 'Сотрудник':
        markup = types.ReplyKeyboardMarkup()
        button1 = types.KeyboardButton('Отправить контакт', request_contact=True)
        markup.add(button1)
        bot.send_message(chat_id=message.chat.id, text="Отправить номер телефона?", reply_markup=markup)
        bot.register_next_step_handler(message, subscribe_employee)

def subscribe_phone(message):
    if message.contact:
        customer = main.Customers.query.filter_by(phone=message.contact.phone_number).first()
        if customer:
            customer.is_subscribed = True
            customer.chat_id = message.chat.id
            customer.username = message.chat.username
            main.db.session.commit()
            bot.send_message(chat_id=message.chat.id, text="Запись оновлена")
        else:
            customer = main.Customers(
                name=f"{message.chat.first_name} {message.chat.last_name}",
                phone=int(message.contact.phone_number),
                is_subscribed=True,
                chat_id=message.chat.id,
                username=message.chat.username
            )
            main.db.session.add(customer)
            main.db.session.commit()
            bot.send_message(chat_id=message.chat.id, text="Вы подписаны")

def send_notification(chat_id, message):
    bot.send_message(chat_id=chat_id, text=message)

@bot.message_handler(commands=['reg_employee'])
def reg_employee(message):
    bot.send_message(
        chat_id=message.chat.id,
        text="Привет. Это бот сервисного центра 'Очень крутой сервисный центр'.")
    markup = types.ReplyKeyboardMarkup(row_width=2)
    button1 = types.KeyboardButton('Да', request_contact=True)
    button2 = types.KeyboardButton('Нет')
    markup.add(button1, button2)
    bot.send_message(chat_id=message.chat.id, text="Вы наш сотрудник?", reply_markup=markup)
    bot.register_next_step_handler(message, subscribe_employee)

def subscribe_employee(message):

    if message.text == "Нет":
        bot.send_message(chat_id=message.chat.id, text="Всего хорошего")

    elif message.contact:
        employye = main.Employees.query.filter_by(phone=message.contact.phone_number).first()
        if employye:
            employye.is_subscribed = True
            employye.chat_id = message.chat.id
            main.db.session.commit()
            bot.send_message(chat_id=message.chat.id, text="Запись оновлена")
        else:
            bot.send_message(
                chat_id=message.chat.id,
                text="Вы не зарегистрированы в системе. Пройдите регистрацию в CRM")



if __name__ == "__main__":
    bot.polling()

