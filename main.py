import logging
import asyncio
from aiogram import Bot, Dispatcher, types, filters
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
# работа с базой данных
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

import config
import base.logics as logics

# Работа с файловой системой и пр.
from os import getenv
from sys import exit
import re
# Для превращения словарей в объекты (хз чет не догоняю)
import datetime

# Пользовательские материалы в проекте
# from content.descriptions import instructions, help, greetings, admins_start


# состояние пользователя в чате - возможно удалить
class dialog(StatesGroup):
    spam = State()
    blacklist = State()
    whitelist = State()

# States - охраняем состояния

class Form(StatesGroup):
    phone = State()
    car_number = State()
    meet_car = State()


# Включение бота и диспетчера
bot_token = getenv("BOT_TOKEN")
if not bot_token:
    exit("Error: no token provided")
storage = MemoryStorage()
bot = Bot(token=bot_token)
dp = Dispatcher(bot=bot, storage=storage)
logging.basicConfig(level=logging.INFO)


# Пример админ меню на развитие функционала
kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
kb.add(types.InlineKeyboardButton(text="Рассылка"))
kb.add(types.InlineKeyboardButton(text="Добавить в ЧС"))
kb.add(types.InlineKeyboardButton(text="Убрать из ЧС"))
kb.add(types.InlineKeyboardButton(text="Статистика"))


# Хороший генератор кнопок. Если потребуются разные форматы на 3 и более столбца, то применять. Пока как пример.
def build_menu(buttons, n_cols,
               header_buttons=None,
               footer_buttons=None):
    menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
    if header_buttons:
        menu.insert(0, [header_buttons])
    if footer_buttons:
        menu.append([footer_buttons])
    return menu


# Создание кнопок для простого пользователя.
user_buttons = types.InlineKeyboardMarkup()
user_buttons.add(
    types.InlineKeyboardButton(text='добавить авто', callback_data='add_car'),
    types.InlineKeyboardButton(text='вижу друга на дороге', callback_data='meet_car')
                )
# Создание клавиатуры со switch-кнопками для отправки бота для админа
send_bot_buttons = types.InlineKeyboardMarkup()
send_bot_buttons.add(
    types.InlineKeyboardButton(text=f"Отправить бота", switch_inline_query=""),
    types.InlineKeyboardButton(text="Вызвать бота здесь", switch_inline_query_current_chat=""))


def initiation():  # OK
    if logics.get_users(config.database):
        print(f'С базой всё ОК, запускаем сервис')
        base_ok = True
    else:
        print(f'не смог открыть базу')
        base_ok = False
    return base_ok


async def start(message: types.Message):  # OK
    # print("Зашли в старт")
    current_user = message.from_user
    if await logics.first_time_user(current_user):
        print('Новый пользователь')
        await message.answer("greetings")
        await bot.send_message(
            358708312,  # Admin
            f'Пришел новый пользователь {message.from_user.first_name}, (@{message.from_user.username})'
        )
        await message.answer("Пользуйся функционалом", reply_markup=user_buttons)

    elif logics.get_admin(current_user.id):
        print(f'Зашёл Админ')
        await message.answer("Функционал админа", reply_markup=send_bot_buttons)
        await message.answer("функционал пользователя", reply_markup=user_buttons)
    else:
        await message.answer("Пользуйся функционалом", reply_markup=user_buttons)


@dp.callback_query_handler(lambda call: call.data == 'add_car')
async def cmd_get_number(call: types.CallbackQuery):
    await call.answer()
    await bot.edit_message_reply_markup(call.message.chat.id,
                                        message_id=call.message.message_id)  # удаляем кнопки у последнего сообщения
    await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)

    await Form.car_number.set()
    await bot.send_message(call.from_user.id, "Привет! Укажите номер своего автомобиля (кириллица).")


@dp.message_handler(lambda message: message.text, state=Form.car_number)
async def number_handler(message: types.Message, state: Form.car_number):
    # Проверяем номер машины по формату
    match = re.fullmatch(r'[а-яА-Я]\d{3}[а-яА-Я]{2}\d{2,3}', message.text)
    if match:  # Если формат, то проверяем есть ли в базе и добавляем.
        car_in_base = await logics.get_car_from_base(message.text)
        if car_in_base is None:
            if await logics.save_car(message.text, message.from_user.id):
                await bot.send_message(message.from_user.id, f'Добавили номер Вашего авто в базу')
                await bot.send_message(358708312, f'У нас новый автомобиль в базе:\n'  # Todo надо писать всем админам
                                                  f'Номер - {message.text}\n'
                                                  f'Пользователь - @{message.from_user.username} '
                )

                await state.finish()
            else:
                await bot.send_message(message.from_user.id, f'По какой-то причине не добавили номер машины в базу.')
        else:
            await bot.send_message(message.from_user.id, f'машина с этим номером уже есть в базе')  # Todo - разрешить менять
        await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
        await start(message)
    else:
        await bot.send_message(message.from_user.id, 'Номер не подходит по формату. Используйте Кириллицу')


