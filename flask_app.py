from flask import Flask, request
import logging
import json
import random

app = Flask(__name__)
import translate

logging.basicConfig(level=logging.INFO, filename='app.log',
                    format='%(asctime)s %(levelname)s %(name)s %(message)s')

Session_data = {}
current_status = "start"
current_dialog = "start"


@app.route('/post', methods=['POST'])
def main():
    logging.info('Request: %r', request.json)

    response = {
        'session': request.json['session'],
        'version': request.json['version'],
        'response': {
            'end_session': False
        }
    }

    main_dialog(response, request.json)

    logging.info('Request: %r', response)

    return json.dumps(response)


def main_dialog(res, req):
    global current_status, current_dialog, Session_data

    user_id = req['session']['user_id']
    if current_dialog == "start":
        if req['session']['new']:
            res['response']['text'] = 'Привет! '
            Session_data[user_id] = {
                'suggests': [],
                'username': "Пользователь"
            }


            return
        if current_status == "start":
            res['response']['text'] = 'О чем хочешь поговорить?'
            current_status = "start_question"
            Session_data[user_id] = {
                'suggests': [
                    "Просто поболтать",
                    "Поговорить о музыке",
                    "Какую песню ты можешь посоветовать мне?",
                    "Открой текст песни",
                    "Переведи текст песни",
                    "Покажи фото с последнего концерта",
                ],
                'username': "Пользователь"
            }
            Session_data[user_id]['quest'] = ['Как погода?', 'Как тебя зовут?', 'Тебе много лет?', 'Чем занимаешься?']

            res['response']['buttons'] = get_suggests(user_id)
            return

        if current_status == "start_question":
            if req['request']['original_utterance'].lower() in ['просто поболтать', 'поболтать', 'поговорим',
                                                                'поговорить']:
                current_dialog = "talk"
                res['response']['text'] = 'Отлично! Как твои дела?'
                current_status = 'talk_alisa'
                return
            if req['request']['original_utterance'].lower() in ['переведи текст песни.', 'переведи', 'переводчик',
                                                                'нужно перевести']:
                current_dialog = "translite"
                res['response']['text'] = 'Отлично! Что нужно перевести?'
                Session_data[user_id]['suggests'] = [
                        "Русский-английский",
                        "Английский-русский"
                    ]
                res['response']['text'] = Session_data[user_id]['username'] + '. Выбери язык'
                res['response']['buttons'] = get_suggests(user_id)
                current_status = 'start'
                current_dialog = 'translite'

                return


            if req['request']['original_utterance'].lower() in ['текст', "открой текст песни", "слова песни", ]:
                current_dialog = "text_pesni"
                res['response']['text'] = 'Я могу открыть текст практически любой песни на этих довольно известных сайтах:'
                Session_data[user_id]['suggests'] = [
                        'altwall.net',
                    ]
                res['response']['text'] = Session_data[user_id]['username'] + ', выбери какой-нибудь из предложенных'
                res['response']['buttons'] = get_suggests(user_id)
                current_status = 'start'
                current_dialog = 'txt_pesni'

                return

            if req['request']['original_utterance'].lower() in ['какую песню ты можешь посоветовать мне?', "посоветуй"]:
                current_dialog = "sovet_pesni"
                res['response']['text'] = 'Без проблем, какой именно жанр вас интересует?'
                Session_data[user_id]['suggests'] = [
                        "Популярное",
                        "Классика",
                        "Рок"
                    ]
                res['response']['text'] = Session_data[user_id]['username'] + ', выбери что-то из предложенных'
                res['response']['buttons'] = get_suggests(user_id)
                current_status = 'start'
                current_dialog = 'd_sovet'

                return

            if req['request']['original_utterance'].lower() in ['покажи фото с последнего концерта', "фото", "концерт"]:
                current_dialog = "photo"
                res['response']['text'] = 'Без проблем, какой именно концерт вас интересует?'
                Session_data[user_id]['suggests'] = [
                        "Louna Тамбов 2018",
                        "ЧЕРНОЗЁМ 2018",
                        "ДДТ (ЧЕРНОЗЁМ 2018)"
                    ]
                res['response']['text'] = Session_data[user_id]['username'] + ', выбери что-то из предложенных'
                res['response']['buttons'] = get_suggests(user_id)
                current_status = 'start'
                current_dialog = 'ph'

                return

            if req['request']['original_utterance'].lower() in ['музыка', "поговорить о музыке"]:
                current_dialog = "rock"
                res['response']['text'] = 'Отлично!'
                Session_data[user_id]['suggests'] = [
                        "Популярное",
                        "Классика",
                        "Рок"
                    ]
                res['response']['text'] = Session_data[user_id]['username'] + ', выбери жанр'
                res['response']['buttons'] = get_suggests(user_id)
                current_status = 'start'
                current_dialog = 'rock_genres'

                return

    if current_dialog == "talk":
        if  current_status == 'talk_name':
            Session_data[user_id]['username'] = get_first_name(req).title()
            res['response']['text'] = 'Приятно познакомиться, ' + Session_data[user_id]['username']
            current_status = 'talk_alisa'
            return
        if '?' in req['request']['original_utterance'].lower():
            current_status = 'talk_user'
        else:
            current_status = 'talk_alisa'
        if current_status == 'talk_alisa':
            if len(Session_data[user_id]['quest']) < 1:
                res['response']['text'] = 'Не знаю, о чем еще спросить'
                Session_data[user_id]['quest'] = ['Как погода?', 'Как тебя зовут?', 'Тебе много лет?',
                                                  'Чем занимаешься?']
                current_dialog = "start"
                current_status = "start"
                return
            st_q = ['Интересно', 'Понятно', 'Ясно']
            c_q = random.choice(Session_data[user_id]['quest'])
            Session_data[user_id]['quest'].remove(c_q)
            if c_q == 'Как тебя зовут?':
                current_status = 'talk_name'
            res['response']['text'] = random.choice(st_q) + '. ' + c_q

            return

        elif current_status == 'talk_user':

            end_q = ['Что-нибудь еще спросишь?', 'Еще поговорим?', 'Мммм']
            if 'погода' in req['request']['original_utterance'].lower():
                res['response']['text'] = 'Нормальная' + '. ' + random.choice(end_q)
                return
            if 'имя' in req['request']['original_utterance'].lower():
                res['response']['text'] = 'Алиса' + '. ' + random.choice(end_q)
                return
            if 'лет' in req['request']['original_utterance'].lower():
                res['response']['text'] = 'Не знаю. Мало. ' + '. ' + random.choice(end_q)
                return
            res['response']['text'] = 'Не понятно о чем ты'
            return
        else:
            res['response']['text'] = 'Что-нибудь хочешь?'
            current_dialog = "start"
            current_status = "start_question"
            Session_data[user_id]= [
                    "Поболтать.",
                    "Переведи текст песни",
                    "Поговорить о музыке",
                ]
            res['response']['buttons'] = get_suggests(user_id)
            return
    if current_dialog == "translite":
        translite_dialog(res, req)
        return
    if current_dialog == 'rock_genres':
        rock(res, req)
        return
    if current_dialog == 'grock':
        genre_rock(res, req)
        return
    if current_dialog == 'gklassika':
        genre_klassika(res, req)
        return
    if current_dialog == 'gpop':
        genre_pop(res, req)
        return
    if current_dialog == 'lou_rock':
        louna(res, req)
        return
    if current_dialog == 'ddt_rock':
        ddt(res, req)
        return
    if current_dialog == 'smgl_rock':
        smgl(res, req)
        return
    if current_dialog == 'may_klassika':
        may(res, req)
        return
    if current_dialog == 'mozart_klassika':
        mozart(res, req)
        return
    if current_dialog == 'vivaldi_klassika':
        vivaldi(res, req)
        return
    if current_dialog == 'raik_pop':
        raik(res, req)
        return
    if current_dialog == 'egor_pop':
        egor(res, req)
        return
    if current_dialog == 'art_pop':
        art(res, req)
        return
    if current_dialog == 'txt_pesni':
        text_ps(res, req)
        return
    if current_dialog == 'klassika_sovet':
        sovet_f(res, req)
        return
    if current_dialog == 'pop_sovet':
        sovet_f(res, req)
        return
    if current_dialog == 'rock_sovet':
        sovet_f(res, req)
        return
    if current_dialog == 'd_sovet':
        sovet_f(res, req)
        return
    if current_dialog == 'ph':
        photo_f(res, req)
        return

