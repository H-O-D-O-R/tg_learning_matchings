from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

import app.database.requests as rq





# СЛОВАРИ

# Формирование клавиатуры для выбора словаря
async def inline_dictionaries(current_page, num_current_page, cnt_pages):

    dicts = [[]]

    # Формируем кнопки для словарей по 2 в ряд
    for user_dict_id, name_user_dict in current_page:
        if len(dicts[-1]) == 2:
            dicts.append([])
        dicts[-1].append(InlineKeyboardButton(text=name_user_dict, callback_data=f'dict_{user_dict_id}'))

    buttons = []
    if dicts:
        buttons.extend(dicts)

    # Добавляем кнопки для навигации между страницами категорий, если страниц больше одной
    if cnt_pages != 1:
        if num_current_page == 0:
            buttons.append([InlineKeyboardButton(text='Вперёд', callback_data=f'next dict page')])
        elif num_current_page == cnt_pages - 1:
            buttons.append([InlineKeyboardButton(text='Назад', callback_data=f'previous dict page')])
        else:
            buttons.append([
                InlineKeyboardButton(text='Назад', callback_data=f'previous dict page'),
                InlineKeyboardButton(text='Вперёд', callback_data=f'next dict page')
            ])

    # Добавляем кнопку для создания новго словаря
    buttons.append([
        InlineKeyboardButton(text='Новый словарь', callback_data='add new dict')
    ])

    return InlineKeyboardMarkup(inline_keyboard=buttons)


# Клавиатура для редактирования словаря
async def inline_edit_user_dict(user_dict_id):

    keyboard = InlineKeyboardBuilder()

    # Кнопки для добавления категории, удаления словаря и возврата к словарям
    keyboard.add(InlineKeyboardButton(text='Новая категория', callback_data=f'add new cat_{user_dict_id}'))
    keyboard.add(InlineKeyboardButton(text='Удалить словарь', callback_data=f'del dict_{user_dict_id}'))
    keyboard.add(InlineKeyboardButton(text='Назад', callback_data=f'dict_{user_dict_id}'))

    return keyboard.adjust(2).as_markup()


# Подтверждение удаления словаря
async def inline_confirm_del_user_dict(user_dict_id):

    # Клавиатура для подтверждения удаления словаря

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Да', callback_data=f'confirm del dict_{user_dict_id}'),
         InlineKeyboardButton(text='Нет', callback_data=f'edit dict_{user_dict_id}')]
    ])

    return keyboard



# КАТЕГОРИИ

# Формирование клавиатуры для категорий с кнопками для навигации
async def inline_categories(user_dict_id, current_page, num_current_page, cnt_pages):

    categories = [[]]

    # Формируем кнопки для категорий по 2 в ряд
    for id_category, name_category in current_page:
        if len(categories[-1]) == 2:
            categories.append([])
        categories[-1].append(InlineKeyboardButton(text=name_category, callback_data=f'cat_{id_category}'))

    buttons = []
    if categories:
        buttons.extend(categories)

    # Добавляем кнопки для навигации между страницами категорий, если страниц больше одной
    if cnt_pages != 1:
        if num_current_page == 0:
            buttons.append([InlineKeyboardButton(text='Вперёд', callback_data=f'next cat page_{user_dict_id}')])
        elif num_current_page == cnt_pages - 1:
            buttons.append([InlineKeyboardButton(text='Назад', callback_data=f'previous cat page_{user_dict_id}')])
        else:
            buttons.append([
                InlineKeyboardButton(text='Назад', callback_data=f'previous cat page_{user_dict_id}'),
                InlineKeyboardButton(text='Вперёд', callback_data=f'next cat page_{user_dict_id}')
            ])

    # Добавляем кнопки для повтора слов, редактирования категории и возврата к словарям
    buttons.extend([
        [InlineKeyboardButton(text='Повторяемые слова', callback_data=f'repeating words_{user_dict_id}')],
        [InlineKeyboardButton(text='Повторять слова', callback_data=f'repeat all_dict_{user_dict_id}')],
        [InlineKeyboardButton(text='Редактировать словарь', callback_data=f'edit dict_{user_dict_id}')],
        [InlineKeyboardButton(text='Назад', callback_data='main')]
    ])

    return InlineKeyboardMarkup(inline_keyboard=buttons)


