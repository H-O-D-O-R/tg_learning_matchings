from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from io import StringIO, BytesIO
from openpyxl import load_workbook
import csv

from random import shuffle


import app.keyboards as kb
import app.database.requests as rq

router = Router()

#region States
class RegistationNewDict(StatesGroup):
    name = State()
    matching = State()

class RegistationNewCat(StatesGroup):
    user_dict_id = ''
    name = State()

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
    words = []
    order_difficult_words = []
    last_word = {}
    name = State()

class RegistationNewWords(StatesGroup):
    category_id = ''
    file = State()

#endregion


@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer('Выбери словарь:', reply_markup= await kb.inline_dictionaries())

@router.callback_query(F.data == 'main')
async def cmd_start_for_callback(callback: CallbackQuery):
    await cmd_start(callback.message)





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
    await state.set_state(RegistationNewDict.name)
    await callback.message.answer('Введите название', reply_markup= await kb.reply_cancel_add_new_item())

#Получение названия словаря
@router.message(RegistationNewDict.name)
async def set_name_dict(message: Message, state: FSMContext):
    if message.text == 'ОТМЕНА':
        await cmd_start(message)
        return
    
    await state.set_state(RegistationNewDict.matching)
    await state.update_data(name=message.text)
    await message.answer('Введите соответствие', reply_markup= await kb.reply_cancel_add_new_item())

#Получение соответствия словаря
@router.message(RegistationNewDict.matching)
async def set_name_dict(message: Message, state: FSMContext):
    if message.text == 'ОТМЕНА':
        await cmd_start(message)
        return
    
    await state.update_data(matching=message.text)
    data = await state.get_data()
    await state.clear()

    name_user_dict = data['name']
    matching_user_dict = data['matching']

    await rq.add_new_user_dict(name_user_dict, matching_user_dict)
    await message.answer('Словарь <b>{name_user_dict}</b> создан!'.format(name_user_dict=name_user_dict), 
                         parse_mode="html")

    user_dict_id = (await rq.get_id_user_dict_by_name(name_user_dict)).first()
    await message.answer(f'Словарь <b>{name_user_dict}</b>', 
                         reply_markup=await kb.inline_categories( user_dict_id ), 
                         parse_mode='html')

#-----------------------------------------------------------------------------------
#endregion



#ВЫВОД КАТЕГОРИЙ СЛОВАРЯ
#region
#-----------------------------------------------------------------------------------
#                              /start/{название словаря}
#-----------------------------------------------------------------------------------


@router.callback_query(F.data.startswith('dict'))
async def displlay_user_dicts(callback: CallbackQuery):
    user_dict_id = callback.data.split('_')[1]
    name_user_dict =  (await rq.get_name_user_dict_by_id(user_dict_id)).first()
    await callback.message.answer(f'Словарь <b>{name_user_dict}</b>', 
                                  reply_markup=await kb.inline_categories( user_dict_id ), 
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
    user_dict_id = callback.data.split('_')[1]
    name_user_dict = (await rq.get_name_user_dict_by_id(user_dict_id)).first()

    await callback.message.answer(f'Словарь <b>{name_user_dict}</b>', 
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
    name_user_dict = (await rq.get_name_user_dict_by_id(callback.data.split('_')[1])).first()
    await callback.message.answer(f'Вы точно хотите удалить словарь {name_user_dict}?', 
                                  reply_markup= await kb.inline_confirm_del_user_dict(callback.data.split('_')[1]))

#Получение подтверждения
@router.callback_query(F.data.startswith('confirm del dict'))
async def confirm_del_user_dict(callback: CallbackQuery):
    user_dict_id = callback.data.split('_')[1]
    name_user_dict = (await rq.get_name_user_dict_by_id(user_dict_id)).first()
    await rq.delete_dict(user_dict_id)
    await callback.message.answer(f"Словарь <b>{name_user_dict}</b> удалён", parse_mode='html')
    await callback.message.answer('Выбери словарь:', 
                                  reply_markup= await kb.inline_dictionaries())

#-----------------------------------------------------------------------------------
#endregion


#endregion





####################################################################################

#                              РАБОТА С КАТЕГОРИЕЙ

####################################################################################
#region CATEGORIES


#ВЫВОД СЛОВ КАТЕГОРИИ
#region
#-----------------------------------------------------------------------------------
#                  /start/{название словаря}/{название категории}
#-----------------------------------------------------------------------------------


@router.callback_query(F.data.startswith('cat'))
async def display_words(callback: CallbackQuery):

    category_id = callback.data.split('_')[1]
    user_dict_id = (await rq.get_id_user_dict_by_id_category(category_id)).first()

    category = (await rq.get_name_category_by_id( callback.data.split('_')[1] )).first()

    items = [item for item in await rq.get_words_by_category(category_id)]
    shuffle(items)
    await callback.message.answer(
        f"Категория <b>{category}</b>\n\n{(
                '\n'.join(item.name +'  -  '+ '<i>'+item.matching+'</i>' for item in items)
                if items else 'Здесь пока пусто'
                	            )}",
        reply_markup=await kb.inline_words( category_id, user_dict_id, bool(items) ),
        parse_mode='html'        
        )