lang = "ru-en"


def translite_dialog(res, req):
    global current_status,current_dialog, Session_data, lang
    user_id = req['session']['user_id']
    if current_status == "start":
        if req['request']['original_utterance'] == "Русский-английский":

            lang = 'ru-en'

        else:
            lang = 'en-ru'
        res['response']['text'] = Session_data[user_id]['username'] + " скажи текст"
        current_status = 'start_translite'
        return

    if 'хватит' in req['request']['original_utterance'].lower():
        current_dialog= 'start'
        res['response']['text'] = "Была рада помочь"
        current_status = 'end_translite'
        return
    if current_status == 'start_translite':
        res['response']['text'] = "Перевод: "+ translate.translate(req['request']['original_utterance'], lang)[0]
        current_status = 'start_translite'
        return


def rock(res, req):

    global current_status, current_dialog, Session_data
    if current_dialog == "rock_genres":

        music_genre = req['request']['original_utterance'].lower()
        logging.info(music_genre)
        if music_genre == "хватит":
            current_dialog = "start"
            current_status = "start"
            res['response']['text'] = 'Ок'
            return
        if music_genre == 'рок':
            user_id = req['session']['user_id']
            Session_data[user_id]['suggests'] = [
                        "Louna",
                        "ДДТ",
                        "Смысловые Галлюцинации"
                    ]
            res['response']['text'] = Session_data[user_id]['username'] + ', выбери группу'
            res['response']['buttons'] = get_suggests(user_id)
            current_dialog = "grock"
            current_status = "start"
            return
        if music_genre == 'популярное':
            user_id = req['session']['user_id']
            Session_data[user_id]['suggests'] = [
                        "Rauf & Faik",
                        "Егор Крид",
                        "Артур Пирожков"
                    ]
            res['response']['text'] = Session_data[user_id]['username'] + ', выбери исполнителя'
            res['response']['buttons'] = get_suggests(user_id)
            current_dialog = "gpop"
            current_status = "start"
            return
        if music_genre == 'классика':
            user_id = req['session']['user_id']
            Session_data[user_id]['suggests'] = [
                        "Ванесса Мэй",
                        "Wolfgang Amadeus Mozart",
                        "Antonio Vivaldi"
                    ]
            res['response']['text'] = Session_data[user_id]['username'] + ', выбери исполнителя'
            res['response']['buttons'] = get_suggests(user_id)
            current_dialog = "gklassika"
            current_status = "start"
            return
        else:
            user_id = req['session']['user_id']
            Session_data[user_id]['suggests'] = [
                        "Популярное",
                        "Классика",
                        "Рок"
                    ]
            res['response']['text'] = Session_data[user_id]['username'] + ', прости, я не знаю такого жанра. Выбери жанр'
            res['response']['buttons'] = get_suggests(user_id)
    return

