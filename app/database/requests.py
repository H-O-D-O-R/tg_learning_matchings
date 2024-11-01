from app.database.models import async_session
from app.database.models import UserDict, Category, Item
from sqlalchemy import select, update, delete

#Вывод пользовательских словарей
async def get_user_dicts():
    async with async_session() as session:
        return await session.scalars(
            select(UserDict)
            )

#------------------------------------------------------------------
#                         СЛОВАРИ
#------------------------------------------------------------------

#Получение названия словаря по его id
async def get_name_user_dict_by_id(user_dict_id):
    async with async_session() as session:
        return await session.scalars(
            select(UserDict.name)
            .where(UserDict.id == user_dict_id)
            )

#Получение названия словаря по его id его категории
async def get_name_user_dict_by_id_category(category_id):
    async with async_session() as session:
        user_dict_id = await get_id_user_dict_by_id_category(category_id)
        return await get_name_user_dict_by_id(user_dict_id)

#Получение названия словаря и соответствия по его id 
async def get_name_and_matching_user_dict_by_id(user_dict_id):
    async with async_session() as session:
        return await session.execute(
            select(UserDict.name, UserDict.matching)
            .where(UserDict.id == user_dict_id)
        )
    
#Получение id словаря по его названию
async def get_id_user_dict_by_name(name):
    async with async_session() as session:
        return await session.scalars(
            select(UserDict.id)
            .where(UserDict.name == name)
            )

#Получение id словаря по id его категории
async def get_id_user_dict_by_id_category(category_id):
    async with async_session() as session:
        return await session.scalars(
            select(Category.dict_id)
            .where(Category.id == category_id)
            )

#Запись нового словаря
async def add_new_user_dict(name, matching):
    async with async_session() as session:
        session.add(
            UserDict(
                name=name,
                matching=matching
                )
            )
        await session.commit()

# удалить словарь
async def delete_dict(user_dict_id):
    async with async_session() as session:
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
async def get_categories_id_by_user_dict_id(user_dict_id):
    async with async_session() as session:
        return await session.scalars(
            select(Category.id)
            .where(Category.dict_id == user_dict_id)
            )

#Получение категорий словаря
async def get_categories(user_dict_id):
    async with async_session() as session:
        return await session.scalars(
            select(Category)
            .where(Category.dict_id == user_dict_id)
            )

#Получение названия категории по ее id
async def get_name_category_by_id(category_id):
    async with async_session() as session:
        return await session.scalars(
            select(Category.name)
            .where(Category.id == category_id)
            )

#Получение id категории по ее названию
async def get_id_category_by_name(category):
    async with async_session() as session:
        return await session.scalars(
            select(Category.id)
            .where(Category.name == category)
            )

#Запись новой категории
async def add_new_category(user_dict_id, name):
    async with async_session() as session:
        session.add(Category(
            name=name, 
            dict_id=user_dict_id)
            )
        await session.commit()

# удалить категорию
async def delete_category(category_id):
    async with async_session() as session:
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
async def get_words_by_category(category_id):
    async with async_session() as session:
        return await session.scalars(
            select(Item)
            .where(Item.category_id == category_id)
            )

#Получние обычных слов категорий
async def get_common_words_by_categories_id(categories_id):
    async with async_session() as session:
        return await session.scalars(
            select(Item)
            .where( 
                (Item.category_id.in_(categories_id)) & 
                                    (Item.level_difficulty == 0) 
                                    )
        )

#Получние слов категорий
async def get_difficult_words_by_categories_id(categories_id):
    async with async_session() as session:
        return await session.scalars(
            select(Item)
            .where( 
                (Item.category_id.in_(categories_id)) & 
                                    (Item.level_difficulty != 0) 
                                    )
        )

#Получние обычных слов словаря 
async def get_common_words_by_dict(user_dict_id):
    async with async_session() as session:
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
async def get_difficult_words_by_dict(user_dict_id):
    async with async_session() as session:
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
    
#Запись нового слова
async def add_new_word(category_id, name, matching):
    async with async_session() as session:
        session.add(
            Item(
                name=name, 
                 matching=matching, 
                 category_id=category_id,
                 level_difficulty=0
                 )
            )
        await session.commit()

#получение id слова по имени
async def get_id_word_by_name(name_word, category_id):
    async with async_session() as session:
        return await session.scalars(
            select(Item.id)
            .where(
                (Item.name == name_word) & 
                   (Item.category_id == category_id)
                   )
                                    )

#получение слова по его id
async def get_name_word_by_id(word_id):
    async with async_session() as session:
        return await session.scalars(
            select(Item.name)
            .where(Item.id == word_id)
            )

# удалить слово
async def delete_word(word_id):
    async with async_session() as session:
        result = await session.execute(
            select(Item)
            .where(Item.id == word_id)
            )
        word = result.scalar_one_or_none()
        if word:
            await session.delete(word)
            await session.commit()

#поменять уровень слодности слова
async def set_new_level_difficulty_word(name, level_difficulty, categories_id):
    async with async_session() as session:

        # Выполняем обновление
        await session.execute(
            update(Item)
            .where((Item.name == name) & (Item.category_id.in_(categories_id)))
            .values(level_difficulty=level_difficulty)
        )
        
        # Сохраняем изменения
        await session.commit()


#получить соответствие по слову и id категории
async def get_matching_by_name_and_category_id(name, category_id):
    async with async_session() as session:

        return await session.scalars(
            select(Item.matching)
            .where(
                (Item.name == name) &
                        (Item.category_id == category_id)
                    )
            )

#получить слово по соответствию и id категории
async def get_name_by_matching_and_category_id(matching, category_id):
    async with async_session() as session:

        return await session.scalars(
            select(Item.name)
            .where(
                (Item.matching == matching) &
                        (Item.category_id == category_id)
                    )
            )