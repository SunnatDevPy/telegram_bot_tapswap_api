from aiogram import Router, html
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove

from bot.buttuns.inline import main_menu, contact, language_inl
from bot.state.states import Contact
from db import User, Statusie
from db.models.model import Referral, Event, UserAndEvent
from db.utils import update_question

start_router = Router()


@start_router.message(CommandStart())
async def command_start(message: Message, state: FSMContext):
    data = await state.get_data()
    locale = data.get('locale')
    if locale == 'rus':
        til = "Выберите язык"
    else:
        til = 'Til tanlang'
    await message.answer(til, reply_markup=language_inl())
    if ' ' in message.text:
        args = message.text.split(' ')[1]
        print(args)
    else:
        args = None

    if args:
        inviter_id = int(args)
        user = await User.get(inviter_id)
        referred = await Referral.get_from_referral_and_referred(inviter_id, message.from_user.id)
        if referred is None:
            await Referral.create(referrer_id=inviter_id, referred_user_id=message.from_user.id)
            await User.update(inviter_id, coins=user.coins + 5000)
        else:
            await state.update_data(referred_id=inviter_id, referred_user_id=message.from_user.id)


@start_router.message(Contact.phone)
async def command_start(message: Message, state: FSMContext):
    data = await state.get_data()
    lang_loc = data.get('locale')
    if lang_loc == "rus":
        xush = "Здравствуйте"
        bosh = "Главный меню"
        contact_message = "Пожалуйста, отправьте свой контакт"
    else:
        xush = "Assalomu aleykum"
        bosh = "Bosh menyu"
        contact_message = "Iltimos o'zingizni contactni yuboring"
    status = await Statusie.get_alls()
    if message.contact and message.from_user.id == message.contact.user_id:
        user = await User.get(message.from_user.id)
        if user:
            if message.from_user.id in [1353080275, 5649321700] + [i for i in await User.get_admins()]:
                await message.answer(f"{xush} Admin {message.from_user.first_name}", reply_markup=ReplyKeyboardRemove())
                await message.answer(bosh,
                                     reply_markup=main_menu(message.from_user.id, data.get('locale'), admin=True, ))
            else:
                await message.answer(f"{xush} {message.from_user.first_name}", reply_markup=ReplyKeyboardRemove())
                await message.answer(bosh,
                                     reply_markup=main_menu(message.from_user.id, data.get('locale')))
        else:
            user = await User.create(id=int(message.from_user.id), last_name=message.from_user.last_name,
                                     first_name=message.from_user.first_name,
                                     username=message.from_user.username, phone=str(message.contact.phone_number),
                                     coins=0,
                                     is_admin=False, status_id=status[0].id, bonus=1, energy=200, max_energy=200,
                                     hour_coin=0)

            for i in await Event.get_alls():
                await UserAndEvent.create(user_id=user.id, event_id=i.id, status=False)

            await update_question(message.from_user.id)

            await message.answer(f"{xush} {message.from_user.first_name}", reply_markup=ReplyKeyboardRemove())
            await message.answer(bosh,
                                 reply_markup=main_menu(message.from_user.id, data.get('locale')))
    else:
        await message.answer(html.bold(contact_message),
                             reply_markup=contact(), parse_mode="HTML")
