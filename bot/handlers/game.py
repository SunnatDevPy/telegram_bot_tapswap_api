from datetime import datetime, timedelta

from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.utils.text_decorations import html_decoration

from bot.buttuns.inline import leagues, world_game, country_btn, settings, main_menu, play_game, network, clear, \
    make_channels
from bot.handlers.admin import mandatory_channel
from bot.handlers.league import uzbekistan_league, england_league, france_league, germany_league, italy_league, \
    portugal_league, spain_league
from bot.handlers.resp import live_game, get_response
from db import Phone, About, Network, User

game_router = Router()

world_photo = {
    "2": 'https://telegra.ph/file/f1ca34ec9819b0b1eaa25.png',
    "3": 'https://upload.wikimedia.org/wikipedia/commons/thumb/7/78/Europa_League_2021.svg/640px-Europa_League_2021.svg.png',
    "21": 'https://telegra.ph/file/5e37be499f73b0b34f1f6.png',
}

country_photo = {
    "Uzbekistan": "https://telegra.ph/file/900a7fdbb33f941ca63f1.png",
    "England": "https://telegra.ph/file/5c7c005d0496df10acc95.png",
    "France": "https://telegra.ph/file/ef50f416c68b4a982cc2b.png",
    "Germany": "https://telegra.ph/file/d824b7f2336422888c23e.png",
    "Italy": "https://telegra.ph/file/c95738a4edfa7eb1f4624.png",
    "Portugal": "https://telegra.ph/file/8eb684a30efca30ad9b5e.png",
    "Spain": "https://telegra.ph/file/6eaa496f4fa0fddbd547b.png"
}


def web_app(leagues, id):
    for i in leagues:
        if i['id'] == int(id):
            return i["web_app"]


@game_router.callback_query(F.data.startswith('game_'))
async def leagues_handler(call: CallbackQuery, bot: Bot):
    channels = await mandatory_channel(call.from_user.id, bot)
    if channels:
        try:
            await call.message.edit_text('Barchasiga obuna boling',
                                         reply_markup=await make_channels(channels, bot))
        except:
            await call.message.answer('Barchasiga obuna boling',
                                      reply_markup=await make_channels(channels, bot))
    else:
        data = call.data.split('_')
        await call.answer()
        if data[-1] == 'world':
            await call.message.edit_text("<b>Jahon o'yinlari</b>", parse_mode='HTML', reply_markup=world_game())
        if data[-1] == 'country':
            await call.message.edit_text("<b>Davlatni tanlang</b>", parse_mode='HTML', reply_markup=country_btn())
        if data[-1] == 'call':
            res = await Phone.get(1)
            if res:
                await call.message.answer(res.name, parse_mode='HTML')
            else:
                await call.message.answer("Ma'lumot yo'q", parse_mode='HTML')
        if data[-1] == 'social':
            photo = 'https://telegra.ph/file/c9258b9460e1f3dccb5bc.png'
            networks = await Network.get_all()
            if networks:
                await call.message.answer_photo(photo, caption='Bizning ijtimoiy tarmoqlar', parse_mode='HTML',
                                                reply_markup=await network(networks))
            else:
                await call.message.answer("Ma'lumot yo'q", parse_mode='HTML')
        if data[-1] == 'info':
            res = await About.get(1)
            if res:
                await call.message.answer(res.name, parse_mode='HTML')
            else:
                await call.message.answer("Ma'lumot yo'q", parse_mode='HTML')
        if data[-1] == 'settings':
            await call.message.edit_text("<b>⚙️Settings⚙️</b>", parse_mode='HTML', reply_markup=settings())
        if data[-1] == 'command':
            pass


