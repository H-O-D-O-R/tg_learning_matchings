from app.database.models import main_async_session
from app.database.user_models import get_user_database
from app.database.models import User
from app.database.user_models import UserDict, Category, Item
from sqlalchemy import select, update
from datetime import date, timedelta



#Проверка новый ли пользователь
async def is_new_user(user_id):

    async with main_async_session() as session:
        return await session.scalars(
            select(User)
            .where(User.user_id == user_id)
        )

#Добавление новго пользователя в общую бд
async def add_new_user(user_name, user_id):

    async with main_async_session() as session:
        session.add(
            User(
                username=user_name,
                user_id=user_id
                )
            )
        await session.commit()

#Вывод пользовательских словарей
async def get_user_dicts(user_id):
    user_session = await get_user_database(user_id)

    async with user_session() as session:
        return await session.scalars(
            select(UserDict)
            )

#------------------------------------------------------------------
#                         СЛОВАРИ
#------------------------------------------------------------------

#Получение названия словаря по его id
async def get_name_user_dict_by_id(user_id, user_dict_id):
    user_session = await get_user_database(user_id)

    async with user_session() as session:
        return await session.scalars(
            select(UserDict.name)
            .where(UserDict.id == user_dict_id)
            )

#Получение названия словаря по его id его категории
async def get_name_user_dict_by_id_category(user_id, category_id):

    user_dict_id = (await get_id_user_dict_by_id_category(user_id, category_id)).first()
    return await get_name_user_dict_by_id(user_dict_id)

#Получение названия словаря и соответствия по его id
async def get_name_and_matching_user_dict_by_id(user_id, user_dict_id):
    user_session = await get_user_database(user_id)

    async with user_session() as session:
        return await session.execute(
            select(UserDict.name, UserDict.matching)
            .where(UserDict.id == user_dict_id)
        )

#Получение id словаря по его названию
async def get_id_user_dict_by_name(user_id, name):
    user_session = await get_user_database(user_id)

    async with user_session() as session:
        return await session.scalars(
            select(UserDict.id)
            .where(UserDict.name == name)
            )

#Получение id словаря по id его категории
async def get_id_user_dict_by_id_category(user_id, category_id):
    user_session = await get_user_database(user_id)

    async with user_session() as session:
        return await session.scalars(
            select(Category.dict_id)
            .where(Category.id == category_id)
            )

#Запись нового словаря
async def add_new_user_dict(user_id, name, matching):
    user_session = await get_user_database(user_id)

    async with user_session() as session:
        session.add(
            UserDict(
                name=name,
                matching=matching
                )
            )
        await session.commit()

# удалить словарь
async def delete_dict(user_id, user_dict_id):
    user_session = await get_user_database(user_id)

    async with user_session() as session:
        result = await session.execute(
            select(UserDict)
            .where(UserDict.id == user_dict_id)
            )
        user_dict = result.scalar_one_or_none()
        if user_dict:
            await session.delete(user_dict)
            await session.commit()



#------------------------------------------------------------------
#                         КАТЕГОРИИ
#------------------------------------------------------------------

#получение id катгорий по id словаря
async def get_categories_id_by_user_dict_id(user_id, user_dict_id):
    user_session = await get_user_database(user_id)

    async with user_session() as session:
        return await session.scalars(
            select(Category.id)
            .where(Category.dict_id == user_dict_id)
            )

#Получение категорий словаря
async def get_categories(user_id, user_dict_id):
    user_session = await get_user_database(user_id)

    async with user_session() as session:
        return await session.scalars(
            select(Category)
            .where(Category.dict_id == user_dict_id)
            )

#Получение названия категории по ее id
async def get_name_category_by_id(user_id, category_id):
    user_session = await get_user_database(user_id)

    async with user_session() as session:
        return await session.scalars(
            select(Category.name)
            .where(Category.id == category_id)
            )

#Получение id категории по ее названию
async def get_id_category_by_name(user_id, category):
    user_session = await get_user_database(user_id)

    async with user_session() as session:
        return await session.scalars(
            select(Category.id)
            .where(Category.name == category)
            )

