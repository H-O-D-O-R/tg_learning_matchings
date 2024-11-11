from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
import asyncio
from io import StringIO, BytesIO
from openpyxl import load_workbook


from random import shuffle


import app.keyboards as kb
import app.database.requests as rq
import app.database.user_models as user_md

router = Router()

#region States
class RegistationNewDict(StatesGroup):
    name = State()
    matching = State()

class RegistationNewCat(StatesGroup):
    user_dict_id = ''
    name = State()

class CategorisePages(StatesGroup):
    check = State()
    current_page = 0
    pages = []

class WordsPages(StatesGroup):
    check = State()
    current_page = 0
    pages = []
    less_name = False
    less_matching = False
    less_common_words = False

class RegistationNewItem(StatesGroup):
    category_id = ''
    name = State()
    matching = State()

class ConfirmDelWord(StatesGroup):
    category_id = ''
    name = State()
    confirm = State()

class LearnWords(StatesGroup):
    categories_id = []
    user_dict_id = 0
    words = []
    order_difficult_words = []
    last_word = {}
    name = State()
    id_message_for_delete = 0

class RegistationNewWords(StatesGroup):
    category_id = ''
    file = State()

#endregion


@router.message(CommandStart())
async def cmd_start(message: Message):
    user_id = message.from_user.id

    if not (await rq.is_new_user(user_id)).first():
        user_name = message.from_user.username
        await user_md.create_user_database(user_id)
        await rq.add_new_user(user_name, user_id)

    await message.answer('Выбери словарь:', reply_markup= await kb.inline_dictionaries(user_id))



async def main(message: Message):
    user_id = message.from_user.id
    await message.answer('Выбери словарь:', reply_markup= await kb.inline_dictionaries(user_id))

@router.callback_query(F.data == 'main')
async def cmd_start_for_callback(callback: CallbackQuery):
    user_id = callback.from_user.id
    await callback.message.edit_text('Выбери словарь:', reply_markup= await kb.inline_dictionaries(user_id))





####################################################################################

#                              РАБОТА С СЛОВАРЯМИ

####################################################################################
#region DICTIONARIES


#СОЗДАНИЕ НОВОГО СЛОВАРЯ
#region
#-----------------------------------------------------------------------------------
#                          /start/Добавить новый словарь
#-----------------------------------------------------------------------------------


