import logging
import config
import database

from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext

logging.basicConfig(level=logging.INFO)

bot = Bot(token=config.TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

# клавиатура
menu = ReplyKeyboardMarkup(resize_keyboard=True)
menu.add("🛍 Каталог", "🛒 Корзина")

class OrderState(StatesGroup):

    phone = State()
    address = State()

# старт
@dp.message_handler(commands=["start"])
async def start(message: types.Message):

    await message.answer(
        "Добро пожаловать в магазин одежды 👕",
        reply_markup=menu
    )

# каталог
@dp.message_handler(lambda m: m.text == "🛍 Каталог")
async def catalog(message: types.Message):

    products = database.get_products()

    if not products:

        await message.answer("Товары скоро появятся")
        return

    for product in products:

        id, name, price, desc, image = product

        keyboard = InlineKeyboardMarkup()

        keyboard.add(
            InlineKeyboardButton(
                text="Добавить в корзину",
                callback_data=f"cart_{id}"
            )
        )

        try:

            photo = open(image, "rb")

            await bot.send_photo(
                message.chat.id,
                photo,
                caption=f"{name}\n{desc}\nЦена: {price}",
                reply_markup=keyboard
            )

        except:

            await message.answer(
                f"{name}\n{desc}\nЦена: {price}",
                reply_markup=keyboard
            )

# добавить в корзину
@dp.callback_query_handler(lambda c: c.data.startswith("cart_"))
async def add_cart(callback: types.CallbackQuery):

    product_id = int(callback.data.split("_")[1])

    database.add_to_cart(callback.from_user.id, product_id)

    await callback.answer("Добавлено")

# корзина
@dp.message_handler(lambda m: m.text == "🛒 Корзина")
async def cart(message: types.Message):

    items = database.get_cart(message.from_user.id)

    if not items:

        await message.answer("Корзина пустая")
        return

    text = "Корзина:\n\n"

    for item in items:

        text += f"{item[1]} - {item[2]}\n"

    keyboard = InlineKeyboardMarkup()

    keyboard.add(
        InlineKeyboardButton(
            text="Оформить заказ",
            callback_data="checkout"
        )
    )

    await message.answer(text, reply_markup=keyboard)

# checkout
@dp.callback_query_handler(lambda c: c.data == "checkout")
async def checkout(callback: types.CallbackQuery):

    await bot.send_message(
        callback.from_user.id,
        "Введите телефон"
    )

    await OrderState.phone.set()

# телефон
@dp.message_handler(state=OrderState.phone)
async def phone(message: types.Message, state: FSMContext):

    await state.update_data(phone=message.text)

    await message.answer("Введите адрес")

    await OrderState.address.set()

# адрес
@dp.message_handler(state=OrderState.address)
async def address(message: types.Message, state: FSMContext):

    data = await state.get_data()

    phone = data["phone"]
    address = message.text

    cart = database.get_cart(message.from_user.id)

    products = ", ".join([item[1] for item in cart])

    database.create_order(
        message.from_user.id,
        products,
        phone,
        address
    )

    database.clear_cart(message.from_user.id)

    await message.answer("Заказ оформлен")

    await bot.send_message(
        config.ADMIN_ID,
        f"Новый заказ\n\n{products}\n{phone}\n{address}"
    )

    await state.finish()

if __name__ == "__main__":

    executor.start_polling(dp)