#Убрать слово/соответствие в категории
@router.callback_query(F.data.startswith('discard'))
async def display_edit_words_discard(callback: CallbackQuery):

    category_id = callback.data.split('_')[1]
    less = callback.data.split('_')[2]
    user_dict_id = (await rq.get_id_user_dict_by_id_category(category_id)).first()

    category = (await rq.get_name_category_by_id( callback.data.split('_')[1] )).first()

    items = [
        ('<i>' if less == 'name' else '') +
        item.split('  -  ')[ less == 'name' ] 
        + ('</i>' if less == 'name' else '')
        for item in callback.message.text.split('\n')[2:]
        ]

    await callback.message.edit_text(
            text=f"Категория <b>{category}</b>\n\n{(
                '\n'.join(items) if items else 'Здесь пока пусто'
                )}",
            reply_markup=await kb.inline_words(category_id, user_dict_id, bool(items), less),
            parse_mode='html'
        )

#Вернуть слово/соответствие в категории
@router.callback_query(F.data.startswith('return'))
async def display_edit_words_return(callback: CallbackQuery):

    category_id = callback.data.split('_')[1]
    less = callback.data.split('_')[2]
    user_dict_id = (await rq.get_id_user_dict_by_id_category(category_id)).first()

    category = (await rq.get_name_category_by_id( callback.data.split('_')[1] )).first()

    if less == 'matching':
        items = [
            item + '  -  ' + '<i>'+(await rq.get_matching_by_name_and_category_id(item, category_id)).first()+'</i>'
            for item in callback.message.text.split('\n')[2:]
            ]
    else:
        items = [
            (await rq.get_name_by_matching_and_category_id(item, category_id)).first() + '  -  ' + item
            for item in callback.message.text.split('\n')[2:]
            ]

    await callback.message.edit_text(
        text=f"Категория <b>{category}</b>\n\n{(
                '\n'.join(items) if items else 'Здесь пока пусто'
                	            )}",
        reply_markup=await kb.inline_words( category_id, user_dict_id, bool(items) ),
        parse_mode='html'
        )


#-----------------------------------------------------------------------------------
#endregion



#СОЗДАНИЕ НОВОЙ КАТЕГОРИИ
#region
#-----------------------------------------------------------------------------------
#    /start/{название словаря}/редактировать словарь/добавить новую категорию
#-----------------------------------------------------------------------------------


@router.callback_query(F.data.startswith('add new cat'))
async def add_new_category(callback: CallbackQuery, state: FSMContext):
    await state.set_state(RegistationNewCat.name)
    await state.update_data(user_dict_id= callback.data.split('_')[1])
    await callback.message.answer('Введите название', reply_markup= await kb.reply_cancel_add_new_item())

