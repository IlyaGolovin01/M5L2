import telebot
from config import *
from logic import *

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def handle_start(message):
    bot.send_message(message.chat.id, "Привет! Я бот, который может показывать города на карте. Напиши /help для списка команд.")

@bot.message_handler(commands=['help'])
def handle_help(message):
    bot.send_message(message.chat.id, "Доступные команды:  ...")
    # Допиши команды бота


@bot.message_handler(commands=['show_city'])
def handle_show_city(message):
    try:
        city_name = message.text.split()[1]
        manager.create_grapf(city_name + ".png", [city_name])
        with open(city_name + ".png", "rb") as photo:
            bot.send_photo(message.chat.id, photo)
    except IndexError:
        bot.send_message(message.chat.id, "Укажите название города. Пример: /show_city London")

@bot.message_handler(commands=['remember_city'])
def handle_remember_city(message):
    user_id = message.chat.id
    city_name = message.text.split()[-1]
    if manager.add_city(user_id, city_name):
        bot.send_message(message.chat.id, f'Город {city_name} успешно сохранен!')
    else:
        bot.send_message(message.chat.id, 'Такого города я не знаю. Убедись, что он написан на английском!')

@bot.message_handler(commands=['show_my_cities'])
def handle_show_visited_cities(message):
    # Получаем список сохраненных городов пользователя
    cities = manager.select_cities(message.chat.id)
    
    if not cities:
        bot.send_message(message.chat.id, "У вас пока нет сохраненных городов. Используйте /remember_city [название], чтобы добавить город")
        return
    
    # Создаем карту со всеми городами
    filename = f"user_{message.chat.id}_cities.png"
    manager.create_grapf(filename, cities)
    
    # Отправляем карту пользователю
    with open(filename, "rb") as photo:
        bot.send_photo(message.chat.id, photo, caption=f"Ваши сохраненные города ({len(cities)} шт.):\n" + ", ".join(cities))


if __name__=="__main__":
    manager = DB_Map(DATABASE)
    bot.infinity_polling(timeout=60, long_polling_timeout=60)
