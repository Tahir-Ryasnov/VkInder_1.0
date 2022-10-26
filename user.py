import vk_api
import vk

CACHE_VARIANT_COUNT = 5


class UserSearchFilter:
    def __init__(self, city_id: int, sex: int, age_from: int, age_to: int, status: int = 6, offset: int = 0):
        self._city_id = city_id
        self._age_from = age_from
        self._age_to = age_to
        self._status = status
        self.offset = offset
        self.sex = sex

    @property
    def city_id(self):
        return self._city_id

    @city_id.setter
    def city_id(self, city_id: int):
        self.reset_offset()
        self._city_id = city_id

    @property
    def age_from(self):
        return self._age_from

    @age_from.setter
    def age_from(self, age: int):
        self.reset_offset()
        self._age_from = age

    @property
    def age_to(self):
        return self._age_to

    @age_to.setter
    def age_to(self, age: int):
        self.reset_offset()
        self._age_to = age

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, new_status):
        self._status = new_status
        self.offset = 0

    def reset_offset(self):
        self._status = 6
        self.offset = 0


class User:
    def __init__(self, user_id, first_name: str, last_name: str, stage: int = 0,
                 search_filter: UserSearchFilter = None):
        self._variants = []
        self.stage = stage
        self.user_id = user_id
        self.first_name = first_name
        self.last_name = last_name
        self.search_filter = search_filter


class UserMatching:
    def __init__(self, vk_session: vk_api, current_user: User):
        self._variants = []
        self._vk = vk_session
        self.user = current_user

    def next(self):
        if self._variants is None:
            if self.user.search_filter.status == 6:
                self.user.search_filter.status = 1
                self._variants = []
                return self.next()
            else:
                return None
        if len(self._variants):
            self.user.search_filter.offset += 1
            return self._variants.pop(0)
        params = self.user.search_filter
        if not (params and params.city_id and params.sex and params.age_from and params.age_to and params.status):
            raise Exception('Фильтры поиска не заполнены!')
        self._variants = vk.get_open_user_pages(vk=self._vk, count=CACHE_VARIANT_COUNT, city_id=params.city_id,
                                                sex=params.sex, age_from=params.age_from, age_to=params.age_to,
                                                status=params.status, offset=params.offset)
        return self.next()



""" 
# Пример использования этих классов:
app_user = user.User(user_id=12345, first_name='Иван', last_name='Иванов')
# в этом случае stage(сцена) равна нулю - пользователь впервые обратился
# параметры поиска (search_filter) не заданы, можно задать их:
app_user.search_filter = user.UserSearchFilter(city_id=1, sex=1, age_from=20, age_to: 25)

# когда меняются свойства city_id, age_from или age_to, offset поиска и фильтр по статусу меняются на дефолтные (0 и 6)
app_user.search_filter.offset = 1
app_user.search_filter.status = 0
app_user.search_filter.city_id = 2
assert(app_user.search_filter.offset == 0 and app_user.search_filter.status == 6)

# также сбрасывается offset когда меняется свойство status:
app_user.search_filter.offset = 1
app_user.search_filter.status = 1
assert(app_user.search_filter.offset == 0)

# чтобы было удобно получать следующие варианты:
vk_session = vk_api.VkApi(token=USER_TOKEN)
# нужно передать в инициализатор UserMatching сессию vk_api ля работы функций VK API
user_matching = user.UserMatching(vk_session=vk_session, current_user=app_user)
# следующий вариант представляет собой словарь (ответ метода users.search VK API ), его можно получить так:
variant = user_matching.next()
# когда все варианты со статусом 6 (активный поиск) закончатся, статус автоматически сменится на 1 (не женат/не замужем)
# и варианты будут выдаваться до тех пор, пока variant не равен None:
if variant is None:
    print('вариантов не осталось')
    
# удобно хранить экзэмпляры UserMatching в списке для петли получения новых сообщений, он уже хранит в себе User 
assert(user_matching.user.first_name == 'Иван')
# можно управлять сценой, например в первой сцене мы ждем возрастной диапазаон:
user_matching.user.stage = 1
age_from, age_to = input('Введите возраст в формате <от до>, например: 30-40').split(' ')
# когда получаем сообщение от юзера на первой сцене, можем поменять параметры поиска:
if user_matching.user.stage == 1:
    user_matching.user.search_filter.age_from = age_from
    user_matching.user.search_filter.age_to = age_to
"""