@dp.callback_query_handler(lambda call: call.data == 'meet_car')
async def cmd_get_number(call: types.CallbackQuery):
    await call.answer()
    await bot.edit_message_reply_markup(call.message.chat.id,
                                        message_id=call.message.message_id)  # удаляем кнопки у последнего сообщения
    await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)

    await Form.meet_car.set()
    await bot.send_message(call.from_user.id,
            "Напишите номер автомобиля (кириллица). Его водитель увидит запрос и ответит, если захочет.")


@dp.message_handler(lambda message: message.text, state=Form.meet_car)
async def number_handler(message: types.Message, state: Form.meet_car):
    # Проверяем, есть ли у пользователя никнейм. Без него не связать водителей.
    if message.from_user.username is None:
        await bot.send_message(message.from_user.id, f'Укажите в настройках профиля Ваш ник. Это необходимо, '
                                                     f'чтобы пользователь мог Вам написать в ответ')
        await state.finish()
        await start(message)

    else:
        # Проверяем номер машины по формату
        match = re.fullmatch(r'[а-яА-Я]\d{3}[а-яА-Я]{2}\d{2,3}', message.text)
        if match:  # Если формат, то проверяем есть ли в базе и добавляем.
            car_in_base = await logics.get_car_from_base(message.text.lower())
            if car_in_base is not None:
                await bot.send_message(car_in_base.user_id,  # пишем водителю искомого авто
                                       f'Дорогой водитель, с Вами пытается связаться участник чата "passat b8.msk" - '
                                       f'@{message.from_user.username} Напишите ему, он будет счастлив.')
                await bot.send_message(message.from_user.id,  # пишем водителю искомого авто
                                       f'Водителю автомобиля с номером {car_in_base.gos_reg_znak} направлено предложение'
                                       f' написать Вам сообщение.')

                await bot.send_message(358708312,
                                       f'Водителю  автомобиля с номером {message.text} направлено предложение ответить '
                                       f'пользователю @{message.from_user.username}. Дальше они сами')

                await state.finish()
            else:
                await bot.send_message(message.from_user.id, f'машины с этим номером нет в базе')  # Todo - разрешить менять
            await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
            await start(message)
        else:
            await bot.send_message(message.from_user.id, 'Номер не подходит по формату. Используйте Кириллицу')


# -- пока тут


# async def instruction_key(message: types.Message):
#     global i_key
#     keyboard = types.InlineKeyboardMarkup(row_width=2, inline_keyboard=None)
#     buttons = []
#     for note_type in instructions.keys():
#         buttons.append(types.InlineKeyboardButton(text=note_type, callback_data=note_type))
#     keyboard.add(*buttons)
#
#     await message.answer("Выбери <u>вид записи</u>.", reply_markup=keyboard, parse_mode=types.ParseMode.HTML)


# @dp.callback_query_handler(lambda call: call.data == 'back_to_instruction')
# async def back_to_instruction(call: types.CallbackQuery):
#     await call.answer()
#     await bot.edit_message_reply_markup(call.message.chat.id,
#                                         message_id=call.message.message_id)  # удаляем кнопки у последнего сообщения
#     await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
#
#     await instruction_key(call.message)


#
#
# @dp.callback_query_handler(lambda call: call.data in instructions.keys())
# async def instruction_value(call: types.CallbackQuery):
#
#     await call.answer()
#     print(f'Запрос от пользователя "{call.from_user.first_name}" - "{call.data}"')
#     global data, i_key
#     i_key = call.data
#     await bot.edit_message_reply_markup(call.message.chat.id,
#                                         message_id=call.message.message_id)  # удаляем кнопки у последнего сообщения
#     keyboard = types.InlineKeyboardMarkup(row_width=2)
#     # Собираем меню кнопок
#     buttons = []
#     for element in instructions[i_key]:
#         buttons.append(types.InlineKeyboardButton(text=element, callback_data=element))
#     keyboard.add(*buttons)
#     # отдельно добавляем кнопку Назад, чтобы она всегда была внизу и одна
#     keyboard.add(types.InlineKeyboardButton(text="Назад", callback_data="back_to_instruction"))
#     data = instructions[i_key].keys()
#     await call.message.edit_text(f'и элемент из "{call.data}" ? ', reply_markup=keyboard)
#

# @dp.callback_query_handler(lambda call: call.data in data)
# async def instruction_notice(call: types.CallbackQuery):
#     global i_value
#     i_value = call.data
#     # print(data)
#     # print(i_key)
#     # print(i_value)
#     # print(call)
#     print(f'Запрос деталей от пользователя "{call.from_user.first_name}" - "{call.data}"')
#     await bot.answer_callback_query(callback_query_id=call.id,
#                                     show_alert=True,
#                                     text=f'В {call.data} важно:\n {instructions[i_key][i_value]}')
#     await call.answer()


# Система хранения состояний. Пока не разобрался.
async def shutdown(dispatcher: Dispatcher):
    await dispatcher.storage.close()
    await dispatcher.storage.wait_closed()


async def main():
    if initiation():
        try:
            dp.register_message_handler(start, commands={"start"})
            dp.register_message_handler(help, commands={"help"})
            await dp.start_polling()
        finally:
            await bot.close()
    else:
        print(f'Работа сервиса невозможна')

asyncio.run(main())