def genre_rock(res, req):

    global current_status, current_dialog, Session_data
    if current_dialog == "grock":
        if req['request']['original_utterance'].lower() in ['louna', 'луна']:
                res['response']['text'] = 'Отлично! Эта группа одна из твоих любимых?'
                current_status = 'start'
                current_dialog = 'lou_rock'
        if req['request']['original_utterance'].lower() in ['ддт']:
                res['response']['text'] = 'Отлично! Эта группа одна из твоих любимых?'
                current_status = 'start'
                current_dialog = 'ddt_rock'
        if req['request']['original_utterance'].lower() in ['смысловые галлюцинации']:
                res['response']['text'] = 'Отлично! Эта группа одна из твоих любимых?'
                current_status = 'start'
                current_dialog = 'smgl_rock'
        if req['request']['original_utterance'].lower() in ['хватит']:
            current_dialog = "start"
            current_status = "start"
            res['response']['text'] = 'Ок'
            return
        else:
            res['response']['text'] = 'Прости, я не знаю такой группы. Назови другую'
    return

def text_ps(res, req):

    global current_status, current_dialog, Session_data
    if current_dialog == "txt_pesni":
        if req['request']['original_utterance'].lower() in ['altwall.net']:
            res['response']['buttons'] = [{
                'title': "altwall.net",
                'url': "https://altwall.net/texts.php",
                'hide': True
                }]
            res['response']['text'] = 'Одну секунду.'
            return
        if req['request']['original_utterance'].lower() in ['хватит']:
            current_dialog = "start"
            current_status = "start"
            res['response']['text'] = 'Ок'
            return
        else:
            res['response']['text'] = 'Я не знаю такого сайта('
    return