#Запись новой категории
async def add_new_category(user_id, user_dict_id, name):
    user_session = await get_user_database(user_id)

    async with user_session() as session:
        session.add(Category(
            name=name,
            dict_id=user_dict_id)
            )
        await session.commit()

# удалить категорию
async def delete_category(user_id, category_id):
    user_session = await get_user_database(user_id)

    async with user_session() as session:
        result = await session.execute(
            select(Category)
            .where(Category.id == category_id)
            )
        category = result.scalar_one_or_none()
        if category:
            await session.delete(category)
            await session.commit()



#------------------------------------------------------------------
#                         СЛОВА
#------------------------------------------------------------------


#Получние слов категории
async def get_words_by_category(user_id, category_id):
    user_session = await get_user_database(user_id)

    async with user_session() as session:
        return await session.scalars(
            select(Item)
            .where(Item.category_id == category_id)
            )

#Получние слов категории без соответствий
async def get_words_by_category_without_matching(user_id, category_id):
    user_session = await get_user_database(user_id)

    async with user_session() as session:
        return await session.scalars(
            select(Item.name)
            .where(Item.category_id == category_id)
            )

#Получние обычных слов категорий
async def get_common_words_by_categories_id(user_id, categories_id):
    user_session = await get_user_database(user_id)

    async with user_session() as session:
        return await session.scalars(
            select(Item)
            .where(
                (Item.category_id.in_(categories_id)) &
                                    (Item.level_difficulty == 0)
                                    )
        )

#Получние сложных слов категорий
async def get_difficult_words_by_categories_id(user_id, categories_id):
    user_session = await get_user_database(user_id)

    async with user_session() as session:
        return await session.scalars(
            select(Item)
            .where(
                (Item.category_id.in_(categories_id)) &
                                    (Item.level_difficulty != 0)
                                    )
        )

#Получние обычных слов словаря
async def get_common_words_by_dict(user_id, user_dict_id):
    user_session = await get_user_database(user_id)

    async with user_session() as session:

        categories_id = [
            category_id for category_id
            in await get_categories_id_by_user_dict_id(user_dict_id)
                         ]
        
        return await session.scalars(
            select(Item)
            .where(
                (
                    Item.category_id.in_(categories_id)) &
                                    (Item.level_difficulty == 0)
                                    )
        )

#Получние сложных слов словаря
async def get_difficult_words_by_dict(user_id, user_dict_id):
    user_session = await get_user_database(user_id)

    async with user_session() as session:

        categories_id = [
            category_id for category_id
            in await get_categories_id_by_user_dict_id(user_dict_id)
                         ]
        
        return await session.scalars(
            select(Item)
            .where(
                (Item.category_id.in_(categories_id)) &
                   (Item.level_difficulty != 0)
                   )
                                    )

#Получение данных слова по его id
async def get_data_word_by_id(user_id, word_id):
    user_session = await get_user_database(user_id)

    async with user_session() as session:
        return await session.scalars(
            select(Item)
            .where(Item.id == word_id)
            )

#Запись нового слова
async def add_new_word(user_id, category_id, name:str, matching:str):
    if '  -  ' in name or '  -  ' in matching or name.endswith('  -') or name.endswith('  - ') or matching.startswith('-  ') or matching.startswith(' -  '):
        return '\nДобавлены только корректные слова'

    user_session = await get_user_database(user_id)

    async with user_session() as session:
        session.add(
            Item(
                name=name,
                matching=matching,
                category_id=category_id,
                level_difficulty=0,
                last_date_answer = date.today(),
                is_repeating = 0,
                date_for_repeat = date.today() + timedelta(days=1),
                repeating_interval = 0
                )
            )
        await session.commit()
    return ''

