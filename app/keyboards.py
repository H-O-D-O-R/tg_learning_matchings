from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

import app.database.requests as rq





#СЛОВАРИ

async def inline_dictionaries():
    keyboard = InlineKeyboardBuilder()
    for user_dict in await rq.get_user_dicts():
        keyboard.add(InlineKeyboardButton(text=user_dict.name, callback_data=f'dict_{user_dict.id}'))
    keyboard.add(InlineKeyboardButton(text='Новый словарь', callback_data='add new dict'))
    return keyboard.adjust(2).as_markup()

async def inline_edit_user_dict( user_dict_id ):
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text='Новая категория', callback_data=f'add new cat_{user_dict_id}'))
    keyboard.add(InlineKeyboardButton(text='Удалить словарь', callback_data=f'del dict_{user_dict_id}'))
    return keyboard.adjust(2).as_markup()

async def inline_confirm_del_user_dict(user_dict_id):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Да', callback_data=f'confirm del dict_{user_dict_id}'),
         InlineKeyboardButton(text='Нет', callback_data=f'dict_{user_dict_id}')]
        ])
    return keyboard





#КАТЕГОРИИ

async def inline_categories(user_dict_id):

    categories = [[]]

    for category in await rq.get_categories(user_dict_id):
        if len(categories[-1]) == 2:
            categories.append([])
        categories[-1].append( InlineKeyboardButton(text=category.name, callback_data=f'cat_{category.id}') )

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        *categories,
        [InlineKeyboardButton(text='Учить слова', callback_data=f'learn all_dict_{user_dict_id}'),
         InlineKeyboardButton(text='Учить сложные слова', callback_data=f'learn diff_dict_{user_dict_id}')],
        [InlineKeyboardButton(text='Редактировать словарь', callback_data=f'edit dict_{user_dict_id}')],
        [InlineKeyboardButton(text='Назад', callback_data='main')]
    ])

    return keyboard

async def inline_edit_category( category_id ):
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text='Новое слово', callback_data=f'add new word_{category_id}'))
    keyboard.add(InlineKeyboardButton(text='Новые слова', callback_data=f'add new words_{category_id}'))
    keyboard.add(InlineKeyboardButton(text='Удалить слово', callback_data=f'del word_{category_id}'))
    keyboard.add(InlineKeyboardButton(text='Удалить категорию', callback_data=f'del cat_{category_id}'))
    return keyboard.adjust(2).as_markup()

async def inline_confirm_del_category(category_id):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Да', callback_data=f'confirm del cat_{category_id}'),
         InlineKeyboardButton(text='Нет', callback_data=f'cat_{category_id}')]
        ])
    return keyboard





#СЛОВА

async def inline_words(category_id, user_dict_id, is_not_empty=False, less=None):

    buttons = [
            [InlineKeyboardButton(text='Редактировать категорию', callback_data=f'edit cat_{category_id}')],
            [InlineKeyboardButton(text='Назад', callback_data=f'dict_{user_dict_id}')]
        ]
    
    if is_not_empty:
        name, matching = (await rq.get_name_and_matching_user_dict_by_id(user_dict_id)).first()

        buttons = [[InlineKeyboardButton(text='Учить слова', callback_data=f'learn all_cat_{category_id}'), 
            InlineKeyboardButton(text='Учить сложные слова', callback_data=f'learn diff_cat_{category_id}')]] + buttons
        
        if less is None:
            buttons = [[
                InlineKeyboardButton(text=f'Убрать {name}', callback_data=f'discard_{category_id}_name'),
                InlineKeyboardButton(text=f'Убрать {matching}', callback_data=f'discard_{category_id}_matching')
            ]] + buttons
        else:
            name_less = ( name if less == 'name' else matching )
            buttons = [[
                InlineKeyboardButton(text=f'Вернуть {name_less}', callback_data=f'return_{category_id}_{less}')
            ]] + buttons


    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard

async def inline_confirm_del_word(word_id, category_id):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Да', callback_data=f'confirm del word_{word_id}_{category_id}'),
         InlineKeyboardButton(text='Нет', callback_data=f'cat_{category_id}')]
        ])
    return keyboard

async def reply_learn_word():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text='/Закончить')]
        ],
        resize_keyboard=True,       # Уменьшает размер кнопки
        one_time_keyboard=True      # Кнопка исчезает после использования
    )
    return keyboard