from aiogram.fsm.state import StatesGroup, State


class SendTextState(StatesGroup):
    text = State()
    video = State()
    link = State()
    confirm = State()


class AddLink(StatesGroup):
    name = State()
    link = State()


class ChangeText(StatesGroup):
    name = State()


class AddChannelState(StatesGroup):
    chat_id = State()
    confirm = State()


class ForwardState(StatesGroup):
    chat_id = State()


class AddAdmin(StatesGroup):
    user_id = State()


class DeleteChannels(StatesGroup):
    chat_id = State()

class Contact(StatesGroup):
    phone = State()
