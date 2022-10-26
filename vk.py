import vk_api
from vk_api.utils import get_random_id


# vk: vk_api.VkApi - о всех функциях первым аргументом является инстанс VkApi
# он создается так: vk = vk_api.VkApi(token=token)
def get_user_info(vk: vk_api.VkApi, user_id):
    user_info = vk.method("users.get", {"user_ids": user_id, "fields": "city, sex"})
    return user_info


def get_popular_photos(vk: vk_api.VkApi, user_id, count=3):
    photos = vk.method("photos.get", {
        "owner_id": user_id,
        "album_id": "profile",
        "extended": 1,
        "count": 1000
    })
    return list(sorted(photos["items"], key=lambda x: x["likes"]["count"], reverse=True)[:count])


# нельзя найти более 1000 пользователей, даже если указать офсет 1000
# поэтому придется играть на критериях, как вариант:
# сначала выводить "в активном поиске", потом "не женат/не замужем" (нет фильтра "статус не указан")
def get_open_user_pages(vk: vk_api.VkApi, city_id, sex, age_from: int, age_to: int, status=6, count=10, offset=0):
    """
    :param vk:
    :param city_id: id города
    :param sex: пол 1 - женский, 2 - мужской
    :param from_age: начало возрастного диапазона
    :param age_to: конец возрастного диапазона
    :param status: 6 по умолчанию - в активном поиске, 0 - любой
    :param count: количество для выборки до фильтрации
    :param offset: смещение для выборки до фильтрации
    :return: в результате может вернуть пустой массив, так как все найденные профили могут быть пустыми
    """
    users = vk.method('users.search', {
        "city": city_id,
        "sex": sex,
        "sort": 0,
        "from_age": age_from,
        "age_to": age_to,
        "age_from": 1,
        "status": status,
        "count": count,
        "offset": offset,
    })
    if not users.get('count'):
        return None
    return [user for user in users['items'] if user['can_access_closed']]


# attachment - это список медиассылок, например для фото они выглядят так:
# ["photo<owner_id>_<photo_id>, ...]
# переформатировать фото, полученные функцией get_popular_photos, в медиассылки можно так:
# map(get_photo_attachment_link, get_popular_photos(*args))

def send_message(vk: vk_api.VkApi, chat_id, message, attachments: list = [], reply_to=None):
    result = vk.method("messages.send", {
        "chat_id": chat_id,
        "message": message,
        "random_id": get_random_id(),
        "attachment": ",".join(attachments),
        "reply_to": reply_to
    })
    return result



def get_photo_attachment_link(photo):
    if 'owner_id' not in photo or 'id' not in photo:
        return None
    return f"photo{photo['owner_id']}_{photo['id']}"
