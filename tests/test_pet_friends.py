from api import PetFriends
from settings import *
import os

pf = PetFriends()


def test_get_api_key_for_valid_user(email=valid_email, password=valid_password):
    """ Проверяем что запрос api ключа возвращает статус 200 и в результате содержится слово key"""

    # Отправляем запрос и сохраняем полученный ответ с кодом статуса в status, а текст ответа в result
    status, result = pf.get_api_key(email, password)

    # Сверяем полученные данные с нашими ожиданиями
    assert status == 200
    assert 'key' in result


def test_get_all_pets_with_valid_key(filter=''):
    """ Проверяем что запрос всех питомцев возвращает не пустой список.
    Для этого сначала получаем api ключ и сохраняем в переменную auth_key. Далее используя этого ключ
    запрашиваем список всех питомцев и проверяем что список не пустой.
    Доступное значение параметра filter - 'my_pets' либо '' """

    _, auth_key = pf.get_api_key(valid_email, valid_password)
    status, result = pf.get_list_of_pets(auth_key, filter)
    assert status == 200
    assert len(result['pets']) > 0


def test_add_new_pet_simple(name='Барбоскин', animal_type='двортерьер', age='4'):
    """Проверяем возможность добавления питомца без фото"""
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    status, result = pf.add_new_pet_simple(auth_key, name, animal_type, age)
    assert status == 200
    assert result['name'] == name


def test_pet_set_photo(pet_photo='images/cat1.jpg'):
    """Проверяем возможность обновления или добавления фото питомца"""
    # Получаем ключ auth_key и список своих питомцев
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Проверяем - если список своих питомцев пустой, то добавляем нового и опять запрашиваем список своих питомцев
    if len(my_pets['pets']) == 0:
        pf.add_new_pet_simple(auth_key, "Tiger", "кот", "3")
        _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    pet_id = my_pets['pets'][0]['id']
    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)
    status, result = pf.post_pet_set_photo(auth_key, pet_id, pet_photo)

    assert status == 200
    assert pet_id not in my_pets.values()


def test_successful_update_pet_info(name='Мурзик', animal_type='Котэ', age=5):
    """Проверяем возможность обновления информации о питомце"""

    # Получаем ключ auth_key и список своих питомцев
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Еслди список не пустой, то пробуем обновить его имя, тип и возраст
    if len(my_pets['pets']) > 0:
        status, result = pf.update_pet_info(auth_key, my_pets['pets'][0]['id'], name, animal_type, age)

        # Проверяем что статус ответа = 200 и имя питомца соответствует заданному
        assert status == 200
        assert result['name'] == name
    else:
        # если спиок питомцев пустой, то выкидываем исключение с текстом об отсутствии своих питомцев
        raise Exception("There is no my pets")


def test_successful_delete_pet():
    """Проверяем возможность удаления питомца"""

    # Получаем ключ auth_key и запрашиваем список своих питомцев
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Проверяем - если список своих питомцев пустой, то добавляем нового и опять запрашиваем список своих питомцев
    if len(my_pets['pets']) == 0:
        pf.add_new_pet_simple(auth_key, "Суперкот", "кот", "3")
        _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Берём id первого питомца из списка и отправляем запрос на удаление
    pet_id = my_pets['pets'][0]['id']
    status, _ = pf.delete_pet(auth_key, pet_id)

    # Ещё раз запрашиваем список своих питомцев
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Проверяем что статус ответа равен 200 и в списке питомцев нет id удалённого питомца
    assert status == 200
    assert pet_id not in my_pets.values()



                # НЕГАТИВНЫЕ ТЕСТЫ


# № 1 GET Негативный тест на ввод неверного email при запросе api_key

def test_get_api_key_for_invalid_email(email=invalid_email, password=valid_password):
    status, result = pf.get_api_key(email, password)

    # Проверяем что статус ответа равен 403 т.е. введены неверные данные
    assert status == 403


# № 2 GET Негативный тест на ввод неверного пароля при запросе api_key

def test_get_api_key_for_invalid_password(email=valid_email, password=invalid_password):
    status, result = pf.get_api_key(email, password)

    # Проверяем что статус ответа равен 403 т.е. введены неверные данные
    assert status == 403


# № 3 POST Негативный тест на ввод неверного auth_key при добавлении питомца