#Получение названия категории
@router.message(RegistationNewCat.name)
async def set_name_category(message: Message, state: FSMContext):
    if message.text == 'ОТМЕНА':
        data = await state.get_data()
        await state.clear()

        user_dict_id = data['user_dict_id']
        name_user_dict =  (await rq.get_name_user_dict_by_id(user_dict_id)).first()

        await message.answer(f'Словарь <b>{name_user_dict}</b>', 
                                  reply_markup=await kb.inline_categories( user_dict_id ), 
                                  parse_mode='html')

        return 
    await state.update_data(name=message.text)
    data = await state.get_data()
    await state.clear()
    await rq.add_new_category(data['user_dict_id'], message.text)
    category_id = (await rq.get_id_category_by_name(message.text)).first()
    await message.answer(f"Категория <b>{message.text}</b>\n\nЗдесь пока пусто", 
                         reply_markup= await kb.inline_words(category_id, data['user_dict_id'], False),
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
    category_id = callback.data.split('_')[1]
    name_category = (await rq.get_name_category_by_id(category_id)).first()
    await callback.message.answer(f'Категория <b>{name_category}</b>', 
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
    category_id = callback.data.split('_')[1]
    name_category = (await rq.get_name_category_by_id(category_id)).first()
    await callback.message.answer(f'Вы точно хотите удалить категорию {name_category}?', 
                                  reply_markup= await kb.inline_confirm_del_category(category_id))

#Получение подтверждения
@router.callback_query(F.data.startswith('confirm del cat'))
async def confirm_del_category(callback: CallbackQuery):
    category_id = callback.data.split('_')[1]
    name_category = (await rq.get_name_category_by_id(category_id)).first()
    user_dict_id = (await rq.get_id_user_dict_by_id_category(category_id)).first()
    name_user_dict = (await rq.get_name_user_dict_by_id(user_dict_id)).first()
    await rq.delete_category(category_id)
    await callback.message.answer(f"Категория <b>{name_category}</b> удалена", 
                                  parse_mode='html')
    await callback.message.answer(f'Словарь <b>{name_user_dict}</b>', 
                                  reply_markup=await kb.inline_categories( user_dict_id ), 
                                  parse_mode='html')

#-----------------------------------------------------------------------------------
#endregion


#endregion




####################################################################################

#                              РАБОТА СО СЛОВАМИ

####################################################################################
#region WORDS


#ДОБАВЛЕНИЕ НОВОГО СЛОВА В КАТЕГОРИЮ
#region
#-----------------------------------------------------------------------------------
#                /start/{название словаря}/{название категории}
#                /редактировать категорию/добавить новое слово
#-----------------------------------------------------------------------------------


@router.callback_query(F.data.startswith('add new word'))
async def add_new_word(callback: CallbackQuery, state: FSMContext):
    await state.set_state(RegistationNewItem.name)
    await state.update_data(category_id=callback.data.split('_')[1])
    await state.update_data(user_dict_id= 
                            (await rq.get_id_user_dict_by_id_category( 
                                callback.data.split('_')[1])).first() )
    await callback.answer('Добавить новое слово')
    await callback.message.answer('Введите слово', reply_markup= await kb.reply_cancel_add_new_item())

#Получение слова
@router.message(RegistationNewItem.name)
async def set_name_word(message: Message, state: FSMContext):
    if message.text == 'ОТМЕНА':
        data = await state.get_data()
        await state.clear()

        category_id = data['category_id']
        category = (await rq.get_name_category_by_id(category_id)).first()
        user_dict_id = (await rq.get_id_user_dict_by_id_category(category_id)).first()
        items = [item for item in await rq.get_words_by_category(category_id)]

        await message.answer(f"Категория <b>{category}</b>\n\n{(
            '\n'.join(item.name +'  -  '+ '<i>'+item.matching+'</i>' for item in items)
            if items else 'Здесь пока пусто'    )}",
                    reply_markup=await kb.inline_words(
                        category_id, user_dict_id, bool(items)
                    ),
                    parse_mode='html'
        )

        return 
    
    await state.update_data(name=message.text)
    await state.set_state(RegistationNewItem.matching)
    await message.answer('Введите перевод', reply_markup= await kb.reply_cancel_add_new_item())

