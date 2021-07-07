import datetime

from telebot import TeleBot, types
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask("my_app")
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://postgres:postgres@localhost/postgres"
db = SQLAlchemy(app)

class BotUsers(db.Model):
    di = db.Column(db.Integer, primary_key=True)
    nick = db.Column(db.String(50), nullable=False)
    chat_id = db.Column(db.Integer, nullable=False)
    mess_time = db.Column(db.DateTime, nullable=False)


x = "1772461411:AAGpWy5vDHgvw0lOpqegfV0tY7BUu-XIgQs"
bot = TeleBot(token=x)
# db.create.all()

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, 'some')
    x = BotUsers(
        nick=message.chat.username,
        chat_id=message.chat.id,
        mess_time=datetime.datetime.now()
    )
    db.session.add(x)
    db.session.commit()

bot.polling()