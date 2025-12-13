import sqlite3
import time
import json
import requests
from telegram.ext import ConversationHandler
from config import API_KEY

async def start(update, context):
    await update.message.reply_text(
        "Доброго времени суток тебе, человек)) Я бот-путешественник, и я помогу сделать твою поездку незабываемой!")
    time.sleep(1)
    await update.message.reply_text(
        "Что я умею?\n\nКоманда /weather <название_города> позволяет узнать погоду в указанном городе.\n\nКоманда /cafes <название_города> дает рекомендации ресторанов в указанном городе.\n\nКоманда /hotels <название_города> выдает информацию об отелях в указанном городе.\n\nКоманда /sights <название_города> позволяет узнать больше о достопримечательностях в указанном городе и об их расположении на карте.\n\nВАЖНО! Я бот-патриот, поэтому хорошо разбираюсь только в тех городах, которые находятся в России.")



async def hotels_in_city(update, context):
    print("==hotels=> hotels initialized")
    try:
        city = context.args[0]
        print(city)
        search_api_server = "https://search-maps.yandex.ru/v1/"
        api_key = API_KEY

        search_params = {
            "apikey": api_key,
            "text": "отель+в+" + city,
            "lang": "ru_RU",
            "type": "biz"
        }

        response = requests.get(search_api_server, params=search_params).json()
        print(response)

        hotels = 'Гостиницы в городе ' + city + '\n'
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
        await update.message.reply_text(hotels)
    except Exception:
        await update.message.reply_text(
            'Не удалось получить информацию о гостиницах. Проверь название города. Он точно находится в России?')



async def restaurants(update, context):
    print("==restaurants=> restaurants initialized")

    try:
        search_api_server = "https://search-maps.yandex.ru/v1/"
        api_key = API_KEY
        city = context.args[0]

        search_params = {
            "apikey": api_key,
            "text": "кафе+в+" + city,
            "lang": "ru_RU",
            "type": "biz"
        }

        response = requests.get(search_api_server, params=search_params).json()
        cnt = 0
        cafes = 'Рестораны недалеко от Вас:\n'
        for cafe in response['features']:
            cnt += 1
            cafe_name = cafe['properties']['CompanyMetaData'].get('name', '')
            cafe_address = cafe['properties']['CompanyMetaData'].get('address', '')
            cafe_url = cafe['properties']['CompanyMetaData'].get('url', '')
            cafe_hours = cafe['properties']['CompanyMetaData'].get('Hours', '').get('text', '')
            if cafe_name:
                cafes += (str(cnt) + ') ' + 'Название: ' + cafe_name + '\n')
                if cafe_address:
                    cafes += ('Адрес: ' + cafe_address + '\n')
                if cafe_url:
                    cafes += ('Сайт: ' + cafe_url + '\n')
                if cafe_hours:
                    cafes += ('График работы: ' + cafe_hours + '\n')
                cafes += '\n'
        await update.message.reply_text(cafes)
    except Exception:
        await update.message.reply_text(
            'Не удалось получить информацию о ресторанах. Проверь название города. Он точно находится в России?')



