from aiogram import Bot, Dispatcher, types, executor
from dotenv import load_dotenv
import logging
import time
import os

from button import loc_button, num_button, inline_button1, inline_button2, inline_button3
from klients import DataBaseCustomers

db = DataBaseCustomers()
connect = db.connect
db.connect_db()



load_dotenv('.env')

bot = Bot(os.environ.get('TOKEN'))
dp = Dispatcher(bot)
logging.basicConfig(level=logging.INFO)

@dp.message_handler(commands='start')
async def start(message:types.Message):
    await message.answer(f'Здравствуйте, {message.from_user.full_name}')
    await message.answer("В этом боте вы можете оставить свой заказ на пиццу.\n\nНо не забывайте оставить ваш адрес и контактный номер!!!", reply_markup=inline_button1)
    cursor = connect.cursor()
    cursor.execute(f'SELECT user_id FROM customers WHERE user_id = {message.from_user.id};')
    result = cursor.fetchall()
    if result == []:
        cursor.execute(f"INSERT INTO customers VALUES ('{message.from_user.first_name}', '{message.from_user.last_name}', '{message.from_user.username}', '{message.from_user.id}', 'None');")
    connect.commit()

@dp.callback_query_handler(lambda call : call)
async def inline(call):
    if call.data == 'send_number':
        await get_number(call.message)
    elif call.data == 'send_location':
        await get_location(call.message)
    elif call.data == 'take_order':
        await get_order(call.message)

@dp.message_handler(commands='number')
async def get_number(message:types.Message):
    await message.answer('Подтвердите отправку своего номера.', reply_markup=num_button)

@dp.message_handler(content_types=types.ContentType.CONTACT)
async def add_number(message:types.Message):
    cursor = connect.cursor()
    cursor.execute(f"UPDATE customers SET phone_number = '{message.contact['phone_number']}' WHERE user_id = {message.from_user.id};")
    connect.commit()
    await message.answer("Ваш номер успешно добавлен.",reply_markup=inline_button3)

@dp.message_handler(commands='location')
async def get_location(message:types.Message):
    await message.answer("Подтвердите отправку местоположения.", reply_markup=loc_button)

@dp.message_handler(content_types=types.ContentType.LOCATION)
async def add_location(message:types.Message):
    address = f"{message.location.longitude}, {message.location.latitude}"
    cursor = connect.cursor()
    cursor.execute(f"INSERT INTO address VALUES ('{message.from_user.id}', '{message.location.longitude}', '{message.location.latitude}');")
    cursor.execute(f"UPDATE orders SET address_destination ='{address}';")
    connect.commit()
    await message.answer("Ваш адрес успешно записан", reply_markup=types.ReplyKeyboardRemove())

@dp.message_handler(commands='order')
async def get_order(message:types.Message):
    await message.reply("Прошу, меню:")

    with open('photo1.webp', 'rb') as photo1:
        await message.answer_photo(photo1, caption='1. Пепперони-сердце\n\n30 см, тонкое тесто, 380 г\n\nПепперони из говядины, моцарелла, томатный соус\n\nЦена: 649 сом')

    with open('photo2.webp', 'rb')as photo2:
        await message.answer_photo(photo2, caption='2. Ветчина и сыр\n\n30 см, традиционное тесто, 480 г\n\nВетчина из цыпленка, моцарелла, соус альфредо\n\nЦена: 475 сом')

    with open('photo3.webp', 'rb')as photo3:
        await message.answer_photo(photo3, caption='3. Сырный цыпленок\n\n30 см, традиционное тесто, 620 г\n\nЦыпленок, сырный соус, моцарелла, томаты, соус альфредо, смесь сыров чеддер и пармезан, чеснок сухой\n\nЦена: 695 сом')

    await message.answer("Введите номер из меню и мы запишем ваш заказ.")



@dp.message_handler(text=[1,2,3,4,5])
async def add_order(message:types.Message):
    cursor = connect.cursor()
    if message.text == '1':
        cursor.execute(f"INSERT INTO orders VALUES('{message.from_user.id}', 'Пицца-сказка', '' , '{time.ctime()}');")
    elif message.text == '2':
        cursor.execute(f"INSERT INTO orders VALUES('{message.from_user.id}', 'Пепперони-сердце', '', '{time.ctime()}');")
    elif message.text == '3':
        cursor.execute(f"INSERT INTO orders VALUES('{message.from_user.id}', 'Четыре сыра', '', '{time.ctime()}');")
    connect.commit()
    await message.reply("Ваш заказ записан. Укажите адрес",reply_markup=inline_button2)

executor.start_polling(dp)