def sovet_f(res, req):

    global current_status, current_dialog, Session_data
    user_id = req['session']['user_id']
    if current_dialog == "d_sovet":
        if req['request']['original_utterance'].lower() in ['популярное']:
            user_id = req['session']['user_id']
            end_pop = ["Rauf & Faik – Детство", "Димы Билана – Молния", "Егора Крида – Время не пришло", "Rauf & Faik – Это ли счастье?", "Артура Пирожкова – Зацепила",]
            res['response']['text'] = 'Попробуй послушать новый трек ' +  random.choice(end_pop)
            Session_data[user_id]['suggests'] = [
                        'Нее, давай дальше',
                        'Открой яндекс музыку',
                        'Спасибо, мне нравится)',
                    ]
            res['response']['buttons'] = get_suggests(user_id)
            current_dialog = "pop_sovet"
            current_status = "start"
            return
        if req['request']['original_utterance'].lower() in ['классика']:
            user_id = req['session']['user_id']
            end_klassika = ["Ванесса Мэй – Квадро скрипка", "Robert Wyatt – Shipbuilding", "Wolfgang Amadeus Mozart – Музыка ангелов", "Antonio Vivaldi – Нарисуй мне дождь"]
            res['response']['text'] = 'Попробуй послушать новый трек ' +  random.choice(end_klassika)
            Session_data[user_id]['suggests'] = [
                        'Нее, давай дальше',
                        'Открой яндекс музыку',
                        'Спасибо, мне нравится)',
                    ]
            res['response']['buttons'] = get_suggests(user_id)
            current_dialog = "klassika_sovet"
            current_status = "start"
            return
        if req['request']['original_utterance'].lower() in ['рок']:
            user_id = req['session']['user_id']
            end_rock = ["Жуки – Батарейка", "Кино – Группа крови", "Гражданская оборона – Всё идёт по плану", "ПФ – Молодость", "Король и Шут – Прыгну со Скалы",]
            res['response']['text'] = 'Попробуй послушать что-то из этого: ' +  random.choice(end_rock) + "или" + random.choice(end_rock)
            Session_data[user_id]['suggests'] = [
                        'Нее, давай дальше',
                        'Открой яндекс музыку',
                        'Спасибо, мне нравится)',
                    ]
            res['response']['buttons'] = get_suggests(user_id)
            current_dialog = "rock_sovet"
            current_status = "start"
            return
        if req['request']['original_utterance'].lower() in ['хватит']:
            current_dialog = "start"
            current_status = "start"
            res['response']['text'] = 'Ок'
            return
        else:
            res['response']['text'] = 'Я не знаю такого жанра('
    if current_dialog == "pop_sovet":
        if req['request']['original_utterance'].lower() in ['нее, давай дальше']:
            end_pop = ["Rauf & Faik – Детство", "Димы Билана – Молния", "Егора Крида – Время не пришло", "Rauf & Faik – Это ли счастье?", "Артура Пирожкова – Зацепила",]

            Session_data[user_id]['suggests'] = [
                        'Нее, давай дальше',
                        'Открой яндекс музыку',
                        'Спасибо, мне нравится)',
                    ]
            res['response']['buttons'] = get_suggests(user_id)
            res['response']['text'] = 'Тогда попробуй послушать новый трек ' +  random.choice(end_pop)
            return
        if req['request']['original_utterance'].lower() in ['открой яндекс музыку']:
            res['response']['text'] = 'Открываю..'
            current_dialog = "start"
            current_status = "start"
            return
        if req['request']['original_utterance'].lower() in ['спасибо, мне нравится)']:
            res['response']['text'] = 'Я ж говорила, что она тебе понравится)'
            current_dialog = "start"
            current_status = "start"
            return
        if req['request']['original_utterance'].lower() in ['хватит']:
            current_dialog = "start"
            current_status = "start"
            res['response']['text'] = 'Ок'
            return
    if current_dialog == "rock_sovet":
        if req['request']['original_utterance'].lower() in ['нее, давай дальше']:
            user_id = req['session']['user_id']
            end_rock = ["Жуки – Батарейка", "Кино – Группа крови", "Гражданская оборона – Всё идёт по плану", "ПФ – Молодость", "Король и Шут – Прыгну со Скалы",]
            res['response']['text'] = 'Тогда попробуй послушать новый трек ' +  random.choice(end_rock)
            Session_data[user_id]['suggests'] = [
                        'Нее, давай дальше',
                        'Открой яндекс музыку',
                        'Спасибо, мне нравится)',
                    ]
            res['response']['buttons'] = get_suggests(user_id)
            return
        if req['request']['original_utterance'].lower() in ['открой яндекс музыку']:
            res['response']['text'] = 'Открываю..'
            current_dialog = "start"
            current_status = "start"
            return
        if req['request']['original_utterance'].lower() in ['спасибо, мне нравится)']:
            res['response']['text'] = 'Я ж говорила, что она тебе понравится)'
            current_dialog = "start"
            current_status = "start"
            return
        if req['request']['original_utterance'].lower() in ['хватит']:
            current_dialog = "start"
            current_status = "start"
            res['response']['text'] = 'Ок'
            return

    if current_dialog == "klassika_sovet":
        user_id = req['session']['user_id']
        if req['request']['original_utterance'].lower() in ['нее, давай дальше']:
            end_klassika = ["Ванесса Мэй – Квадро скрипка", "Robert Wyatt – Shipbuilding", "Wolfgang Amadeus Mozart – Музыка ангелов", "Antonio Vivaldi – Нарисуй мне дождь"]
            res['response']['text'] = 'Тогда попробуй послушать новый трек ' +  random.choice(end_klassika)
            Session_data[user_id]['suggests'] = [
                        'Нее, давай дальше',
                        'Открой яндекс музыку',
                        'Спасибо, мне нравится)',
                    ]
            res['response']['buttons'] = get_suggests(user_id)
            return
        if req['request']['original_utterance'].lower() in ['открой яндекс музыку']:
            res['response']['text'] = 'Открываю..'
            current_dialog = "start"
            current_status = "start"
            return
        if req['request']['original_utterance'].lower() in ['спасибо, мне нравится)']:
            res['response']['text'] = 'Я ж говорила, что она тебе понравится)'
            current_dialog = "start"
            current_status = "start"
            return
        if req['request']['original_utterance'].lower() in ['хватит']:
            current_dialog = "start"
            current_status = "start"
            res['response']['text'] = 'Ок'
            return
    return

def photo_f(res, req):

    global current_status, current_dialog, Session_data
    if current_dialog == "ph":
        if req['request']['original_utterance'].lower() in ['чернозём 2018']:
            res['response']['buttons'] = [{
                'title': "Чернозём 2018",
                'url': "https://yandex.ru/images/search?text=чернозём%202018",
                'hide': True
                }]
            res['response']['text'] = 'Одну секунду..'
            return
        if req['request']['original_utterance'].lower() in ['ддт (чернозём 2018)']:
            res['response']['buttons'] = [{
                'title': "ДДТ (чернозём 2018)",
                'url': "https://yandex.ru/images/search?text=%D0%B4%D0%B4%D1%82%20%D1%87%D0%B5%D1%80%D0%BD%D0%BE%D0%B7%D1%91%D0%BC%202018&family=yes",
                'hide': True
                }]
            res['response']['text'] = 'Одну секунду..'
            return
        if req['request']['original_utterance'].lower() in ['louna тамбов 2018']:
            res['response']['buttons'] = [{
                'title': "Louna тамбов 2018",
                'url': "https://yandex.ru/images/search?text=louna%20%D1%87%D0%B5%D1%80%D0%BD%D0%BE%D0%B7%D1%91%D0%BC%202018&family=yes",
                'hide': True
                }]
            res['response']['text'] = 'Одну секунду..'
            return
        if req['request']['original_utterance'].lower() in ['хватит']:
            current_dialog = "start"
            current_status = "start"
            res['response']['text'] = 'Ок'
            return
        else:
            res['response']['text'] = 'Я ничего не знаю об этом концерте('
    return