def test_add_new_pet_with_valid_data_simple_invalid_auth_key(name="Барт", animal_type='двортерьер', age='4'):
    status, result = pf.add_new_pet_simple_invalid_auth_key(invalid_auth_key, name, animal_type, age)

    # Проверяем что статус ответа равен 403 т.е. введен неверный auth_key
    assert status == 403


# № 4 POST Негативный тест на ввод числа в поле name при добавлении питомца

def test_add_new_pet_with_valid_data_simple_invalid_name(name="123", animal_type='двортерьер',
                                     age='4'):
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    status, result = pf.add_new_pet_simple(auth_key, name, animal_type, age)

    if status == 200:
        print("БАГ - форма не должна принимать в поле 'ИМЯ' числовые значения")
    else:
        print("Норма")
    assert status == 400


# № 5 POST Негативный тест на ввод числа в поле animal_type при добавлении питомца

def test_add_new_pet_with_valid_data_simple_invalid_animal_type(name="Karl", animal_type='123',
                                     age='4'):
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    status, result = pf.add_new_pet_simple(auth_key, name, animal_type, age)

    if status == 200:
        print("БАГ - форма не должна принимать в поле 'ПОРОДА' числовые значения")
    else:
        print("Норма")
    assert status == 400


# № 6 POST Негативный тест на ввод букв в поле age при добавлении питомца

def test_add_new_pet_with_valid_data_simple_invalid_age(name="Karl", animal_type='dog', age='odin'):
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    status, result = pf.add_new_pet_simple(auth_key, name, animal_type, age)

    if status == 200:
        print("БАГ - форма не должна принимать в поле 'ВОЗРАСТ' буквенные значения")
    else:
        print("Норма")
    assert status == 400


# № 7 GET Негативный тест на ввод неверного auth_key типа string

def test_get_all_pets_with_invalid_key_str(filter=''):

    status, result = pf.get_list_of_pets_invalid_auth_key(invalid_auth_key, filter)

    # Проверяем что статус ответа равен 403 т.е. введен неверный auth_key
    assert status == 403


# № 8 POST Негативный тест на ввод неверного параметра path pet_id при обновлении фото питомца

def test_add_photo_pet_invalid_pet_id(pet_photo='images/cat1.jpg'):
    """Проверяем возможность обновления фото питомца с неверным pet_id"""

    # Получаем ключ auth_key и список своих питомцев
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Проверяем - если список своих питомцев пустой, то добавляем нового и опять запрашиваем список своих питомцев
    if len(my_pets['pets']) == 0:
        pf.add_new_pet_simple(auth_key, "Tiger", "кот", "3")
        _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    pet_id = my_pets['pets'][0]['id']
    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)
    status, result = pf.post_add_photo_pet_invalid_pet_id(auth_key, pet_id, pet_photo)

    # Проверяем что статус ответа равен 404 т.е. введены неверные данные
    assert status == 404


# № 9 POST Негативный тест на ввод неверного id при обновлении фото питомца

def test_add_photo_pet_invalid_auth_key(pet_photo='images/cat1.jpg'):
    """Проверяем возможность обновления фото питомца с неверным auth_key"""

    # Получаем ключ auth_key и список своих питомцев
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Проверяем - если список своих питомцев пустой, то добавляем нового и опять запрашиваем список своих питомцев
    if len(my_pets['pets']) == 0:
        pf.add_new_pet_simple(auth_key, "Tiger", "кот", "3")
        _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    pet_id = my_pets['pets'][0]['id']
    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)
    status, result = pf.post_add_photo_pet_invalid_auth_key(invalid_auth_key, pet_id, pet_photo)

    # Проверяем что статус ответа равен 403 т.е. введен неверный auth_key
    assert status == 403


# № 10 DELETE Негативный тест на ввод неверного auth_key при удалении питомца

def test_unsuccessful_delete_pet_invalid_auth_key():
    """Проверяем возможность удаления питомца при вводе неверного auth_key"""

    # Получаем ключ auth_key и запрашиваем список своих питомцев
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Проверяем - если список своих питомцев пустой, то добавляем нового и опять запрашиваем список своих питомцев
    if len(my_pets['pets']) == 0:
        pf.add_new_pet_simple(auth_key, "Суперкот", "кот", "3")
        _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Берём id первого питомца из списка и отправляем запрос на удаление
    pet_id = my_pets['pets'][0]['id']
    status, _ = pf.unsuccessful_delete_pet_invalid_auth_key(invalid_auth_key, pet_id)

    # Проверяем что статус ответа равен 403 т.е. введен неверный auth_key
    assert status == 403
