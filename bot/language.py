from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from aiogram.utils.i18n import gettext as _

from bot.buttuns.inline import main_menu, make_channels, contact
from bot.handlers.admin import mandatory_channel
from bot.state.states import Contact
from db import User

language_router = Router()


@language_router.callback_query(F.data.startswith('lang_'))
async def language_handler(call: CallbackQuery, state: FSMContext, bot: Bot):
    lang_code = call.data.split('lang_')[-1]
    await call.message.delete()
    await state.update_data(locale=lang_code)
    await call.answer(_('Til tanlandi', locale=lang_code), show_alert=True)
    channels = await mandatory_channel(call.from_user.id, bot)
    if channels:
        try:
            await call.message.edit_text(_('Barchasiga obuna boling'),
                                         reply_markup=await make_channels(channels, bot))
        except:
            await call.message.answer(_('Barchasiga obuna boling'),
                                      reply_markup=await make_channels(channels, bot))
    else:
        user = await User.get(call.from_user.id)
        salom = _("Assalomu aleykum")
        davom = _("davom etish uchun contact yuboring")
        xush = _("Xush kelibsiz")
        if not user:
            await state.set_state(Contact.phone)
            await call.message.answer(
                f'{salom} {call.from_user.first_name}, {davom}',
                reply_markup=contact())
        else:
            if call.from_user.id in [1353080275, 5649321700] + [i for i in await User.get_admins()]:
                await call.message.answer(f'Xush kelibsiz Admin {call.from_user.first_name}',
                                          reply_markup=main_menu(call.from_user.id, admin=True))
            else:
                await call.message.answer(f'{xush} {call.from_user.first_name}',
                                          reply_markup=main_menu(call.from_user.id))