def genre_pop(res, req):

    global current_status, current_dialog, Session_data
    if current_dialog == "gpop":
        if req['request']['original_utterance'].lower() in ['rauf & faik']:
                res['response']['text'] = 'Отлично! Этот исполнитель один из твоих любимых?'
                current_status = 'start'
                current_dialog = 'raik_pop'
                return
        if req['request']['original_utterance'].lower() in ['егор крид']:
                res['response']['text'] = 'Отлично! Этот исполнитель один из твоих любимых?'
                current_status = 'start'
                current_dialog = 'egor_pop'
                return
        if req['request']['original_utterance'].lower() in ['артур пирожков']:
                res['response']['text'] = 'Отлично! Этот исполнитель один из твоих любимых?'
                current_status = 'start'
                current_dialog = 'art_pop'
                return
        if req['request']['original_utterance'].lower() in ['хватит']:
            current_dialog = "start"
            current_status = "start"
            res['response']['text'] = 'Ок'
            return
        else:
            res['response']['text'] = 'Прости, я не знаю такого исполнителя. Назови другого'
            return
    return

def genre_klassika(res, req):

    global current_status, current_dialog, Session_data
    if current_dialog == "gklassika":
        if req['request']['original_utterance'].lower() in ['ванесса мэй']:
                res['response']['text'] = 'Отлично! Этот исполнитель один из твоих любимых?'
                current_status = 'start'
                current_dialog = 'may_klassika'
                return
        if req['request']['original_utterance'].lower() in ['wolfgang amadeus mozart']:
                res['response']['text'] = 'Отлично! Этот исполнитель один из твоих любимых?'
                current_status = 'start'
                current_dialog = 'mozart_klassika'
                return
        if req['request']['original_utterance'].lower() in ['antonio vivaldi']:
                res['response']['text'] = 'Отлично! Этот исполнитель один из твоих любимых?'
                current_status = 'start'
                current_dialog = 'vivaldi_klassika'
                return
        if req['request']['original_utterance'].lower() in ['хватит']:
            current_dialog = "start"
            current_status = "start"
            res['response']['text'] = 'Ок'
            return
        else:
            res['response']['text'] = 'Прости, я не знаю такого исполнителя. Назови другого'
    return

def may(res, req):

    global current_status, current_dialog, Session_data
    if current_dialog == "may_klassika":

        if req['request']['original_utterance'].lower() in ['да', 'конечно', 'ага', 'угу',]:
            res['response']['text'] = 'Да у тебя отличный музыкальный вкус!'
            return
        elif req['request']['original_utterance'].lower() in ['правда', 'серьёзно', 'сарказм', 'думаешь',]:
            res['response']['text'] = 'Да, в этом я польностью уверена'
            return
        elif req['request']['original_utterance'].lower() in ['сомневаюсь', 'врешь', 'врёшь', 'обманываешь',]:
            res['response']['text'] = 'Нет, я честно!'
            return
        elif req['request']['original_utterance'].lower() in ['расскажи', 'группе', 'знаешь', 'можешь', 'кто', 'когда', 'состав', 'какая', 'концерты']:
            res['response']['text'] = 'Я могу немного рассказать о Ванессе Мэй: ' + 'Ванесса-Мэй Ванакорн Николсон (англ. Vanessa-Mae Vanakorn Nicholson; кит. 陳美, Chén Měi, род. 27 октября 1978) — британская скрипачка, композитор, горнолыжница, певица. Известна в основном благодаря техно-обработкам классических композиций. Стиль исполнения: «скрипичный техно-акустический фьюжн» (англ. violin techno-acoustic fusion), или «эстрадная скрипка».)'
            return
        elif req['request']['original_utterance'].lower() in ['песню', 'песни', 'трек', 'треки', 'музыка', 'музыку',]:
            res['response']['text'] = 'Я думаю Яндекс Музыка справится лучше меня, открыть Яндекс Музыку?'
            return
        elif req['request']['original_utterance'].lower() in ['открой']:
            res['response']['text'] = 'Ок, открываю Яндекс Музыку..'
            current_dialog = "start"
            current_status = "start"
            return
        elif req['request']['original_utterance'].lower() in ['хватит']:
            current_dialog = "start"
            current_status = "start"
            res['response']['text'] = 'Ок'
            return
        else:
            res['response']['text'] = 'Хмм, не желаешь что-нибудь спросить?'
    return