# Клавиатура для редактирования категории
async def inline_edit_category(category_id):

    keyboard = InlineKeyboardBuilder()

    # Кнопки для добавления, удаления слов и категорий, а также кнопка возврата
    keyboard.add(InlineKeyboardButton(text='Новое слово', callback_data=f'add new word_{category_id}'))
    keyboard.add(InlineKeyboardButton(text='Новые слова', callback_data=f'add words_{category_id}'))
    keyboard.add(InlineKeyboardButton(text='Удалить слово', callback_data=f'del word_{category_id}'))
    keyboard.add(InlineKeyboardButton(text='Удалить категорию', callback_data=f'del cat_{category_id}'))
    keyboard.add(InlineKeyboardButton(text='Назад', callback_data=f'cat_{category_id}'))

    return keyboard.adjust(2).as_markup()


# Клавиатура для подтверждения удаления категории
async def inline_confirm_del_category(category_id):
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Да', callback_data=f'confirm del cat_{category_id}'),
         InlineKeyboardButton(text='Нет', callback_data=f'edit cat_{category_id}')]
    ])
    return keyboard



# СЛОВА

# Формирование клавиатуры для управления списком слов, включая фильтры и навигацию
async def inline_words(user_id, category_id, user_dict_id, current_page, cnt_pages, is_not_empty, less_name=False, less_matching=False, less_common_words=0):

    buttons = []

    # Добавляем кнопки навигации между страницами, если есть несколько страниц
    if is_not_empty:
        if cnt_pages != 1:
            if current_page == 0:
                buttons.append([InlineKeyboardButton(text='Вперёд', callback_data=f'next page_{category_id}')])
            elif current_page == cnt_pages - 1:
                buttons.append([InlineKeyboardButton(text='Назад', callback_data=f'previous page_{category_id}')])
            else:
                buttons.append([
                    InlineKeyboardButton(text='Назад', callback_data=f'previous page_{category_id}'),
                    InlineKeyboardButton(text='Вперёд', callback_data=f'next page_{category_id}')
                ])

        # Определяем, какие кнопки отображать: скрыть или вернуть слова/соответствия, и добавляем их
        name, matching = (await rq.get_name_and_matching_user_dict_by_id(user_id, user_dict_id)).first()
        if not less_name and not less_matching:
            buttons.append([
                InlineKeyboardButton(text=f'Убрать {name}', callback_data=f'discard name_{category_id}'),
                InlineKeyboardButton(text=f'Убрать {matching}', callback_data=f'discard matching_{category_id}')
            ])
        elif less_name:
            buttons.append([InlineKeyboardButton(text=f'Вернуть {name}', callback_data=f'return name_{category_id}')])
        else:
            buttons.append([InlineKeyboardButton(text=f'Вернуть {matching}', callback_data=f'return matching_{category_id}')])

        # Кнопка для того, чтобы убрать/вернуть простые слова и перемешивания
        buttons.append([
            InlineKeyboardButton(text=f'{"Вернуть" if less_common_words else "Убрать"} простые слова', 
                                 callback_data=(f'return common_{category_id}' if less_common_words else f'discard common_{category_id}')),
            InlineKeyboardButton(text='Перемешать слова', callback_data=f'shuffle_{category_id}')
        ])
    elif less_common_words:
        buttons.append([
            InlineKeyboardButton(text="Вернуть простые слова", 
                                 callback_data=(f'return common_{category_id}'))
        ])

    # Добавляем кнопки для изучения слов и возврата к редактированию категории
    if is_not_empty:
        buttons.append([
            InlineKeyboardButton(text='Учить слова', callback_data=f'learn all_cat_{category_id}'), 
            InlineKeyboardButton(text='Учить сложные слова', callback_data=f'learn diff_cat_{category_id}')
        ])
    buttons.extend([
        [InlineKeyboardButton(text='Редактировать категорию', callback_data=f'edit cat_{category_id}')],
        [InlineKeyboardButton(text='Назад', callback_data=f'dict_{user_dict_id}')]
    ])

    return InlineKeyboardMarkup(inline_keyboard=buttons)