async def sights_in_city(update, context):
    print("==sights=> sights initialized")
    global all_coords
    try:
        search_api_server = "https://search-maps.yandex.ru/v1/"
        api_key = API_KEY
        print(context.args)
        city = context.args[0]
        print(context)
        search_params = {
            "apikey": api_key,
            "text": "достопримечательности+в+" + city,
            "lang": "ru_RU",
            "type": "biz"
        }

        response = requests.get(search_api_server, params=search_params).json()
        with open('api_response.json', 'w') as f:
            json.dump(response, f, indent=4)

        print(response)
        cnt = 0
        all_coords = []
        sights = 'Достопримечательности в городе ' + city + '\n'
        coords_left = []
        coords_right = []
        for sight in response['features']:
            cnt += 1
            sight_name = sight['properties']['CompanyMetaData'].get('name', '')
            sight_address = sight['properties']['CompanyMetaData'].get('address', '')
            sight_coords = sight['geometry']['coordinates']
            # all_coords.append(','.join([str(i) for i in sight_coords[::-1]]))
            all_coords.append(sight_coords)
            coords_left.append(sight_coords[0])
            coords_right.append(sight_coords[1])
            if sight_name:
                sights += (str(cnt) + ') ' + 'Название: ' + sight_name + '\n')
                if sight_address:
                    sights += ('Адрес: ' + sight_address + '\n')
                sights += '\n'
        # all_coords = ','.join(all_coords)
        print(all_coords)
        metks = ''
        req = "http://static-maps.yandex.ru/1.x/?ll=" + str(
            round((min(coords_left) + max(coords_left)) / 2, 6)) + ',' + str(
            round((min(coords_right) + max(coords_right)) / 2, 6)) + '&spn=0.2,0.2&l=map&pt=' + str(
            all_coords[0][0]) + ',' + str(all_coords[0][1]) + ',' + 'pmorl1'
        k = 0
        print(req)
        print(all_coords)
        for coord in all_coords:
            k += 1
            metks += '~' + str(coord[0]) + ',' + str(coord[1]) + ',' + 'pmorl' + str(k)
        req += metks
        print(sights)
        with open('im.jpg', 'wb') as f:
            f.write(requests.get(req).content)
        print(7)

        # await update.message.reply_text(sights)
        print(len(sights))
        # await update.message.reply_photo(photo="im.jpg", caption=sights[:1025])
        await update.message.reply_text(sights)
        await update.message.reply_photo(photo="im.jpg",
                                         caption='Введи номер/номера достопримечательностей, которые ты хотел бы посетить, через пробел.\nНапример, 1 3 10')

        return 1

    except Exception as ex:
        print(ex)
        await update.message.reply_text(
            'Не удалось получить информацию о достопримечательностях. Проверь название города. Он точно находится в России?')


async def sights_numbers(update, context):
    print("==sights_n=> sights_n initialized")
    numbers = update.message.text.split()
    global all_coords

    with open('api_response.json', 'r') as f:  # Открываем файл с данными о достопримечательностях
        response = json.load(f)

    conn = sqlite3.connect('cities.db')
    cursor = conn.cursor()

    for number in numbers:
        sight = response['features'][int(number) - 1]
        city_id = 1
        cursor.execute("SELECT * FROM cities WHERE city_id=?", (city_id,))
        city_data = cursor.fetchone()
        if city_data:
            city_name = city_data[1]
            # sights = city_data[2]
            sights = '\n' + sight['properties']['CompanyMetaData'].get('name', '')
        else:
            city_name = city_data[1]
            sights = sight['properties']['CompanyMetaData'].get('name', '')

        cursor.execute("INSERT OR REPLACE INTO cities (city_id, city_name, sights) VALUES (?, ?, ?)",
                       (city_id, city_name, sights))

        sight_name = sight['properties']['CompanyMetaData'].get('name', '')
        req = "http://static-maps.yandex.ru/1.x/?ll=" + str(all_coords[int(number) - 1][0]) + ',' + str(
            all_coords[int(number) - 1][1]) + '&spn=0.02,0.02&l=map&pt=' + str(
            all_coords[int(number) - 1][0]) + ',' + str(all_coords[int(number) - 1][1]) + ',' + 'pmorl' + number

        with open('im.jpg', 'wb') as f:
            f.write(requests.get(req).content)

        await update.message.reply_photo(photo="im.jpg", caption=sight_name)

    conn.commit()
    conn.close()
    return ConversationHandler.END



async def weather_response(update, context):
    print("==weather=> weather initialized")

    try:

        city = context.args[0]
        print(city)

        url = 'https://api.openweathermap.org/data/2.5/weather?q=' + city + '&units=metric&lang=ru&appid=79d1ca96933b0328e1c7e3e7a26cb347'
        weather_data = requests.get(url).json()

        temperature = round(weather_data['main']['temp'])
        temperature_feels = round(weather_data['main']['feels_like'])

        t_now = 'Сейчас в городе ' + city + ' ' + str(temperature) + ' °C.'
        t_feels = 'Ощущается как ' + str(temperature_feels) + ' °C.'
        t_desc = 'В городе ' + city + ' сейчас ' + weather_data['weather'][0]['description'] + '.'
        await update.message.reply_text(t_now + '\n' + t_feels + '\n' + t_desc)
    except Exception as ex:
        print("==wheather_main_exception=>", ex)
        await update.message.reply_text("Проверьте название города!")

