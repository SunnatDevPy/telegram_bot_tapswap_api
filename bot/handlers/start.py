from aiogram import Router, Bot, html
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from bot.buttuns.inline import main_menu, make_channels, contact
from bot.handlers.admin import mandatory_channel
from bot.state.states import Contact
from config import BOT
from db import User, Statusie, Experience
from db.models.model import UserAndExperience, Referral

start_router = Router()


@start_router.message(CommandStart())
async def command_start(message: Message, bot: Bot, state: FSMContext):
    if ' ' in message.text:
        args = message.text.split(' ')[1]
        print(args)
    else:
        args = None

    if args:
        inviter_id = int(args)
        user = await User.get(inviter_id)
        if inviter_id != message.from_user.id:
            if await User.get(message.from_user.id):
                await Referral.create(referrer_id=inviter_id, referred_user_id=message.from_user.id)
                await User.update(inviter_id, coins=user.coins + 5000)
            else:
                await state.update_data(referred_id=inviter_id, referred_user_id=message.from_user.id)

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
            if message.from_user.id in [1353080275, 5649321700] + [i for i in await User.get_admins()]:
                await message.answer(f'Hush kelibsiz Admin {message.from_user.first_name}',
                                     reply_markup=main_menu(message.from_user.id, admin=True))
            else:
                await message.answer(f'Hush kelibsiz {message.from_user.first_name}',
                                     reply_markup=main_menu(message.from_user.id))


@start_router.message(Contact.phone)
async def command_start(message: Message, bot: Bot, state: FSMContext):
    data = await state.get_data()
    print(data)
    status = await Statusie.get_all()
    user_data = {'id': int(message.from_user.id), 'username': message.from_user.username,
                 'first_name': message.from_user.first_name, 'last_name': message.from_user.last_name,
                 "phone": str(message.contact.phone_number), 'coins': 0, "status_id": int(status[0].id), "bonus": 1,
                 "energy": 200, "max_energy": 200}
    if message.contact and message.from_user.id == message.contact.user_id:
        user = await User.create(**user_data)
        if data.get("referred_id") and data.get("referred_user_id"):
            user = await User.get(data.get("referred_id"))
            await Referral.create(referrer_id=data.get("referred_id"), referred_user_id=data.get("referred_user_id"))
            await User.update(user.id, coins=user.coins + 5000)
        experience = await Experience.get_all()
        for i in experience:
            await UserAndExperience.create(user_id=user.id, degree=i.degree, hour_coin=i.hour_coin, price=i.price,
                                           experience_id=i.id, energy=0, bonus=0)
        await message.answer(f'Hush kelibsiz {message.from_user.first_name}',
                             reply_markup=main_menu(message.from_user.id))
        await bot.send_message(int(BOT.ADMIN),
                               f'Yangi user qo\'shildi @{message.from_user.username}!')
        await bot.send_message(1353080275,
                               f'Yangi user qo\'shildi @{message.from_user.username}!')
    else:
        await message.answer(html.bold("Iltimos o'zingizni contactni yuboring"), reply_markup=contact())