@game_router.callback_query(F.data == 'live')
async def leagues_handler(call: CallbackQuery, state: FSMContext, bot: Bot):
    channels = await mandatory_channel(call.from_user.id, bot)
    if channels:
        try:
            await call.message.edit_text('Barchasiga obuna boling',
                                         reply_markup=await make_channels(channels, bot))
        except:
            await call.message.answer('Barchasiga obuna boling',
                                      reply_markup=await make_channels(channels, bot))
    else:
        data = await state.get_data()
        await call.answer()
        ikb = InlineKeyboardBuilder()
        league = live_game(get_response("fixtures", {"live": "all"}), int(data['id']))
        await state.update_data(abouts=league[-1])
        if league[0]:
            await call.message.answer(f"{data['league']} live o'yinlari")
            for i, val in enumerate(league[0]):
                ikb.row(InlineKeyboardButton(text="Batafsil", callback_data=f"abouts_{i + 1}"))
                await call.message.answer(val, parse_mode='HTML', reply_markup=ikb.as_markup())
        else:
            await call.message.answer(html_decoration.bold(f"Boshlangan o'yin yo'q"), parse_mode='HTML')


@game_router.callback_query(F.data == 'old_game')
async def leagues_handler(call: CallbackQuery, state: FSMContext, bot: Bot):
    channels = await mandatory_channel(call.from_user.id, bot)
    if channels:
        try:
            await call.message.edit_text('Barchasiga obuna boling',
                                         reply_markup=await make_channels(channels, bot))
        except:
            await call.message.answer('Barchasiga obuna boling',
                                      reply_markup=await make_channels(channels, bot))
    else:
        data = await state.get_data()
        await call.answer()
        league = live_game(
            get_response("fixtures", {"league": data['id'], "season": datetime.now().year,
                                      "from": datetime.now().date() - timedelta(days=10), "to": datetime.now().date()}),
            int(data['id']))
        await state.update_data(abouts=league[-1])
        if league[0]:
            await call.message.answer(f"{data['league']} oldingi natija")
            for i, val in enumerate(league[0]):
                ikb = InlineKeyboardBuilder()
                ikb.add(*[InlineKeyboardButton(text="Batafsil", callback_data=f"abouts_{i + 1}")])
                await call.message.answer(val, parse_mode='HTML', reply_markup=ikb.as_markup())
        else:
            await call.message.answer(html_decoration.bold(f"Natija yo'q"), parse_mode='HTML')


@game_router.callback_query(F.data.startswith('abouts_'))
async def leagues_handler(call: CallbackQuery, state: FSMContext, bot: Bot):
    channels = await mandatory_channel(call.from_user.id, bot)
    if channels:
        try:
            await call.message.edit_text('Barchasiga obuna boling',
                                         reply_markup=await make_channels(channels, bot))
        except:
            await call.message.answer('Barchasiga obuna boling',
                                      reply_markup=await make_channels(channels, bot))
    else:
        data = await state.get_data()
        res = call.data.split('_')
        abouts = data.get('abouts')
        text = abouts[res[-1]]
        await call.message.edit_text(text, parse_mode='HTML', reply_markup=clear())


@game_router.callback_query(F.data == 'clear')
async def leagues_handler(call: CallbackQuery, state: FSMContext):
    await call.message.delete()


@game_router.callback_query(F.data == 'confirm_channel')
async def leagues_handler(call: CallbackQuery, state: FSMContext, bot: Bot):
    channels = await mandatory_channel(call.from_user.id, bot)
    if channels:
        try:
            await call.message.edit_text('Barchasiga obuna boling',
                                         reply_markup=await make_channels(channels, bot))
        except:
            await call.message.answer('Barchasiga obuna boling',
                                      reply_markup=await make_channels(channels, bot))
    else:
        await call.message.answer('Bosh menyu', reply_markup=main_menu())


@game_router.callback_query(F.data.startswith('cup_'))
async def leagues_handler(call: CallbackQuery, state: FSMContext, bot: Bot):
    channels = await mandatory_channel(call.from_user.id, bot)
    if channels:
        try:
            await call.message.edit_text('Barchasiga obuna boling',
                                         reply_markup=await make_channels(channels, bot))
        except:
            await call.message.answer('Barchasiga obuna boling',
                                      reply_markup=await make_channels(channels, bot))
    else:
        data = call.data.split('_')
        await call.message.delete()
        photo = world_photo[data[1]]
        await state.update_data(id=data[1])
        if data[1] == '2':
            await call.message.answer_photo(photo, caption=f"{data[-1]}", reply_markup=play_game(back='world'))
        elif data[1] == '3':
            await call.message.answer_photo(photo, caption=f"{data[-1]}", reply_markup=play_game(back='world'))
        elif data[1] == '21':
            await call.message.answer_photo(photo, caption=f"{data[-1]}", reply_markup=play_game(back='world'))