def mozart(res, req):

    global current_status, current_dialog, Session_data
    if current_dialog == "mozart_klassika":
        if req['request']['original_utterance'].lower() in ['да', 'конечно', 'ага', 'угу',]:
            res['response']['text'] = 'Да у тебя отличный музыкальный вкус!'
            return
        elif req['request']['original_utterance'].lower() in ['правда', 'серьёзно', 'сарказм', 'думаешь',]:
            res['response']['text'] = 'Да, в этом я польностью уверена'
            return
        elif req['request']['original_utterance'].lower() in ['сомневаюсь', 'врешь', 'врёшь', 'обманываешь',]:
            res['response']['text'] = 'Нет, я честно!'
            return
        elif req['request']['original_utterance'].lower() in ['расскажи', 'группе', 'знаешь', 'можешь', 'кто', 'когда', 'состав', 'какая', 'концерты']:
            res['response']['text'] = 'Я могу немного рассказать о Моцарте: ' + 'Полное имя — Иога́нн Хризосто́м Во́льфганг Амадéй Мо́царт; 27 января 1756, Зальцбург — 5 декабря 1791, Вена) — австрийский композитор и музыкант-виртуоз. Один из самых популярных классических композиторов, Моцарт оказал большое влияние на мировую музыкальную культуру.)'
            return
        elif req['request']['original_utterance'].lower() in ['песню', 'песни', 'трек', 'треки', 'музыка', 'музыку',]:
            res['response']['text'] = 'Я думаю Яндекс Музыка справится лучше меня, открыть Яндекс Музыку?'
            return
        elif req['request']['original_utterance'].lower() in ['открой']:
            res['response']['text'] = 'Ок, открываю Яндекс Музыку..'
            return
        elif req['request']['original_utterance'].lower() in ['хватит']:
            current_dialog = "start"
            current_status = "start"
            res['response']['text'] = 'Ок'
            return
        else:
            res['response']['text'] = 'Хмм, не желаешь что-нибудь спросить?'
    return

def vivaldi(res, req):

    global current_status, current_dialog, Session_data
    if current_dialog == "vivaldi_klassika":
        if req['request']['original_utterance'].lower() in ['да', 'конечно', 'ага', 'угу',]:
            res['response']['text'] = 'Да у тебя отличный музыкальный вкус!'
            return
        elif req['request']['original_utterance'].lower() in ['правда', 'серьёзно', 'сарказм', 'думаешь',]:
            res['response']['text'] = 'Да, в этом я польностью уверена'
            return
        elif req['request']['original_utterance'].lower() in ['сомневаюсь', 'врешь', 'врёшь', 'обманываешь',]:
            res['response']['text'] = 'Нет, я честно!'
            return
        elif req['request']['original_utterance'].lower() in ['расскажи', 'группе', 'знаешь', 'можешь', 'кто', 'когда', 'состав', 'какая', 'концерты']:
            res['response']['text'] = 'Я могу немного рассказать о Vivaldi: ' + 'Итальянский композитор, скрипач-виртуоз, педагог, дирижёр, католический священник. Вивальди считается одним из крупнейших представителей итальянского скрипичного искусства XVIII века, при жизни получил широкое признание во всей Европе. Мастер ансамблево-оркестрового концерта — кончерто гроссо, автор около 40 опер. Вивальди в основном известен благодаря своим инструментальным концертам, в особенности для скрипки. Одними из наиболее известных его работ являются четыре скрипичных концерта «Времена года»..'
            return
        elif req['request']['original_utterance'].lower() in ['песню', 'песни', 'трек', 'треки', 'музыка', 'музыку',]:
            res['response']['text'] = 'Я думаю Яндекс Музыка справится лучше меня, открыть Яндекс Музыку?'
            return
        elif req['request']['original_utterance'].lower() in ['открой']:
            res['response']['text'] = 'Ок, открываю Яндекс Музыку..'
            return
        elif req['request']['original_utterance'].lower() in ['хватит']:
            current_dialog = "start"
            current_status = "start"
            res['response']['text'] = 'Ок'
            return
        else:
            res['response']['text'] = 'Хмм, не желаешь что-нибудь спросить?'
    return

def raik(res, req):

    global current_status, current_dialog, Session_data
    if current_dialog == "raik_pop":
        if req['request']['original_utterance'].lower() in ['да', 'конечно', 'ага', 'угу',]:
            res['response']['text'] = 'Да у тебя отличный музыкальный вкус!'
            return
        elif req['request']['original_utterance'].lower() in ['правда', 'серьёзно', 'сарказм', 'думаешь',]:
            res['response']['text'] = 'Да, в этом я польностью уверена'
            return
        elif req['request']['original_utterance'].lower() in ['сомневаюсь', 'врешь', 'врёшь', 'обманываешь',]:
            res['response']['text'] = 'Нет, я честно!'
            return
        elif req['request']['original_utterance'].lower() in ['расскажи', 'группе', 'знаешь', 'можешь', 'кто', 'когда', 'состав', 'какая', 'концерты']:
            res['response']['text'] = 'Я могу немного рассказать о rauf & faik: ' + 'Rauf & Faik (Рау́ф и Фáик) — российский музыкальный дуэт, состоящий из братьев-двойняшек Рауфа и Фаика Мирзаевых из Азербайджана (родились 7 июля 1999 году в Ижевске)'
            return
        elif req['request']['original_utterance'].lower() in ['песню', 'песни', 'трек', 'треки', 'музыка', 'музыку',]:
            res['response']['text'] = 'Я думаю Яндекс Музыка справится лучше меня, открыть Яндекс Музыку?'
            return
        elif req['request']['original_utterance'].lower() in ['открой']:
            res['response']['text'] = 'Ок, открываю Яндекс Музыку..'
            return
        elif req['request']['original_utterance'].lower() in ['хватит']:
            current_dialog = "start"
            current_status = "start"
            res['response']['text'] = 'Ок'
            return
        else:
            res['response']['text'] = 'Хмм, не желаешь что-нибудь спросить?'
    return

