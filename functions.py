import sqlite3
from telegram import ReplyKeyboardMarkup
from telegram.ext import ConversationHandler
from config import API_KEY
import requests
import json
from db_operators import add_sights_to_db


async def start(update, context):
    # Вывод приветственного сообщения
    await update.message.reply_text(
        "Доброго времени суток тебе, человек)) Я бот-путешественник, и я помогу сделать твою поездку незабываемой!")

    # Информация о том, что умеет бот
    await update.message.reply_text(
        "Что я умею?\n\nКоманда /weather <название_города> позволяет узнать погоду в указанном городе.\n\nКоманда "
        "/cafes <название_города> дает рекомендации ресторанов в указанном городе.\n\nКоманда /hotels <название_города>"
        " выдает информацию об отелях в указанном городе.\n\nКоманда /sights <название_города> позволяет узнать больше"
        " о достопримечательностях в указанном городе и об их расположении на карте.\n\nКоманда /help напомпит о том, "
        "что я умею.\n\nДля /cafes и /hotels город можно не указывать. Тогда я запрошу твое местоположение и расскажу о тех ресторанах или отелях, которые находятся недалеко от тебя.\n\nВАЖНО! Я бот-патриот, поэтому хорошо разбираюсь только в тех городах, которые находятся в "
        "России.")


async def help(update, context):
    # Информация о том, что умеет бот
    await update.message.reply_text(
        "Что я умею?\n\nКоманда /weather <название_города> позволяет узнать погоду в указанном городе.\n\nКоманда "
        "/cafes <название_города> дает рекомендации ресторанов в указанном городе.\n\nКоманда /hotels <название_города>"
        " выдает информацию об отелях в указанном городе.\n\nКоманда /sights <название_города> позволяет узнать больше"
        " о достопримечательностях в указанном городе и об их расположении на карте.\n\nКоманда /help напомпит о том, "
        "что я умею.\n\nДля /cafes и /hotels город можно не указывать. Тогда я запрошу твое местоположение и расскажу о тех ресторанах или отелях, которые находятся недалеко от тебя.\n\nВАЖНО! Я бот-патриот, поэтому хорошо разбираюсь только в тех городах, которые находятся в "
        "России.")


# Сбор информации об отелях
def find_hotels(response):
    hotels = ''
    cnt = 0
    for hotel in response['features']:
        cnt += 1
        hotel_name = hotel['properties']['CompanyMetaData'].get('name', '')
        hotel_address = hotel['properties']['CompanyMetaData'].get('address', '')
        hotel_url = hotel['properties']['CompanyMetaData'].get('url', '')
        if hotel_name:
            hotels += (str(cnt) + ') ' + 'Название: ' + hotel_name + '\n')
            if hotel_address:
                hotels += ('Адрес: ' + hotel_address + '\n')
            if hotel_url:
                hotels += ('Сайт: ' + hotel_url + '\n')
            hotels += '\n'
    return hotels


# Отели в городе
async def hotels_in_city(update, context):
    try:
        search_api_server = "https://search-maps.yandex.ru/v1/"

        # Если задан город
        if context.args:
            city = context.args[0]
            search_params = {
                "apikey": API_KEY,
                "text": "отель+в+" + city,
                "lang": "ru_RU",
                "type": "biz"
            }

            response = requests.get(search_api_server, params=search_params).json()
            await update.message.reply_text('Гостиницы в городе ' + city + '\n' + find_hotels(response))

        # Если город не задан
        else:
            reply_keyboard = [[{"request_location": True, "text": "Где я?"}]]
            markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
            await update.message.reply_text(
                f'''Укажите свое местоположение''', reply_markup=markup)
            return 2

    except Exception:
        await update.message.reply_text(
            'Не удалось получить информацию о гостиницах. Проверь название города. Он точно находится в России?')


