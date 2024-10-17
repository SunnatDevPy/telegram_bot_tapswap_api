from aiogram import Bot
from aiogram.types import InlineKeyboardButton, KeyboardButton, WebAppInfo
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder

from db import User, Channel

FASTAPI_URL = "https://yengi.mussi.uz/token"


def main_menu(user_id, language='uz', admin=False):
    if language == 'rus':
        tur = "⚽ Турниры"
        world = '🇪🇺 Евро турниры'
    else:
        world = "🇪🇺 Yevro turnirlar"
        tur = "⚽ Turnirlar"
    print(language)
    ikb = InlineKeyboardBuilder()
    ikb.add(*[InlineKeyboardButton(text="🔴LIVE🔴",
                                   web_app=WebAppInfo(
                                       url=f'https://football-stock.uz/#/{user_id}/{language}/')),
              InlineKeyboardButton(text=world, callback_data='game_world'),
              InlineKeyboardButton(text=tur, callback_data='game_country'),
              ])
    if admin:
        ikb.add(*[InlineKeyboardButton(text="⚙️Settings⚙️", callback_data='game_settings')])
    ikb.adjust(1, 2)
    return ikb.as_markup()


def link(url):
    ikb = InlineKeyboardBuilder()
    ikb.row(InlineKeyboardButton(text='Link', url=url))
    return ikb.as_markup()


def language_inl():
    ikb = InlineKeyboardBuilder()
    ikb.add(*[InlineKeyboardButton(text='🇺🇿Uz', callback_data='lang_uz'),
              InlineKeyboardButton(text='🇷🇺Ru', callback_data='lang_rus')])
    ikb.adjust(2)
    return ikb.as_markup()


async def admins():
    ikb = InlineKeyboardBuilder()
    for i in await User.get_admins():
        ikb.add(*[
            InlineKeyboardButton(text=i.username, callback_data=f'admins_{i.id}'),
            InlineKeyboardButton(text="❌", callback_data=f'admins_delete_{i.id}')
        ])
    ikb.row(InlineKeyboardButton(text="Admin qo'shish", callback_data="admins_add"))
    ikb.row(InlineKeyboardButton(text="⬅️Ortga️", callback_data="back_settings"))
    ikb.adjust(2, repeat=True)
    return ikb.as_markup()


def play_game(back, language="uz"):
    if language == 'rus':
        nat = "🔵Результаты🔵"
        live = "⚽️Живые игры⚽️"
        ortga = "⬅️Назад"
    else:
        ortga = "⬅️Ortga"
        live = "⚽️Live o'yinlar⚽️"
        nat = "🔵Natijalar🔵"
    ikb = InlineKeyboardBuilder()
    ikb.add(*[InlineKeyboardButton(text=live, callback_data='live'),
              InlineKeyboardButton(text=nat, callback_data='old_game'),
              InlineKeyboardButton(text=ortga, callback_data=f'back_{back}')])
    ikb.adjust(2, repeat=True)
    return ikb.as_markup()


def settings():
    ikb = InlineKeyboardBuilder()
    ikb.add(*[InlineKeyboardButton(text="📊Statistika📊", callback_data='settings_static'),
              InlineKeyboardButton(text="📝Xabar jo'natish📝", callback_data='settings_send'),
              InlineKeyboardButton(text="Adminlar", callback_data='settings_admins'),
              InlineKeyboardButton(text="Majburiy obuna", callback_data='settings_subscribe'),
              InlineKeyboardButton(text="ID olish", callback_data='settings_get-id'),
              InlineKeyboardButton(text="⬅️Ortga", callback_data='back_home')])
    ikb.adjust(2, repeat=True)
    return ikb.as_markup()


def send_text():
    ikb = InlineKeyboardBuilder()
    ikb.add(*[InlineKeyboardButton(text="Oddiy xabar", callback_data='send_text'),
              InlineKeyboardButton(text="📸Rasm-Videoli Xabar🎥", callback_data='send_video'),
              InlineKeyboardButton(text="⬅️Ortga", callback_data='back_settings')])
    ikb.adjust(2, repeat=True)
    return ikb.as_markup()


def clear():
    ikb = InlineKeyboardBuilder()
    ikb.row(InlineKeyboardButton(text='❌', callback_data='clear'))
    return ikb.as_markup()


def contact():
    ikb = ReplyKeyboardBuilder()
    ikb.row(KeyboardButton(text='📞 Contact 📞', request_contact=True))
    return ikb.as_markup(resize_keyboard=True)


def confirm_text():
    ikb = InlineKeyboardBuilder()
    ikb.add(*[InlineKeyboardButton(text="✅Jo'natish✅", callback_data='confirm'),
              InlineKeyboardButton(text="❌To'xtatish❌", callback_data='stop')])
    ikb.adjust(2, repeat=True)
    return ikb.as_markup()


