import requests
import urllib
def translate(text,hint='en',lang='ru',key = "trnsl.1.1.20190401T141303Z.df3305cf098f00f8.836327f2e8520442fad0173356e900eaf4b92249"):
    request = f"https://translate.yandex.net/api/v1.5/tr.json/translate?key={key}&text={urllib.parse.quote(text)}&lang={lang}"


    response = requests.get(request)
    if response:
        # Преобразуем ответ в json-объект
        json_response = response.json()
    else:
        raise RuntimeError(
            f"""Ошибка выполнения запроса:
            {response}
            Http статус: {response.status_code} ({response.reason})""")
    return json_response['text']