# Отели по местоположению пользователя
async def get_location_hotels(update, context):
    search_api_server = "https://search-maps.yandex.ru/v1/"
    current_pos = (update.message.location.latitude, update.message.location.longitude)
    search_params = {
        "apikey": API_KEY,
        "text": "отель",
        "ll": str(current_pos[1]) + ',' + str(current_pos[0]),
        "lang": "ru_RU",
        "type": "biz"
    }

    response = requests.get(search_api_server, params=search_params).json()
    await update.message.reply_text('Отели недалеко от Вас:\n' + find_hotels(response))

    return ConversationHandler.END


# Сбор информации о ресторанах
def find_cafes(response):
    cnt = 0
    cafes = ''
    for cafe in response['features']:
        cnt += 1
        cafe_name = cafe['properties']['CompanyMetaData'].get('name', '')
        cafe_address = cafe['properties']['CompanyMetaData'].get('address', '')
        cafe_url = cafe['properties']['CompanyMetaData'].get('url', '')
        cafe_hours = cafe['properties']['CompanyMetaData'].get('Hours', '')
        if cafe_hours:
            cafe_hours = cafe_hours.get('text', '')
        else:
            cafe_hours = ''
        if cafe_name:
            cafes += (str(cnt) + ') ' + 'Название: ' + cafe_name + '\n')
            if cafe_address:
                cafes += ('Адрес: ' + cafe_address + '\n')
            if cafe_url:
                cafes += ('Сайт: ' + cafe_url + '\n')
            if cafe_hours:
                cafes += ('График работы: ' + cafe_hours + '\n')
            cafes += '\n'
    return cafes


# Рестораны в городе
async def restaurants(update, context):
    try:
        search_api_server = "https://search-maps.yandex.ru/v1/"
        if context.args:
            city = context.args[0]
            search_params = {
                "apikey": API_KEY,
                "text": "кафе+в+" + city,
                "lang": "ru_RU",
                "type": "biz"
            }

            response = requests.get(search_api_server, params=search_params).json()

            await update.message.reply_text('Рестораны в городе ' + city + ':\n' + find_cafes(response))

        else:
            reply_keyboard = [[{"request_location": True, "text": "Где я?"}]]
            markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)

            await update.message.reply_text(
                f'''Укажите свое местоположение''', reply_markup=markup)

            return 1

    except Exception as ex:
        print(ex)
        await update.message.reply_text(
            'Не удалось получить информацию о ресторанах. Проверь название города. Он точно находится в России?')


# Рестораны по местоположению пользователя
async def get_location_cafes(update, context):
    search_api_server = "https://search-maps.yandex.ru/v1/"
    current_pos = (update.message.location.latitude, update.message.location.longitude)
    search_params = {
        "apikey": API_KEY,
        "text": "кафе",
        "ll": str(current_pos[1]) + ',' + str(current_pos[0]),
        "lang": "ru_RU",
        "type": "biz"
    }

    response = requests.get(search_api_server, params=search_params).json()
    await update.message.reply_text('Рестораны недалеко от Вас:\n' + find_cafes(response))

    return ConversationHandler.END