def world_game(language='uz'):
    if language == 'rus':
        chemp = "Лига Чемпионов УЕФА"
        evro = "Лига Европы УЕФА"
        ortga = "Назад"
        konf = "Конференция Лиги"
    else:
        ortga = "Ortga"
        chemp = "UEFA Chempionlar ligasi"
        evro = "UEFA Yevropa ligasi"
        konf = "Konferensiyalar ligasi"
    ikb = InlineKeyboardBuilder()
    ikb.add(*[InlineKeyboardButton(text=f"🏆{chemp}",
                                   callback_data=f"cup_2_{chemp}"),
              InlineKeyboardButton(text=f"🏆{evro}",
                                   callback_data=f"cup_3_{evro}"),
              InlineKeyboardButton(text=f"🏆{konf}",
                                   callback_data=f'cup_21_{konf}'),
              InlineKeyboardButton(text=f"⬅️{ortga}",
                                   callback_data='back_home')])
    ikb.adjust(2, 1, 1)
    return ikb.as_markup()


def country_btn(language='uz'):
    if language == 'rus':
        ortga = "⬅️Назад"
    else:
        ortga = "⬅️Ortga"
    ikb = InlineKeyboardBuilder()
    ikb.add(*[InlineKeyboardButton(text="🇺🇿Uzbekistan🇺🇿",
                                   callback_data="country_Uzbekistan"),  # ✅
              InlineKeyboardButton(text="🏴󠁧󠁢󠁥󠁮󠁧󠁿England🏴󠁧󠁢󠁥󠁮󠁧󠁿",
                                   callback_data='country_England'),  # ✅
              InlineKeyboardButton(text="🇫🇷France🇫🇷",
                                   callback_data='country_France'),  # ✅
              InlineKeyboardButton(text="🇩🇪Germany🇩🇪",
                                   callback_data='country_Germany'),  # ✅
              InlineKeyboardButton(text="🇮🇹Italy🇮🇹",
                                   callback_data='country_Italy'),  # ✅
              InlineKeyboardButton(text="🇵🇹Portugal🇵🇹",
                                   callback_data='country_Portugal'),  # ✅
              InlineKeyboardButton(text="🇪🇸Spain🇪🇸",
                                   callback_data='country_Spain'),  # ✅
              ])
    ikb.add(*[InlineKeyboardButton(text=ortga,
                                   callback_data='back_home')])
    ikb.adjust(2, repeat=True)
    return ikb.as_markup()


def leagues(res, back='home', language='uz'):
    if language == 'rus':
        ortga = "⬅️Назад"
    else:
        ortga = "⬅️Ortga"
    ikb = InlineKeyboardBuilder()
    for i in res:
        ikb.add(*[InlineKeyboardButton(text=i['name'], callback_data=f"league_{i['name']}_{i['id']}")])
    ikb.add(*[InlineKeyboardButton(text=ortga,
                                   callback_data=f'back_{back}')])
    ikb.adjust(2, repeat=True)
    return ikb.as_markup()


async def network(net):
    ikb = InlineKeyboardBuilder()
    ikb.add(*[InlineKeyboardButton(text=i.name, url=i.link) for i in net])
    ikb.adjust(2, repeat=True)
    return ikb.as_markup()


def confirm_inl():
    ikb = InlineKeyboardBuilder()
    ikb.add(*[InlineKeyboardButton(text='✅Tasdiqlash✅', callback_data=f'confirm_network'),
              InlineKeyboardButton(text="❌Toxtatish❌", callback_data=f'cancel_network')])
    ikb.adjust(2, repeat=True)
    return ikb.as_markup()


async def make_channels(channel_ids, bot):
    ikb = InlineKeyboardBuilder()
    count = 1
    print(channel_ids)
    for channel_id in channel_ids:
        data = await bot.create_chat_invite_link(chat_id=channel_id)
        ikb.row(InlineKeyboardButton(text=f'Kanal {count}', url=data.invite_link))
        count += 1
    ikb.row(InlineKeyboardButton(text='Tasdiqlash', callback_data='confirm_channel'))
    return ikb.as_markup()


def confirm_channels(title, url):
    ikb = InlineKeyboardBuilder()
    ikb.add(*[InlineKeyboardButton(text="Kanal " + f'{title}', url=f'https://t.me/{url}')])
    ikb.add(*[InlineKeyboardButton(text="✅", callback_data='confirm_add_channel'),
              InlineKeyboardButton(text="❌", callback_data='cancel_add_channel')])
    ikb.adjust(1, 2)
    return ikb.as_markup()


async def show_channels(bot: Bot):
    ikb = InlineKeyboardBuilder()
    channels: list['Channel'] = await Channel.get_all()
    for i in channels:
        data = await bot.create_chat_invite_link(i.id)
        print(i.id, data.invite_link)
        ikb.add(*[InlineKeyboardButton(text=i.title, url=data.invite_link),
                  InlineKeyboardButton(text='❌', callback_data=f'channel_clear_{i.id}')])
    ikb.add(*[InlineKeyboardButton(text="Kanal qo'shish", callback_data='channel_add'),
              InlineKeyboardButton(text="⬅️Ortga", callback_data='back_settings')])
    ikb.adjust(2, repeat=True)
    return ikb.as_markup()
