import asyncio
import os
from datetime import datetime
from random import shuffle

from pykeyboard import InlineKeyboard
from pyrogram import filters
from pyrogram.errors.exceptions.bad_request_400 import (
    ChatAdminRequired, UserNotParticipant)
from pyrogram.types import (ChatPermissions, InlineKeyboardButton,
                            InlineKeyboardMarkup, Message, User)

from prime import SUDOERS, WELCOME_DELAY_KICK_SEC, app
from prime.core.decorators.errors import capture_err
from prime.core.decorators.permissions import adminsOnly
from prime.utils.dbfunctions import (captcha_off, captcha_on,
                                   del_welcome, get_captcha_cache,
                                   get_welcome, is_captcha_on,
                                   is_gbanned_user, set_welcome,
                                   update_captcha_cache)
from prime.utils.filter_groups import welcome_captcha_group
from prime.utils.functions import generate_captcha

__MODULE__ = "Greetings"
__HELP__ = """
/captcha [ENABLE|DISABLE] - Enable/Disable captcha.
/set_welcome - Reply this to a message containing correct
format for a welcome message, check end of this message.
/del_welcome - Delete the welcome message.
/get_welcome - Get the welcome message.
**SET_WELCOME ->**
The format should be something like below.
```
**Hi** {name} Welcome to {chat}
~ #This separater (~) should be there between text and buttons, remove this comment also
button=[Duck, https://duckduckgo.com]
button2=[Github, https://github.com]
```
**NOTES ->**
for /rules, you can do /filter rules to a message
containing rules of your groups whenever a user
sends /rules, he'll get the message
"""




""" WELCOME MESSAGE """


@app.on_message(filters.command("setwelcome") & ~filters.private)
@adminsOnly("can_change_info")
async def set_welcome_func(_, message):
    usage = "You need to reply to a text, check the Greetings module in /help"
    if not message.reply_to_message:
        await message.reply_text(usage)
        return
    if not message.reply_to_message.text:
        await message.reply_text(usage)
        return
    chat_id = message.chat.id
    raw_text = str(message.reply_to_message.text.markdown)
    await set_welcome(chat_id, raw_text)
    await message.reply_text(
        "Welcome message has been successfully set."
    )


@app.on_message(filters.command("delwelcome") & ~filters.private)
@adminsOnly("can_change_info")
async def del_welcome_func(_, message):
    chat_id = message.chat.id
    await del_welcome(chat_id)
    await message.reply_text("Welcome message has been deleted.")


@app.on_message(filters.command("welcome") & ~filters.private)
@adminsOnly("can_change_info")
async def get_welcome_func(_, message):
    chat_id = message.chat.id
    welcome_message = await get_welcome(chat_id)
    await message.reply_text(welcome_message)
