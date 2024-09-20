from aiogram import Router, Bot, html
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from bot.buttuns.inline import main_menu, make_channels, contact
from bot.handlers.admin import mandatory_channel
from bot.state.states import Contact
from config import BOT
from db import User, Statusie

start_router = Router()


@start_router.message(CommandStart())
async def command_start(message: Message, bot: Bot, state: FSMContext):
    if message.from_user.id in [1353080275, 5649321700] + [i for i in await User.get_admins()]:
        await message.answer(f'Hush kelibsiz Admin {message.from_user.first_name}',
                             reply_markup=main_menu(message.from_user.id, admin=True))
    else:
        channels = await mandatory_channel(message.from_user.id, bot)
        if channels:
            try:
                await message.edit_text('Barchasiga obuna boling',
                                        reply_markup=await make_channels(channels, bot))
            except:
                await message.answer('Barchasiga obuna boling',
                                     reply_markup=await make_channels(channels, bot))
        else:
            user = await User.get(message.from_user.id)
            if not user:
                await state.set_state(Contact.phone)
                await message.answer(
                    f'Assalomu aleykum {message.from_user.first_name},davom etish uchun contact yuboring',
                    reply_markup=contact())

            else:
                await message.answer(f'Hush kelibsiz {message.from_user.first_name}',
                                     reply_markup=main_menu(message.from_user.id))


@start_router.message(Contact.phone)
async def command_start(message: Message, bot: Bot):
    status = await Statusie.get_all()
    user_data = {'id': int(message.from_user.id), 'username': message.from_user.username,
                 'first_name': message.from_user.first_name, 'last_name': message.from_user.last_name,
                 "phone": str(message.contact.phone_number), 'coins': 0, "status_id": int(status[0].id), "bonus": 1,
                 "energy": 200}
    if message.contact and message.from_user.id == message.contact.user_id:
        await User.create(**user_data)
        await message.answer(f'Hush kelibsiz {message.from_user.first_name}',
                             reply_markup=main_menu(message.from_user.id))
        await bot.send_message(int(BOT.ADMIN),
                               f'Yangi user qo\'shildi @{message.from_user.username}!',
                               reply_markup=main_menu(message.from_user.id))
        await bot.send_message(1353080275,
                               f'Yangi user qo\'shildi @{message.from_user.username}!',
                               reply_markup=main_menu(message.from_user.id))
    else:
        await message.answer(html.bold("Iltimos o'zingizni contactni yuboring"), reply_markup=contact())