#Запись новых слов
async def add_new_words(user_id, category_id, words_data):
    
    # Получение уникальных слов из категории
    names = { name for name in await get_words_by_category_without_matching(user_id, category_id) }
    items = []

    user_session = await get_user_database(user_id)

    incorrect_flag = False
    ununique_flag = False

    # Проверка и добавление уникальных и корректных слов
    for name, matching in words_data:
        if name not in names:
            if '  -  ' in name or '  -  ' in matching or name.endswith('  -') or name.endswith('  - ') or matching.startswith('-  ') or matching.startswith(' -  '):
                incorrect_flag = True
                continue
            items.append(
                Item(
                    name=name,
                    matching=matching,
                    category_id=category_id,
                    level_difficulty=0,
                    last_date_answer = date.today(),
                    is_repeating = 0,
                    date_for_repeat = date.today() + timedelta(days=1),
                    repeating_interval = 0
                )
            )
            names.add(name)
        else:
            ununique_flag = True

    # Составляем сообщение об исключениях
    extra_words = ''
    if incorrect_flag:
        extra_words = extra_words + '\nДобавлены только корректные слова'
    if ununique_flag:
        extra_words = extra_words + '\nДобавлены только уникальные слова'

    async with user_session() as session:
        session.add_all(items)
        await session.commit()
    return extra_words

#получение id слова по имени
async def get_id_word_by_name(user_id, name_word, category_id):
    user_session = await get_user_database(user_id)

    async with user_session() as session:
        return await session.scalars(
            select(Item.id)
            .where(
                (Item.name == name_word) &
                   (Item.category_id == category_id)
                   )
                                    )

#получение слова по его id
async def get_name_word_by_id(user_id, word_id):
    user_session = await get_user_database(user_id)

    async with user_session() as session:
        return await session.scalars(
            select(Item.name)
            .where(Item.id == word_id)
            )

# удалить слово
async def delete_word(user_id, word_id):
    user_session = await get_user_database(user_id)

    async with user_session() as session:
        result = await session.execute(
            select(Item)
            .where(Item.id == word_id)
            )
        word = result.scalar_one_or_none()
        if word:
            await session.delete(word)
            await session.commit()

#поменять уровень сложности слова
async def set_new_level_difficulty_word(user_id, name, level_difficulty, categories_id):
    user_session = await get_user_database(user_id)

    async with user_session() as session:
        await session.execute(
            update(Item)
            .where((Item.name == name) & (Item.category_id.in_(categories_id)))
            .values(level_difficulty=level_difficulty)
        )
        await session.commit()

#получить соответствие по слову и id категории
async def get_matching_by_name_and_category_id(user_id, name, category_id):
    user_session = await get_user_database(user_id)

    async with user_session() as session:

        return await session.scalars(
            select(Item.matching)
            .where(
                (Item.name == name) &
                        (Item.category_id == category_id)
                    )
            )

#получить слово по соответствию и id категории
async def get_name_by_matching_and_category_id(user_id, matching, category_id):
    user_session = await get_user_database(user_id)

    async with user_session() as session:

        return await session.scalars(
            select(Item.name)
            .where(
                (Item.matching == matching) &
                        (Item.category_id == category_id)
                    )
            )

#проверка наличия слова в категории
async def check_word_in_category(user_id, name_word, category_id):
    user_session = await get_user_database(user_id)

    async with user_session() as session:
        return await session.scalars(
            select(Item.id)
            .where(
                (Item.name == name_word) &
                        (Item.category_id == category_id)
            )
        )

#Отметить что слово отвечалось сегодня
async def word_was_answered_today(user_id, word_id, today):
    user_session = await get_user_database(user_id)

    async with user_session() as session:
        await session.execute(
            update(Item)
            .where(Item.id == word_id )
            .values(last_date_answer =today)
        )
        await session.commit()

#Установить новую дату повтора слова
async def set_new_date_answer(user_id, word_id, new_date_answer, repeating_interval):
    user_session = await get_user_database(user_id)

    async with user_session() as session:
        await session.execute(
            update(Item)
            .where(Item.id == word_id )
            .values(
                date_for_repeat = new_date_answer,
                repeating_interval = repeating_interval
                )
        )
        await session.commit()

#Сделать слово повторяемым
async def make_word_repeating(user_id, word_id, today, new_date_answer):
    user_session = await get_user_database(user_id)

    async with user_session() as session:
        await session.execute(
            update(Item)
            .where( Item.id == word_id )
            .values(
                last_date_answer= today,
                is_repeating = 1,
                date_for_repeat = new_date_answer,
                repeating_interval = 1
                )
        )
        await session.commit()