#Получение соответствия (перевод)
@router.message(RegistationNewItem.matching)
async def set_matching_word(message: Message, state: FSMContext):
    if message.text == 'ОТМЕНА':
        data = await state.get_data()
        await state.clear()

        category_id = data['category_id']
        category = (await rq.get_name_category_by_id(category_id)).first()
        user_dict_id = (await rq.get_id_user_dict_by_id_category(category_id)).first()
        items = [item for item in await rq.get_words_by_category(category_id)]

        await message.answer(f"Категория <b>{category}</b>\n\n{(
        '\n'.join(item.name +'  -  '+ '<i>'+item.matching+'</i>' for item in items)
        if items else 'Здесь пока пусто'    )}",
                reply_markup=await kb.inline_words( 
                    category_id, user_dict_id, bool(items)
                ),
                parse_mode='html'
        )

        return 
    
    await state.update_data(matching=message.text)
    data = await state.get_data()
    await state.clear()

    await rq.add_new_word(data['category_id'], data['name'], data['matching'])
    await message.answer('Слово добавлено!')

    category = (await rq.get_name_category_by_id( data['category_id'] )).first()
    user_dict_id = (await rq.get_id_user_dict_by_id_category(data['category_id'])).first()
    items = [item for item in await rq.get_words_by_category(data['category_id'])]

    await message.answer(f"Категория <b>{category}</b>\n\n{(
        '\n'.join(item.name +'  -  '+ '<i>'+item.matching+'</i>' for item in items)
        if items else 'Здесь пока пусто'    )}",
                reply_markup=await kb.inline_words( 
                    data['category_id'], user_dict_id, bool(items)
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
    await state.set_state(RegistationNewWords.file)
    await state.update_data(category_id=callback.data.split('_')[1])

    await callback.message.answer(
        'Отправьте файл формата .txt. Каждая строка должна быть шаблона: "<i>слово</i> - <i>соответветствие</i>"', 
                                  parse_mode='html', 
                                  reply_markup= await kb.reply_cancel_add_new_item()
                                  )



@router.message(RegistationNewWords.file)
async def set_new_words(message: Message, state: FSMContext):
    if message.text == 'ОТМЕНА':
        data = await state.get_data()
        await state.clear()

        category_id = data['category_id']
        category = (await rq.get_name_category_by_id(category_id)).first()
        user_dict_id = (await rq.get_id_user_dict_by_id_category(category_id)).first()
        items = [item for item in await rq.get_words_by_category(category_id)]

        await message.answer(f"Категория <b>{category}</b>\n\n{(
        '\n'.join(item.name +'  -  '+ '<i>'+item.matching+'</i>' for item in items)
        if items else 'Здесь пока пусто'    )}",
                reply_markup=await kb.inline_words( 
                    category_id, user_dict_id, bool(items)
                ),
                parse_mode='html'
        )

        return 
    
    document = message.document

    if not document or not (
        document.mime_type.startswith('text/') or 
        document.mime_type in ['application/vnd.ms-excel', 'text/csv', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet']
    ):
        await message.answer("Пожалуйста, отправьте текстовый, CSV или XLSX документ")
        return

    data = await state.get_data()
    await state.clear()

    file = await message.bot.get_file(document.file_id)
    downloaded_file = await message.bot.download_file(file.file_path)

    try:
        if document.mime_type in ['application/vnd.ms-excel', 'text/csv']:
            content = downloaded_file.read().decode('utf-8')
            string_io = StringIO(content)
            csv_reader = csv.reader(string_io)
            
            words_data = [
                (name, matching)
                for name, matching 
                in csv_reader
            ]

        elif document.mime_type.startswith('text/'):
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
        
        await rq.add_new_words(data['category_id'], words_data)
        await message.answer('Слова добавлены!')

    except:
        await message.answer(f"Произошла ошибка при обработке файла")
        return

    category = (await rq.get_name_category_by_id(data['category_id'])).first()
    user_dict_id = (await rq.get_id_user_dict_by_id_category(data['category_id'])).first()
    items = [item for item in await rq.get_words_by_category(data['category_id'])]

    await message.answer(f"Категория <b>{category}</b>\n\n{(
        '\n'.join(item.name + '  -  ' + '<i>' + item.matching + '</i>' for item in items)
        if items else 'Здесь пока пусто'
    )}",
        reply_markup=await kb.inline_words(
            data['category_id'], user_dict_id, bool(items)
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
    await state.set_state(ConfirmDelWord.name)
    await state.update_data(category_id=callback.data.split('_')[1])
    await callback.answer('Удалить слово')
    await callback.message.answer('Введите слово, которое хотите удалить')

#Получение слова
@router.message(ConfirmDelWord.name)
async def get_name_word_for_delete(message: Message, state: FSMContext):
    name_word = message.text
    data = await state.get_data()
    await state.clear()
    category_id = data['category_id']

    if (await rq.check_word_in_category(name_word, category_id)).first() is None:
        name_category = (await rq.get_name_category_by_id(category_id)).first()

        await message.answer(f'Слово {name_word} отсутствует в категории {name_category}')
        await message.answer(f'Категория <b>{name_category}</b>', 
                                  reply_markup= await kb.inline_edit_category(category_id),
                                  parse_mode='html'
                                  )
    
        return

    word_id = (await rq.get_id_word_by_name(name_word, category_id)).first()
    await message.answer(f'Вы точно хотите удалить слово {name_word}?', 
                                  reply_markup= await kb.inline_confirm_del_word(word_id, category_id))

#Получение подтверждения
@router.callback_query(F.data.startswith('confirm del word'))
async def confirm_del_word(callback: CallbackQuery):
    word_id = callback.data.split('_')[1]
    name_word = (await rq.get_name_word_by_id(word_id)).first()
    category_id = callback.data.split('_')[2]
    name_category = (await rq.get_name_category_by_id(category_id)).first()


    await rq.delete_word(word_id)
    await callback.message.answer(f"Слово {name_word} удалено")
    items = [item for item in await rq.get_words_by_category(category_id)]
    await callback.message.answer(f"Категория <b>{name_category}</b>\n\n{(
        '\n'.join(item.name +'  -  '+ '<i>'+item.matching+'</i>' for item in items)
        if items else 'Здесь пока пусто'    )}",
                                   reply_markup=await kb.inline_words( 
                                       category_id, 
                                       (await rq.get_id_user_dict_by_id_category(category_id)).first(),
                                       bool(items)
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

    if callback.data.split('_')[1] == 'dict':
        user_dict_id = callback.data.split('_')[2]
        categories_id = [category_id for category_id in await rq.get_categories_id_by_user_dict_id(user_dict_id)]
    else:
        categories_id = [ callback.data.split('_')[2] ]

    words = []
    
    for word in await rq.get_common_words_by_categories_id(categories_id):
        name, matching = word.name, word.matching
        words.append({'name': name, 'matching': matching, 'level_difficulty': 0})
    
    shuffle(words)

    await list_of_difficult_words(callback, state, words, categories_id, True)
    
#Обработка списка сложных слов
@router.callback_query(F.data.startswith('learn diff'))
async def list_of_difficult_words(callback: CallbackQuery, state: FSMContext, words: list = [], categories_id: list = [], is_call: bool = False):

    if not is_call:
        if callback.data.split('_')[1] == 'dict':
            user_dict_id = callback.data.split('_')[2]
            categories_id = [category_id for category_id in await rq.get_categories_id_by_user_dict_id(user_dict_id)]
        else:
            categories_id = [ callback.data.split('_')[2] ]

    difficult_words = {1: [], 2: [], 3: []}

    for word in await rq.get_difficult_words_by_categories_id(categories_id):
        name, matching = word.name, word.matching
        difficult_words[word.level_difficulty].append( (name, matching) )

    order_difficult_words = []
    for level_difficulty in range(1, 4):
        shuffle(difficult_words[level_difficulty])
        for word in difficult_words[level_difficulty]:
            name, matching = word
            await set_level_difficulty({'name': name, 'matching': matching, 'level_difficulty': level_difficulty},
                                       order_difficult_words, categories_id)
    
    await give_word(callback.message, order_difficult_words, words, categories_id, state)

#Изменить сложность слова
async def set_level_difficulty(word, order_difficult_words, categories_id: list, correct_answer=None):
    if correct_answer is None:
        level_difficulty = word['level_difficulty']
    elif correct_answer:
        level_difficulty = word['level_difficulty'] + 1
        if level_difficulty == 4:
            level_difficulty = 0
        await rq.set_new_level_difficulty_word(word['name'], level_difficulty, categories_id)
    else:
        level_difficulty = word['level_difficulty']
        if level_difficulty != 1:
            level_difficulty = 1
            await rq.set_new_level_difficulty_word(word['name'], level_difficulty, categories_id)
    
    word['level_difficulty'] = level_difficulty

    if level_difficulty != 0:
        step_for_word = 5 * level_difficulty
        for _ in range( step_for_word - 1 - len(order_difficult_words) ):
            order_difficult_words.append(None)
        
        order_difficult_words.insert( 5 * level_difficulty, word )

#Вывод слова изучаемого раздела
async def give_word(message: Message, order_difficult_words: list, words: list, categories_id: list, state:FSMContext):
    await state.set_state(LearnWords.name)
    await state.update_data(categories_id = categories_id)
    await state.update_data(words = words)
    await state.update_data(order_difficult_words = order_difficult_words)

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
        await message.answer('Поздравяю! Ты выучил слова')
        user_dict_id = (await rq.get_id_user_dict_by_id_category(categories_id[0])).first()
        name_user_dict =  (await rq.get_name_user_dict_by_id(user_dict_id)).first()
        await message.answer(f'Словарь <b>{name_user_dict}</b>', 
                             reply_markup=await kb.inline_categories( user_dict_id ), 
                             parse_mode='html')

#Проверка правильности соотеветствия/перевода
@router.message(LearnWords.name)
async def get_name(message: Message, state: FSMContext):
    data = await state.get_data()
    word = data['last_word']
    order_difficult_words = data['order_difficult_words']
    categories_id = data['categories_id']
    words = data['words']
    
    if message.text != '/Закончить':
        is_correct_answer = (message.text.lower() == word['name'].lower())
        if not is_correct_answer:
            await message.answer( f"{word['name']}  -  {word['matching']}")

        if (not is_correct_answer) or (word['level_difficulty'] != 0):
            await set_level_difficulty(word, order_difficult_words, categories_id, is_correct_answer)

        await give_word(message, order_difficult_words, words, categories_id, state)
    else:
        await state.clear()

        await message.answer('Ты большой молодец!')
        user_dict_id = (await rq.get_id_user_dict_by_id_category(categories_id[0])).first()
        name_user_dict =  (await rq.get_name_user_dict_by_id(user_dict_id)).first()
        await message.answer(f'Словарь <b>{name_user_dict}</b>', 
                             reply_markup=await kb.inline_categories( user_dict_id ), 
                             parse_mode='html')


#-----------------------------------------------------------------------------------
#endregion


#endregion