@game_router.callback_query(F.data.startswith('country_'))
async def league_handler(call: CallbackQuery, state: FSMContext, bot: Bot):
    channels = await mandatory_channel(call.from_user.id, bot)
    if channels:
        try:
            await call.message.edit_text('Barchasiga obuna boling',
                                         reply_markup=await make_channels(channels, bot))
        except:
            await call.message.answer('Barchasiga obuna boling',
                                      reply_markup=await make_channels(channels, bot))
    else:
        data = call.data.split('_')
        await state.update_data(name=data[1], back='country')
        await call.message.delete()
        photo = country_photo[data[-1]]
        if data[-1] == 'Uzbekistan':
            await state.update_data(leagues=uzbekistan_league)
            await call.message.answer_photo(photo=photo,
                                            caption=f'{data[-1]} ',
                                            reply_markup=leagues(uzbekistan_league, back='country'))
        elif data[-1] == 'England':
            await state.update_data(leagues=england_league)
            await call.message.answer_photo(photo=photo, caption=f'{data[-1]} ',
                                            reply_markup=leagues(england_league, back='country'))
        elif data[-1] == 'France':
            await state.update_data(leagues=france_league)
            await call.message.answer_photo(photo=photo, caption=f'{data[-1]} ',
                                            reply_markup=leagues(france_league, back='country'))
        elif data[-1] == 'Germany':
            await state.update_data(leagues=germany_league)
            await call.message.answer_photo(photo=photo, caption=f'{data[-1]} ',
                                            reply_markup=leagues(germany_league, back='country'))
        elif data[-1] == 'Italy':
            await state.update_data(leagues=italy_league)
            await call.message.answer_photo(photo=photo, caption=f'{data[-1]} ',
                                            reply_markup=leagues(italy_league, back='country'))
        elif data[-1] == 'Portugal':
            await state.update_data(leagues=portugal_league)
            await call.message.answer_photo(photo=photo, caption=f'{data[-1]} ',
                                            reply_markup=leagues(portugal_league, back='country'))
        elif data[-1] == 'Spain':
            await state.update_data(leagues=spain_league)
            await call.message.answer_photo(photo=photo, caption=f'{data[-1]} ',
                                            reply_markup=leagues(spain_league, back='country'))


@game_router.callback_query(F.data.startswith('league_'))
async def league_handler(call: CallbackQuery, state: FSMContext, bot: Bot):
    channels = await mandatory_channel(call.from_user.id, bot)
    if channels:
        try:
            await call.message.edit_text('Barchasiga obuna boling',
                                         reply_markup=await make_channels(channels, bot))
        except:
            await call.message.answer('Barchasiga obuna boling',
                                      reply_markup=await make_channels(channels, bot))
    else:
        await call.message.delete()
        data = call.data.split('_')
        res = await state.get_data()
        await call.answer()
        await state.update_data(league=data[1], id=data[-1])
        await call.message.answer(f'{data[1]} liga',
                                  reply_markup=play_game('country' if res.get('back') == 'country' else 'world'))


@game_router.callback_query(F.data.startswith('back_'))
async def leagues_handler(call: CallbackQuery, bot: Bot):
    data = call.data.split('_')
    if data[-1] == 'home':
        await call.message.delete()
        if call.from_user.id in [1353080275, 5649321700] + [i for i in await User.get_admins()]:
            await call.message.answer(f'Admin {call.from_user.first_name}',
                                      reply_markup=main_menu(admin=True))
        else:
            await call.message.answer("<b>Bosh menyu</b>", parse_mode='HTML', reply_markup=main_menu())
    if data[-1] == 'settings':
        await call.message.edit_text("<b>⚙️Settings⚙️</b>", parse_mode='HTML', reply_markup=settings())
    if data[-1] == 'country':
        await call.message.delete()
        await call.message.answer("<b>Davlatlar️</b>", parse_mode='HTML', reply_markup=country_btn())
    if data[-1] == 'world':
        await call.message.delete()
        await call.message.answer("<b>Davlatlar️</b>", parse_mode='HTML', reply_markup=world_game())