def egor(res, req):

    global current_status, current_dialog, Session_data
    if current_dialog == "egor_pop":
        if req['request']['original_utterance'].lower() in ['да', 'конечно', 'ага', 'угу',]:
            res['response']['text'] = 'Да у тебя отличный музыкальный вкус!'
            return
        elif req['request']['original_utterance'].lower() in ['правда', 'серьёзно', 'сарказм', 'думаешь',]:
            res['response']['text'] = 'Да, в этом я польностью уверена'
            return
        elif req['request']['original_utterance'].lower() in ['сомневаюсь', 'врешь', 'врёшь', 'обманываешь',]:
            res['response']['text'] = 'Нет, я честно!'
            return
        elif req['request']['original_utterance'].lower() in ['расскажи', 'группе', 'знаешь', 'можешь', 'кто', 'когда', 'состав', 'какая', 'концерты']:
            res['response']['text'] = 'Я могу немного рассказать о Егоре Криде: ' + 'Егор Николаевич Булаткин (род. 25 июня 1994, Пенза, Россия) более известный под сценическим псевдонимом Егор Крид — российский певец и автор песен. Сольную карьеру начал в 2011 году, с тех пор выпустил два студийных альбома.'
            return
        elif req['request']['original_utterance'].lower() in ['песню', 'песни', 'трек', 'треки', 'музыка', 'музыку',]:
            res['response']['text'] = 'Я думаю Яндекс Музыка справится лучше меня, открыть Яндекс Музыку?'
            return
        elif req['request']['original_utterance'].lower() in ['открой']:
            res['response']['text'] = 'Ок, открываю Яндекс Музыку..'
            return
        elif req['request']['original_utterance'].lower() in ['хватит']:
            current_dialog = "start"
            current_status = "start"
            res['response']['text'] = 'Ок'
            return
        else:
            res['response']['text'] = 'Хмм, не желаешь что-нибудь спросить?'
    return

def art(res, req):

    global current_status, current_dialog, Session_data
    if current_dialog == "art_pop":
        if req['request']['original_utterance'].lower() in ['да', 'конечно', 'ага', 'угу',]:
            res['response']['text'] = 'Да у тебя отличный музыкальный вкус!'
            return
        elif req['request']['original_utterance'].lower() in ['правда', 'серьёзно', 'сарказм', 'думаешь',]:
            res['response']['text'] = 'Да, в этом я польностью уверена'
            return
        elif req['request']['original_utterance'].lower() in ['сомневаюсь', 'врешь', 'врёшь', 'обманываешь',]:
            res['response']['text'] = 'Нет, я честно!'
            return
        elif req['request']['original_utterance'].lower() in ['расскажи', 'группе', 'знаешь', 'можешь', 'кто', 'когда', 'состав', 'какая', 'концерты']:
            res['response']['text'] = 'Я могу немного рассказать о Артуре: ' + 'Сейчас Александр Ревва продолжает с успехом развивать персонаж Артура Пирожкова на сцене и телевидении. Актер регулярно публикует фото в полюбившемся образе на странице «Инстаграма».'
            return
        elif req['request']['original_utterance'].lower() in ['песню', 'песни', 'трек', 'треки', 'музыка', 'музыку',]:
            res['response']['text'] = 'Я думаю Яндекс Музыка справится лучше меня, открыть Яндекс Музыку?'
            return
        elif req['request']['original_utterance'].lower() in ['открой']:
            res['response']['text'] = 'Ок, открываю Яндекс Музыку..'
            return
        elif req['request']['original_utterance'].lower() in ['хватит']:
            current_dialog = "start"
            current_status = "start"
            res['response']['text'] = 'Ок'
            return
        else:
            res['response']['text'] = 'Хмм, не желаешь что-нибудь спросить?'
    return

def louna(res, req):

    global current_status, current_dialog, Session_data
    if current_dialog == "lou_rock":
        if req['request']['original_utterance'].lower() in ['да', 'конечно', 'ага', 'угу',]:
            res['response']['text'] = 'Да у тебя отличный музыкальный вкус!'
            return
        elif req['request']['original_utterance'].lower() in ['правда', 'серьёзно', 'сарказм', 'думаешь',]:
            res['response']['text'] = 'Да, в этом я польностью уверена'
            return
        elif req['request']['original_utterance'].lower() in ['сомневаюсь', 'врешь', 'врёшь', 'обманываешь',]:
            res['response']['text'] = 'Нет, я честно!'
            return
        elif req['request']['original_utterance'].lower() in ['расскажи', 'группе', 'знаешь', 'можешь', 'кто', 'когда', 'состав', 'какая', 'концерты']:
            res['response']['text'] = 'Я могу немного рассказать тебе о этой группе: ' + 'Louna — российская рок-группа с женским вокалом. ' + 'Музыканты: ' + '1. Лусинэ «Лу» Геворкян — вокал ' + '2. Виталий «Вит» Демиденко — бас-гитара, бэк-вокал ' + '3. Рубен «Ру» Казарьян — гитара, бэк-вокал ' + '4. Сергей «Серж» Понкратьев — гитара, бэк-вокал ' + '5. Леонид «Пилот» Кинзбурский — барабаны '
            return
        elif req['request']['original_utterance'].lower() in ['песню', 'песни', 'трек', 'треки', 'музыка', 'музыку',]:
            res['response']['text'] = 'Я думаю Яндекс Музыка справится лучше меня, открыть Яндекс Музыку?'
            return
        elif req['request']['original_utterance'].lower() in ['открой']:
            res['response']['text'] = 'Ок, открываю Яндекс Музыку..'
            return
        elif req['request']['original_utterance'].lower() in ['хватит']:
            current_dialog = "start"
            current_status = "start"
            res['response']['text'] = 'Ок'
            return
        else:
            res['response']['text'] = 'Хмм, не желаешь что-нибудь спросить?'
    return