# Формирование клавиатуры для управления списком слов, включая фильтры и навигацию
async def inline_repeating_words(user_id, user_dict_id, current_page, cnt_pages, is_not_empty, less_name=False, less_matching=False):

    buttons = []

    # Добавляем кнопки навигации между страницами, если есть несколько страниц
    if is_not_empty:
        if cnt_pages != 1:
            if current_page == 0:
                buttons.append([InlineKeyboardButton(text='Вперёд', callback_data=f'next repeating page_{user_dict_id}')])
            elif current_page == cnt_pages - 1:
                buttons.append([InlineKeyboardButton(text='Назад', callback_data=f'previous repeating page_{user_dict_id}')])
            else:
                buttons.append([
                    InlineKeyboardButton(text='Назад', callback_data=f'previous repeating page_{user_dict_id}'),
                    InlineKeyboardButton(text='Вперёд', callback_data=f'next repeating page_{user_dict_id}')
                ])

        # Определяем, какие кнопки отображать: скрыть или вернуть слова/соответствия, и добавляем их
        name, matching = (await rq.get_name_and_matching_user_dict_by_id(user_id, user_dict_id)).first()
        if not less_name and not less_matching:
            buttons.append([
                InlineKeyboardButton(text=f'Убрать {name}', callback_data=f'discard repeating name_{user_dict_id}'),
                InlineKeyboardButton(text=f'Убрать {matching}', callback_data=f'discard repeating matching_{user_dict_id}')
            ])
        elif less_name:
            buttons.append([InlineKeyboardButton(text=f'Вернуть {name}', callback_data=f'return repeating name_{user_dict_id}')])
        else:
            buttons.append([InlineKeyboardButton(text=f'Вернуть {matching}', callback_data=f'return repeating matching_{user_dict_id}')])

        # Кнопка для перемешивания
        buttons.append([
            InlineKeyboardButton(text='Перемешать слова', callback_data=f'shuffle repeating_{user_dict_id}')
        ])

    # Добавляем кнопки для изучения слов и возврата к редактированию категории
    if is_not_empty:
        buttons.append([
            InlineKeyboardButton(text='Повторять слова', callback_data=f'repeat all_dict_{user_dict_id}')
        ])
    buttons.append([
        InlineKeyboardButton(text='Назад', callback_data=f'dict_{user_dict_id}')
    ])

    return InlineKeyboardMarkup(inline_keyboard=buttons)


# Клавиатура для подтверждения удаления слова
async def inline_confirm_del_word(word_id, category_id):
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Да', callback_data=f'confirm del word_{word_id}_{category_id}'),
         InlineKeyboardButton(text='Нет', callback_data=f'edit cat_{category_id}')]
    ])

    return keyboard


# Клавиатура для кнопки завершения обучения
async def reply_learn_word():
    
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text='ЗАКОНЧИТЬ')]],
        resize_keyboard=True,
        one_time_keyboard=True
    )

    return keyboard


# Клавиатура для отмены добавления словаря
async def cancel_add_new_dict():
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Отмена', callback_data='main')]
    ])

    return keyboard


# Клавиатура для отмены удаления слова
async def cancel_delete_word():
    
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text='ОТМЕНА')]],
        resize_keyboard=True,
        one_time_keyboard=True
    )

    return keyboard


# Клавиатура для отмены добавления нового элемента
async def reply_cancel_add_new_item():
    
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text='ОТМЕНА')]],
        resize_keyboard=True,
        one_time_keyboard=True
    )

    return keyboard
