import logging
import requests
import json
import time
from pymongo import MongoClient

client = MongoClient(host='localhost', port=27017)
db = client['OneTwoTrip']
collection = db['MOV-LED - %s' % (dep_date)]
parc_date = time.strftime("%d/%m/%Y")
dates = ['30042020', '03092019', '04092019', '05092019', '06092019', '07092019', '08092019']
print(parc_date)


def GD1(dep_date):
    collection = db['MOV-LED - %s' % (dep_date)]
    main_json_data = json.loads(requests.get(
        'https://www.onetwotrip.com/_api/rzd/metaTimetable/?adults=1&children=0&'
        'infants=0&date=%s&from=22823&to=22871&isReturn=false&source=web' % dep_date).text)
    json_data = main_json_data['result']
    for item in json_data:
        train_number = item['trainNumber']
        duration_minutes = item['durationInMinutes']
        from_station = item['from']['station']
        to_station = item['to']['station']
        departure_time = item['departure']['time'].split("T")[1]
        try:
            train_name = item['name']
        except:
            train_name = ''
        from_code = item['from']['code']
        to_code = item['to']['code']
        date = item['departure']['time'].split('T')[1].split(':')
        date_code = '%s%s' % (date[0], date[1])
        places = item['places']
        if train_name == 'Сапсан':
            print(train_number)
            for carType in places:
                type_name = carType['typeName']
                train_url = 'https://www.onetwotrip.com/_api/rzd/searchManager?type=trainCarPlaces&carType=' \
                            '%s&date=%s%s&from=%s&to=%s&train=%s&full=true&adults=1&children=0' \
                            '&infants=0&isReturn=false&roundtrip=false' % (
                        carType['type'], dep_date, date_code, from_code, to_code, train_number)
                train_json_data = json.loads(train_url).text

                cars = train_json_data['result']['cars']
                for car in cars:
                    class_of_car = car['classService']['id']
                    car_number = car['number']
                    sum_of_seats = 0
                    average = 0
                    for tariff in car['tariffs']:
                        sum_of_seats = sum_of_seats + tariff['seats']['SeatsUndef']
                        average = average + tariff['price']
                    average = average / len(car['tariffs'])
                    print(car_number)
                    collection.update_one(
                        {"Поезд_вагон": '%s+%s' % (train_number, car_number)},
                        {"$set": {
                            "Номер поезда": train_number,
                            "Время выезда ": departure_time,
                            'Вокзал приезда': to_station,
                            'Вокзал выезда': from_station,
                            "Продолжительность поездки (мин)": duration_minutes,
                            "Класс вагона": class_of_car,
                            "Цена %s" % (parc_date): average,
                            "Количество мест %s" % (parc_date): sum_of_seats,
                            "Дата выезда": dep_date,
                            "Номер вагона": car_number
                        }
                        }, upsert=True)


def GD2(dep_date):
    collection = db['LED-MOV - %s' % (dep_date)]
    main_json_data = json.loads(requests.get(
        'https://www.onetwotrip.com/_api/rzd/metaTimetable/?adults=1&children=0&infants=0&date=%s&from=22871&to=22823&isReturn=false&source=web' % (
            dep_date)).text)
    json_data = main_json_data['result']
    for item in json_data:
        train_number = item['trainNumber']
        duration_minutes = item['durationInMinutes']
        from_station = item['from']['station']
        to_station = item['to']['station']
        departure_time = item['departure']['time'].split("T")[1]
        try:
            train_name = item['name']
        except:
            train_name = ''
        from_code = item['from']['code']
        to_code = item['to']['code']
        date = item['departure']['time'].split('T')[1].split(':')
        date_code = '%s%s' % (date[0], date[1])
        places = item['places']
        if train_name == 'Сапсан':
            print(train_number)
            for carType in places:
                type_name = carType['typeName']
                train_json_data = json.loads(requests.get(
                    'https://www.onetwotrip.com/_api/rzd/searchManager?type=trainCarPlaces&carType=%s&date=%s%s&from=%s&to=%s&train=%s&full=true&adults=1&children=0&infants=0&isReturn=false&roundtrip=false' % (
                        carType['type'], dep_date, date_code, from_code, to_code, train_number)).text)
                cars = train_json_data['result']['cars']
                for car in cars:
                    class_of_car = car['classService']['id']
                    car_number = car['number']
                    sum_of_seats = 0
                    average = 0
                    for tariff in car['tariffs']:
                        sum_of_seats = sum_of_seats + tariff['seats']['SeatsUndef']
                        average = average + tariff['price']
                    average = average / len(car['tariffs'])
                    print(car_number)
                    collection.update_one(
                        {"Поезд_вагон": '%s+%s' % (train_number, car_number)},
                        {"$set": {
                            "Номер поезда": train_number,
                            "Время выезда ": departure_time,
                            'Вокзал приезда': to_station,
                            'Вокзал выезда': from_station,
                            "Продолжительность поездки (мин)": duration_minutes,
                            "Класс вагона": class_of_car,
                            "Цена %s" % (parc_date): average,
                            "Количество мест %s" % (parc_date): sum_of_seats,
                            "Дата выезда": dep_date,
                            "Номер вагона": car_number
                        }
                        }, upsert=True)


start = time.time()
for dat in dates:
    GD1(dat)
    GD2(dat)
print(time.time() - start)