# Достопримечательности в городе
async def sights_in_city(update, context):
    try:
        search_api_server = "https://search-maps.yandex.ru/v1/"
        city = context.args[0]
        name = update.message.from_user.username
        print(context)
        search_params = {
            "apikey": API_KEY,
            "text": "достопримечательности+в+" + city,
            "lang": "ru_RU",
            "type": "biz"
        }

        response = requests.get(search_api_server, params=search_params).json()
        with open('jsons.json', 'w') as f:
            json.dump(response, f, indent=4)

        cnt = 0
        all_coords = []
        sights_names = []
        sights = 'Достопримечательности в городе ' + city + '\n'
        coords_left = []
        coords_right = []

        for sight in response['features']:
            cnt += 1
            sight_name = sight['properties']['CompanyMetaData'].get('name', '')
            sight_address = sight['properties']['CompanyMetaData'].get('address', '')
            sight_coords = sight['geometry']['coordinates']

            all_coords.append(sight_coords)
            coords_left.append(sight_coords[0])
            coords_right.append(sight_coords[1])

            if sight_name:
                sights += (str(cnt) + ') ' + 'Название: ' + sight_name + '\n')
                sights_names.append(sight_name)
                if sight_address:
                    sights += ('Адрес: ' + sight_address + '\n')
                sights += '\n'

        metks = ''
        req = "http://static-maps.yandex.ru/1.x/?ll=" + str(
            round((min(coords_left) + max(coords_left)) / 2, 6)) + ',' + str(
            round((min(coords_right) + max(coords_right)) / 2, 6)) + '&spn=0.1,0.1&l=map&pt=' + str(
            all_coords[0][0]) + ',' + str(all_coords[0][1]) + ',' + 'pmorl1'
        k = 0

        for coord in all_coords:
            k += 1
            metks += '~' + str(coord[0]) + ',' + str(coord[1]) + ',' + 'pmorl' + str(k)
        req += metks

        with open('im.jpg', 'wb') as f:
            f.write(requests.get(req).content)

        await update.message.reply_text(sights)
        await update.message.reply_photo(photo="im.jpg",
                                         caption='Введи номер/номера достопримечательностей, которые ты хотел бы посетить, через пробел.\nНапример, 1 3 10')

        add_sights_to_db(name, city, sights_names, all_coords)

        return 1

    except Exception as ex:
        print(ex)
        await update.message.reply_text(
            'Не удалось получить информацию о достопримечательностях. Проверь название города. Он точно находится в России?')


# Достопримечательности в городе по номерам
async def sights_numbers(update, context):
    numbers = update.message.text.split()
    name = update.message.from_user.username
    conn = sqlite3.connect('cities.db')
    cursor = conn.cursor()

    cursor.execute("SELECT city_id FROM users_cities WHERE user_name=?", (name,))
    city_id = cursor.fetchone()[0]

    cursor.execute("SELECT * FROM sights WHERE city_id=?",
                   (city_id,))
    city_info = cursor.fetchall()
    print(7)
    for number in numbers:
        if number in ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"]:
            print(77)
            sight = city_info[int(number) - 1][1]
            req = "http://static-maps.yandex.ru/1.x/?ll=" + str(city_info[int(number) - 1][3]) + ',' + str(
                city_info[int(number) - 1][4]) + '&spn=0.02,0.02&l=map&pt=' + str(
                city_info[int(number) - 1][3]) + ',' + str(city_info[int(number) - 1][4]) + ',' + 'pmorl' + number
            with open('im.jpg', 'wb') as f:
                f.write(requests.get(req).content)
            await update.message.reply_photo(photo="im.jpg",
                                            caption=sight)
        else:
            await update.message.reply_text(
            'Достопримечательности с номером ' + number + ' не существует.')

            

    return ConversationHandler.END  


# Погода в городе
async def weather_response(update, context):
    try:
        city = context.args[0]
        url = 'https://api.openweathermap.org/data/2.5/weather?q=' + city + '&units=metric&lang=ru&appid=79d1ca96933b0328e1c7e3e7a26cb347'
        weather_data = requests.get(url).json()

        temperature = round(weather_data['main']['temp'])
        temperature_feels = round(weather_data['main']['feels_like'])
        t_now = 'Сейчас в городе ' + city + ' ' + str(temperature) + ' °C.'
        t_feels = 'Ощущается как ' + str(temperature_feels) + ' °C.'
        t_desc = 'В городе ' + city + ' сейчас ' + weather_data['weather'][0]['description'] + '.'
        await update.message.reply_text(t_now + '\n' + t_feels + '\n' + t_desc)
    except Exception as ex:
        print(ex)
        await update.message.reply_text("Проверьте название города!")


async def stop(update, context):
    await update.message.reply_text("Всего доброго!")
    return ConversationHandler.END