@router.callback_query(F.data == 'add new dict')
async def add_new_dict(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()

    state_name = await state.get_state()
    if state_name is not None:
        await state.clear()

    await state.set_state(RegistationNewDict.name)
    await callback.message.answer('Введите название нового словаря',
                          reply_markup= await kb.reply_cancel_add_new_item())

#Получение названия словаря
@router.message(RegistationNewDict.name)
async def set_name_dict(message: Message, state: FSMContext):
    if message.text == 'ОТМЕНА':
        await main(message)
        return

    await state.set_state(RegistationNewDict.matching)
    await state.update_data(name=message.text)
    await message.answer('Введите соответствие', reply_markup= await kb.reply_cancel_add_new_item())

#Получение соответствия словаря
@router.message(RegistationNewDict.matching)
async def set_name_dict(message: Message, state: FSMContext):
    user_id = message.from_user.id

    if message.text == 'ОТМЕНА':
        await main(message)
        return

    await state.update_data(matching=message.text)
    data = await state.get_data()
    await state.clear()

    name_user_dict = data['name']
    matching_user_dict = data['matching']

    await rq.add_new_user_dict(user_id, name_user_dict, matching_user_dict)
    await message.answer(f'Словарь <b>{name_user_dict}</b> создан!',
                         parse_mode="html")

    user_dict_id = (await rq.get_id_user_dict_by_name(user_id, name_user_dict)).first()
    await message.answer(f'Словарь <b>{name_user_dict}</b>',
                         reply_markup=await kb.inline_categories(user_id, user_dict_id ),
                         parse_mode='html')

#-----------------------------------------------------------------------------------
#endregion



#РЕДАКТИРОВАНИЕ СЛОВАРЯ
#region
#-----------------------------------------------------------------------------------
#                     /start/{название словаря}/редактировать словарь
#-----------------------------------------------------------------------------------


@router.callback_query(F.data.startswith('edit dict'))
async def edit_user_dict(callback: CallbackQuery):
    user_id = callback.from_user.id

    user_dict_id = callback.data.split('_')[1]
    name_user_dict = (await rq.get_name_user_dict_by_id(user_id, user_dict_id)).first()

    await callback.message.edit_text(f'Словарь <b>{name_user_dict}</b>',
                                  reply_markup=await kb.inline_edit_user_dict( user_dict_id ),
                                  parse_mode='html')

#-----------------------------------------------------------------------------------
#endregion



#УДАЛЕНИЕ СЛОВАРЯ
#region
#-----------------------------------------------------------------------------------
#            /start/{название словаря}/редактировать словарь/удалить словарь
#-----------------------------------------------------------------------------------


@router.callback_query(F.data.startswith('del dict'))
async def del_user_dict(callback: CallbackQuery):
    user_id = callback.from_user.id

    name_user_dict = (await rq.get_name_user_dict_by_id(user_id, callback.data.split('_')[1])).first()
    await callback.message.edit_text(f'Вы точно хотите удалить словарь {name_user_dict}?',
                                  reply_markup= await kb.inline_confirm_del_user_dict(callback.data.split('_')[1]))

#Получение подтверждения
@router.callback_query(F.data.startswith('confirm del dict'))
async def confirm_del_user_dict(callback: CallbackQuery):
    user_id = callback.from_user.id

    user_dict_id = callback.data.split('_')[1]
    name_user_dict = (await rq.get_name_user_dict_by_id(user_id, user_dict_id)).first()
    await rq.delete_dict(user_id, user_dict_id)
    await callback.message.edit_text(f"Словарь <b>{name_user_dict}</b> удалён",
                                     parse_mode='html')
    await callback.message.answer('Выбери словарь:',
                                     reply_markup= await kb.inline_dictionaries(user_id))

#-----------------------------------------------------------------------------------
#endregion


#endregion





####################################################################################

#                              РАБОТА С КАТЕГОРИЕЙ

####################################################################################
#region CATEGORIES


#ВЫВОД КАТЕГОРИЙ СЛОВАРЯ
#region
#-----------------------------------------------------------------------------------
#                              /start/{название словаря}
#-----------------------------------------------------------------------------------

#создание основы для вывода категорий
async def base_for_display_categories(user_id: int, user_dict_id: int, state: FSMContext):
    
    pages = [[]]
    for item in await rq.get_categories(user_id, user_dict_id):
        if len(pages[-1]) == 10:
            pages.append([])

        pages[-1].append( (item.id, item.name) )
    
    await state.set_state(CategorisePages.check)
    await state.update_data(pages=pages)
    await state.update_data(current_page=0)


#Вывод слов категории
@router.callback_query(F.data.startswith('dict'))
async def display_categories(callback: CallbackQuery, state: FSMContext):

    user_id = callback.from_user.id
    user_dict_id = callback.data.split('_')[1]

    name_state = await state.get_state()
    if name_state != CategorisePages.check:
        await state.clear()

        await base_for_display_categories(user_id, user_dict_id, state)
    
    data = await state.get_data()
    pages = data['pages']
    current_page = data['current_page']

    name_user_dict = (await rq.get_name_user_dict_by_id(user_id, user_dict_id)).first()
    await callback.message.edit_text(f'Словарь <b>{name_user_dict}</b>',
                                  reply_markup=await kb.inline_categories(user_dict_id, pages[current_page], current_page, len(pages)),
                                  parse_mode='html')

#Слудующая страница
@router.callback_query(F.data.startswith('next cat page'))
async def next_categories_page(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    current_page = data['current_page']
    await state.update_data(current_page=current_page + 1)

    await display_categories(callback, state)

#Предыдущая страница
@router.callback_query(F.data.startswith('previous cat page'))
async def previous_categories_page(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    current_page = data['current_page']
    await state.update_data(current_page=current_page - 1)

    await display_categories(callback, state)


#-----------------------------------------------------------------------------------
#endregion




#СОЗДАНИЕ НОВОЙ КАТЕГОРИИ
#region
#-----------------------------------------------------------------------------------
#    /start/{название словаря}/редактировать словарь/добавить новую категорию
#-----------------------------------------------------------------------------------


@router.callback_query(F.data.startswith('add new cat'))
async def add_new_category(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id

    await callback.message.delete()

    state_name = await state.get_state()
    if state_name is not None:
        await state.clear()

    await state.set_state(RegistationNewCat.name)
    user_dict_id = callback.data.split('_')[1]
    await state.update_data(user_dict_id=user_dict_id)
    name_user_dict = (await rq.get_name_user_dict_by_id(user_id, user_dict_id)).first()

    await callback.message.answer(f'Введите название новой категории словаря <b>{name_user_dict}</b>',
                                  reply_markup= await kb.reply_cancel_add_new_item(),
                                  parse_mode='html')

#Получение названия категории
@router.message(RegistationNewCat.name)
async def set_name_category(message: Message, state: FSMContext):
    user_id = message.from_user.id

    if message.text == 'ОТМЕНА':
        data = await state.get_data()
        await state.clear()

        user_dict_id = data['user_dict_id']
        name_user_dict =  (await rq.get_name_user_dict_by_id(user_id, user_dict_id)).first()

        await message.answer(f'Словарь <b>{name_user_dict}</b>',
                                    reply_markup=await kb.inline_edit_user_dict( user_dict_id ),
                                    parse_mode='html')
        return

    await state.update_data(name=message.text)
    data = await state.get_data()
    await state.clear()
    await rq.add_new_category(user_id, data['user_dict_id'], message.text)
    category_id = (await rq.get_id_category_by_name(user_id, message.text)).first()


    pages = [[]]

    await state.set_state(WordsPages.check)
    await state.update_data(pages=pages)
    await state.update_data(current_page=0)
    await state.update_data(less_name=False)
    await state.update_data(less_matching=False)
    await state.update_data(less_common_words=False)

    await message.answer(f"Категория <b>{message.text}</b>\n\nЗдесь пока пусто",
                         reply_markup= await kb.inline_words(
                             user_id=user_id,
                             category_id=category_id,
                             user_dict_id=data['user_dict_id'],
                             current_page=0,
                             cnt_pages=len(pages),
                             is_not_empty=False,
                             ),
                         parse_mode='html'
                         )

#-----------------------------------------------------------------------------------
#endregion



#РЕДАКТИРОВАНИЕ КАТЕГОРИИ
#region
#-----------------------------------------------------------------------------------
#     /start/{название словаря}/{название категории}/редактировать категорию
#-----------------------------------------------------------------------------------


@router.callback_query(F.data.startswith('edit cat'))
async def edit_category(callback: CallbackQuery):
    user_id = callback.from_user.id

    category_id = callback.data.split('_')[1]
    name_category = (await rq.get_name_category_by_id(user_id, category_id)).first()
    await callback.message.edit_text(f'Категория <b>{name_category}</b>',
                                  reply_markup= await kb.inline_edit_category(category_id),
                                  parse_mode='html'
                                  )

#-----------------------------------------------------------------------------------
#endregion



#УДАЛЕНИЕ КАТЕГОРИИ
#region
#-----------------------------------------------------------------------------------
#          /start/{название словаря}/редактировать словарь/удалить словарь
#-----------------------------------------------------------------------------------


@router.callback_query(F.data.startswith('del cat'))
async def del_category(callback: CallbackQuery):
    user_id = callback.from_user.id

    category_id = callback.data.split('_')[1]
    name_category = (await rq.get_name_category_by_id(user_id, category_id)).first()
    await callback.message.edit_text(f'Вы точно хотите удалить категорию {name_category}?',
                                  reply_markup= await kb.inline_confirm_del_category(category_id))

#Получение подтверждения
@router.callback_query(F.data.startswith('confirm del cat'))
async def confirm_del_category(callback: CallbackQuery):
    user_id = callback.from_user.id

    category_id = callback.data.split('_')[1]
    name_category = (await rq.get_name_category_by_id(user_id, category_id)).first()
    user_dict_id = (await rq.get_id_user_dict_by_id_category(user_id, category_id)).first()
    name_user_dict = (await rq.get_name_user_dict_by_id(user_id, user_dict_id)).first()
    await rq.delete_category(user_id, category_id)
    await callback.message.edit_text(f"Категория <b>{name_category}</b> удалена",
                                  parse_mode='html')
    await callback.message.answer(f'Словарь <b>{name_user_dict}</b>',
                                  reply_markup=await kb.inline_categories(user_id, user_dict_id ),
                                  parse_mode='html')

#-----------------------------------------------------------------------------------
#endregion


#endregion




####################################################################################

#                              РАБОТА СО СЛОВАМИ

####################################################################################
#region WORDS



#ВЫВОД СЛОВ КАТЕГОРИИ
#region
#-----------------------------------------------------------------------------------
#                  /start/{название словаря}/{название категории}
#-----------------------------------------------------------------------------------

#создание основы для вывода слов категории
async def base_for_display_words(user_id, category_id, state):

    items = [
        (item.name, item.matching)
        for item in await rq.get_words_by_category(user_id, category_id)
    ]

    shuffle(items)

    pages = []
    len_items = len(items)
    for num in range((len_items + 14) // 15):
        pages.append(items[num * 15: (num + 1) * 15])

    await state.set_state(WordsPages.check)
    await state.update_data(pages=pages)
    await state.update_data(current_page=0)
    await state.update_data(less_name=False)
    await state.update_data(less_matching=False)
    await state.update_data(less_common_words=False)

#Текст для вывода слов
async def text_words(user_id, category_id, pages, page, less_name, less_matching):

    name_category = (await rq.get_name_category_by_id(user_id, category_id)).first()

    def decorate(item, less_name, less_matching):
        if less_name == less_matching:
            name, matching = item
            return f"{name}  -  <i>{matching}</i>"
        if less_name:
            matching = item[0]
            return f"<i>{matching}</i>"
        name = item[0]
        return name

    new_line = '\n'
    return f"Категория <b>{name_category}</b>\n\n{(new_line.join(decorate(item, less_name, less_matching) for item in pages[page]) if pages else 'Здесь пока пусто')}"

#Вывод слов категории
@router.callback_query(F.data.startswith('cat'))
async def display_words(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id

    category_id = callback.data.split('_')[1]
    user_dict_id = (await rq.get_id_user_dict_by_id_category(user_id, category_id)).first()


    name_state = await state.get_state()
    if name_state != WordsPages.check:
        await state.clear()

        await base_for_display_words(user_id, category_id, state)


    data = await state.get_data()
    pages = data['pages']
    current_page = data['current_page']
    less_name = data['less_name']
    less_matching = data['less_matching']
    less_common_words = data['less_common_words']

    await callback.message.edit_text(
        await text_words(
            user_id=user_id,
            category_id=category_id,
            pages=pages,
            page=current_page,
            less_name=less_name,
            less_matching=less_matching
            ),
        reply_markup=await kb.inline_words(
            user_id=user_id,
            category_id=category_id,
            user_dict_id=user_dict_id,
            current_page=current_page,
            cnt_pages=len(pages),
            is_not_empty=bool(pages[0] if pages else False),
            less_name = less_name,
            less_matching = less_matching,
            less_common_words = less_common_words
            ),
        parse_mode='html'
        )

#следующая страница
@router.callback_query(F.data.startswith('next page'))
async def next_page(callback:CallbackQuery, state: FSMContext):
    data = await state.get_data()
    current_page = data['current_page']
    await state.update_data(current_page=current_page + 1)

    await display_words(callback, state)

#предыдущая страница
@router.callback_query(F.data.startswith('previous page'))
async def next_page(callback:CallbackQuery, state: FSMContext):
    data = await state.get_data()
    current_page = data['current_page']
    await state.update_data(current_page=current_page - 1)

    await display_words(callback, state)

#Убрать слово в категории
@router.callback_query(F.data.startswith('discard name'))
async def discard_name(callback: CallbackQuery, state: FSMContext):

    data = await state.get_data()
    pages = data['pages']

    pages = [
        [
        (item[1],)
        for item in page
        ] for page in pages
    ]

    await state.update_data(pages=pages)
    await state.update_data(less_name=True)

    await display_words(callback, state)

#Убрать соответствие в категории
@router.callback_query(F.data.startswith('discard matching'))
async def discard_matching(callback: CallbackQuery, state: FSMContext):

    data = await state.get_data()
    pages = data['pages']

    pages = [
        [
        (item[0],)
        for item in page
        ] for page in pages
    ]

    await state.update_data(pages=pages)
    await state.update_data(less_matching=True)

    await display_words(callback, state)

#Вернуть слово в категорию
@router.callback_query(F.data.startswith('return name'))
async def return_name(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id

    category_id = callback.data.split('_')[1]

    data = await state.get_data()
    pages = data['pages']

    new_pages = []
    for page in pages:
        new_pages.append([])
        for item in page:
            new_pages[-1].append( ((await rq.get_name_by_matching_and_category_id(user_id, item[0], category_id)).first(), item[0]) )

    await state.update_data(pages=new_pages)
    await state.update_data(less_name=False)

    await display_words(callback, state)

#Вернуть соответствие в категорию
@router.callback_query(F.data.startswith('return matching'))
async def return_name(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id

    category_id = callback.data.split('_')[1]

    data = await state.get_data()
    pages = data['pages']

    new_pages = []
    for page in pages:
        new_pages.append([])
        for item in page:
            new_pages[-1].append( (item[0], (await rq.get_matching_by_name_and_category_id(user_id, item[0], category_id)).first()) )

    await state.update_data(pages=new_pages)
    await state.update_data(less_matching=False)

    await display_words(callback, state)

#Убрать простые слова в категории
@router.callback_query(F.data.startswith('discard common'))
async def discard_common(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id

    category_id = callback.data.split('_')[1]

    data = await state.get_data()
    less_name = data['less_name']
    less_matching = data['less_matching']

    if less_name == less_matching:
        items = [
            (item.name, item.matching)
            for item in await rq.get_difficult_words_by_categories_id(user_id,  [category_id] )
        ]
    elif less_name:
        items = [
            (item.matching,)
            for item in await rq.get_difficult_words_by_categories_id(user_id,  [category_id] )
        ]
    else:
        items = [
            (item.name,)
            for item in await rq.get_difficult_words_by_categories_id(user_id,  [category_id] )
        ]

    shuffle(items)

    pages = []
    len_items = len(items)
    for num in range((len_items + 14) // 15):
        pages.append(items[num * 15: (num + 1) * 15])

    await state.update_data(pages=pages)
    await state.update_data(current_page=0)
    await state.update_data(less_common_words=True)


    await display_words(callback, state)

#Вернуть простые слова
@router.callback_query(F.data.startswith('return common'))
async def return_common(callback: CallbackQuery, state: FSMContext):
    await state.clear()

    await display_words(callback, state)

#Перемешать слова категории
@router.callback_query(F.data.startswith('shuffle'))
async def shuffle_words(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id

    category_id = callback.data.split('_')[1]
    user_dict_id = (await rq.get_id_user_dict_by_id_category(user_id, category_id)).first()

    data = await state.get_data()
    pages = data['pages']
    current_page = data['current_page']
    less_name = data['less_name']
    less_matching = data['less_matching']
    less_common_words = data['less_common_words']

    first_line = callback.message.text.split('\n')[0]
    items = callback.message.text.split('\n')[2:]

    shuffle(items)

    new_line = '\n'
    await callback.message.edit_text(
        f"{first_line}\n\n{(new_line.join( item for item in items ))}",
        reply_markup=await kb.inline_words(
            user_id=user_id,
            category_id=category_id,
            user_dict_id=user_dict_id,
            current_page=current_page,
            cnt_pages=len(pages),
            is_not_empty=bool(pages[0] if pages else False),
            less_name = less_name,
            less_matching = less_matching,
            less_common_words = less_common_words
            ),
        parse_mode='html'
    )

#-----------------------------------------------------------------------------------
#endregion



#ДОБАВЛЕНИЕ НОВОГО СЛОВА В КАТЕГОРИЮ
#region
#-----------------------------------------------------------------------------------
#                /start/{название словаря}/{название категории}
#                /редактировать категорию/добавить новое слово
#-----------------------------------------------------------------------------------


@router.callback_query(F.data.startswith('add new word'))
async def add_new_word(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id

    await callback.message.delete()
    category_id = callback.data.split('_')[1]
    user_dict_id = (await rq.get_id_user_dict_by_id_category(
                                user_id, callback.data.split('_')[1])).first()

    state_name = await state.get_state()
    if state_name is not None:
        await state.clear()

    await state.set_state(RegistationNewItem.name)
    await state.update_data(category_id=category_id)
    await state.update_data(user_dict_id=user_dict_id)
    name_category = (await rq.get_name_category_by_id(user_id, category_id)).first()
    await callback.message.answer(f'Введите новое слово категории <b>{name_category}</b>',
                                  reply_markup= await kb.reply_cancel_add_new_item(),
                                  parse_mode='html')

#Получение слова
@router.message(RegistationNewItem.name)
async def set_name_word(message: Message, state: FSMContext):
    user_id = message.from_user.id

    data = await state.get_data()
    category_id = data['category_id']

    if message.text == 'ОТМЕНА':
        await state.clear()

        name_category = (await rq.get_name_category_by_id(user_id, category_id)).first()
        await message.answer(f'Категория <b>{name_category}</b>',
                                    reply_markup= await kb.inline_edit_category(category_id),
                                    parse_mode='html'
                                    )

        return

    if (await rq.check_word_in_category(user_id, message.text, category_id)).first() is not None:
        await state.clear()

        name_category = (await rq.get_name_category_by_id(user_id, category_id)).first()
        await message.answer(f'Слово {message.text} уже есть в категории {name_category}')

        await message.answer(f'Категория <b>{name_category}</b>',
                                  reply_markup= await kb.inline_edit_category(category_id),
                                  parse_mode='html'
                                  )
        return

    await state.update_data(name=message.text)
    await state.set_state(RegistationNewItem.matching)
    await message.answer('Введите перевод', reply_markup= await kb.reply_cancel_add_new_item())

#Получение соответствия (перевод)
@router.message(RegistationNewItem.matching)
async def set_matching_word(message: Message, state: FSMContext):
    user_id = message.from_user.id

    await state.update_data(matching=message.text)
    data = await state.get_data()
    await state.clear()

    category_id = data['category_id']

    if message.text == 'ОТМЕНА':

        name_category = (await rq.get_name_category_by_id(user_id, category_id)).first()
        await message.answer(f'Категория <b>{name_category}</b>',
                                    reply_markup= await kb.inline_edit_category(category_id),
                                    parse_mode='html'
                                    )

        return

    extra_words = await rq.add_new_word(user_id, category_id, data['name'], data['matching'])
    await message.answer(f"Слово <b>{data['name']}</b> - <i>{data['matching']}</i> добавлено!" + extra_words,
                         parse_mode='html')

    user_dict_id = (await rq.get_id_user_dict_by_id_category(user_id, category_id)).first()


    await base_for_display_words(user_id, category_id, state)

    data = await state.get_data()

    pages = data['pages']
    current_page = data['current_page']
    less_name = data['less_name']
    less_matching = data['less_matching']
    less_common_words = data['less_common_words']

    await message.answer(
        await text_words(
            user_id=user_id,
            category_id=category_id,
            pages=pages,
            page=current_page,
            less_name=less_name,
            less_matching=less_matching
            ),
        reply_markup=await kb.inline_words(
            user_id=user_id,
            category_id=category_id,
            user_dict_id=user_dict_id,
            current_page=current_page,
            cnt_pages=len(pages),
            is_not_empty=bool(pages[0] if pages else False),
            less_name = less_name,
            less_matching = less_matching,
            less_common_words = less_common_words
            ),
        parse_mode='html'
        )

#-----------------------------------------------------------------------------------
#endregion



#ДОБАВЛЕНИЕ НОВЫХ СЛОВ В КАТЕГОРИЮ
#region
#-----------------------------------------------------------------------------------
#                /start/{название словаря}/{название категории}
#                /редактировать категорию/добавить новые слова
#-----------------------------------------------------------------------------------


@router.callback_query(F.data.startswith('add words'))
async def add_new_words(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()

    state_name = await state.get_state()
    if state_name is not None:
        await state.clear()

    await state.set_state(RegistationNewWords.file)
    await state.update_data(category_id=callback.data.split('_')[1])

    await callback.message.answer(
'''Отправьте файл текстового или табличного формата
Каждая строка текстового файла должна соответствовать шаблону: "<i>слово</i> - <i>перевод</i>"
Табличный файл должен быть без заголовков''',
                    parse_mode='html',
                    reply_markup= await kb.reply_cancel_add_new_item()
                    )



@router.message(RegistationNewWords.file)
async def set_new_words(message: Message, state: FSMContext):
    user_id = message.from_user.id

    data = await state.get_data()
    category_id = data['category_id']
    await state.clear()

    if message.text == 'ОТМЕНА':

        user_dict_id = (await rq.get_id_user_dict_by_id_category(user_id, category_id)).first()

        name_category = (await rq.get_name_category_by_id(user_id, category_id)).first()
        await message.answer(f'Категория <b>{name_category}</b>',
                                    reply_markup= await kb.inline_edit_category(category_id),
                                    parse_mode='html'
                                    )

        return

    document = message.document

    if not document or document.mime_type == 'text/csv' or not (
        document.mime_type.startswith('text/') or
        document.mime_type in ['application/vnd.ms-excel', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet']
    ):
        await message.answer("Пожалуйста, отправьте текстовый или XLSX документ")

        name_category = (await rq.get_name_category_by_id(user_id, category_id)).first()
        await message.answer(f'Категория <b>{name_category}</b>',
                                    reply_markup= await kb.inline_edit_category(category_id),
                                    parse_mode='html'
                                    )

        return

    file = await message.bot.get_file(document.file_id)
    downloaded_file = await message.bot.download_file(file.file_path)

    try:
        if document.mime_type.startswith('text/'):
            content = downloaded_file.read().decode('utf-8')
            string_io = StringIO(content)

            words_data = [
                (name, matching)
                for name, matching
                in map(
                    lambda line: line.rstrip().split(' - '), string_io
                 )
            ]

        elif document.mime_type == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet':
            excel_io = BytesIO(downloaded_file.read())
            workbook = load_workbook(excel_io, data_only=True)
            sheet = workbook.active

            words_data = [
                (name, matching)
                for name, matching
                in sheet.iter_rows(values_only=True)
            ]


        extra_words = await rq.add_new_words(user_id, category_id, words_data)
        name_category = (await rq.get_name_category_by_id(user_id, category_id)).first()
        await message.answer(f'Слова добавлены в категорию {name_category}!' + extra_words)

    except Exception as e:
        await message.answer(f"Произошла ошибка при обработке файла")

    user_dict_id = (await rq.get_id_user_dict_by_id_category(user_id, category_id)).first()


    await base_for_display_words(user_id, category_id, state)

    data = await state.get_data()
    pages = data['pages']
    current_page = data['current_page']
    less_name = data['less_name']
    less_matching = data['less_matching']
    less_common_words = data['less_common_words']

    await message.answer(
        await text_words(
            user_id=user_id,
            category_id=category_id,
            pages=pages,
            page=current_page,
            less_name=less_name,
            less_matching=less_matching
            ),
        reply_markup=await kb.inline_words(
            user_id=user_id,
            category_id=category_id,
            user_dict_id=user_dict_id,
            current_page=current_page,
            cnt_pages=len(pages),
            is_not_empty=bool(pages[0] if pages else False),
            less_name = less_name,
            less_matching = less_matching,
            less_common_words = less_common_words
            ),
        parse_mode='html'
        )


#endregion



#УДАЛЕНИЕ СЛОВА ИЗ КАТЕГОРИИ
#region
#-----------------------------------------------------------------------------------
#                 /start/{название словаря}/{название категории}
#                     /редактировать категорию/удалить слово
#-----------------------------------------------------------------------------------


@router.callback_query(F.data.startswith('del word'))
async def del_word(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()

    state_name = await state.get_state()
    if state_name is not None:
        await state.clear()

    await state.set_state(ConfirmDelWord.name)
    category_id = callback.data.split('_')[1]
    await state.update_data(category_id=category_id)
    await callback.message.answer('Введите слово, которое хотите удалить',
                                  reply_markup= await kb.cancel_delete_word(category_id))

#Получение слова
@router.message(ConfirmDelWord.name)
async def get_name_word_for_delete(message: Message, state: FSMContext):
    user_id = message.from_user.id

    name_word = message.text
    data = await state.get_data()
    await state.clear()
    category_id = data['category_id']

    if name_word == 'ОТМЕНА':
        name_category = (await rq.get_name_category_by_id(user_id, category_id)).first()
        await message.answer(f'Категория <b>{name_category}</b>',
                                    reply_markup= await kb.inline_edit_category(category_id),
                                    parse_mode='html'
                                    )
        return

    if (await rq.check_word_in_category(user_id, name_word, category_id)).first() is None:
        name_category = (await rq.get_name_category_by_id(user_id, category_id)).first()

        await message.answer(f'Слово {name_word} отсутствует в категории {name_category}')
        await message.answer(f'Категория <b>{name_category}</b>',
                                  reply_markup= await kb.inline_edit_category(category_id),
                                  parse_mode='html'
                                  )

        return

    word_id = (await rq.get_id_word_by_name(user_id, name_word, category_id)).first()
    await message.answer(f'Вы точно хотите удалить слово {name_word}?',
                                  reply_markup= await kb.inline_confirm_del_word(word_id, category_id))

#Получение подтверждения
@router.callback_query(F.data.startswith('confirm del word'))
async def confirm_del_word(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id

    word_id = callback.data.split('_')[1]
    name_word = (await rq.get_name_word_by_id(user_id, word_id)).first()
    category_id = callback.data.split('_')[2]
    name_category = (await rq.get_name_category_by_id(user_id, category_id)).first()
    user_dict_id = (await rq.get_id_user_dict_by_id_category(user_id, category_id)).first()

    await rq.delete_word(user_id, word_id)
    await callback.message.edit_text(f"Слово <b>{name_word}</b> удалено из категории <b>{name_category}</b>",
                                     parse_mode='html')

    name_state = await state.get_state()
    if name_state != None:
        await state.clear()

    await base_for_display_words(user_id, category_id, state)

    data = await state.get_data()
    pages = data['pages']
    current_page = data['current_page']
    less_name = data['less_name']
    less_matching = data['less_matching']
    less_common_words = data['less_common_words']

    await callback.message.answer(
        await text_words(
            user_id=user_id,
            category_id=category_id,
            pages=pages,
            page=current_page,
            less_name=less_name,
            less_matching=less_matching
            ),
        reply_markup=await kb.inline_words(
            user_id=user_id,
            category_id=category_id,
            user_dict_id=user_dict_id,
            current_page=current_page,
            cnt_pages=len(pages),
            is_not_empty=bool(pages[0] if pages else False),
            less_name = less_name,
            less_matching = less_matching,
            less_common_words = less_common_words
            ),
        parse_mode='html'
        )

#-----------------------------------------------------------------------------------
#endregion



#ИЗУЧЕНИЕ СЛОВ
#region
#-----------------------------------------------------------------------------------
#                 /start/{название словаря}/учить слова или сложные слова
#-----------------------------------------------------------------------------------

#Обработка списка обычных слов
@router.callback_query(F.data.startswith('learn all'))
async def list_of_common_words(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id

    if callback.data.split('_')[1] == 'dict':
        user_dict_id = callback.data.split('_')[2]
        categories_id = [category_id for category_id in await rq.get_categories_id_by_user_dict_id(user_id, user_dict_id)]
    else:
        categories_id = [ callback.data.split('_')[2] ]
        user_dict_id = (await rq.get_id_user_dict_by_id_category(user_id, categories_id[0])).first()

    words = []

    for word in await rq.get_common_words_by_categories_id(user_id, categories_id):
        name, matching = word.name, word.matching
        words.append({'name': name, 'matching': matching, 'level_difficulty': 0})

    shuffle(words)

    state_name = await state.get_state()
    if state_name is not None:
        await state.clear()

    await state.set_state(LearnWords.name)
    await state.update_data(categories_id=categories_id)
    await state.update_data(user_dict_id=user_dict_id)
    await state.update_data(words=words)

    await list_of_difficult_words(callback, state, True)

#Обработка списка сложных слов
@router.callback_query(F.data.startswith('learn diff'))
async def list_of_difficult_words(callback: CallbackQuery, state: FSMContext, is_call: bool = False):
    user_id = callback.from_user.id

    await callback.message.delete()
    if not is_call:
        if callback.data.split('_')[1] == 'dict':
            user_dict_id = callback.data.split('_')[2]
            categories_id = [category_id for category_id in await rq.get_categories_id_by_user_dict_id(user_id, user_dict_id)]
        else:
            categories_id = [ callback.data.split('_')[2] ]
            user_dict_id = (await rq.get_id_user_dict_by_id_category(user_id, categories_id[0])).first()

        state_name = await state.get_state()
        if state_name is not None:
            await state.clear()

        await state.set_state(LearnWords.name)
        await state.update_data(categories_id=categories_id)
        await state.update_data(user_dict_id=user_dict_id)
        await state.update_data(words=[])
    else:
        data = await state.get_data()
        categories_id = data['categories_id']



    difficult_words = {1: [], 2: [], 3: []}

    for word in await rq.get_difficult_words_by_categories_id(user_id, categories_id):
        name, matching = word.name, word.matching
        difficult_words[word.level_difficulty].append( (name, matching) )

    tasks = []
    order_difficult_words = []
    for level_difficulty in range(1, 4):
        shuffle(difficult_words[level_difficulty])
        for word in difficult_words[level_difficulty]:
            name, matching = word
            tasks.append( set_level_difficulty(user_id, {'name': name, 'matching': matching, 'level_difficulty': level_difficulty},
                                       order_difficult_words, categories_id) )
    await asyncio.gather(*tasks)

    await state.update_data(order_difficult_words=order_difficult_words)
    await state.update_data(difficult_words=difficult_words)

    await give_word(callback.message, state )

#Изменить сложность слова
async def set_level_difficulty(user_id, word, order_difficult_words, categories_id: list, correct_answer=None):

    if correct_answer is None:
        level_difficulty = word['level_difficulty']
    elif correct_answer:
        level_difficulty = word['level_difficulty'] + 1
        if level_difficulty == 4:
            level_difficulty = 0
        await rq.set_new_level_difficulty_word(user_id, word['name'], level_difficulty, categories_id)
    else:
        level_difficulty = word['level_difficulty']
        if level_difficulty != 1:
            level_difficulty = 1
            await rq.set_new_level_difficulty_word(user_id, word['name'], level_difficulty, categories_id)

    word['level_difficulty'] = level_difficulty

    if level_difficulty != 0:
        step_for_word = 5 * level_difficulty
        for _ in range( step_for_word - 1 - len(order_difficult_words) ):
            order_difficult_words.append(None)

        order_difficult_words.insert( 5 * level_difficulty, word )

#Вывод слова изучаемого раздела
async def give_word(message: Message, state:FSMContext ):
    user_id = message.from_user.id

    data = await state.get_data()

    order_difficult_words = data['order_difficult_words']
    words = data['words']
    categories_id = data['categories_id']
    user_dict_id = data['user_dict_id']

    word = (order_difficult_words.pop(0) if order_difficult_words else None)
    if word is None:
        if words:
            word = words.pop(0)
        else:
            while word is None:
                if order_difficult_words:
                    word = order_difficult_words.pop(0)
                else:
                    break
    if word:
        await message.answer(word['matching'], reply_markup = await kb.reply_learn_word())
        await state.update_data(last_word = word)
    else:
        name_user_dict =  (await rq.get_name_user_dict_by_id(user_id, user_dict_id)).first()

        if len(categories_id) == 1:
            name_category = (await rq.get_name_category_by_id(user_id, categories_id[0])).first()
            extra_words = f'категории <b>{name_category}</b>'
        else:
            extra_words = f'словаря <b>{name_user_dict}</b>'

        await message.answer(f'Поздравяю! Ты выучил слова ' + extra_words, parse_mode='html')
        await message.answer(f'Словарь <b>{name_user_dict}</b>',
                             reply_markup=await kb.inline_categories(user_id, user_dict_id ),
                             parse_mode='html')

#Проверка правильности соотеветствия/перевода
@router.message(LearnWords.name)
async def get_name(message: Message, state: FSMContext):
    user_id = message.from_user.id

    data = await state.get_data()

    word = data['last_word']
    order_difficult_words = data['order_difficult_words']
    categories_id = data['categories_id']
    user_dict_id = data['user_dict_id']

    if message.text != 'ЗАКОНЧИТЬ':
        is_correct_answer = (message.text.lower() == word['name'].lower())
        if not is_correct_answer:
            await message.answer( f"{word['name']}  -  {word['matching']}" )

        if (not is_correct_answer) or (word['level_difficulty'] != 0):
            await set_level_difficulty(user_id, word, order_difficult_words, categories_id, is_correct_answer)

        await give_word(message, state)
    else:
        await state.clear()
        await message.answer('Ты большой молодец!')

        name_user_dict =  (await rq.get_name_user_dict_by_id(user_id, user_dict_id)).first()
        await message.answer(f'Словарь <b>{name_user_dict}</b>',
                             reply_markup=await kb.inline_categories(user_id, user_dict_id ),
                             parse_mode='html')


#-----------------------------------------------------------------------------------
#endregion


#endregion

