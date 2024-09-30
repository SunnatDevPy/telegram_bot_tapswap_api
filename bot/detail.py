import datetime

import bcrypt
from aiogram.utils.text_decorations import html_decoration

from db import User


def hello(first_name):
    return html_decoration.bold(f'''
Assalomu aleykum, Hush kelibsiz {first_name}
Bot orqali dunyo bo'ylab futbol malumotlarini bilib oling
    ''')


def channel_detail(chat):
    text = html_decoration.bold(f'''
Chat
ID: {html_decoration.code(chat.id)}
Name: {chat.title}
Username: {chat.username}
Count users: {chat.get_member_count()}
    ''')
    return text

# date_format = '%Y-%m-%d %H:%M:%S'
#
# print(datetime.datetime.strptime(date_format))
