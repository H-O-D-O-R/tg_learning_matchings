from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

import app.database.requests as rq





#СЛОВАРИ

async def inline_dictionaries(chat_id):
    keyboard = InlineKeyboardBuilder()
    await rq.get_user_dicts(chat_id)
    for user_dict in await rq.get_user_dicts(chat_id):
        keyboard.add(InlineKeyboardButton(text=user_dict.name, callback_data=f'dict_{user_dict.id}'))
    keyboard.add(InlineKeyboardButton(text='Новый словарь', callback_data='add new dict'))
    return keyboard.adjust(2).as_markup()

async def inline_edit_user_dict( user_dict_id ):
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text='Новая категория', callback_data=f'add new cat_{user_dict_id}'))
    keyboard.add(InlineKeyboardButton(text='Удалить словарь', callback_data=f'del dict_{user_dict_id}'))
    keyboard.add(InlineKeyboardButton(text='Назад', callback_data=f'dict_{user_dict_id}'))
    return keyboard.adjust(2).as_markup()

async def inline_confirm_del_user_dict(user_dict_id):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Да', callback_data=f'confirm del dict_{user_dict_id}'),
         InlineKeyboardButton(text='Нет', callback_data=f'edit dict_{user_dict_id}')]
        ])
    return keyboard





#КАТЕГОРИИ

async def inline_categories(chat_id, user_dict_id):

    categories = [[]]

    for category in await rq.get_categories(chat_id, user_dict_id):
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
    keyboard.add(InlineKeyboardButton(text='Новые слова', callback_data=f'add words_{category_id}'))
    keyboard.add(InlineKeyboardButton(text='Удалить слово', callback_data=f'del word_{category_id}'))
    keyboard.add(InlineKeyboardButton(text='Удалить категорию', callback_data=f'del cat_{category_id}'))
    keyboard.add(InlineKeyboardButton(text='Назад', callback_data=f'cat_{category_id}'))
    return keyboard.adjust(2).as_markup()

async def inline_confirm_del_category(category_id):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Да', callback_data=f'confirm del cat_{category_id}'),
         InlineKeyboardButton(text='Нет', callback_data=f'edit cat_{category_id}')]
        ])
    return keyboard





#СЛОВА

async def inline_words(chat_id, category_id, user_dict_id, current_page, cnt_pages, is_not_empty, less_name=False, less_matching=False, less_common_words=0):
    
    buttons = []

    if is_not_empty:

        if cnt_pages != 1:
            if current_page == 0:
                buttons.append([
                    InlineKeyboardButton(text='Вперёд', callback_data= f'next page_{category_id}')
                ])
            elif current_page == cnt_pages - 1:
                buttons.append([
                    InlineKeyboardButton(text='Назад', callback_data= f'previous page_{category_id}' )
                ])
            else:
                buttons.append([
                        InlineKeyboardButton(text='Назад', callback_data= f'previous page_{category_id}' ),
                        InlineKeyboardButton(text='Вперёд', callback_data= f'next page_{category_id}' )
                ])

        name, matching = (await rq.get_name_and_matching_user_dict_by_id(chat_id, user_dict_id)).first()
        
        if less_name == less_matching == False:
            buttons.append([
                InlineKeyboardButton(text=f'Убрать {name}', callback_data=f'discard name_{category_id}'),
                InlineKeyboardButton(text=f'Убрать {matching}', callback_data=f'discard matching_{category_id}')
            ])
        elif less_name:
            buttons.append([
                InlineKeyboardButton(text=f'Вернуть {name}', callback_data=f'return name_{category_id}')
            ])
        else:
            buttons.append([
                InlineKeyboardButton(text=f'Вернуть {matching}', callback_data=f'return matching_{category_id}')
            ]) 
        

        buttons.append([
            InlineKeyboardButton(text=f'{"Вернуть" if less_common_words else "Убрать"} простые слова', 
                                     callback_data=( f'return common_{category_id}' if less_common_words else f'discard common_{category_id}' ) ),
            InlineKeyboardButton(text=f'Перемешать слова', callback_data=f'shuffle_{category_id}')
        ])


    elif less_common_words:
        buttons.append([
            InlineKeyboardButton(text=f'{"Вернуть" if less_common_words else "Убрать"} простые слова', 
                                     callback_data=( f'return common_{category_id}' if less_common_words else f'discard common_{category_id}' ) )
        ])
    
    if is_not_empty:
        buttons.append([
            InlineKeyboardButton(text='Учить слова', callback_data=f'learn all_cat_{category_id}'), 
            InlineKeyboardButton(text='Учить сложные слова', callback_data=f'learn diff_cat_{category_id}')
            ])
    
    buttons.extend([
            [InlineKeyboardButton(text='Редактировать категорию', callback_data=f'edit cat_{category_id}')],
            [InlineKeyboardButton(text='Назад', callback_data=f'dict_{user_dict_id}')]
        ])

    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard

async def inline_confirm_del_word(word_id, category_id):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Да', callback_data=f'confirm del word_{word_id}_{category_id}'),
         InlineKeyboardButton(text='Нет', callback_data=f'edit cat_{category_id}')]
        ])
    return keyboard

async def reply_learn_word():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text='ЗАКОНЧИТЬ')]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    return keyboard

async def cancel_add_new_dict():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Отмена', callback_data=f'main')]
        ])
    return keyboard

async def cancel_delete_word(category_id):
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text='ОТМЕНА')]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    return keyboard

async def reply_cancel_add_new_item():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text='ОТМЕНА')]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    return keyboard