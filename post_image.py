from requests import post
def post_image(skill_id, token, filename):
    url = f'https://dialogs.yandex.net/api/v1/skills/{skill_id}/images'
    files = {'file': open(filename, 'rb')}
    headers = {'Authorization': f'OAuth {token}'}
    s = post(url, files=files, headers=headers)
    print(s.json())


token = "AQAAAAACFWAxAAT7owUAyPAPHExvhBizbv_MIJI"
skill = "df580121-04cd-4e5c-aaff-13fd7077f6a4"
image = "ddt.jpg"
post_image(skill,token,image)
image = "egor.png"
post_image(skill,token,image)
image = "louna.jpg"
post_image(skill,token,image)
image = "may.jpg"
post_image(skill,token,image)
image = "mozart.jpg"
post_image(skill,token,image)
image = "pirozhkov.jpg"
post_image(skill,token,image)
image = "rauffaik.jpg"
post_image(skill,token,image)
image = "smgl.jpg"
post_image(skill,token,image)
image = "vivaldi.jpg"
post_image(skill,token,image)