def ddt(res, req):

    global current_status, current_dialog, Session_data
    if current_dialog == "ddt_rock":
        if req['request']['original_utterance'].lower() in ['да', 'конечно', 'ага', 'угу',]:
            res['response']['text'] = 'Да у тебя отличный музыкальный вкус!'
            return
        elif req['request']['original_utterance'].lower() in ['правда', 'серьёзно', 'сарказм', 'думаешь',]:
            res['response']['text'] = 'Да, в этом я польностью уверена'
            return
        elif req['request']['original_utterance'].lower() in ['сомневаюсь', 'врешь', 'врёшь', 'обманываешь',]:
            res['response']['text'] = 'Нет, я честно!'
            return
        elif req['request']['original_utterance'].lower() in ['расскажи', 'группе', 'знаешь', 'можешь', 'кто', 'когда', 'состав', 'какая', 'концерты']:
            res['response']['text'] = 'Я могу немного рассказать тебе о этой группе: ' + '«ДДТ» (DDT) — советская и российская рок-группа, основанная летом 1980 года в Уфе. Лидер группы, автор большинства песен и единственный бессменный участник — Юрий Шевчук.'
            return
        elif req['request']['original_utterance'].lower() in ['песню', 'песни', 'трек', 'треки', 'музыка', 'музыку',]:
            res['response']['text'] = 'Я думаю Яндекс Музыка справится лучше меня, открыть Яндекс Музыку?'
            return
        elif req['request']['original_utterance'].lower() in ['открой']:
            res['response']['text'] = 'Ок, открываю Яндекс Музыку..'
            return
        elif req['request']['original_utterance'].lower() in ['хватит']:
            current_dialog = "start"
            current_status = "start"
            res['response']['text'] = 'Ок'
            return
        else:
            res['response']['text'] = 'Хмм, не желаешь что-нибудь спросить?'
    return

def smgl(res, req):

    global current_status, current_dialog, Session_data
    if current_dialog == "smgl_rock":
        if req['request']['original_utterance'].lower() in ['да', 'конечно', 'ага', 'угу',]:
            res['response']['text'] = 'Да у тебя отличный музыкальный вкус!'
            return
        elif req['request']['original_utterance'].lower() in ['правда', 'серьёзно', 'сарказм', 'думаешь',]:
            res['response']['text'] = 'Да, в этом я польностью уверена'
            return
        elif req['request']['original_utterance'].lower() in ['сомневаюсь', 'врешь', 'врёшь', 'обманываешь',]:
            res['response']['text'] = 'Нет, я честно!'
            return
        elif req['request']['original_utterance'].lower() in ['расскажи', 'группе', 'знаешь', 'можешь', 'кто', 'когда', 'состав', 'какая', 'концерты']:
            res['response']['text'] = '«Смысловы́е Галлюцина́ции» — советская и российская рок-группа из Екатеринбурга. Первоначально относилась к панк-рок-группам Свердловска, позднее стиль группы стал тяготеть к пост-панку и инди-року.' + 'Музыканты: ' +  '1.Сергей Бобунец — вокал, акустика, электрогитара, музыка, текстыал ' + '2.Константин Лекомцев — клавишные, саксофон, гитара, бэк-вокал, аранжировки, музыка, тексты' + '3.Николай Ротов — бас-гитара ' + '4. Максим Митенков — ударные, вокал, тексты ' + '5. Евгений Гантимуров — гитара '
            return
        elif req['request']['original_utterance'].lower() in ['песню', 'песни', 'трек', 'треки', 'музыка', 'музыку',]:
            res['response']['text'] = 'Я думаю Яндекс Музыка справится лучше меня, открыть Яндекс Музыку?'
            return
        elif req['request']['original_utterance'].lower() in ['открой']:
            res['response']['text'] = 'Ок, открываю Яндекс Музыку..'
            return
        elif req['request']['original_utterance'].lower() in ['хватит']:
            current_dialog = "start"
            current_status = "start"
            res['response']['text'] = 'Ок'
            return
        else:
            res['response']['text'] = 'Хмм, не желаешь что-нибудь спросить?'
    return



def get_first_name(req):
    for entity in req['request']['nlu']['entities']:
        if entity['type'] == 'YANDEX.FIO':
            return entity['value'].get('first_name', None)


def get_suggests(user_id):
    session = Session_data[user_id]
    suggests = [
        {'title': suggest, 'hide': True}
        for suggest in session['suggests']
    ]
    Session_data[user_id] = session

    return suggests


if __name__ == '__main__':
    app.run()
