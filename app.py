import vk_api
import os
from vk import get_user_info, send_message, get_popular_photos, get_photo_attachment_link
from vk_api.longpoll import VkLongPoll, VkEventType
from user import User, UserMatching, UserSearchFilter

COMMUNITY_TOKEN = os.getenv('COMMUNITY_TOKEN')
USER_TOKEN = os.getenv('USER_TOKEN')

vk_session = vk_api.VkApi(token=USER_TOKEN)
vk_group = vk_api.VkApi(token=COMMUNITY_TOKEN)
longpoll = VkLongPoll(vk_group)


def start():
    favourites = []
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            user_id = event.user_id
            chat_id = event.chat_id
            user_info = get_user_info(vk_session, user_id)
            app_user = User(user_id=user_id,
                            first_name=user_info[0]['first_name'],
                            last_name=user_info[0]['last_name'])
            if app_user.stage == 0:
                req_city_id = user_info[0]['city']['id']
                if user_info[0]['sex'] == 1:
                    req_sex = 2
                elif user_info[0]['sex'] == 2:
                    req_sex = 1
                send_message(vk_group, chat_id,
                             "Привет!\nМеня зовут VKinder, и я - бот для поиска пары.\n"
                             "Укажи интересующий тебя возрастной диапазон\nВ формате '18 99', где:\n"
                             "18 - минимальный возраст,\n99 - максимальный возраст")
                words = event.text.split()
                age_from = int(words[0])
                age_to = int(words[1])
                send_message(vk_group, chat_id,
                             f"Ок. Буду искать не моложе {age_from}"
                             f"и не старше {age_to} лет.\nНачинаем(Да/Нет)")
                app_user.search_filter = UserSearchFilter(city_id=req_city_id, sex=req_sex,
                                                          age_from=age_from, age_to=age_to)
                user_mathcing = UserMatching(vk_session=vk_session, current_user=app_user)
                app_user.stage += 1
                if app_user.stage == 1:
                    if event.text.lower() == 'да':
                        send_message(vk_group, chat_id, "Ищу...")
                        user_mathcing.next()
                        variant = user_mathcing.next()
                        if variant is not None:
                            photos = get_popular_photos(vk_session, variant['id'])
                            send_message(vk_group, chat_id,
                                         f"{variant['first_name']} {variant['last_name']}\n"
                                         f"https://vk.com/id{variant['id']}\n",
                                         reply_to=event.message_id,
                                         attachments=list(map(get_photo_attachment_link, photos)))
                            send_message(vk_group, chat_id,
                                         "\n\n1 - добавить в Избранное\n0 - просмотреть Избранное\n"
                                         "R - начать сначала\n\n"
                                         "Продолжить поиск? (Да/Нет)\n")
                        else:
                            send_message(vk_group, chat_id,
                                         "Похоже больше я не смогу ничего найти.\n"
                                         "0 - просмотреть Избранное\n"
                                         "R - начать сначала")
                    elif event.text.lower() == '1':
                        send_message(vk_session, chat_id,
                                     "Добавляю в Избранное...\n\n"
                                     "0 - просмотреть Избранное\n"
                                     "R - начать сначала"
                                     "Продолжить поиск? (Да/Нет)")
                        favourites.append(variant['id'])
                    elif event.text == '0':
                        send_message(vk_session, chat_id, "Избранное:")
                        for favourite in favourites:
                            favourite_info = get_user_info(vk_session, favourite)
                            favourite_name = favourite_info[0]['first_name']
                            favourite_surname = favourite_info[0]['last_name']
                            photos = get_popular_photos(vk_session, favourite)
                            send_message(vk_group, chat_id, message=f"\n\n{favourite_name} {favourite_surname}\n"
                                                                    f"https://vk.com/id{favourite}\n",
                                         reply_to=event.message_id,
                                         attachments=list(map(get_photo_attachment_link, photos)))
                            send_message(vk_session, chat_id,
                                         "\n\nR - начать сначала"
                                         "Поискать ещё? (Да/Нет)")
                    elif event.text.lower() == 'нет':
                        send_message(vk_group, chat_id,
                                     "Поиск остановлен.\nДа - поиск\n "
                                     "0 - просмотреть Избранное\n"
                                     "R - начать сначала")
                    elif event.text.lower() == 'r':
                        send_message(vk_group, chat_id,
                                     "Перезапуск...\n"
                                     "Избранные сохраняются\n")
                        app_user.stage = 0
